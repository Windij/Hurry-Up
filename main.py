import pygame

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BOARD_WIDTH = 9
BOARD_HEIGHT = 9

#Класс Board из урока
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 230
        self.top = 50
        self.cell_size = 60

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, 'white', (
                    x * self.cell_size + self.left,
                    y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), width=1)
                pygame.draw.rect(screen, 'grey', (
                    x * self.cell_size + self.left + 1,
                    y * self.cell_size + self.top + 1, self.cell_size - 2,
                    self.cell_size - 2))

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
        if self.left <= mouse_pos[1] < self.left + self.height * self.cell_size and self.top <= mouse_pos[
            0] < self.top + self.width * self.cell_size:
            return (int((mouse_pos[0] - self.top) / self.cell_size),
                    int((mouse_pos[1] - self.left) / self.cell_size))
        else:
            return None

    def on_click(self, cell_coords):
        pass


def main():
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
