import pygame
import random
import math
import sys
from player import Player, EVENT_SPAWN_PROJECTILE, EVENT_PLAYER_HIT
from enemy import Enemy

EVENT_SPAWN_ENEMY = pygame.USEREVENT + 1
WIDTH, HEIGHT = 800, 600
FPS = 60


class Projectile:
    def __init__(self, pos, direction):
        self.pos = list(pos)
        self.dir = direction
        self.speed = 500
        self.rect = pygame.Rect(self.pos[0] - 5, self.pos[1] - 5, 10, 10)

    def update(self, dt):
        norm = math.hypot(self.dir[0], self.dir[1])
        if norm > 0:
            dx = (self.dir[0] / norm) * self.speed * dt
            dy = (self.dir[1] / norm) * self.speed * dt
            self.pos[0] += dx
            self.pos[1] += dy
            self.rect.x = int(self.pos[0])
            self.rect.y = int(self.pos[1])

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 220, 0), (int(self.pos[0]), int(self.pos[1])), 5)


def handle_input(player, game_over):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    return ("restart",)
            else:
                if event.key == pygame.K_SPACE:
                    player.action_1()
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if event.button == 1:
                player.action_1()

        elif event.type == EVENT_SPAWN_ENEMY and not game_over:
            x_pos = random.randint(20, 740)
            return ("spawn_enemy", (x_pos, -50))

        elif event.type == EVENT_SPAWN_PROJECTILE and not game_over:
            return ("spawn_projectile", event.pos, event.dir)

        elif event.type == EVENT_PLAYER_HIT:
            return ("player_hit", event.hp)

    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Atividade 3 - Defesa de Patos")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 60)

    ground_y = 500
    player = Player((400, ground_y))
    enemies = []
    projectiles = []
    score = 0
    game_over = False

    pygame.time.set_timer(EVENT_SPAWN_ENEMY, 1200)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        event_result = handle_input(player, game_over)
        if event_result:
            if event_result[0] == "restart":
                player.reset((400, ground_y))
                enemies.clear()
                projectiles.clear()
                score = 0
                game_over = False
            elif event_result[0] == "spawn_enemy":
                enemies.append(Enemy(event_result[1]))
            elif event_result[0] == "spawn_projectile":
                projectiles.append(Projectile(event_result[1], event_result[2]))
            elif event_result[0] == "player_hit":
                if event_result[1] <= 0:
                    game_over = True

        if not game_over:
            player.update(dt)

            for proj in projectiles[:]:
                proj.update(dt)
                if proj.pos[1] < -20 or proj.pos[0] < -20 or proj.pos[0] > 820:
                    projectiles.remove(proj)

            for enemy in enemies[:]:
                enemy.update(dt, player.pos)

                for proj in projectiles[:]:
                    if enemy.rect.colliderect(proj.rect):
                        projectiles.remove(proj)
                        enemy.take_hit()
                        if enemy.hp <= 0:
                            enemies.remove(enemy)
                            score += 10
                        break

                if enemy.rect.colliderect(player.rect) or enemy.rect.y >= ground_y:
                    player.take_damage()
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if player.hp <= 0:
                        game_over = True

        screen.fill((30, 30, 45))
        pygame.draw.rect(screen, (40, 140, 50), (0, ground_y + 48, WIDTH, HEIGHT - (ground_y + 48)))

        for proj in projectiles:
            proj.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        hud_text = font.render(f"Vida: {player.hp} | Score: {score} | [A/D] ou [Setas]: Mover | [ESPAÇO]: Atirar", True, (255, 255, 255))
        screen.blit(hud_text, (10, 10))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            go_text = big_font.render("GAME OVER", True, (255, 60, 60))
            sub_text = font.render(f"Score Final: {score} - Pressione [R] para Reiniciar", True, (255, 255, 255))
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()