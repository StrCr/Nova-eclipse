
import pygame
import math
import sys
import os
import json
import random


class GameSettings:
    """
    Класс для хранения основных настроек игры и инициализации Pygame.
    """

    def __init__(self):
        self.width = 1000
        self.height = 750
        self.fps = 60
        self.caption = "Nova Eclipse"

        # Цвета
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)
        self.gray = (200, 200, 200)

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

        # Пути
        self.save_dir = "saves"
        os.makedirs(self.save_dir, exist_ok=True)

        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.caption)
        self.clock = pygame.time.Clock()


# Создаем экземпляр класса настроек
settings = GameSettings()

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
    'cloudy': load_image('planet_Cloudy.png'),
    'spaceship': load_image('spaceship.png'),
    'population': load_image('icon_population.png'),
    'production': load_image('icon_gear.png'),
    'power': load_image('icon_power.png')
}

planet_types = {
    'tropical': {
        'population_growth_rate': 8,
        'production_bonus': 3,
        'image': load_image('Planet_Tropical.png')},
    'ocean': {
        'population_growth_rate': 7,
        'production_bonus': 4,
        'image': load_image('Planet_Ocean.png')},
    'cloudy': {
        'population_growth_rate': 6,
        'production_bonus': 5,
        'image': load_image('planet_Cloudy.png')},
    'snowy': {
        'population_growth_rate': 5,
        'production_bonus': 6,
        'image': load_image('Planet_Snowy.png')},
    'muddy': {
        'population_growth_rate': 4,
        'production_bonus': 7,
        'image': load_image('Planet_Muddy.png')},
    'lunar': {
        'population_growth_rate': 3,
        'production_bonus': 8,
        'image': load_image('Planet_Lunar.png')}
}


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
    return (abs(hex1["q"] - hex2["q"])
            + abs(hex1["q"] + hex1["r"] - hex2["q"] - hex2["r"])
            + abs(hex1["r"] - hex2["r"])) // 2


def generate_hex_map(center_cords, radius):
    hex_map = []

    # creating hex_map with value 0
    for map_q in range(-radius, radius + 1):
        for map_r in range(max(-radius, -map_q - radius), min(radius, -map_q + radius) + 1):
            x = center_cords[0] + (map_q * settings.x_offset) + (map_r * settings.x_offset / 2)
            y = center_cords[1] + (map_r * settings.y_offset)
            if 0 <= x <= settings.width and 0 <= y <= settings.height:
                hex_map.append({"q": map_q, "r": map_r, "value": 0, "x": x, "y": y})

    # creating sun with value 1
    sun_hex = [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    for one_hex in hex_map:
        if (one_hex["q"], one_hex["r"]) in sun_hex:
            one_hex["value"] = 1

    empty_hex = [one_hex for one_hex in hex_map if one_hex["value"] == 0]

    # creating planets with value 2
    planet_types_list = list(planet_types.keys())
    random.shuffle(planet_types_list)
    num_planets = random.randint(5, 6)
    for i in range(num_planets):
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


class HexMap:
    def __init__(self, center_cords, radius):
        self.hex_map = generate_hex_map(center_cords, radius)
        self.selected_spaceship = None
        self.movement_hex = []
        self.selected_planet = None
        self.font = pygame.font.Font(None, 30)
        self.planet_menu_active = False
        self.exit_button_rect = None
        self.save_map()

    def save_map(self):
        file_path = os.path.join(settings.save_dir, "map.json")
        with open(file_path, "w") as file:
            json.dump(self.hex_map, file, indent=4)

    def get_clicked_hex(self, pos):
        mouse_x, mouse_y = pos
        nearest_hex = min(self.hex_map, key=lambda h: (mouse_x - h["x"]) ** 2 + (mouse_y - h["y"]) ** 2)

        # Exit menu
        if self.planet_menu_active:
            if self.exit_button_rect.collidepoint(pos):
                self.planet_menu_active = False
                self.selected_planet = None
            return

        # if the spaceship was selected
        if self.selected_spaceship and nearest_hex in self.movement_hex:
            nearest_hex["value"] = 3
            self.selected_spaceship["value"] = 0
            self.selected_spaceship = None
            self.movement_hex = []
            return

        # spaceship select
        if nearest_hex["value"] == 3:
            self.selected_spaceship = nearest_hex
            self.movement_area(nearest_hex)
            self.selected_planet = None
        # planet select
        elif nearest_hex["value"] == 2:
            if self.can_select_planet(nearest_hex):
                self.selected_planet = nearest_hex
                self.planet_menu_active = True
                self.selected_spaceship = None
                self.movement_hex = []
        else:
            self.selected_spaceship = None
            self.movement_hex = []
            self.selected_planet = None

    def can_select_planet(self, planet_hex):
        for other_hex in self.hex_map:
            if other_hex["value"] == 3 and hex_distance(planet_hex, other_hex) == 1:
                return True
        return False

    def movement_area(self, start_hex):
        self.movement_hex = [h for h in self.hex_map if hex_distance(start_hex, h) == 1 and h["value"] == 0]

    def draw(self, screen):
        # Draw info bar
        pygame.draw.rect(screen, settings.black, (0, 0, settings.width, settings.info_bar_height))
        total_population = sum(one_hex.get("population", 0) for one_hex in self.hex_map)
        total_production = sum(one_hex.get("production", 0) for one_hex in self.hex_map)
        total_power = sum(one_hex.get("power", 0) for one_hex in self.hex_map)

        info_bar_x_offset = 5
        info_bar_y_offset = 5

        # Draw Population
        population_icon = pygame.transform.scale(hex_images['population'], (settings.icon_size, settings.icon_size))
        screen.blit(population_icon, (info_bar_x_offset, info_bar_y_offset))
        population_text = self.font.render(f": {total_population}", True, settings.white)
        screen.blit(population_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + population_text.get_width() + 10

        # Draw Production
        production_icon = pygame.transform.scale(hex_images['production'], (settings.icon_size, settings.icon_size))
        screen.blit(production_icon, (info_bar_x_offset, info_bar_y_offset))
        production_text = self.font.render(f": {total_production}", True, settings.white)
        screen.blit(production_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + production_text.get_width() + 10

        # Draw Power
        power_icon = pygame.transform.scale(hex_images['power'], (settings.icon_size, settings.icon_size))
        screen.blit(power_icon, (info_bar_x_offset, info_bar_y_offset))
        power_text = self.font.render(f": {total_power}", True, settings.white)
        screen.blit(power_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))

        for one_hex in self.hex_map:
            hex_points = get_hex_points(one_hex["x"], one_hex["y"], settings.hex_radius)
            # Draw planet hex
            if self.selected_planet == one_hex:
                pygame.draw.polygon(screen, settings.green, hex_points, 3)
            else:
                pygame.draw.polygon(screen, settings.white, hex_points, 1)
            # Draw barrier
            if self.selected_spaceship == one_hex:
                pygame.draw.polygon(screen, settings.red, hex_points, 3)

            # Draw planets # перенести в draw
            if one_hex["value"] == 2:
                planet_type = one_hex.get('planet_type')
                scaled_planet_image = pygame.transform.scale(planet_types[planet_type]['image'],
                                                             (int(settings.hex_width) - settings.indent,
                                                              int(settings.hex_width) - settings.indent))
                screen.blit(scaled_planet_image, scaled_planet_image.get_rect(center=(one_hex["x"], one_hex["y"])))

        # Draw possible movement
        if self.selected_spaceship:
            for one_hex in self.movement_hex:
                hex_points = get_hex_points(one_hex["x"], one_hex["y"], settings.hex_radius)
                pygame.draw.polygon(screen, settings.blue, hex_points, 3)

        # Draw objects
        self.draw_hex_image(screen, 'sun', 2.5)
        self.draw_hex_image(screen, 'spaceship', 1)

        # Draw planet menu
        if self.planet_menu_active and self.selected_planet:
            self.draw_planet_menu(screen)

    def draw_hex_image(self, screen, image, size):
        scaled_image = pygame.transform.scale(hex_images[image],
                                              (int(settings.hex_width) * size - settings.indent * size,
                                               int(settings.hex_width) * size - settings.indent * size))

        if image == 'sun':
            screen.blit(scaled_image, scaled_image.get_rect(center=(settings.width // 2, settings.height // 2)))
        elif image == 'spaceship':
            for one_hex in self.hex_map:
                if one_hex["value"] == 3:
                    screen.blit(scaled_image, scaled_image.get_rect(center=(one_hex["x"], one_hex["y"])))

    def draw_planet_menu(self, screen):
        # Draw menu background
        menu_x = settings.width // 2 - settings.menu_width // 2
        menu_y = settings.height // 2 - settings.menu_height // 2
        pygame.draw.rect(screen, settings.black, (menu_x, menu_y, settings.menu_width, settings.menu_height))
        pygame.draw.rect(screen, settings.white, (
            menu_x - settings.menu_outline, menu_y - settings.menu_outline,
            settings.menu_width + settings.menu_outline * 2, settings.menu_height + settings.menu_outline * 2),
                         settings.menu_outline)

        # Draw planet image area
        planet_area_x = menu_x + settings.menu_padding
        planet_area_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.white,
                         (planet_area_x, planet_area_y, settings.planet_image_size, settings.planet_image_size), 2)

        # Draw planet image
        planet_type = self.selected_planet.get('planet_type')
        planet_image = pygame.transform.scale(planet_types[planet_type]['image'], (
            settings.planet_image_size - 2 * settings.menu_padding,
            settings.planet_image_size - 2 * settings.menu_padding))
        screen.blit(planet_image, (planet_area_x + settings.menu_padding, planet_area_y + settings.menu_padding))

        stats_x = planet_area_x + settings.planet_image_size + settings.menu_padding
        stats_y = planet_area_y

        # Population
        pop_icon = pygame.transform.scale(hex_images['population'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(pop_icon, (stats_x, stats_y))
        pop_text = self.font.render(f": {self.selected_planet.get('population')}", True, settings.white)
        screen.blit(pop_text, (stats_x + settings.menu_icon_size, stats_y + (settings.menu_icon_size // 4)))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Production
        prod_icon = pygame.transform.scale(hex_images['production'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(prod_icon, (stats_x, stats_y))
        prod_text = self.font.render(f": {self.selected_planet.get('production')}", True, settings.white)
        screen.blit(prod_text, (stats_x + settings.menu_icon_size, stats_y + (settings.menu_icon_size // 4)))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Draw separation lines
        pygame.draw.line(screen, settings.white,
                         (planet_area_x, planet_area_y + settings.planet_image_size + settings.menu_padding),
                         (menu_x + settings.menu_width - settings.menu_padding,
                          planet_area_y + settings.planet_image_size + settings.menu_padding),
                         settings.menu_line_width)

        # Draw exit button
        button_x = menu_x + settings.menu_width - settings.exit_button_size - settings.menu_padding
        button_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.red,
                         (button_x, button_y, settings.exit_button_size, settings.exit_button_size))
        pygame.draw.rect(screen, settings.white,
                         (button_x - settings.exit_btn_outline, button_y - settings.exit_btn_outline,
                          settings.exit_button_size + settings.exit_btn_outline * 2,
                          settings.exit_button_size + settings.exit_btn_outline * 2),
                         settings.exit_btn_outline)
        exit_text = self.font.render('X', True, settings.white)
        screen.blit(exit_text, (button_x + 9, button_y + 7))
        self.exit_button_rect = pygame.Rect(button_x, button_y, settings.exit_button_size, settings.exit_button_size)


def game():
    hex_map = HexMap((settings.width // 2, settings.height // 2), settings.map_radius)
    background = pygame.transform.scale(load_image("cosmos.jpg"), (settings.width, settings.height))
    while True:
        settings.screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                hex_map.get_clicked_hex(event.pos)
        hex_map.draw(settings.screen)
        pygame.display.flip()
        settings.clock.tick(settings.fps)


def terminate():
    pygame.quit()
    sys.exit()


def main():
    game()


if __name__ == "__main__":
    sys.exit(main())
