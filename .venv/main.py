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
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
LIGHT_YELLOW = (255, 255, 150)
WHITE = (255, 255, 255)
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


class Chips(Base):
    def __init__(self, x, y):
        super().__init__(x, y, LIGHT_YELLOW)


class Water(Base):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE)


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
    keys = pygame.sprite.Group()
    doors = pygame.sprite.Group()
    chips = pygame.sprite.Group()
    water = pygame.sprite.Group()
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
            elif tile_type == '*':
                tile = Chips(x, y)
                chips.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
            elif tile_type == 'W':
                tile = Water(x, y)
                water.add(tile)
                tile = Floor(x, y)
                floor_tiles.add(tile)
    return wall_tiles, floor_tiles, player, p1, keys, doors, chips, water


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = (SCREEN_WIDTH - width * TILE_SIZE) // 2
        self.top = 0
        self.cell_size = TILE_SIZE
        self.wall_tiles = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.chips = pygame.sprite.Group()
        self.water = pygame.sprite.Group()
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
                pygame.draw.rect(screen, GRAY, (
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
        self.wall_tiles, self.floor_tiles, self.player, self.p1, self.keys, self.doors, self.chips, self.water = create_level(
            level_data)
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
        for tile in self.keys:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.doors:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.chips:
            tile.rect.x += delta_x
            tile.rect.y += delta_y
        for tile in self.water:
            tile.rect.x += delta_x
            tile.rect.y += delta_y

    def move_level(self, dx, dy, inventory, chips_left):
        flag_of_door = False
        for tile in self.wall_tiles:
            tile.move(dx, dy)
        if self.p1.is_collide(self.wall_tiles):
            for tile in self.wall_tiles:
                tile.move(-dx, -dy)
        else:
            for tile in self.floor_tiles:
                tile.move(dx, dy)
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
            for tile in self.chips:
                tile.move(dx, dy)
                if self.p1.rect.colliderect(tile.rect):
                    self.chips.remove(tile)
                    chips_left -= 1
            for tile in self.water:
                tile.move(dx, dy)
        if flag_of_door:
            self.move_level(-dx, -dy, inventory, chips_left)
        return chips_left

    def draw_level(self, screen):
        self.screen_2.fill((0, 0, 0, 0))
        self.render(self.screen_2)
        self.wall_tiles.draw(self.screen_2)
        self.floor_tiles.draw(self.screen_2)
        self.player.draw(self.screen_2)
        self.keys.draw(self.screen_2)
        self.doors.draw(self.screen_2)
        self.chips.draw(self.screen_2)
        self.water.draw(self.screen_2)
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
                pygame.draw.rect(screen, GRAY, (
                    x * self.cell_size + self.left + 1, y * self.cell_size + self.top + 1,
                    self.cell_size - 2, self.cell_size - 2))
        for i, item in enumerate(self.items):
            item.rect.x = self.left + i * self.cell_size
            item.rect.y = self.top
            screen.blit(item.image, item.rect)

    def add_to_inventory(self, item):
        if len(self.items) < self.width:
            self.items.append(item)


class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 36)
        self.text_surface = self.font.render(text, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()



class PopupWindow:
    def __init__(self, screen, text, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.text = text
        self.font = pygame.font.Font(None, 24)
        self.text_surface = self.font.render(text, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - width // 2, SCREEN_HEIGHT // 2 - height // 2, width, height)
        self.running = True
        self.close_button = Button('Закрыть', self.rect.x + self.width - 140, self.rect.y + self.height - 40, 120, 30,
                                   RED, (200, 0, 0), self.close)

    def close(self):
        self.running = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.close_button.handle_event(event)

            pygame.draw.rect(self.screen, GRAY, self.rect)
            self.screen.blit(self.text_surface, self.text_rect)
            self.close_button.draw(self.screen)
            pygame.display.flip()


class StartWindow:
    def __init__(self, screen):
        self.screen = screen
        self.buttons = []
        self.running = True
        self.create_buttons()
        self.popup_window = None

    def create_buttons(self):
        button_width = 200
        button_height = 50
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = 200
        space = 80
        self.buttons.append(
            Button('Начать игру', start_x, button_y, button_width, button_height, GREEN, (0, 200, 0), self.start_game))
        button_y += space
        self.buttons.append(
            Button('О игре', start_x, button_y, button_width, button_height, BLUE, (0, 0, 200), self.show_about))
        button_y += space
        self.buttons.append(Button('Об авторах', start_x, button_y, button_width, button_height, GOLD, (200, 170, 0),
                                   self.show_authors))

    def start_game(self):
        self.running = False

    def show_about(self):
        self.popup_window = PopupWindow(self.screen, "Здесь будет информация об игре", 400, 200)
        self.popup_window.run()
        self.popup_window = None

    def show_authors(self):
        self.popup_window = PopupWindow(self.screen, "Здесь информация об авторах", 400, 200)
        self.popup_window.run()
        self.popup_window = None

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.buttons:
                    button.handle_event(event)

            self.screen.fill(BLACK)
            for button in self.buttons:
                button.draw(self.screen)

            pygame.display.flip()


font_size = 40

font1 = pygame.font.Font(None, font_size)
font2 = pygame.font.Font("DS-DIGIB.TTF", font_size)

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
game_duration = 100

level = 1
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
    level = 1
    chips_left = 1
    time_left = 100
    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Level Mover')

    start_window = StartWindow(screen)
    start_window.run()

    is_paused = False
    last_time = 0
    game_over = False

    if not start_window.running:
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
                mouse_pos = pygame.mouse.get_pos()
                pause_button_rect = draw_pause_button(screen, is_paused)
                if pause_button_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    is_paused = not is_paused
                if event.type == pygame.KEYDOWN and not is_paused and not game_over:
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
                    chips_left = board.move_level(dx, dy, inventory, chips_left)
                    if board.p1.is_collide(board.water):
                        game_over = True
                if event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_RETURN:
                        game_over = False
                        board.load_level(LEVEL_FILE)
                        chips_left = 1
                        time_left = 100
            if not is_paused and chips_left > 0 and not game_over:
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
            if game_over:
                draw_text(screen, "GAME OVER!",
                          SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50, RED)
                draw_text(screen, "Press Enter to restart", SCREEN_WIDTH // 2 - 150,
                          SCREEN_HEIGHT // 2, RED)
                inventory.items = []
            pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
