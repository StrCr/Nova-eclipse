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
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

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
    'planet': load_image('planet_Cloudy.png')
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


class HexMap:
    def __init__(self, center_cords, radius):
        self.hexagon_points = []
        self.sun_hex_points = []
        self.planets_hex_points = []
        self.hex_positions = {}
        self.sun_hex_positions = {}
        self.planets_hex_positions = {}
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
                hex_points = get_hex_points(x, y, HEX_RADIUS)
                if value == 1:
                    self.sun_hex_points.append(hex_points)
                    self.sun_hex_positions[(x, y)] = (map_q, map_r)
                elif value == 2:
                    self.planets_hex_points.append(hex_points)
                    self.planets_hex_positions[(x, y)] = (map_q, map_r)
                self.hexagon_points.append(hex_points)
                self.hex_positions[(x, y)] = (map_q, map_r)

        return hex_map

    def save_map(self):
        file_path = os.path.join(SAVE_DIR, "map.json")
        with open(file_path, "w") as file:
            json.dump([{"q": key[0], "r": key[1], "value": value} for key, value in self.hex_map.items()], file, indent=4)

    def draw(self, screen):
        for hex_points in self.hexagon_points:
            pygame.draw.polygon(screen, WHITE, hex_points, 1)
        if self.sun_hex_points:
            self.draw_hex_image(screen, 'sun', 2.5)
        if self.planets_hex_points:
            self.draw_hex_image(screen, 'planet', 1)

    def draw_hex_image(self, screen, image, size):
        scaled_image = pygame.transform.scale(hex_images[image],
                                              (int(HEX_WIDTH) * size - INDENT * size,
                                               int(HEX_WIDTH) * size - INDENT * size))
        if size == 2.5:
            screen.blit(scaled_image, scaled_image.get_rect(center=CENTER_CORDS))
        if size == 1:
            if image == 'planet':
                for (x, y), _ in self.planets_hex_positions.items():
                    screen.blit(scaled_image, scaled_image.get_rect(center=(x, y)))

    def get_clicked_hex(self, pos):
        mouse_x, mouse_y = pos
        nearest_hex_cords = min(self.hex_positions, key=lambda p: (mouse_x - p[0]) ** 2 + (mouse_y - p[1]) ** 2)
        map_q, map_r = self.hex_positions[nearest_hex_cords]
        print(f"q={map_q}, r={map_r}")
        return map_q, map_r


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
