import math
import os
import pygame

from constants import hex_images


class GameSettings:
    """Storing basic game settings and initializing Pygame"""
    def __init__(self):
        self.width = 1000
        self.height = 750
        self.fps = 60

        # Colors
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'gray': (200, 200, 200)
        }

        # Visual settings
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

        # Saves
        self.save_dir = "../saves"
        os.makedirs(self.save_dir, exist_ok=True)

        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("scr")
        pygame.display.set_icon(hex_images['icon'])
        self.clock = pygame.time.Clock()


settings = GameSettings()
