import math


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
