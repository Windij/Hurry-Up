import sys
import pygame
import os
import time

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 850
BOARD_WIDTH = 9
BOARD_HEIGHT = 9
TILE_SIZE = 60
BROWN = (123, 63, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
SILVER = (200, 200, 200)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
LIGHT_YELLOW = (255, 255, 150)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
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
    return wall_tiles, floor_tiles, lifting_objects, player, p1


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
        self.wall_tiles, self.floor_tiles, self.lifting_objects, self.player, self.p1 = create_level(level_data)
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

    def move_level(self, dx, dy, inventory):
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

    def draw_level(self, screen):
        self.screen_2.fill((0, 0, 0, 0))
        self.render(self.screen_2)
        self.wall_tiles.draw(self.screen_2)
        self.floor_tiles.draw(self.screen_2)
        self.lifting_objects.draw(self.screen_2)
        self.player.draw(self.screen_2)
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
        self.items.append(item)


font_size = 40

font1 = pygame.font.Font(None, font_size)
font2 = pygame.font.Font("DS-DIGIB.TTF", font_size)

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
game_duration = 100


level = 1
chips_left = 10
digit_width = 20
digit_height = 20


PAUSE_BUTTON_X = 720
PAUSE_BUTTON_Y = 780
PAUSE_BUTTON_WIDTH = 120
PAUSE_BUTTON_HEIGHT = 40


y_offset = SCREEN_HEIGHT - digit_height

def draw_digit(screen, number, x, y, color):
    num_str = str(number).zfill(3)
    for i, digit in enumerate(num_str):
        digit_surface = font2.render(digit, True, color)
        digit_rect = digit_surface.get_rect(center=(x + digit_width * i + digit_width // 2, y + digit_height // 2))
        screen.blit(digit_surface, digit_rect)



def draw_text(screen, text, x, y, color):
    text_surface = font1.render(text, True, color)
    screen.blit(text_surface, (x, y))


def draw_clock_face(screen, x, y, width, height, color):
    pygame.draw.rect(screen, color, (x, y, width, height))


def draw_pause_button(screen, is_paused):
    text = "PAUSE" if not is_paused else "RESUME"
    text_surface = font1.render(text, True, WHITE)
    button_rect = pygame.Rect(PAUSE_BUTTON_X, PAUSE_BUTTON_Y, PAUSE_BUTTON_WIDTH, PAUSE_BUTTON_HEIGHT)
    pygame.draw.rect(screen, GRAY, button_rect)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect


def main():
    pygame.init()
    level = 1
    chips_left = 10
    time_left = 100

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Level Mover')

    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    board.load_level(LEVEL_FILE)

    inventory = Inventory(7, 1)
    inventory.set_view(board.left + TILE_SIZE,
                       board.top + board.cell_size * board.height + TILE_SIZE, TILE_SIZE)

    is_paused = False
    last_time = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            mouse_pos = pygame.mouse.get_pos()
            pause_button_rect = draw_pause_button(screen, is_paused)
            if pause_button_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                is_paused = not is_paused

            if event.type == pygame.KEYDOWN and not is_paused:
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

        if not is_paused:
            current_time = time.time()
            if last_time == 0:
                last_time = current_time
            if current_time - last_time >= 1:
                time_left -= 1
                last_time = current_time
            if time_left < 0:
                time_left = 100


        screen.fill(BLACK)

        draw_text(screen, "TIME:", 700, 760 - font_size, YELLOW)
        draw_clock_face(screen, 790, 710, 70, 40, BLUE)
        draw_digit(screen, time_left, 794, 720, LIGHT_YELLOW)

        draw_text(screen, "LEVEL:", 90, 780, YELLOW)
        draw_clock_face(screen, 275, 775, 70, 40, BLUE)
        draw_digit(screen, level, 282, 782, LIGHT_YELLOW)

        draw_text(screen, "STARS LEFT:", 90, 760 - font_size, YELLOW)
        draw_clock_face(screen, 275, 710, 70, 40, BLUE)
        draw_digit(screen, chips_left, 280, 720, LIGHT_YELLOW)
        draw_pause_button(screen, is_paused)

        board.draw_level(screen)
        inventory.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()