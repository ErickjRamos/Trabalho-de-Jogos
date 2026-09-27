import math
import pygame


class Collide:
    
    # polygon/convex/axes/project sao do Trab4/polygonCollision/collision.py,
    # sem alteracao. circle_polygon foi adicionado pra este trabalho: em vez
    # de testar poligono contra poligono, testa a bola (um circulo) contra
    # um poligono qualquer, incluindo os concavos (via decomposicao).

   
    # Poligono x poligono (Trab4)
   

    @staticmethod
    def polygon(a, b):
        if not a.bounding_box.colliderect(b.bounding_box):
            return None

        for shape_a in a.convex_shapes:
            for shape_b in b.convex_shapes:
                if Collide.convex(shape_a.points, shape_b.points):
                    return shape_a, shape_b
        return None

    @staticmethod
    def convex(a, b):
        for axis in Collide.axes(a) + Collide.axes(b):
            min_a, max_a = Collide.project(a, axis)
            min_b, max_b = Collide.project(b, axis)
            if max_a < min_b or max_b < min_a:
                return False
        return True

    @staticmethod
    def axes(points):
        axes = []
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            dx = x2 - x1
            dy = y2 - y1
            axis = (-dy, dx)
            length = (axis[0] ** 2 + axis[1] ** 2) ** 0.5

            if length:
                axes.append((axis[0] / length, axis[1] / length))
        return axes

    @staticmethod
    def project(points, axis):
        values = [p[0] * axis[0] + p[1] * axis[1] for p in points]
        return min(values), max(values)

    # Circulo x poligono convexo -- versao estendida pra bola
   

    @staticmethod
    def _circle_convex(center, radius, points):
        axes = Collide.axes(points)

        # eixo extra: centro do circulo -> vertice mais proximo.
        # sem isso o SAT erra quando quem toca primeiro e um canto
        # do poligono, nao uma aresta
        closest = min(
            points,
            key=lambda p: (p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2
        )
        dx = closest[0] - center[0]
        dy = closest[1] - center[1]
        dist = math.hypot(dx, dy)
        if dist > 1e-6:
            axes = axes + [(dx / dist, dy / dist)]

        min_overlap = None
        min_axis = None

        for axis in axes:
            min_p, max_p = Collide.project(points, axis)
            c = center[0] * axis[0] + center[1] * axis[1]
            min_c, max_c = c - radius, c + radius

            overlap = min(max_p, max_c) - max(min_p, min_c)
            if overlap < 0:
                return None  # achou eixo separador, nao colide

            if min_overlap is None or overlap < min_overlap:
                min_overlap = overlap
                min_axis = axis

        # a normal tem que apontar do poligono pro circulo, senao
        # o push-out empurra a bola pro lado errado
        poly_center = (
            sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points),
        )
        to_circle = (center[0] - poly_center[0], center[1] - poly_center[1])
        if to_circle[0] * min_axis[0] + to_circle[1] * min_axis[1] < 0:
            min_axis = (-min_axis[0], -min_axis[1])

        return min_axis, min_overlap

    @staticmethod
    def circle_polygon(center, radius, polygon):
        """Testa um circulo contra um Polygon (convexo ou nao).
        Retorna (normal, profundidade) ou None."""
        cbox = pygame.Rect(
            center[0] - radius, center[1] - radius, radius * 2, radius * 2
        )
        if not polygon.bounding_box.colliderect(cbox):
            return None

        best = None
        for shape in polygon.convex_shapes:
            result = Collide._circle_convex(center, radius, shape.points)
            if result is None:
                continue
            axis, overlap = result
            if best is None or overlap > best[1]:
                best = (axis, overlap)

        return best

    @staticmethod
    def reflect(velocity, normal, restitution=1.0):
        """v' = v - (1+e)(v.n)n -- reflexao de velocidade num plano."""
        vx, vy = velocity
        nx, ny = normal
        dot = vx * nx + vy * ny
        if dot > 0:
            return velocity  # ja esta se afastando, nao reflete
        factor = (1 + restitution) * dot
        return (vx - factor * nx, vy - factor * ny)
