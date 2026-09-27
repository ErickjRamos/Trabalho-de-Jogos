"""
fx.py - utilitarios de renderizacao (gradientes, brilho neon, texto com glow).

Este modulo e puramente estetico: nada aqui participa da fisica, das
colisoes (SAT) ou das regras do jogo. Ele so existe para deixar a mesa
com uma cara mais moderna (estilo "arcade neon"), reaproveitado por
entities.py, flipper.py, ball.py e main.py.
"""

import math
import pygame

_glow_cache = {}


def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def shade(color, amount):
    """Clareia (amount > 0) ou escurece (amount < 0) uma cor RGB."""
    return tuple(max(0, min(255, c + amount)) for c in color)


def vertical_gradient(size, color_top, color_bottom):
    """Surface (w, h) opaca com gradiente vertical liso."""
    w, h = max(1, int(size[0])), max(1, int(size[1]))
    surf = pygame.Surface((w, h))
    if h <= 1:
        surf.fill(color_top)
        return surf
    for y in range(h):
        t = y / (h - 1)
        pygame.draw.line(surf, lerp_color(color_top, color_bottom, t), (0, y), (w, y))
    return surf


def gradient_polygon_surface(points, color_top, color_bottom, margin=0):
    """Retorna (surface, offset) com o poligono preenchido por um degrade
    vertical, recortado exatamente na forma do poligono (via mascara alfa)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, min_y = min(xs) - margin, min(ys) - margin
    max_x, max_y = max(xs) + margin, max(ys) + margin
    w = max(1, int(round(max_x - min_x)))
    h = max(1, int(round(max_y - min_y)))
    local_points = [(p[0] - min_x, p[1] - min_y) for p in points]

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_points)

    grad = vertical_gradient((w, h), color_top, color_bottom).convert_alpha()
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return grad, (min_x, min_y)


def draw_polygon_glow(screen, points, color, layers=4, base_width=3, max_alpha=90, margin=18):
    """Desenha um brilho neon ao redor do contorno de um poligono (halo)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, min_y = min(xs) - margin, min(ys) - margin
    max_x, max_y = max(xs) + margin, max(ys) + margin
    w = max(1, int(round(max_x - min_x)))
    h = max(1, int(round(max_y - min_y)))
    local_points = [(p[0] - min_x, p[1] - min_y) for p in points]

    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(layers, 0, -1):
        width = base_width * i
        alpha = int(max_alpha * (1 - i / (layers + 1)))
        if alpha <= 0:
            continue
        pygame.draw.polygon(glow, (*color, alpha), local_points, width)
    screen.blit(glow, (min_x, min_y), special_flags=pygame.BLEND_RGBA_ADD)


def get_radial_glow(radius, color, max_alpha=190, layers=7):
    key = (radius, color, max_alpha, layers)
    surf = _glow_cache.get(key)
    if surf is not None:
        return surf
    size = max(2, radius * 2)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for i in range(layers, 0, -1):
        r = max(1, int(radius * i / layers))
        alpha = int(max_alpha * (1 - i / layers) ** 2)
        pygame.draw.circle(surf, (*color, alpha), (size // 2, size // 2), r)
    _glow_cache[key] = surf
    return surf


def draw_glow_circle(screen, pos, radius, color, max_alpha=190, layers=7):
    surf = get_radial_glow(int(radius), color, max_alpha, layers)
    size = surf.get_width()
    screen.blit(surf, (pos[0] - size / 2, pos[1] - size / 2), special_flags=pygame.BLEND_RGBA_ADD)


def draw_text_glow(screen, font, text, pos, color, glow_color=None, center=False, glow_radius=3, glow_alpha=70):
    """Texto com um leve halo neon (poucas copias deslocadas, alpha normal
    para nao saturar em branco quando o texto e grande)."""
    glow_color = glow_color or color
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)

    if glow_radius > 0:
        glow = font.render(text, True, glow_color)
        glow.set_alpha(glow_alpha)
        for dx, dy in ((glow_radius, 0), (-glow_radius, 0), (0, glow_radius), (0, -glow_radius)):
            screen.blit(glow, (rect.x + dx, rect.y + dy))

    screen.blit(surf, rect)
    return rect


def rounded_panel(size, color, radius=14, border_color=None, border_width=2):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=radius)
    if border_color:
        pygame.draw.rect(surf, border_color, surf.get_rect(), border_width, border_radius=radius)
    return surf


def pulse(t, speed=3.0, lo=0.0, hi=1.0):
    """Valor oscilando suavemente entre lo e hi (usado em brilhos pulsantes)."""
    s = 0.5 + 0.5 * math.sin(t * speed)
    return lo + (hi - lo) * s
