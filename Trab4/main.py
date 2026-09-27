
import math
import random
import sys
import pygame

from shape import Polygon
from collision import Collide
from ball import Ball
from flipper import Flipper
from entities import Wall, Bumper, BonusTrigger, regular_polygon
import fx

WIDTH, HEIGHT = 500, 800
FIELD_LEFT, FIELD_RIGHT = 20, 430
LANE_LEFT, LANE_RIGHT = 450, 490

# Paleta "arcade neon" - so estetica, nao influencia fisica/colisao.
BG_TOP = (14, 10, 34)
BG_BOTTOM = (30, 14, 48)
NEON_CYAN = (110, 225, 255)
NEON_PINK = (255, 90, 160)
NEON_YELLOW = (250, 210, 90)
NEON_GREEN = (110, 255, 190)
PANEL_COLOR = (14, 10, 28, 235)
PANEL_BORDER = (120, 90, 200, 220)

STATE_READY = "ready"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"

MAX_CHARGE_TIME = 1.1
LAUNCH_MIN_SPEED = 550
LAUNCH_MAX_SPEED = 1250

SUBSTEPS = 4
RESTITUTION_WALL = 0.65
RESTITUTION_FLIPPER = 0.55
FLIPPER_KICK = 0.9


def build_table():
    walls = [
        # bordas
        Wall([(0, 120), (20, 120), (20, 760), (0, 760)],
             color=(110, 120, 150), glow=NEON_CYAN),                          # parede esquerda
        Wall([(FIELD_RIGHT, 120), (LANE_LEFT, 120),
              (LANE_LEFT, 760), (FIELD_RIGHT, 760)],
             color=(110, 120, 150), glow=NEON_CYAN),                          # separador campo/lançador
        Wall([(LANE_RIGHT, 20), (500, 20), (500, 780), (LANE_RIGHT, 780)],
             color=(110, 120, 150), glow=NEON_CYAN),                          # parede externa do lançador
        Wall([(LANE_LEFT, 760), (500, 760), (500, 780), (LANE_LEFT, 780)],
             color=(110, 120, 150), glow=NEON_CYAN),                          # piso do lançador
        Wall([(20, 20), (FIELD_RIGHT, 20), (FIELD_RIGHT, 40), (20, 40)],
             color=(110, 120, 150), glow=NEON_CYAN),                          # topo do campo

        # canto (triangulo - regiao NAO retangular/circular);
        # o canto superior direito fica sem cunha de propósito, pois é
        # por ali que a bola entra vinda do lançador (ver defletor abaixo)
        Wall([(20, 40), (20, 95), (75, 40)], color=(110, 120, 150), glow=NEON_CYAN),

        # defletor que leva a bola lançada de volta ao campo (triangulo)
        Wall([(FIELD_RIGHT, 40), (500, 20), (500, 95)],
             color=(140, 95, 210), glow=(190, 150, 255)),

        # slingshots acima dos flippers (triangulos)
        Wall([(60, 660), (150, 660), (60, 585)],
             color=(220, 70, 170), glow=NEON_PINK),
        Wall([(FIELD_RIGHT - 60, 660), (FIELD_RIGHT - 150, 660), (FIELD_RIGHT - 60, 585)],
             color=(220, 70, 170), glow=NEON_PINK),
    ]

    bumpers = [
        Bumper((170, 230)),
        Bumper((280, 230)),
        Bumper((225, 150)),
    ]

    triggers = [
        BonusTrigger((225, 440), radius=42),
    ]

    flippers = [
        Flipper(pivot=(150, 715), rest_angle_deg=35, active_angle_deg=-42, facing=1),
        Flipper(pivot=(300, 715), rest_angle_deg=-35, active_angle_deg=42, facing=-1),
    ]

    return walls, bumpers, triggers, flippers


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Pinball - Colisao Poligonal (SAT)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 46, bold=True)

        self.walls, self.bumpers, self.triggers, self.flippers = build_table()
        self.left_flipper, self.right_flipper = self.flippers

        self.lane_rest_pos = (470, 745)
        self.ball = Ball(self.lane_rest_pos)

        self.score = 0
        self.lives = 3
        self.state = STATE_READY
        self.charge = 0.0
        self.charging = False

        self.collidables = self.walls + self.bumpers

        self.stuck_timer = 0.0
        self.stuck_ref_pos = None

        # --- estetica: fundo, estrelas e paineis (nao afeta jogabilidade) ---
        self.time = 0.0
        self.bg_surface = fx.vertical_gradient((WIDTH, HEIGHT), BG_TOP, BG_BOTTOM)
        self.star_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.stars = [
            {
                "pos": (random.uniform(4, WIDTH - 4), random.uniform(4, HEIGHT - 4)),
                "r": random.uniform(1.0, 2.2),
                "base": random.uniform(70, 170),
                "speed": random.uniform(0.8, 2.4),
                "phase": random.uniform(0, math.tau),
            }
            for _ in range(70)
        ]

        self.hud_panel = fx.rounded_panel((WIDTH, 44), PANEL_COLOR, radius=0,
                                           border_color=None)
        pygame.draw.line(self.hud_panel, PANEL_BORDER, (0, 43), (WIDTH, 43), 2)

    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.state = STATE_READY
        self.ball.reset(self.lane_rest_pos)

    def new_ball(self):
        self.ball.reset(self.lane_rest_pos)
        self.state = STATE_READY


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.left_flipper.set_active(True)
                if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_l):
                    self.right_flipper.set_active(True)
                if event.key == pygame.K_SPACE and self.state == STATE_READY:
                    self.charging = True
                if event.key == pygame.K_r:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.left_flipper.set_active(False)
                if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_l):
                    self.right_flipper.set_active(False)
                if event.key == pygame.K_SPACE and self.charging:
                    self.launch_ball()

    def launch_ball(self):
        self.charging = False
        power = self.charge / MAX_CHARGE_TIME
        power = max(0.0, min(1.0, power))
        speed = LAUNCH_MIN_SPEED + (LAUNCH_MAX_SPEED - LAUNCH_MIN_SPEED) * power
        self.ball.vel[0] = 0.0
        self.ball.vel[1] = -speed
        self.ball.launched = True
        self.state = STATE_PLAYING
        self.charge = 0.0
        self.stuck_timer = 0.0
        self.stuck_ref_pos = None


    def update(self, dt):
        self.time += dt
        for flipper in self.flippers:
            flipper.update(dt)
        for bumper in self.bumpers:
            bumper.update(dt)
        for trigger in self.triggers:
            trigger.update(dt)

        if self.state == STATE_READY and self.charging:
            self.charge = min(MAX_CHARGE_TIME, self.charge + dt)

        if self.state != STATE_PLAYING:
            return

        sub_dt = dt / SUBSTEPS
        for _ in range(SUBSTEPS):
            self.ball.apply_gravity(sub_dt)
            self.ball.clamp_speed()
            self.ball.integrate(sub_dt)
            self.resolve_collisions()

        self.ball.update_trail()

        # zonas de bonus: efeito sem alterar a trajetoria
        for trigger in self.triggers:
            if trigger.try_trigger(self.ball.pos):
                self.score += trigger.POINTS_VALUE
                speed = self.ball.speed()
                new_speed = min(Ball.MAX_SPEED, speed * trigger.SPEED_BOOST + 40)
                if speed > 1e-3:
                    scale = new_speed / speed
                    self.ball.vel[0] *= scale
                    self.ball.vel[1] *= scale

        # a bola escapou por baixo dos flippers, perde a vida
        if self.ball.pos[1] - self.ball.radius > HEIGHT:
            self.lose_ball()
            return

        self.check_stuck(dt)

    def check_stuck(self, dt):
        if self.stuck_ref_pos is None:
            self.stuck_ref_pos = tuple(self.ball.pos)
            self.stuck_timer = 0.0
            return

        moved = math.hypot(
            self.ball.pos[0] - self.stuck_ref_pos[0],
            self.ball.pos[1] - self.stuck_ref_pos[1],
        )

        if moved < 6:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0.0
            self.stuck_ref_pos = tuple(self.ball.pos)

        if self.stuck_timer >= 1.2:
            self.stuck_timer = 0.0
            self.stuck_ref_pos = None
            self.lose_ball()

    def resolve_collisions(self):
        # paredes e cantos (apenas reflete)
        for wall in self.walls:
            result = Collide.circle_polygon(self.ball.pos, self.ball.radius, wall.polygon)
            if result:
                self.apply_collision(result, RESTITUTION_WALL)

        # bumpers (reflete + soma pontos)
        for bumper in self.bumpers:
            result = Collide.circle_polygon(self.ball.pos, self.ball.radius, bumper.polygon)
            if result:
                self.apply_collision(result, Bumper.RESTITUTION)
                self.score += bumper.hit()

        # flippers (reflete + transfere parte da velocidade angular)
        for flipper in self.flippers:
            result = Collide.circle_polygon(self.ball.pos, self.ball.radius, flipper.polygon)
            if result:
                normal, depth = result
                self.push_out(normal, depth)
                self.ball.vel[0], self.ball.vel[1] = Collide.reflect(
                    self.ball.vel, normal, RESTITUTION_FLIPPER
                )
                tip_vx, tip_vy = flipper.tip_speed_at(self.ball.pos)
                self.ball.vel[0] += tip_vx * FLIPPER_KICK
                self.ball.vel[1] += tip_vy * FLIPPER_KICK
                self.ball.clamp_speed()

    def apply_collision(self, result, restitution):
        normal, depth = result
        self.push_out(normal, depth)
        self.ball.vel[0], self.ball.vel[1] = Collide.reflect(
            self.ball.vel, normal, restitution
        )

    def push_out(self, normal, depth):
        self.ball.pos[0] += normal[0] * depth
        self.ball.pos[1] += normal[1] * depth

    def lose_ball(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAMEOVER
        else:
            self.new_ball()

    def draw(self):
        self.screen.blit(self.bg_surface, (0, 0))
        self.draw_stars()

        for wall in self.walls:
            wall.draw(self.screen)
        for trigger in self.triggers:
            trigger.draw(self.screen)
        for bumper in self.bumpers:
            bumper.draw(self.screen)
        for flipper in self.flippers:
            flipper.draw(self.screen)

        if self.state in (STATE_READY, STATE_PLAYING):
            self.ball.draw(self.screen)

        self.draw_hud()

        if self.state == STATE_GAMEOVER:
            self.draw_center_text("FIM DE JOGO", "Pressione R para reiniciar")
        elif self.state == STATE_READY:
            self.draw_charge_meter()

        pygame.display.flip()

    def draw_stars(self):
        self.star_surf.fill((0, 0, 0, 0))
        for s in self.stars:
            alpha = s["base"] * fx.pulse(self.time, speed=s["speed"], lo=0.35, hi=1.0)
            x, y = s["pos"]
            pygame.draw.circle(self.star_surf, (255, 255, 255, int(alpha)),
                                (int(x), int(y)), max(1, int(s["r"])))
        self.screen.blit(self.star_surf, (0, 0))

    def draw_hud(self):
        self.screen.blit(self.hud_panel, (0, 0))

        fx.draw_text_glow(self.screen, self.font, f"PONTOS {self.score:05d}",
                           (16, 12), (235, 245, 255), glow_color=NEON_CYAN, glow_radius=3)

        lives_txt = "BOLA " + "\u25CF " * self.lives
        lives_surf = self.font.render(lives_txt, True, (235, 235, 235))
        fx.draw_text_glow(self.screen, self.font, lives_txt,
                           (WIDTH - lives_surf.get_width() - 16, 12),
                           (255, 210, 230), glow_color=NEON_PINK, glow_radius=3)

        if self.state == STATE_READY:
            alpha = int(150 + 90 * fx.pulse(self.time, speed=3.2))
            hint_surf = self.small_font.render(
                "SEGURE ESPACO p/ carregar  \u2022  SOLTE p/ lancar", True, NEON_YELLOW
            )
            hint_surf.set_alpha(alpha)
            self.screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 28))

    def draw_charge_meter(self):
        if self.charge <= 0:
            return
        ratio = min(1.0, self.charge / MAX_CHARGE_TIME)
        bar_h = 120
        bar_w = 14
        x, top_y = LANE_LEFT + 8, 760 - bar_h
        fill_h = int(bar_h * ratio)
        fill_y = 760 - fill_h

        bar_color = fx.lerp_color(NEON_CYAN, NEON_PINK, ratio)

        track = fx.rounded_panel((bar_w, bar_h), (20, 20, 30, 160), radius=5,
                                  border_color=(90, 90, 110, 200), border_width=1)
        self.screen.blit(track, (x, top_y))

        if fill_h > 0:
            glow_alpha = 140 if ratio < 0.999 else int(160 + 60 * fx.pulse(self.time, speed=6.0))
            fx.draw_glow_circle(self.screen, (x + bar_w / 2, fill_y), bar_w,
                                 bar_color, max_alpha=glow_alpha, layers=4)
            fill = fx.rounded_panel((bar_w, fill_h), (*bar_color, 235), radius=4)
            self.screen.blit(fill, (x, fill_y))

    def draw_center_text(self, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 4, 16, 175))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 340, 130
        panel = fx.rounded_panel((panel_w, panel_h), (22, 14, 40, 210), radius=18,
                                  border_color=(*NEON_PINK, 200), border_width=2)
        panel_pos = (WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2)
        self.screen.blit(panel, panel_pos)

        fx.draw_text_glow(self.screen, self.big_font, title,
                           (WIDTH // 2, HEIGHT // 2 - 22), (255, 110, 130),
                           glow_color=NEON_PINK, center=True, glow_radius=4, glow_alpha=140)
        fx.draw_text_glow(self.screen, self.font, subtitle,
                           (WIDTH // 2, HEIGHT // 2 + 28), (235, 235, 245),
                           glow_color=NEON_CYAN, center=True, glow_radius=2, glow_alpha=90)

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 1 / 30)  # evita saltos grandes se a janela travar
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
