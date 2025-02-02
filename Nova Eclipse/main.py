import pygame
import math
import sys
import os

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
MALINA = (220, 20, 60)
GREEN = (0, 255, 0)

# Hex settings
HEX_RADIUS = 30
HEX_WIDTH = math.sqrt(3) * HEX_RADIUS
HEX_HEIGHT = 2 * HEX_RADIUS
X_OFFSET = HEX_WIDTH
Y_OFFSET = HEX_HEIGHT * 3 / 4
CENTER_CORDS = (WIDTH // 2, HEIGHT // 2)
MAP_RADIUS = 6


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


def terminate():
    pygame.quit()
    sys.exit()


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
        # self.q_hexagons = []
        # self.r_hexagons = []
        self.hex_positions = {}
        self.generate_hex_map(center_cords, radius)

    def generate_hex_map(self, center_cords, radius):
        for map_q in range(-radius, radius + 1):
            for map_r in range(max(-radius, -map_q - radius), min(radius, -map_q + radius) + 1):
                x = center_cords[0] + (map_q * X_OFFSET) + (map_r * X_OFFSET / 2)
                y = center_cords[1] + (map_r * Y_OFFSET)
                if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:  # изменить для камеры
                    hex_points = get_hex_points(x, y, HEX_RADIUS)
                    # if map_q == 1:
                    #     self.q_hexagons.append(hex_points)
                    # elif map_r == 0:
                    #     self.r_hexagons.append(hex_points)
                    self.hexagons.append(hex_points)
                    self.hex_positions[(x, y)] = (map_q, map_r)

    def draw(self, screen):
        for hex_points in self.hexagons:
            pygame.draw.polygon(screen, WHITE, hex_points, 1)
        # for q_hex_points in self.q_hexagons:
        #     pygame.draw.polygon(screen, MALINA, q_hex_points)
        # for r_hex_points in self.r_hexagons:
        #     pygame.draw.polygon(screen, GREEN, r_hex_points)

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


def main():
    game()


if __name__ == "__main__":
    sys.exit(main())
