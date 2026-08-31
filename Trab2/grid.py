from abc import ABC, abstractmethod
import pygame

class obj(ABC):
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        self.sprites = sprites

    def draw(self, screen):
        for s in self.sprites:
            screen.blit(s, (self.x, self.y))

    @abstractmethod
    def update(self, dt):
        pass

class Cell(obj):
    def __init__(self, row, col, x, y, size):
        super().__init__(x, y, [])
        self.row = row
        self.col = col
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.neighbor_mines = 0

    def draw(self, screen, font):
        if self.revealed:
            if self.is_mine:
                pygame.draw.rect(screen, (200, 50, 50), self.rect)
                pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.rect.width // 4)
            else:
                pygame.draw.rect(screen, (200, 200, 200), self.rect)
                if self.neighbor_mines > 0:
                    colors = [
                        (0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
                        (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)
                    ]
                    color = colors[min(self.neighbor_mines - 1, 7)]
                    txt = font.render(str(self.neighbor_mines), True, color)
                    screen.blit(txt, txt.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)
            if self.flagged:
                center_x, center_y = self.rect.center
                pygame.draw.polygon(screen, (255, 50, 50), [
                    (center_x - 5, center_y - 12),
                    (center_x + 8, center_y - 6),
                    (center_x - 5, center_y)
                ])
                pygame.draw.line(screen, (0, 0, 0), (center_x - 5, center_y - 12), (center_x - 5, center_y + 10), 2)

        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2)

    def update(self, dt):
        pass

class Grid(obj):
    def __init__(self, x, y, rows, cols, cell_size):
        super().__init__(x, y, [])
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cells = []

        for r in range(rows):
            row_cells = []
            for c in range(cols):
                cx = self.x + c * cell_size
                cy = self.y + r * cell_size
                row_cells.append(Cell(r, c, cx, cy, cell_size))
            self.cells.append(row_cells)

    def draw(self, screen, font):
        for row in self.cells:
            for cell in row:
                cell.draw(screen, font)

    def update(self, dt):
        pass