import pygame
import math
import sys
import os
import json
import random

# Game settings
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nova Eclipse")
FPS = 60
clock = pygame.time.Clock()

# Colour
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255,255,0)
GREEN = (0, 255, 0)

# Hex settings # переместить константы внутрь кода
HEX_RADIUS = 30
HEX_WIDTH = math.sqrt(3) * HEX_RADIUS
HEX_HEIGHT = 2 * HEX_RADIUS
X_OFFSET = HEX_WIDTH
Y_OFFSET = HEX_HEIGHT * 3 / 4
CENTER_CORDS = (WIDTH // 2, HEIGHT // 2)
MAP_RADIUS = 6

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


def get_hex_points(center_x, center_y, radius):
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points


class HexMap:
    def __init__(self, center_cords, radius):
        self.hexagons = []
        self.sun = []
        self.planets = []
        self.hex_positions = {}
        self.hex_map = self.generate_hex_map(center_cords, radius)
        self.save_map()

    def generate_hex_map(self, center_cords, radius):
        hex_map = {}

        # creating hex_map with value 0
        for map_q in range(-radius, radius + 1):
            for map_r in range(max(-radius, -map_q - radius), min(radius, -map_q + radius) + 1):
                hex_map[(map_q, map_r)] = 0

        # creating sun with value 1
        sun_hexs = [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        for q, r in sun_hexs:
            if (q, r) in hex_map:
                hex_map[(q, r)] = 1

        empty_hexes = [pos for pos, value in hex_map.items() if value == 0]  # empty_hexes for random hexes
        # creating planets with value 2
        for _ in range(random.randint(3, 6)):
            if empty_hexes:
                chosen_hex = random.choice(empty_hexes)
                hex_map[chosen_hex] = 2
                empty_hexes.remove(chosen_hex)

        # creating self.hex_positions for get_clicked_hex
        # creating self.hexagons, self.sun, self.planets for draw
        for (map_q, map_r), value in hex_map.items():
            x = center_cords[0] + (map_q * X_OFFSET) + (map_r * X_OFFSET / 2)
            y = center_cords[1] + (map_r * Y_OFFSET)
            if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                self.hex_positions[(x, y)] = (map_q, map_r)
                hex_points = get_hex_points(x, y, HEX_RADIUS)
                if value == 1:
                    self.sun.append(hex_points)
                elif value == 2:
                    self.planets.append(hex_points)
                self.hexagons.append(hex_points)

        return hex_map

    def save_map(self):
        file_path = os.path.join(SAVE_DIR, "map.json")
        with open(file_path, "w") as file:
            json.dump({f"({key[0]}, {key[1]})": value for key, value in self.hex_map.items()}, file, indent=4)

    def draw(self, screen):
        for hex_points in self.hexagons:
            pygame.draw.polygon(screen, WHITE, hex_points, 1)
        for sun in self.sun:
            pygame.draw.polygon(screen, YELLOW, sun)
        for planet in self.planets:
            pygame.draw.polygon(screen, GREEN, planet)

    def get_clicked_hex(self, pos):
        mouse_x, mouse_y = pos
        for (hex_x, hex_y), (map_q, map_r) in self.hex_positions.items():
            distance = math.sqrt((mouse_x - hex_x) ** 2 + (mouse_y - hex_y) ** 2)
            if distance < HEX_RADIUS:
                print(f"q={map_q}, r={map_r}")
                return map_q, map_r
        return None


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
