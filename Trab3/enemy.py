import pygame
import os
import math
from abc import ABC, abstractmethod

SPRITE_SIZE = (48, 48)

def colored_sprite(color, size=SPRITE_SIZE):
    sprite = pygame.Surface(size)
    sprite.fill(color)
    return sprite

def load_upside_down_duck_image(filename, fallback_color):
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
                return pygame.transform.flip(img, False, True)
            except Exception:
                pass
    surf = colored_sprite(fallback_color)
    pygame.draw.polygon(surf, (0, 0, 0), [(12, 12), (36, 12), (24, 42)])
    return surf


class EnemyState(ABC):
    def __init__(self, enemy):
        self.E = enemy

    def draw(self, screen):
        pass

    def delete(self):
        pass

    @abstractmethod
    def update(self, dt, player_pos):
        pass


class ApproachingState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.sprite = load_upside_down_duck_image("base.png", (220, 50, 50))

    def update(self, dt, player_pos):
        self.E.pos[1] += self.E.speed * dt
        dx = player_pos[0] - self.E.pos[0]
        if abs(dx) > 5:
            self.E.pos[0] += (1 if dx > 0 else -1) * (self.E.speed * 0.3) * dt

        self.E.rect.x = int(self.E.pos[0])
        self.E.rect.y = int(self.E.pos[1])

    def draw(self, screen):
        screen.blit(self.sprite, self.E.pos)


class StunnedState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.sprite_crouch = load_upside_down_duck_image("crouch.png", (150, 150, 255))
        self.sprite_blink = load_upside_down_duck_image("blink.png", (200, 200, 255))
        self.sprite = self.sprite_crouch
        self.timer = 0.8
        self.blink_timer = 0.0

    def update(self, dt, player_pos):
        self.timer -= dt
        self.blink_timer += dt
        if int(self.blink_timer * 10) % 2 == 0:
            self.sprite = self.sprite_crouch
        else:
            self.sprite = self.sprite_blink

        if self.timer <= 0:
            self.E.change_state(ApproachingState)

    def draw(self, screen):
        screen.blit(self.sprite, self.E.pos)


class Enemy:
    def __init__(self, pos):
        self.pos = list(pos)
        self.speed = 130
        self.hp = 2
        self.rect = pygame.Rect(self.pos[0], self.pos[1], SPRITE_SIZE[0], SPRITE_SIZE[1])
        self.state = ApproachingState(self)

    def update(self, dt, player_pos):
        self.state.update(dt, player_pos)

    def draw(self, screen):
        self.state.draw(screen)

    def take_hit(self):
        self.hp -= 1
        if self.hp > 0:
            self.change_state(StunnedState)

    def change_state(self, new_state_cls):
        self.state.delete()
        self.state = new_state_cls(self)