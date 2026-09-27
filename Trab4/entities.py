import math
import pygame
from shape import Polygon
import fx


def regular_polygon(center, radius, sides, rotation_deg=0):
    """Gera os vertices de um poligono regular (usado nos bumpers e
    na zona de bonus)."""
    points = []
    rot = math.radians(rotation_deg)
    for i in range(sides):
        ang = rot + (2 * math.pi * i / sides)
        points.append((
            center[0] + radius * math.cos(ang),
            center[1] + radius * math.sin(ang),
        ))
    return points


class Wall:
    """Obstaculo estatico que so reflete a bola (geometria/hitbox
    inalteradas -- so o desenho ganhou degrade + brilho neon)."""

    def __init__(self, points, color=(150, 158, 178), glow=None):
        self.polygon = Polygon(points)
        self.color = color
        self.glow_color = glow or fx.shade(color, 70)
        top = fx.shade(color, 45)
        bottom = fx.shade(color, -75)
        self.fill_surf, self.fill_offset = fx.gradient_polygon_surface(
            self.polygon.points, top, bottom
        )

    def draw(self, screen):
        fx.draw_polygon_glow(screen, self.polygon.points, self.glow_color,
                              layers=3, base_width=3, max_alpha=55)
        screen.blit(self.fill_surf, self.fill_offset)
        pygame.draw.polygon(screen, self.glow_color, self.polygon.points, 2)


class Bumper:
    """Hexagono que reflete a bola com bastante impulso (restituicao > 1,
    como um bumper de pinball de verdade) e tambem soma pontos -- ou
    seja, muda a trajetoria E aplica um efeito ao mesmo tempo."""

    POINTS_VALUE = 100
    RESTITUTION = 1.8

    def __init__(self, center, radius=26, color=(255, 60, 110)):
        self.center = center
        self.radius = radius
        self.color = color
        self.polygon = Polygon(regular_polygon(center, radius, 6))
        self.flash_timer = 0.0
        self.time = 0.0

        self.glow_color = fx.shade(color, 40)
        self.fill_normal, self.fill_offset = fx.gradient_polygon_surface(
            self.polygon.points, fx.shade(color, 55), fx.shade(color, -95)
        )

        flash_color = (255, 232, 140)
        self.flash_glow_color = flash_color
        self.fill_flash, _ = fx.gradient_polygon_surface(
            self.polygon.points, fx.shade(flash_color, 15), fx.shade(flash_color, -55)
        )

    def hit(self):
        self.flash_timer = 0.18
        return self.POINTS_VALUE

    def update(self, dt):
        self.time += dt
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

    def draw(self, screen):
        flashing = self.flash_timer > 0
        glow_color = self.flash_glow_color if flashing else self.glow_color
        base_alpha = 150 if flashing else int(70 + 25 * fx.pulse(self.time, speed=2.2))

        fx.draw_glow_circle(screen, self.center, self.radius + 16, glow_color,
                             max_alpha=base_alpha, layers=5)
        fx.draw_polygon_glow(screen, self.polygon.points, glow_color,
                              layers=4, base_width=4, max_alpha=110 if flashing else 60)

        screen.blit(self.fill_flash if flashing else self.fill_normal, self.fill_offset)
        pygame.draw.polygon(screen, glow_color, self.polygon.points, 2)


class BonusTrigger:
    """Zona de bonus que da pontos e aumenta a velocidade da bola."""

    POINTS_VALUE = 250
    SPEED_BOOST = 1.18
    COOLDOWN = 0.8

    def __init__(self, center, radius=42, color=(80, 255, 175)):
        self.center = center
        self.radius = radius
        self.polygon = Polygon(regular_polygon(center, radius, 5, rotation_deg=-90))
        self.color = color
        self.cooldown_timer = 0.0
        self.flash_timer = 0.0
        self.time = 0.0

        self.glow_color = fx.shade(color, 10)
        self.fill_normal, self.fill_offset = fx.gradient_polygon_surface(
            self.polygon.points, fx.shade(color, -30), fx.shade(color, -120)
        )

        flash_color = (225, 255, 235)
        self.flash_glow_color = flash_color
        self.fill_flash, _ = fx.gradient_polygon_surface(
            self.polygon.points, fx.shade(flash_color, 0), fx.shade(color, -20)
        )

    def update(self, dt):
        self.time += dt
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

    def try_trigger(self, ball_pos):
        """True se o efeito deve disparar agora (com cooldown pra nao
        somar pontos em todo frame enquanto a bola estiver dentro)."""
        if self.cooldown_timer > 0:
            return False
        if self.polygon.point_inside(ball_pos):
            self.cooldown_timer = self.COOLDOWN
            self.flash_timer = 0.3
            return True
        return False

    def draw(self, screen):
        flashing = self.flash_timer > 0
        glow_color = self.flash_glow_color if flashing else self.glow_color
        pulse_alpha = int(55 + 35 * fx.pulse(self.time, speed=2.6))
        base_alpha = 170 if flashing else pulse_alpha

        fx.draw_glow_circle(screen, self.center, self.radius + 22, glow_color,
                             max_alpha=base_alpha, layers=6)
        fx.draw_polygon_glow(screen, self.polygon.points, glow_color,
                              layers=4, base_width=4, max_alpha=130 if flashing else 70)

        screen.blit(self.fill_flash if flashing else self.fill_normal, self.fill_offset)
        pygame.draw.polygon(screen, (235, 255, 240) if flashing else self.color,
                             self.polygon.points, 2)
