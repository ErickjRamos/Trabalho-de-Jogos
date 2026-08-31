import pygame
import sys
import random
from grid import Grid

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Campo Minado")

GRID_ROWS, GRID_COLS = 10, 10
NUM_MINES = 15
CELL_SIZE = 40

GRID_X = (WIDTH - (GRID_COLS * CELL_SIZE)) // 2
GRID_Y = (HEIGHT - (GRID_ROWS * CELL_SIZE)) // 2 + 30

FONT_LARGE = pygame.font.Font(None, 64)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)


STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"

class MinesweeperGame:
    def __init__(self):
        self.state = STATE_MENU
        self.reset_game()

    def reset_game(self):
        self.grid = Grid(GRID_X, GRID_Y, GRID_ROWS, GRID_COLS, CELL_SIZE)
        self.first_click = True
        self.flags_left = NUM_MINES
        self.cursor_pos = [0, 0]

    def place_mines(self, safe_row, safe_col):
        positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if (r, c) != (safe_row, safe_col)]
        mine_positions = random.sample(positions, NUM_MINES)

        for r, c in mine_positions:
            self.grid.cells[r][c].is_mine = True

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if not self.grid.cells[r][c].is_mine:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                                if self.grid.cells[nr][nc].is_mine:
                                    count += 1
                    self.grid.cells[r][c].neighbor_mines = count

    def reveal_cell(self, r, c):
        if not (0 <= r < GRID_ROWS and 0 <= c < GRID_COLS):
            return
        cell = self.grid.cells[r][c]
        if cell.revealed or cell.flagged:
            return

        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False

        cell.revealed = True

        if cell.is_mine:
            self.state = STATE_GAME_OVER
            self.reveal_all_mines()
            return

        if cell.neighbor_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr != 0 or dc != 0:
                        self.reveal_cell(r + dr, c + dc)

        self.check_victory()

    def toggle_flag(self, r, c):
        cell = self.grid.cells[r][c]
        if not cell.revealed:
            cell.flagged = not cell.flagged
            self.flags_left += -1 if cell.flagged else 1

    def reveal_all_mines(self):
        for row in self.grid.cells:
            for cell in row:
                if cell.is_mine:
                    cell.revealed = True

    def check_victory(self):
        unrevealed_non_mines = 0
        for row in self.grid.cells:
            for cell in row:
                if not cell.is_mine and not cell.revealed:
                    unrevealed_non_mines += 1
        if unrevealed_non_mines == 0:
            self.state = STATE_VICTORY

    def handle_click(self, pos, is_right_click):
        if self.state != STATE_PLAYING:
            return
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cell = self.grid.cells[r][c]
                if cell.rect.collidepoint(pos):
                    self.cursor_pos = [r, c]
                    if is_right_click:
                        self.toggle_flag(r, c)
                    else:
                        self.reveal_cell(r, c)
                    return

    def handle_key(self, key):
        if self.state == STATE_MENU:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.reset_game()
                self.state = STATE_PLAYING

        elif self.state == STATE_PLAYING:
            r, c = self.cursor_pos
            if key == pygame.K_UP and r > 0:
                self.cursor_pos[0] -= 1
            elif key == pygame.K_DOWN and r < GRID_ROWS - 1:
                self.cursor_pos[0] += 1
            elif key == pygame.K_LEFT and c > 0:
                self.cursor_pos[1] -= 1
            elif key == pygame.K_RIGHT and c < GRID_COLS - 1:
                self.cursor_pos[1] += 1
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.reveal_cell(r, c)
            elif key == pygame.K_f:
                self.toggle_flag(r, c)

        elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.reset_game()
                self.state = STATE_PLAYING

    def draw(self, screen):
        screen.fill((30, 30, 30))

        if self.state == STATE_MENU:
            title = FONT_LARGE.render("CAMPO MINADO", True, (255, 215, 0))
            sub = FONT_MEDIUM.render("Pressione [ ENTER ] para Iniciar", True, (255, 255, 255))
            controls_1 = FONT_SMALL.render("Mouse: Clique Esquerdo = Revelar | Clique Direito = Bandeira", True, (180, 180, 180))
            controls_2 = FONT_SMALL.render("Teclado: Setas = Mover | Enter/Espaço = Revelar | F = Bandeira", True, (180, 180, 180))

            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
            screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            screen.blit(controls_1, controls_1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))
            screen.blit(controls_2, controls_2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130)))

        else:
            flags_txt = FONT_MEDIUM.render(f"Bandeiras: {self.flags_left}", True, (255, 255, 255))
            screen.blit(flags_txt, (GRID_X, GRID_Y - 40))

            self.grid.draw(screen, FONT_SMALL)

            cur_r, cur_c = self.cursor_pos
            target_cell = self.grid.cells[cur_r][cur_c]
            pygame.draw.rect(screen, (255, 215, 0), target_cell.rect, 3)

            if self.state == STATE_GAME_OVER:
                msg = FONT_MEDIUM.render("GAME OVER! Pressione [ ENTER ] para Reiniciar", True, (255, 80, 80))
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 30)))
            elif self.state == STATE_VICTORY:
                msg = FONT_MEDIUM.render("VOCÊ VENCEU! Pressione [ ENTER ] para Reiniciar", True, (80, 255, 80))
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 30)))


game = MinesweeperGame()
clock = pygame.time.Clock()

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                game.handle_click(event.pos, is_right_click=False)
            elif event.button == 3:
                game.handle_click(event.pos, is_right_click=True)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            else:
                game.handle_key(event.key)

    game.draw(screen)
    pygame.display.flip()