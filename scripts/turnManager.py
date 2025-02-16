import pygame

from scripts.constants import hex_images
from scripts.settings import settings


class TurnManager:
    """Control moves in the game"""
    def __init__(self):
        self.game_over = False
        self.turn_count = 0
        self.max_turns = 10
        self.turn_button_rect = pygame.Rect(settings.width - settings.turn_button_size,
                                            settings.height - settings.turn_button_size,
                                            settings.turn_button_size, settings.turn_button_size)

    def draw_turn_button(self, screen):
        """Draws the change move button"""
        screen.blit(
            pygame.transform.scale(hex_images['next_turn'], (settings.turn_button_size, settings.turn_button_size)),
            self.turn_button_rect.topleft)

    def handle_input(self, event, hexmap):
        """Changes the move and checks whether the game is finished"""
        if ((event.type == pygame.MOUSEBUTTONDOWN and self.turn_button_rect.collidepoint(event.pos)) or
           (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):  # изменить
            for one_cell in hexmap.hex_map:
                if one_cell["value"] == 3 and "fuel" in one_cell and one_cell['fuel'] <= 0:
                    self.game_over = True
            if self.turn_count >= self.max_turns:
                self.game_over = True
            hexmap.deselect_all()
            hexmap.spaceship_moved_this_turn = False
            self.turn_count += 1
            hexmap.save_map()  # изменить


turn_manager = TurnManager()
