import pygame

from scripts.constants import hex_images
from scripts.settings import settings


class TurnManager:
    """Control moves in the game"""

    def __init__(self):
        self.turn_count = 0
        self.max_turns = 30
        self.turn_button_rect = pygame.Rect(settings.width - settings.turn_button_size,
                                            settings.height - settings.turn_button_size,
                                            settings.turn_button_size, settings.turn_button_size)

    def is_game_over(self):
        """Checks if the game is over"""
        return self.turn_count >= self.max_turns

    def draw_turn_button(self, screen):
        """Draws the change move button"""
        screen.blit(
            pygame.transform.scale(hex_images['next_turn'], (settings.turn_button_size, settings.turn_button_size)),
            self.turn_button_rect.topleft)

    def handle_input(self, event, hex_map):
        """handles the change of move"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.turn_button_rect.collidepoint(event.pos):
                hex_map.deselect_all()
                self.turn_count += 1
                hex_map.spaceship_moved_this_turn = False


turn_manager = TurnManager()
