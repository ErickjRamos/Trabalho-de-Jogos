import math
import pygame


class Polygon:


    def __init__(self, points):
        self.points = list(points)
        self.update_geometry()

  
    def update_geometry(self):
        self.bounding_box = self.get_bounding_box()
        self.convex = self.is_convex()

        if self.convex:
            self.convex_shapes = [self]
            self.decomposition_edges = []
        else:
            self.convex_shapes, self.decomposition_edges = \
                self.decompose(self.points)

    def get_bounding_box(self):
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]

        return pygame.Rect(
            min(xs), min(ys),
            max(xs) - min(xs),
            max(ys) - min(ys)
        )

    @property
    def centroid(self):
        n = len(self.points)
        cx = sum(p[0] for p in self.points) / n
        cy = sum(p[1] for p in self.points) / n
        return (cx, cy)

    def cross(self, a, b, c):
        return (
            (b[0] - a[0]) * (c[1] - b[1])
            - (b[1] - a[1]) * (c[0] - b[0])
        )

    def is_convex(self, points=None):
        points = self.points if points is None else points

        signs = []
        for i in range(len(points)):
            a = points[i - 1]
            b = points[i]
            c = points[(i + 1) % len(points)]

            cross = self.cross(a, b, c)
            if abs(cross) > 0.0001:
                signs.append(cross > 0)

        return not signs or all(s == signs[0] for s in signs)

    # Ponto dentro do polígono (usado pelas zonas de bônus)
   

    def point_inside(self, point, polygon=None):
        polygon = self.points if polygon is None else polygon
        x, y = point
        inside = False

        for i in range(len(polygon)):
            a = polygon[i]
            b = polygon[(i + 1) % len(polygon)]

            if (a[1] > y) != (b[1] > y):
                x_intersection = (
                    (b[0] - a[0]) *
                    (y - a[1]) /
                    (b[1] - a[1]) +
                    a[0]
                )
                if x < x_intersection:
                    inside = not inside

        return inside



    def segments_intersect(self, a, b, c, d):
        def orientation(p, q, r):
            value = self.cross(p, q, r)
            if abs(value) < 0.0001:
                return 0
            return 1 if value > 0 else -1

        o1 = orientation(a, b, c)
        o2 = orientation(a, b, d)
        o3 = orientation(c, d, a)
        o4 = orientation(c, d, b)

        return o1 != o2 and o3 != o4

    def valid_diagonal(self, a, b, points):
        for i in range(len(points)):
            c = points[i]
            d = points[(i + 1) % len(points)]

            if c in (a, b) or d in (a, b):
                continue

            if self.segments_intersect(a, b, c, d):
                return False

        midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return self.point_inside(midpoint, points)

    def decompose(self, points):
        if self.is_convex(points):
            return [Polygon(points)], []

        n = len(points)
        for i in range(n):
            prev = points[i - 1]
            curr = points[i]
            nxt = points[(i + 1) % n]

            if self.cross(prev, curr, nxt) <= 0:
                continue

            triangle = [prev, curr, nxt]
            remaining = points[:i] + points[i + 1:]

            if not self.valid_diagonal(prev, nxt, points):
                continue

            if self.is_convex(remaining):
                return (
                    [Polygon(triangle), Polygon(remaining)],
                    [(prev, nxt)]
                )

            shapes, edges = self.decompose(remaining)
            return (
                [Polygon(triangle)] + shapes,
                [(prev, nxt)] + edges
            )

        return [Polygon(points)], []



    def rotated_points(self, base_points, pivot, angle_rad):
        px, py = pivot
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        result = []
        for x, y in base_points:
            dx = x - px
            dy = y - py
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            result.append((px + rx, py + ry))
        return result

    def set_points(self, points):
        self.points = list(points)
        self.update_geometry()

    
    # Desenho
    

    def draw(self, screen, color, outline=(255, 255, 255), width=2):
        pygame.draw.polygon(screen, color, self.points)
        if outline and width:
            pygame.draw.polygon(screen, outline, self.points, width)
