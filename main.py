import sys

import pygame
import os

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BOARD_WIDTH = 9
BOARD_HEIGHT = 9
TILE_SIZE = 60
BROWN = (123, 63, 0)
RED = (255, 0, 0)
GREEN = (0,255,0)
BLACK = (0, 0, 0)
SILVER = (200,200,200)
GRID_LINE_COLOR = BLACK
LEVEL_FILE = 'level.txt'

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


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

class Floor(Base):
    def __init__(self, x, y):
        super().__init__(x, y, BROWN)


class Player(Base):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)

    def move(self, dx, dy):
        pass

    def is_collide(self, all_tiles):
        return pygame.sprite.spritecollideany(self, all_tiles)


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
    wall_tiles = pygame.sprite.Group()
    floor_tiles = pygame.sprite.Group()
    player = pygame.sprite.Group()
    for y, row in enumerate(level_data):
        for x, tile_type in enumerate(row):
            if tile_type == '#':
                tile = Wall(x, y)
                wall_tiles.add(tile)
            elif tile_type == '.':
                tile = Floor(x, y)
                floor_tiles.add(tile)
            elif tile_type == 'P':
                p1 = Player(x, y)
                tile = Floor(x, y)
                player.add(p1)
                floor_tiles.add(tile)
    return wall_tiles,floor_tiles, player, p1


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = (SCREEN_WIDTH - width * TILE_SIZE) // 2
        self.top = (SCREEN_HEIGHT - height * TILE_SIZE) // 2
        self.cell_size = TILE_SIZE
        self.wall_tiles = pygame.sprite.Group()
        self.screen_2 = pygame.Surface((self.width * self.cell_size,
                                       self.height * self.cell_size))

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.screen_2 = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size))

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, 'white', (
                    x * self.cell_size,
                    y * self.cell_size, self.cell_size,
                    self.cell_size), width=1)
                pygame.draw.rect(screen, SILVER, (
                    x * self.cell_size + 1,
                    y * self.cell_size + 1, self.cell_size - 2,
                    self.cell_size - 2))

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
        self.wall_tiles,self.floor_tiles, self.player, self.p1 = create_level(level_data)
        delta_x = self.width // 2 * self.cell_size - self.p1.rect.x
        delta_y = self.height // 2 * self.cell_size - self.p1.rect.y
        for tile in self.wall_tiles:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.floor_tiles:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.player:
            tile.rect.x += delta_x
            tile.rect.y += delta_y

    def move_level(self, dx, dy):
        for tile in self.wall_tiles:
            tile.move(dx, dy)
        if self.p1.is_collide(self.wall_tiles):
            for tile in self.wall_tiles:
                tile.move(-dx, -dy)
        else:
            for tile in self.floor_tiles:
                tile.move(dx, dy)

    def draw_level(self, screen):
        self.screen_2.fill((0,0,0,0))
        self.render(self.screen_2)
        self.wall_tiles.draw(self.screen_2)
        self.floor_tiles.draw(self.screen_2)
        self.player.draw(self.screen_2)
        screen.blit(self.screen_2, (self.left,self.top))


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
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
