import pygame
import os
from abc import ABC, abstractmethod

EVENT_SPAWN_PROJECTILE = pygame.USEREVENT + 2
EVENT_PLAYER_HIT = pygame.USEREVENT + 3

SPRITE_SIZE = (48, 48)

def colored_sprite(color, size=SPRITE_SIZE):
    sprite = pygame.Surface(size)
    sprite.fill(color)
    return sprite

def load_duck_image(filename, fallback_color, flip_h=False):
    possible_paths = [
        filename,
        os.path.join("images", "duck", filename),
    ]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths.extend([
        os.path.join(base_dir, filename),
        os.path.join(base_dir, "images", "duck", filename),
    ])

    for path in possible_paths:
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img.convert_alpha(), SPRITE_SIZE)
                if flip_h:
                    img = pygame.transform.flip(img, True, False)
                return img
            except Exception:
                pass
    surf = colored_sprite(fallback_color)
    if flip_h:
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, 10, 48))
    return surf


class PlayerState(ABC):
    def __init__(self, player):
        self.P = player

    def draw(self, screen):
        pass

    def delete(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def action_1(self):
        pass


class NormalState(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.sprites_right = [
            load_duck_image("base.png", (0, 200, 255), flip_h=False),
            load_duck_image("step.png", (0, 180, 230), flip_h=False),
            load_duck_image("wing.png", (0, 220, 255), flip_h=False)
        ]
        self.sprites_left = [
            load_duck_image("base.png", (0, 200, 255), flip_h=True),
            load_duck_image("step.png", (0, 180, 230), flip_h=True),
            load_duck_image("wing.png", (0, 220, 255), flip_h=True)
        ]
        self.anim_timer = 0.0
        self.anim_frame = 0

    def update(self, dt):
        if self.P.is_moving:
            self.anim_timer += dt
            if self.anim_timer >= 0.12:
                self.anim_timer = 0.0
                self.anim_frame = (self.anim_frame + 1) % len(self.sprites_right)
        else:
            self.anim_frame = 0

    def draw(self, screen):
        sprites = self.sprites_left if self.P.facing_left else self.sprites_right
        screen.blit(sprites[self.anim_frame], self.P.pos)

    def action_1(self):
        spawn_pos = (self.P.pos[0] + SPRITE_SIZE[0] // 2, self.P.pos[1])
        evt = pygame.event.Event(EVENT_SPAWN_PROJECTILE, {"pos": spawn_pos, "dir": (0, -1)})
        pygame.event.post(evt)


class InvincibleState(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.crouch_r = load_duck_image("crouch.png", (255, 100, 100), flip_h=False)
        self.crouch_l = load_duck_image("crouch.png", (255, 100, 100), flip_h=True)
        self.blink_r = load_duck_image("blink.png", (200, 200, 200), flip_h=False)
        self.blink_l = load_duck_image("blink.png", (200, 200, 200), flip_h=True)
        self.timer = 2.0
        self.blink_timer = 0.0

    def update(self, dt):
        self.timer -= dt
        self.blink_timer += dt
        if self.timer <= 0:
            self.P.change_state(NormalState)

    def draw(self, screen):
        is_blink = (int(self.blink_timer * 10) % 2 == 1)
        if self.P.facing_left:
            sprite = self.blink_l if is_blink else self.crouch_l
        else:
            sprite = self.blink_r if is_blink else self.crouch_r
        screen.blit(sprite, self.P.pos)

    def action_1(self):
        spawn_pos = (self.P.pos[0] + SPRITE_SIZE[0] // 2, self.P.pos[1])
        evt = pygame.event.Event(EVENT_SPAWN_PROJECTILE, {"pos": spawn_pos, "dir": (0, -1)})
        pygame.event.post(evt)


class Player:
    def __init__(self, pos):
        self.ground_y = pos[1]
        self.pos = [pos[0], self.ground_y]
        self.speed = 320
        self.max_hp = 5
        self.hp = 5
        self.facing_left = False
        self.is_moving = False
        self.rect = pygame.Rect(self.pos[0], self.pos[1], SPRITE_SIZE[0], SPRITE_SIZE[1])
        self.state = NormalState(self)

    def update(self, dt):
        if self.hp <= 0:
            return
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        
        if dx < 0:
            self.facing_left = False
            self.is_moving = True
        elif dx > 0:
            self.facing_left = True
            self.is_moving = True
        else:
            self.is_moving = False

        self.pos[0] += dx * self.speed * dt
        self.pos[0] = max(0, min(800 - SPRITE_SIZE[0], self.pos[0]))
        self.pos[1] = self.ground_y

        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])

        self.state.update(dt)

    def draw(self, screen):
        if self.hp > 0:
            self.state.draw(screen)

    def action_1(self):
        if self.hp > 0:
            self.state.action_1()

    def take_damage(self):
        if self.hp > 0 and not isinstance(self.state, InvincibleState):
            self.hp -= 1
            if self.hp > 0:
                self.change_state(InvincibleState)
            pygame.event.post(pygame.event.Event(EVENT_PLAYER_HIT, {"hp": self.hp}))

    def change_state(self, new_state_cls):
        self.state.delete()
        self.state = new_state_cls(self)

    def reset(self, pos):
        self.ground_y = pos[1]
        self.pos = [pos[0], self.ground_y]
        self.hp = self.max_hp
        self.facing_left = False
        self.is_moving = False
        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])
        self.change_state(NormalState)