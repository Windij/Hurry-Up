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
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
SILVER = (200, 200, 200)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
GRID_LINE_COLOR = BLACK
LEVEL_FILE = 'level.txt'


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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


class Lifting_objects(Base):
    def __init__(self, x, y):
        super().__init__(x, y, (160, 50, 120))


class Player(Base):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)

    def move(self, dx, dy):
        pass

    def is_collide(self, all_tiles):
        return pygame.sprite.spritecollideany(self, all_tiles)


class Key(Base):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.color = color


class Door(Base):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.color = color
        self.is_open = False


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
    lifting_objects = pygame.sprite.Group()
    player = pygame.sprite.Group()
    keys = pygame.sprite.Group()
    doors = pygame.sprite.Group()
    p1 = None
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
            elif tile_type == '{':
                tile = Lifting_objects(x, y)
                lifting_objects.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
            elif tile_type == 'K':
                tile = Key(x, y, GOLD)
                keys.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
            elif tile_type == 'k':
                tile = Key(x, y, BLUE)
                keys.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
            elif tile_type == 'D':
                tile = Door(x, y, GOLD)
                doors.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
            elif tile_type == 'd':
                tile = Door(x, y, BLUE)
                doors.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
    return wall_tiles, floor_tiles, lifting_objects, player, p1, keys, doors


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = (SCREEN_WIDTH - width * TILE_SIZE) // 2
        self.top = 0
        self.cell_size = TILE_SIZE
        self.wall_tiles = pygame.sprite.Group()
        self.lifting_objects = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
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
        self.wall_tiles, self.floor_tiles, self.lifting_objects, self.player, self.p1, self.keys, self.doors = create_level(
            level_data)
        delta_x = self.width // 2 * self.cell_size - self.p1.rect.x
        delta_y = self.height // 2 * self.cell_size - self.p1.rect.y
        for tile in self.wall_tiles:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.floor_tiles:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.lifting_objects:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.player:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.keys:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.doors:
            tile.rect.x += delta_x
            tile.rect.y += delta_y

    def move_level(self, dx, dy, inventory):
        flag_of_door = False
        for tile in self.wall_tiles:
            tile.move(dx, dy)
        if self.p1.is_collide(self.wall_tiles):
            for tile in self.wall_tiles:
                tile.move(-dx, -dy)
        else:
            for tile in self.floor_tiles:
                tile.move(dx, dy)
            for tile in self.lifting_objects:
                tile.move(dx, dy)
                if self.p1.rect.colliderect(tile.rect):
                    inventory.add_to_inventory(tile)
                    self.lifting_objects.remove(tile)
            for tile in self.keys:
                tile.move(dx, dy)
                if self.p1.rect.colliderect(tile.rect):
                    inventory.add_to_inventory(tile)
                    self.keys.remove(tile)
            for tile in self.doors:
                tile.move(dx, dy)
                if self.p1.rect.colliderect(tile.rect):
                    if any(item.color == tile.color for item in inventory.items):
                        tile.is_open = True
                        self.doors.remove(tile)
                    else:
                        # Блокируем проход, если дверь не открыта
                        flag_of_door = True
        if flag_of_door:
            self.move_level(-dx, -dy, inventory)

    def draw_level(self, screen):
        self.screen_2.fill((0, 0, 0, 0))
        self.render(self.screen_2)
        self.wall_tiles.draw(self.screen_2)
        self.floor_tiles.draw(self.screen_2)
        self.lifting_objects.draw(self.screen_2)
        self.player.draw(self.screen_2)
        self.keys.draw(self.screen_2)
        self.doors.draw(self.screen_2)
        screen.blit(self.screen_2, (self.left, self.top))


class Inventory(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.items = []

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, 'white', (
                    x * self.cell_size + self.left, y * self.cell_size + self.top,
                    self.cell_size, self.cell_size), width=1)
                pygame.draw.rect(screen, SILVER, (
                    x * self.cell_size + self.left + 1, y * self.cell_size + self.top + 1,
                    self.cell_size - 2, self.cell_size - 2))
        for i, item in enumerate(self.items):
            item.rect.x = self.left + i * self.cell_size
            item.rect.y = self.top
            screen.blit(item.image, item.rect)

    def add_to_inventory(self, item):
        if len(self.items) < self.width:
            self.items.append(item)


def main():
    pygame.init()
    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Level Mover')

    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    board.load_level(LEVEL_FILE)

    inventory = Inventory(7, 1)
    inventory.set_view(board.left + TILE_SIZE,
                       board.top + board.cell_size * board.height + TILE_SIZE, TILE_SIZE)

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
                board.move_level(dx, dy, inventory)

        screen.fill(BLACK)
        board.draw_level(screen)
        inventory.render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
