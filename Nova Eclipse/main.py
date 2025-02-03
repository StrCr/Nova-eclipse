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

# Hex settings # переместить константы внутрь кода
HEX_RADIUS = 35
HEX_WIDTH = math.sqrt(3) * HEX_RADIUS
HEX_HEIGHT = 2 * HEX_RADIUS
X_OFFSET = HEX_WIDTH
Y_OFFSET = HEX_HEIGHT * 3 / 4
CENTER_CORDS = (WIDTH // 2, HEIGHT // 2)
MAP_RADIUS = 6
INDENT = 10

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
    'spaceship': load_image('spaceship.png')
}


# player_image = load_image('mar.png')


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
            empty_hex.remove(chosen_hex)

    # creating spaceship with value 3
    if empty_hex:
        chosen_hex = random.choice(empty_hex)
        chosen_hex["value"] = 3
        empty_hex.remove(chosen_hex)

    return hex_map


class HexMap:
    def __init__(self, center_cords, radius):
        self.hex_map = generate_hex_map(center_cords, radius)
        self.selected_spaceship = None
        self.movement_hex = []
        self.save_map()

    def save_map(self):
        file_path = os.path.join(SAVE_DIR, "map.json")
        with open(file_path, "w") as file:
            json.dump(self.hex_map, file, indent=4)

    def get_clicked_hex(self, pos):
        mouse_x, mouse_y = pos
        nearest_hex = min(self.hex_map, key=lambda h: (mouse_x - h["x"]) ** 2 + (mouse_y - h["y"]) ** 2)
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
        else:
            self.selected_spaceship = None
            self.movement_hex = []

    def movement_area(self, start_hex):
        self.movement_hex = [h for h in self.hex_map if hex_distance(start_hex, h) == 1 and h["value"] == 0]

    def draw(self, screen):
        for one_hex in self.hex_map:
            hex_points = get_hex_points(one_hex["x"], one_hex["y"], HEX_RADIUS)
            pygame.draw.polygon(screen, WHITE, hex_points, 1)
            if self.selected_spaceship == one_hex:
                pygame.draw.polygon(screen, RED, hex_points, 3)

        if self.selected_spaceship:
            for one_hex in self.movement_hex:
                hex_points = get_hex_points(one_hex["x"], one_hex["y"], HEX_RADIUS)
                pygame.draw.polygon(screen, BLUE, hex_points, 3)

        self.draw_hex_image(screen, 'sun', 2.5)
        self.draw_hex_image(screen, 'planet', 1)
        self.draw_hex_image(screen, 'spaceship', 1)

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
