import pygame
import math
import sys
import os
import json
import random

# Game settings
pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nova Eclipse")
FPS = 60
clock = pygame.time.Clock()

# Colour
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Visual settings # переместить константы внутрь кода
HEX_RADIUS = 35
HEX_WIDTH = math.sqrt(3) * HEX_RADIUS
HEX_HEIGHT = 2 * HEX_RADIUS
X_OFFSET = HEX_WIDTH
Y_OFFSET = HEX_HEIGHT * 3 / 4
CENTER_CORDS = (WIDTH // 2, HEIGHT // 2)
MAP_RADIUS = 6
INDENT = 10
INFO_BAR_HEIGHT = 30
ICON_SIZE = 20
MENU_WIDTH = WIDTH // 2
MENU_HEIGHT = HEIGHT // 2
EXIT_BUTTON_SIZE = 30
EXIT_BTN_OUTLINE = 2
MENU_OUTLINE = 4
PLANET_IMAGE_SIZE = 100
MENU_ICON_SIZE = 40
MENU_LINE_WIDTH = 2
MENU_PADDING = 10

# Saves
SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)


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
    'planet': load_image('planet_Cloudy.png'),
    'spaceship': load_image('spaceship.png'),
    'population': load_image('icon_population.png'),
    'production': load_image('icon_gear.png'),
    'power': load_image('icon_power.png')
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
            x = center_cords[0] + (map_q * X_OFFSET) + (map_r * X_OFFSET / 2)
            y = center_cords[1] + (map_r * Y_OFFSET)
            if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                hex_map.append({"q": map_q, "r": map_r, "value": 0, "x": x, "y": y})

    # creating sun with value 1
    sun_hex = [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    for one_hex in hex_map:
        if (one_hex["q"], one_hex["r"]) in sun_hex:
            one_hex["value"] = 1

    empty_hex = [one_hex for one_hex in hex_map if one_hex["value"] == 0]

    # creating planets with value 2
    for _ in range(random.randint(3, 6)):
        if empty_hex:
            chosen_hex = random.choice(empty_hex)
            chosen_hex["value"] = 2
            chosen_hex["population"] = random.randint(50, 150)
            chosen_hex["production"] = random.randint(50, 150)
            empty_hex.remove(chosen_hex)

    # creating spaceship with value 3
    if empty_hex:
        chosen_hex = random.choice(empty_hex)
        chosen_hex["value"] = 3
        chosen_hex["power"] = random.randint(10, 100)
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
        file_path = os.path.join(SAVE_DIR, "map.json")
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
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, INFO_BAR_HEIGHT))
        total_population = sum(one_hex.get("population", 0) for one_hex in self.hex_map)
        total_production = sum(one_hex.get("production", 0) for one_hex in self.hex_map)
        total_power = sum(one_hex.get("power", 0) for one_hex in self.hex_map)

        info_bar_x_offset = 5
        info_bar_y_offset = 5

        # Draw Population
        population_icon = pygame.transform.scale(hex_images['population'], (ICON_SIZE, ICON_SIZE))
        screen.blit(population_icon, (info_bar_x_offset, info_bar_y_offset))
        population_text = self.font.render(f": {total_population}", True, WHITE)
        screen.blit(population_text, (info_bar_x_offset + ICON_SIZE, info_bar_y_offset))
        info_bar_x_offset += ICON_SIZE + population_text.get_width() + 10

        # Draw Production
        production_icon = pygame.transform.scale(hex_images['production'], (ICON_SIZE, ICON_SIZE))
        screen.blit(production_icon, (info_bar_x_offset, info_bar_y_offset))
        production_text = self.font.render(f": {total_production}", True, WHITE)
        screen.blit(production_text, (info_bar_x_offset + ICON_SIZE, info_bar_y_offset))
        info_bar_x_offset += ICON_SIZE + production_text.get_width() + 10

        # Draw Power
        power_icon = pygame.transform.scale(hex_images['power'], (ICON_SIZE, ICON_SIZE))
        screen.blit(power_icon, (info_bar_x_offset, info_bar_y_offset))
        power_text = self.font.render(f": {total_power}", True, WHITE)
        screen.blit(power_text, (info_bar_x_offset + ICON_SIZE, info_bar_y_offset))

        for one_hex in self.hex_map:
            hex_points = get_hex_points(one_hex["x"], one_hex["y"], HEX_RADIUS)
            # Draw planet hex
            if self.selected_planet == one_hex:
                pygame.draw.polygon(screen, GREEN, hex_points, 3)
            else:
                pygame.draw.polygon(screen, WHITE, hex_points, 1)
            # Draw barrier
            if self.selected_spaceship == one_hex:
                pygame.draw.polygon(screen, RED, hex_points, 3)

        # Draw possible movement
        if self.selected_spaceship:
            for one_hex in self.movement_hex:
                hex_points = get_hex_points(one_hex["x"], one_hex["y"], HEX_RADIUS)
                pygame.draw.polygon(screen, BLUE, hex_points, 3)

        # Draw objects
        self.draw_hex_image(screen, 'sun', 2.5)
        self.draw_hex_image(screen, 'planet', 1)
        self.draw_hex_image(screen, 'spaceship', 1)


        # Draw planet menu
        if self.planet_menu_active and self.selected_planet:
            self.draw_planet_menu(screen)

    def draw_planet_menu(self, screen):
        # Draw menu background
        menu_x = WIDTH // 2 - MENU_WIDTH // 2
        menu_y = HEIGHT // 2 - MENU_HEIGHT // 2
        pygame.draw.rect(screen, BLACK, (menu_x, menu_y, MENU_WIDTH, MENU_HEIGHT))
        pygame.draw.rect(screen, WHITE, (
        menu_x - MENU_OUTLINE, menu_y - MENU_OUTLINE, MENU_WIDTH + MENU_OUTLINE * 2, MENU_HEIGHT + MENU_OUTLINE * 2),
                         MENU_OUTLINE)

        # Draw planet image area
        planet_area_x = menu_x + MENU_PADDING
        planet_area_y = menu_y + MENU_PADDING
        pygame.draw.rect(screen, WHITE, (planet_area_x, planet_area_y, PLANET_IMAGE_SIZE, PLANET_IMAGE_SIZE), 2)

        # Draw planet image
        planet_image = pygame.transform.scale(hex_images['planet'], (
        PLANET_IMAGE_SIZE - 2 * MENU_PADDING, PLANET_IMAGE_SIZE - 2 * MENU_PADDING))
        screen.blit(planet_image, (planet_area_x + MENU_PADDING, planet_area_y + MENU_PADDING))

        stats_x = planet_area_x + PLANET_IMAGE_SIZE + MENU_PADDING
        stats_y = planet_area_y

        # Population
        pop_icon = pygame.transform.scale(hex_images['population'], (MENU_ICON_SIZE, MENU_ICON_SIZE))
        screen.blit(pop_icon, (stats_x, stats_y))
        pop_text = self.font.render(f": {self.selected_planet.get('population')}", True, WHITE)
        screen.blit(pop_text, (stats_x + MENU_ICON_SIZE, stats_y + (MENU_ICON_SIZE // 4)))
        stats_y += MENU_ICON_SIZE + MENU_PADDING

        # Production
        prod_icon = pygame.transform.scale(hex_images['production'], (MENU_ICON_SIZE, MENU_ICON_SIZE))
        screen.blit(prod_icon, (stats_x, stats_y))
        prod_text = self.font.render(f": {self.selected_planet.get('production')}", True, WHITE)
        screen.blit(prod_text, (stats_x + MENU_ICON_SIZE, stats_y + (MENU_ICON_SIZE // 4)))

        # Draw separation lines
        pygame.draw.line(screen, WHITE, (planet_area_x, planet_area_y + PLANET_IMAGE_SIZE + MENU_PADDING),
                         (menu_x + MENU_WIDTH - MENU_PADDING, planet_area_y + PLANET_IMAGE_SIZE + MENU_PADDING),
                         MENU_LINE_WIDTH)
        pygame.draw.line(screen, WHITE, (menu_x + MENU_WIDTH // 2, planet_area_y + PLANET_IMAGE_SIZE + MENU_PADDING),
                         (menu_x + MENU_WIDTH // 2, menu_y + MENU_HEIGHT - MENU_PADDING), MENU_LINE_WIDTH)

        # Draw decisions area
        decisions_area_x = menu_x + MENU_PADDING
        decisions_area_y = planet_area_y + PLANET_IMAGE_SIZE + 2 * MENU_PADDING

        decision_title = self.font.render("Решения:", True, WHITE)
        screen.blit(decision_title, (decisions_area_x, decisions_area_y))
        decisions_y = decisions_area_y + self.font.get_height() + MENU_PADDING

        decision_1 = self.font.render("Решение 1", True, WHITE)
        screen.blit(decision_1, (decisions_area_x, decisions_y))
        decisions_y += self.font.get_height() + MENU_PADDING

        decision_2 = self.font.render("Решение 2", True, WHITE)
        screen.blit(decision_2, (decisions_area_x, decisions_y))

        # Draw events area
        events_area_x = menu_x + MENU_WIDTH // 2 + MENU_PADDING
        events_area_y = planet_area_y + PLANET_IMAGE_SIZE + 2 * MENU_PADDING

        events_title = self.font.render("События:", True, WHITE)
        screen.blit(events_title, (events_area_x, events_area_y))
        events_y = events_area_y + self.font.get_height() + MENU_PADDING

        event_1 = self.font.render("Событие 1", True, WHITE)
        screen.blit(event_1, (events_area_x, events_y))
        events_y += self.font.get_height() + MENU_PADDING

        event_2 = self.font.render("Событие 2", True, WHITE)
        screen.blit(event_2, (events_area_x, events_y))

        # Draw exit button
        button_x = menu_x + MENU_WIDTH - EXIT_BUTTON_SIZE - MENU_PADDING
        button_y = menu_y + MENU_PADDING
        pygame.draw.rect(screen, RED, (button_x, button_y, EXIT_BUTTON_SIZE, EXIT_BUTTON_SIZE))
        pygame.draw.rect(screen, WHITE, (button_x - EXIT_BTN_OUTLINE, button_y - EXIT_BTN_OUTLINE,
                                         EXIT_BUTTON_SIZE + EXIT_BTN_OUTLINE * 2,
                                         EXIT_BUTTON_SIZE + EXIT_BTN_OUTLINE * 2),
                         EXIT_BTN_OUTLINE)
        exit_text = self.font.render('X', True, WHITE)
        screen.blit(exit_text, (button_x + 9, button_y + 7))
        self.exit_button_rect = pygame.Rect(button_x, button_y, EXIT_BUTTON_SIZE, EXIT_BUTTON_SIZE)

    def draw_hex_image(self, screen, image, size):
        scaled_image = pygame.transform.scale(hex_images[image],
                                              (int(HEX_WIDTH) * size - INDENT * size,
                                               int(HEX_WIDTH) * size - INDENT * size))

        if image == 'sun':
            screen.blit(scaled_image, scaled_image.get_rect(center=CENTER_CORDS))
        else:
            for one_hex in self.hex_map:
                if one_hex["value"] == 2 and image == 'planet':
                    screen.blit(scaled_image, scaled_image.get_rect(center=(one_hex["x"], one_hex["y"])))
                elif one_hex["value"] == 3 and image == 'spaceship':
                    screen.blit(scaled_image, scaled_image.get_rect(center=(one_hex["x"], one_hex["y"])))


def game():
    hex_map = HexMap(CENTER_CORDS, MAP_RADIUS)
    background = pygame.transform.scale(load_image("cosmos.jpg"), (WIDTH, HEIGHT))
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                hex_map.get_clicked_hex(event.pos)
        hex_map.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def main():
    game()


if __name__ == "__main__":
    sys.exit(main())
