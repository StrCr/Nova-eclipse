import math
import os
import sys
import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('../data', name)
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


def hex_distance(hex1, hex2):
    """Calculates the distance between two hexagons with cords (q, r)"""
    return (abs(hex1["q"] - hex2["q"]) + abs(hex1["q"] + hex1["r"] - hex2["q"] - hex2["r"])
            + abs(hex1["r"] - hex2["r"])) // 2
