import pygame
import math
import sys
import os
import json
import random


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


hex_images = {
    'sun': load_image('Sun_Red.png'),
    'spaceship': load_image('spaceship.png'),
    'population': load_image('icon_population.png'),
    'production': load_image('icon_gear.png'),
    'power': load_image('icon_power.png'),
    'plus': load_image('icon_plus.png'),
    'minus': load_image('icon_minus.png'),
    'icon': load_image('icon_minus.png'),
    'tropical': load_image('Planet_Tropical.png'),
    'snowy': load_image('Planet_Snowy.png'),
    'ocean': load_image('Planet_Ocean.png'),
    'lunar': load_image('Planet_Lunar.png'),
    'muddy': load_image('Planet_Muddy.png'),
    'cloudy': load_image('planet_Cloudy.png'),
    'next_turn': load_image('icon_next_turn.png')
}

planet_types = {
    'tropical': {
        'population_growth_rate': 1.2,
        'production_bonus': 1.1,
        'image': 'tropical'
    },
    'snowy': {
        'population_growth_rate': 0.8,
        'production_bonus': 1.2,
        'image': 'snowy'
    },
    'ocean': {
        'population_growth_rate': 1.0,
        'production_bonus': 1.0,
        'image': 'ocean'
    },
    'lunar': {
        'population_growth_rate': 0.5,
        'production_bonus': 1.3,
        'image': 'lunar'
    },
    'muddy': {
        'population_growth_rate': 0.9,
        'production_bonus': 0.8,
        'image': 'muddy'
    },
    'cloudy': {
        'population_growth_rate': 1.1,
        'production_bonus': 0.9,
        'image': 'cloudy'
    }
}


class GameSettings:
    """Класс для хранения основных настроек игры и инициализации Pygame"""

    def __init__(self):
        self.width = 1000
        self.height = 750
        self.fps = 60

        # Цвета (создаем словарь для удобства)
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'gray': (200, 200, 200)
        }

        # Визуальные настройки
        self.hex_radius = 35
        self.hex_width = math.sqrt(3) * self.hex_radius
        self.hex_height = 2 * self.hex_radius
        self.x_offset = self.hex_width
        self.y_offset = self.hex_height * 3 / 4
        self.map_radius = 6
        self.indent = 10
        self.info_bar_height = 30
        self.icon_size = 20
        self.menu_width = self.width // 2
        self.menu_height = self.height // 2
        self.exit_button_size = 30
        self.exit_btn_outline = 2
        self.menu_outline = 4
        self.planet_image_size = 100
        self.menu_icon_size = 40
        self.menu_line_width = 2
        self.menu_padding = 10
        self.button_width = 150
        self.button_height = 40
        self.turn_button_size = 90

        # Пути
        self.save_dir = "../../../../Downloads/saves"
        os.makedirs(self.save_dir, exist_ok=True)

        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Nova Eclipse")
        pygame.display.set_icon(hex_images['icon'])
        self.clock = pygame.time.Clock()


# Создаем экземпляр класса настроек
settings = GameSettings()


def get_hex_points(center_x, center_y, radius):
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points


def hex_distance(hex1, hex2):
    """Вычисляет расстояние между двумя шестиугольниками (q, r)"""
    return (abs(hex1["q"] - hex2["q"]) + abs(hex1["q"] + hex1["r"] - hex2["q"] - hex2["r"])
            + abs(hex1["r"] - hex2["r"])) // 2


def generate_hex_map(center_cords, radius):
    hex_map = []

    for map_q in range(-radius, radius + 1):
        for map_r in range(max(-radius, -map_q - radius), min(radius, -map_q + radius) + 1):
            x = center_cords[0] + (map_q * settings.x_offset) + (map_r * settings.x_offset / 2)
            y = center_cords[1] + (map_r * settings.y_offset)
            if 0 <= x <= settings.width and 0 <= y <= settings.height:
                hex_map.append({"q": map_q, "r": map_r, "value": 0, "x": x, "y": y})

    # creating sun with value 1
    sun_hex_coords = [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    for one_hex in hex_map:
        if (one_hex["q"], one_hex["r"]) in sun_hex_coords:
            one_hex["value"] = 1

    empty_hex = [one_hex for one_hex in hex_map if one_hex["value"] == 0]

    # creating planets with value 2
    planet_types_list = list(planet_types.keys())
    random.shuffle(planet_types_list)
    for i in range(random.randint(5, 6)):
        if empty_hex:
            chosen_hex = random.choice(empty_hex)
            chosen_hex["value"] = 2
            chosen_hex["planet_type"] = planet_types_list[i % len(planet_types_list)]
            chosen_hex["population"] = random.randint(100, 1000)
            chosen_hex["production"] = random.randint(100, 1000)
            empty_hex.remove(chosen_hex)

    # creating spaceship with value 3
    if empty_hex:
        chosen_hex = random.choice(empty_hex)
        chosen_hex["value"] = 3
        chosen_hex["power"] = random.randint(75, 100)
        empty_hex.remove(chosen_hex)

    return hex_map


class TurnManager:
    """Класс для управления ходами в игре"""

    def __init__(self):
        self.turn_count = 0
        self.max_turns = 250
        self.turn_button_rect = pygame.Rect(settings.width - settings.turn_button_size,
                                            settings.height - settings.turn_button_size,
                                            settings.turn_button_size, settings.turn_button_size)

    def is_game_over(self):
        """Проверяет, окончена ли игра"""
        return self.turn_count >= self.max_turns

    def draw_turn_button(self, screen):
        """Отрисовывает кнопку смены хода"""
        screen.blit(
            pygame.transform.scale(hex_images['next_turn'], (settings.turn_button_size, settings.turn_button_size)),
            self.turn_button_rect.topleft)

    def draw_turn_counter(self, screen, font):
        """Отрисовывает счетчик ходов"""
        turn_text = font.render(f"{self.turn_count}/{self.max_turns}", True, settings.colors['white'])
        text_rect = turn_text.get_rect(topright=(settings.width - 10, settings.info_bar_height + 10))
        screen.blit(turn_text, text_rect)

    def handle_input(self, event, hex_map):
        """Обрабатывает нажатие кнопки смены хода"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.turn_button_rect.collidepoint(event.pos):
                hex_map.deselect_all()
                self.turn_count += 1
                hex_map.spaceship_moved_this_turn = False


class HexMap:
    def __init__(self, center_cords, radius):
        self.hex_map = generate_hex_map(center_cords, radius)
        self.selected_spaceship = None
        self.movement_hex = []
        self.selected_planet = None
        self.spaceship_moved_this_turn = False
        self.font = pygame.font.Font(None, 30)
        self.save_map()

        # status
        self.planet_menu_active = False
        self.bonus_menu_active = False
        self.event_menu_active = False

        # rects
        self.exit_button_rect = None  # Exit from planet menu
        self.bonus_button_rect = None  # Enter the bonus menu
        self.event_button_rect = None  # Enter the event menu
        self.return_button_rect = None  # Return from bonus/event
        self.menu_exit_button_rect = None  # Exit from bonus/event to game

    def save_map(self):
        file_path = os.path.join(settings.save_dir, "map.json")
        with open(file_path, "w") as file:
            json.dump(self.hex_map, file, indent=4)

    def get_clicked_hex(self, pos):
        mouse_x, mouse_y = pos
        nearest_hex = min(self.hex_map, key=lambda h: (mouse_x - h["x"]) ** 2 + (mouse_y - h["y"]) ** 2)

        # Exit/return buttons
        if self.bonus_menu_active or self.event_menu_active:
            if self.menu_exit_button_rect and self.menu_exit_button_rect.collidepoint(pos):
                self.bonus_menu_active = False
                self.event_menu_active = False
                self.planet_menu_active = False
                self.selected_planet = None
                return
            elif self.return_button_rect and self.return_button_rect.collidepoint(pos):
                self.bonus_menu_active = False
                self.event_menu_active = False
                self.planet_menu_active = True
                return
            else:
                return

        # Planet menu buttons
        if self.planet_menu_active:
            if self.exit_button_rect and self.exit_button_rect.collidepoint(pos):
                self.planet_menu_active = False
                self.selected_planet = None
            elif self.bonus_button_rect and self.bonus_button_rect.collidepoint(pos):
                self.planet_menu_active = False
                self.bonus_menu_active = True
            elif self.event_button_rect and self.event_button_rect.collidepoint(pos):
                self.planet_menu_active = False
                self.event_menu_active = True
            return

        # Selected hexagon
        if self.selected_spaceship and nearest_hex in self.movement_hex and not self.spaceship_moved_this_turn:
            self.move_spaceship(nearest_hex)
        elif nearest_hex["value"] == 3 and not self.spaceship_moved_this_turn:
            self.select_spaceship(nearest_hex)
        elif nearest_hex["value"] == 2 and self.can_select_planet(nearest_hex):
            self.select_planet(nearest_hex)
        else:
            self.deselect_all()

    def move_spaceship(self, target_hex):
        target_hex["value"] = 3
        self.selected_spaceship["value"] = 0
        self.deselect_all()
        self.spaceship_moved_this_turn = True  # Корабль походил в этот ход

    def select_spaceship(self, hex):
        self.selected_spaceship = hex
        self.movement_area(hex)
        self.selected_planet = None

    def select_planet(self, hex):
        self.selected_planet = hex
        self.planet_menu_active = True
        self.selected_spaceship = None
        self.movement_hex = []

    def deselect_all(self):
        self.selected_spaceship = None
        self.movement_hex = []
        self.selected_planet = None
        self.planet_menu_active = False
        self.bonus_menu_active = False
        self.event_menu_active = False

    def can_select_planet(self, planet_hex):
        for other_hex in self.hex_map:
            if other_hex["value"] == 3 and hex_distance(planet_hex, other_hex) == 1:
                return True
        return False

    def movement_area(self, start_hex):
        self.movement_hex = [h for h in self.hex_map if hex_distance(start_hex, h) == 1 and h["value"] == 0]

    def draw(self, screen, turn):
        # Draw info bar
        self.draw_info_bar(screen, turn)

        # Draw hexes
        for one_hex in self.hex_map:
            self.draw_hex(screen, one_hex)

        # Draw possible movement
        if self.selected_spaceship:
            self.draw_movement_area(screen)

        # Draw objects (sun и spaceship)
        self.draw_hex_image(screen, 'sun', 2.5)
        self.draw_hex_image(screen, 'spaceship', 1)

        # Draw planet menu
        if self.planet_menu_active and self.selected_planet:
            self.draw_planet_menu(screen)
        elif self.bonus_menu_active:
            self.draw_bonus_menu(screen)
        elif self.event_menu_active:
            self.draw_event_menu(screen)

    def draw_info_bar(self, screen, turn):
        pygame.draw.rect(screen, settings.colors['black'], (0, 0, settings.width, settings.info_bar_height))
        total_population = sum(one_hex.get("population", 0) for one_hex in self.hex_map)
        total_production = sum(one_hex.get("production", 0) for one_hex in self.hex_map)
        total_power = sum(one_hex.get("power", 0) for one_hex in self.hex_map)

        info_bar_x_offset = 5
        info_bar_y_offset = 5

        # Draw Population
        population_icon = pygame.transform.scale(hex_images['population'], (settings.icon_size, settings.icon_size))
        screen.blit(population_icon, (info_bar_x_offset, info_bar_y_offset))
        population_text = self.font.render(f" {total_population}", True, settings.colors['white'])
        screen.blit(population_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + population_text.get_width() + 10

        # Draw Production
        production_icon = pygame.transform.scale(hex_images['production'], (settings.icon_size, settings.icon_size))
        screen.blit(production_icon, (info_bar_x_offset, info_bar_y_offset))
        production_text = self.font.render(f" {total_production}", True, settings.colors['white'])
        screen.blit(production_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + production_text.get_width() + 10

        # Draw Power
        power_icon = pygame.transform.scale(hex_images['power'], (settings.icon_size, settings.icon_size))
        screen.blit(power_icon, (info_bar_x_offset, info_bar_y_offset))
        power_text = self.font.render(f" {total_power}", True, settings.colors['white'])
        screen.blit(power_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))

        turn.draw_turn_counter(screen, self.font)

    def draw_hex(self, screen, one_hex):
        hex_points = get_hex_points(one_hex["x"], one_hex["y"], settings.hex_radius)
        width = 1

        if self.selected_spaceship == one_hex:
            color = settings.colors['red']
            width = 3
        elif self.selected_planet == one_hex:
            color = settings.colors['green']
            width = 3
        else:
            color = settings.colors['white']

        pygame.draw.polygon(screen, color, hex_points, width)

        if one_hex["value"] == 2:
            planet_type = one_hex.get('planet_type')
            planet_image_key = planet_types[planet_type]['image']
            scaled_planet_image = pygame.transform.scale(hex_images[planet_image_key], (
                int(settings.hex_width) - settings.indent, int(settings.hex_width) - settings.indent))
            screen.blit(scaled_planet_image, scaled_planet_image.get_rect(center=(one_hex["x"], one_hex["y"])))

    def draw_movement_area(self, screen):
        for one_hex in self.movement_hex:
            hex_points = get_hex_points(one_hex["x"], one_hex["y"], settings.hex_radius)
            pygame.draw.polygon(screen, settings.colors['blue'], hex_points, 3)

    def draw_hex_image(self, screen, image, size):
        scaled_image = pygame.transform.scale(hex_images[image],
                                              (int(settings.hex_width) * size - settings.indent * size,
                                               int(settings.hex_width) * size - settings.indent * size))
        rect = scaled_image.get_rect()
        if image == 'sun':
            rect.center = (settings.width // 2, settings.height // 2)
        elif image == 'spaceship':
            for one_hex in self.hex_map:
                if one_hex["value"] == 3:
                    rect = scaled_image.get_rect(center=(one_hex["x"], one_hex["y"]))
                    break
        screen.blit(scaled_image, rect)

    def draw_planet_menu(self, screen):
        # Draw menu background
        menu_x = settings.width // 2 - settings.menu_width // 2
        menu_y = settings.height // 2 - settings.menu_height // 2
        pygame.draw.rect(screen, settings.colors['black'], (menu_x, menu_y, settings.menu_width, settings.menu_height))
        pygame.draw.rect(screen, settings.colors['white'], (
            menu_x - settings.menu_outline, menu_y - settings.menu_outline,
            settings.menu_width + settings.menu_outline * 2, settings.menu_height + settings.menu_outline * 2),
                         settings.menu_outline)

        # Draw planet image area
        planet_area_x = menu_x + settings.menu_padding
        planet_area_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['white'],
                         (planet_area_x, planet_area_y, settings.planet_image_size, settings.planet_image_size), 2)

        # Draw planet image
        planet_type = self.selected_planet.get('planet_type')
        planet_image_key = planet_types[planet_type]['image']
        planet_image = pygame.transform.scale(hex_images[planet_image_key], (
            settings.planet_image_size - 2 * settings.menu_padding,
            settings.planet_image_size - 2 * settings.menu_padding))
        screen.blit(planet_image, (planet_area_x + settings.menu_padding, planet_area_y + settings.menu_padding))

        stats_x = planet_area_x + settings.planet_image_size + settings.menu_padding
        stats_y = planet_area_y

        # Population
        pop_icon = pygame.transform.scale(hex_images['population'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(pop_icon, (stats_x, stats_y))
        pop_text = self.font.render(f": {self.selected_planet.get('population')}", True, settings.colors['white'])
        screen.blit(pop_text, (stats_x + settings.menu_icon_size, stats_y + (settings.menu_icon_size // 4)))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Production
        prod_icon = pygame.transform.scale(hex_images['production'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(prod_icon, (stats_x, stats_y))
        prod_text = self.font.render(f": {self.selected_planet.get('production')}", True, settings.colors['white'])
        screen.blit(prod_text, (stats_x + settings.menu_icon_size, stats_y + (settings.menu_icon_size // 4)))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Draw separation lines
        separator_y = planet_area_y + settings.planet_image_size + settings.menu_padding
        pygame.draw.line(screen, settings.colors['white'],
                         (planet_area_x, separator_y),
                         (menu_x + settings.menu_width - settings.menu_padding, separator_y),
                         settings.menu_line_width)

        # Add bonus lines
        line_y = separator_y + settings.menu_padding
        plus_icon = pygame.transform.scale(hex_images['plus'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(plus_icon, (planet_area_x, line_y))
        plus_text = self.font.render("Debuff", True, settings.colors['white'])
        screen.blit(plus_text, (planet_area_x + settings.menu_icon_size + settings.menu_padding // 2,
                                line_y + (settings.menu_icon_size // 4)))

        line_y += settings.menu_icon_size + settings.menu_padding // 2
        minus_icon = pygame.transform.scale(hex_images['minus'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(minus_icon, (planet_area_x, line_y))
        minus_text = self.font.render("Buff", True, settings.colors['white'])
        screen.blit(minus_text, (planet_area_x + settings.menu_icon_size + settings.menu_padding // 2,
                                 line_y + (settings.menu_icon_size // 4)))

        # Draw separation lines
        separator_y = line_y + settings.menu_icon_size + settings.menu_padding
        pygame.draw.line(screen, settings.colors['white'],
                         (planet_area_x, separator_y),
                         (menu_x + settings.menu_width - settings.menu_padding, separator_y),
                         settings.menu_line_width)

        # Draw buttons
        button_y = separator_y + settings.menu_padding
        bonus_button_x = menu_x + settings.menu_padding
        event_button_x = menu_x + settings.menu_width - settings.button_width - settings.menu_padding

        self.bonus_button_rect = pygame.Rect(bonus_button_x, button_y, settings.button_width, settings.button_height)
        self.event_button_rect = pygame.Rect(event_button_x, button_y, settings.button_width, settings.button_height)

        pygame.draw.rect(screen, settings.colors['white'], self.bonus_button_rect)
        pygame.draw.rect(screen, settings.colors['white'], self.event_button_rect)

        bonus_text = self.font.render("Бонусы", True, settings.colors['black'])
        event_text = self.font.render("События", True, settings.colors['black'])

        bonus_text_rect = bonus_text.get_rect(center=self.bonus_button_rect.center)
        event_text_rect = event_text.get_rect(center=self.event_button_rect.center)

        screen.blit(bonus_text, bonus_text_rect)
        screen.blit(event_text, event_text_rect)

        # Draw exit button
        button_x = menu_x + settings.menu_width - settings.exit_button_size - settings.menu_padding
        button_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['red'],
                         (button_x, button_y, settings.exit_button_size, settings.exit_button_size))
        pygame.draw.rect(screen, settings.colors['white'],
                         (button_x - settings.exit_btn_outline, button_y - settings.exit_btn_outline,
                          settings.exit_button_size + settings.exit_btn_outline * 2,
                          settings.exit_button_size + settings.exit_btn_outline * 2),
                         settings.exit_btn_outline)
        exit_text = self.font.render('X', True, settings.colors['white'])
        screen.blit(exit_text, (button_x + 9, button_y + 7))
        self.exit_button_rect = pygame.Rect(button_x, button_y, settings.exit_button_size, settings.exit_button_size)

    def draw_bonus_menu(self, screen):
        self.draw_extra_menu(screen, "Список бонусов")

    def draw_event_menu(self, screen):
        self.draw_extra_menu(screen, "Список событий")

    def draw_extra_menu(self, screen, title):
        # Draw menu background
        menu_x = settings.width // 2 - settings.menu_width // 2
        menu_y = settings.height // 2 - settings.menu_height // 2
        pygame.draw.rect(screen, settings.colors['black'], (menu_x, menu_y, settings.menu_width, settings.menu_height))
        pygame.draw.rect(screen, settings.colors['white'], (
            menu_x - settings.menu_outline, menu_y - settings.menu_outline,
            settings.menu_width + settings.menu_outline * 2, settings.menu_height + settings.menu_outline * 2),
                         settings.menu_outline)

        # Draw title
        title_text = self.font.render(title, True, settings.colors['white'])
        title_rect = title_text.get_rect(center=(settings.width // 2, menu_y + 30))
        screen.blit(title_text, title_rect)

        # Draw exit button
        button_x = menu_x + settings.menu_width - settings.exit_button_size - settings.menu_padding
        button_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['red'],
                         (button_x, button_y, settings.exit_button_size, settings.exit_button_size))
        pygame.draw.rect(screen, settings.colors['white'],
                         (button_x - settings.exit_btn_outline, button_y - settings.exit_btn_outline,
                          settings.exit_button_size + settings.exit_btn_outline * 2,
                          settings.exit_button_size + settings.exit_btn_outline * 2),
                         settings.exit_btn_outline)
        exit_text = self.font.render('X', True, settings.colors['white'])
        screen.blit(exit_text, (button_x + 9, button_y + 7))
        self.menu_exit_button_rect = pygame.Rect(button_x, button_y, settings.exit_button_size,
                                                 settings.exit_button_size)

        # Draw return button
        button_x = menu_x + settings.menu_width // 2 - settings.button_width // 2
        button_y = menu_y + settings.menu_height - settings.button_height - settings.menu_padding
        self.return_button_rect = pygame.Rect(button_x, button_y, settings.button_width, settings.button_height)
        pygame.draw.rect(screen, settings.colors['blue'], self.return_button_rect)
        return_text = self.font.render('Return', True, settings.colors['white'])
        return_text_rect = return_text.get_rect(center=self.return_button_rect.center)
        screen.blit(return_text, return_text_rect)


def start_screen():
    """Функция для отображения начального экрана"""
    title_font = pygame.font.Font(None, 72)
    button_font = pygame.font.Font(None, 36)

    title_text = title_font.render("Nova Eclipse", True, settings.colors['white'])
    title_rect = title_text.get_rect(center=(settings.width // 2, settings.height // 3))

    start_button_text = button_font.render("Начать", True, settings.colors['black'])
    start_button_rect = start_button_text.get_rect(center=(settings.width // 2, settings.height // 2))
    start_button_cords = pygame.Rect(start_button_rect.left - 10, start_button_rect.top - 5,
                                     start_button_rect.width + 20, start_button_rect.height + 10)

    background = pygame.transform.scale(load_image("cosmos.jpg"), (settings.width, settings.height))
    while True:
        settings.screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_cords.collidepoint(event.pos):
                    return

        settings.screen.blit(title_text, title_rect)

        pygame.draw.rect(settings.screen, settings.colors['white'], start_button_cords)
        settings.screen.blit(start_button_text, start_button_rect)

        pygame.display.flip()
        settings.clock.tick(settings.fps)


def game():
    """Основная часть игры"""
    hex_map = HexMap((settings.width // 2, settings.height // 2), settings.map_radius)
    background = pygame.transform.scale(load_image("cosmos.jpg"), (settings.width, settings.height))
    turn_manager = TurnManager()

    while not turn_manager.is_game_over():
        settings.screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                hex_map.get_clicked_hex(event.pos)

            turn_manager.handle_input(event, hex_map)

        hex_map.draw(settings.screen, turn_manager)
        turn_manager.draw_turn_button(settings.screen)
        pygame.display.flip()
        settings.clock.tick(settings.fps)
    return


def terminate():
    pygame.quit()
    sys.exit()


def main():
    start_screen()
    game()
    print('s')


if __name__ == "__main__":
    sys.exit(main())
