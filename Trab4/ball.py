import math
import pygame
import fx


class Ball:
    RADIUS = 10
    GRAVITY = 900.0
    MAX_SPEED = 1400.0
    COLOR = (250, 205, 70)

    def __init__(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.vel = [0.0, 0.0]
        self.radius = self.RADIUS
        self.launched = False
        self.trail = []

    def reset(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.vel = [0.0, 0.0]
        self.launched = False
        self.trail.clear()

    def apply_gravity(self, dt):
        if self.launched:
            self.vel[1] += self.GRAVITY * dt

    def clamp_speed(self):
        speed = math.hypot(self.vel[0], self.vel[1])
        if speed > self.MAX_SPEED:
            scale = self.MAX_SPEED / speed
            self.vel[0] *= scale
            self.vel[1] *= scale

    def integrate(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt

    def speed(self):
        return math.hypot(self.vel[0], self.vel[1])

    def update_trail(self):
        self.trail.append(tuple(self.pos))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, screen):
        n = len(self.trail)
        for i, p in enumerate(self.trail):
            t = (i + 1) / max(1, n)
            r = max(2, int(self.radius * t))
            fx.draw_glow_circle(screen, p, r + 3, (255, 205, 90), max_alpha=int(70 * t), layers=3)
            pygame.draw.circle(screen, (150, 120, 45), (int(p[0]), int(p[1])), r)

        # brilho externo (efeito neon ao redor da bola)
        fx.draw_glow_circle(screen, self.pos, self.radius + 11, (255, 220, 130),
                             max_alpha=175, layers=6)

        cx, cy = int(self.pos[0]), int(self.pos[1])
        pygame.draw.circle(screen, fx.shade(self.COLOR, -60), (cx, cy), self.radius)
        pygame.draw.circle(screen, self.COLOR, (cx, cy), self.radius - 2)

        # reflexo tipo "cromado" no canto superior esquerdo da bola
        hx = cx - int(self.radius * 0.35)
        hy = cy - int(self.radius * 0.35)
        pygame.draw.circle(screen, (255, 255, 255), (hx, hy), max(1, int(self.radius * 0.32)))

        pygame.draw.circle(screen, fx.shade(self.COLOR, -110), (cx, cy), self.radius, 1)
