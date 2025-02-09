import os
import sys
import pygame


class ResourceManager:
    def __init__(self, images_dir):
        self.images_dir = images_dir
        self.loaded_images = {}  # Cash for loaded images

    def load_image(self, name, colorkey=None):
        if name in self.loaded_images:
            return self.loaded_images[name]

        fullname = os.path.join(self.images_dir, name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)

        self.loaded_images[name] = image  # Cash the image
        return image

    def load_sound(self, name):
        ...

    def load_font(self, name, size):
        ...

    def load_saves(self, name):
        ...
