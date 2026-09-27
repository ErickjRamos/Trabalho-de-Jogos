import math
from shape import Polygon
import pygame
import fx


class Flipper:

    LENGTH = 95
    BASE_WIDTH = 24
    TIP_WIDTH = 10
    ANGULAR_SPEED = math.radians(720)

    REST_COLOR = (70, 170, 235)
    ACTIVE_COLOR = (130, 235, 255)

    def __init__(self, pivot, rest_angle_deg, active_angle_deg, facing=1):

        self.pivot = pivot
        self.rest_angle = math.radians(rest_angle_deg)
        self.active_angle = math.radians(active_angle_deg)
        self.angle = self.rest_angle
        self.active = False
        self.angular_velocity = 0.0

        half_base = self.BASE_WIDTH / 2
        half_tip = self.TIP_WIDTH / 2
        length = self.LENGTH * facing

        # pontos locais, relativos ao pivo, com angulo 0
        self.base_points = [
            (0, -half_base),
            (0, half_base),
            (length, half_tip),
            (length, -half_tip),
        ]

        self.polygon = Polygon(self._world_points(self.angle))

    def _world_points(self, angle):
        px, py = self.pivot
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        result = []
        for x, y in self.base_points:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            result.append((px + rx, py + ry))
        return result

    def set_active(self, active):
        self.active = active

    def update(self, dt):
        target = self.active_angle if self.active else self.rest_angle
        diff = target - self.angle
        step = self.ANGULAR_SPEED * dt

        prev_angle = self.angle
        if abs(diff) <= step:
            self.angle = target
        else:
            self.angle += step if diff > 0 else -step

        self.angular_velocity = (self.angle - prev_angle) / dt if dt > 0 else 0.0
        self.polygon.set_points(self._world_points(self.angle))

    def tip_speed_at(self, point):

        rx = point[0] - self.pivot[0]
        ry = point[1] - self.pivot[1]
        vx = -self.angular_velocity * ry
        vy = self.angular_velocity * rx
        return (vx, vy)

    def draw(self, screen):
        base = self.ACTIVE_COLOR if self.active else self.REST_COLOR
        glow_color = (185, 255, 255) if self.active else (100, 195, 255)

        fx.draw_polygon_glow(screen, self.polygon.points, glow_color,
                              layers=4, base_width=4,
                              max_alpha=140 if self.active else 65)

        fill, offset = fx.gradient_polygon_surface(
            self.polygon.points, fx.shade(base, 45), fx.shade(base, -95)
        )
        screen.blit(fill, offset)

        # pequeno brilho na "articulacao" do flipper
        fx.draw_glow_circle(screen, self.pivot, 14, glow_color, max_alpha=120, layers=4)
        pygame.draw.circle(screen, fx.shade(base, -40), (int(self.pivot[0]), int(self.pivot[1])), 6)

        pygame.draw.polygon(screen, glow_color, self.polygon.points, 2)
