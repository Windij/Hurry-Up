import pygame
import os

from pygame.examples.sprite_texture import sprite

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BOARD_WIDTH = 9
BOARD_HEIGHT = 9
TILE_SIZE = 60
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRID_LINE_COLOR = BLACK
LEVEL_FILE = 'level.txt'

class Base(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def move(self, dx, dy):
        self.rect.x += dx * TILE_SIZE
        self.rect.y += dy * TILE_SIZE

class Wall(Base):
    def __init__(self, x, y):
        super().__init__(x, y, RED)

class Player(Base):
    def __init__(self, x, y):
        super().__init__(x, y, GRAY)
    def move(self, dx, dy):
        pass
    def is_collide(self, all_tiles):
        return pygame.sprite.spritecollideany(self,all_tiles)


def load_level(filename):
    level_data = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                level_data.append(line.strip())
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []
    return level_data

def create_level(level_data):
    all_tiles = pygame.sprite.Group()
    player = pygame.sprite.Group()
    for y, row in enumerate(level_data):
        for x, tile_type in enumerate(row):
            if tile_type == '#':
                tile = Wall(x, y)
                all_tiles.add(tile)
            elif tile_type == 'P':
                p1 = Player(x,y)
                player.add(p1)
    return all_tiles, player, p1

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = (SCREEN_WIDTH - width * TILE_SIZE) // 2
        self.top = (SCREEN_HEIGHT - height * TILE_SIZE) // 2
        self.cell_size = TILE_SIZE
        self.all_tiles = pygame.sprite.Group()

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # def render(self, screen):
    #     for y in range(self.height):
    #         for x in range(self.width):
    #             pygame.draw.rect(screen, 'white', (
    #                 x * self.cell_size + self.left,
    #                 y * self.cell_size + self.top, self.cell_size,
    #                 self.cell_size), width=1)
    #             pygame.draw.rect(screen, 'grey', (
    #                 x * self.cell_size + self.left + 1,
    #                 y * self.cell_size + self.top + 1, self.cell_size - 2,
    #                 self.cell_size - 2))

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
       if self.left <= mouse_pos[0] < self.left + self.width * self.cell_size and \
              self.top <= mouse_pos[1] < self.top + self.height * self.cell_size:
          return (int((mouse_pos[1] - self.top) / self.cell_size),
                  int((mouse_pos[0] - self.left) / self.cell_size))
       else:
           return None


    def on_click(self, cell_coords):
        pass

    def load_level(self, filename):
        level_data = load_level(filename)
        self.all_tiles, self.player, self.p1 = create_level(level_data)
        for tile in self.all_tiles:
            tile.rect.x += self.left
            tile.rect.y += self.top
        for tile in self.player:
            tile.rect.x += self.left
            tile.rect.y += self.top

    def move_level(self, dx, dy):
        for tile in self.all_tiles:
            tile.move(dx, dy)

    def draw_level(self, screen):
        self.all_tiles.draw(screen)
        self.player.draw(screen)


def main():
    pygame.init()
    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Level Mover')

    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    board.load_level(LEVEL_FILE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
              dx = 0
              dy = 0
              if event.key == pygame.K_d:
                  dx = -1
              if event.key == pygame.K_s:
                  dy = -1
              if event.key == pygame.K_w:
                  dy = 1
              if event.key == pygame.K_a:
                  dx = 1
              board.move_level(dx, dy)


        screen.fill(BLACK)
        board.draw_level(screen)
        # board.render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
