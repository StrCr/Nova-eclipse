import pygame
import sys

from turn_manager import turn_manager
from settings import settings
from utils import load_image
from hex_map import HexMap


def start_screen():
    """Display start menu"""
    title_font = pygame.font.Font(None, 72)
    button_font = pygame.font.Font(None, 36)

    title_text = title_font.render("Nova Eclipse", True, settings.colors['white'])
    title_rect = title_text.get_rect(center=(settings.width // 2, settings.height // 3))

    start_button_text = button_font.render("Начать", True, settings.colors['black'])
    start_button_rect = start_button_text.get_rect(center=(settings.width // 2, settings.height // 2))
    start_button_cords = pygame.Rect(start_button_rect.left - 10, start_button_rect.top - 5,
                                     start_button_rect.width + 20, start_button_rect.height + 10)

    background = pygame.transform.scale(load_image("cosmos.jpg"), (settings.width, settings.height))
    while True:
        settings.screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_cords.collidepoint(event.pos):
                    return

        settings.screen.blit(title_text, title_rect)

        pygame.draw.rect(settings.screen, settings.colors['white'], start_button_cords)
        settings.screen.blit(start_button_text, start_button_rect)

        pygame.display.flip()
        settings.clock.tick(settings.fps)


def game():
    """Display main game"""
    hex_map = HexMap((settings.width // 2, settings.height // 2), settings.map_radius)
    background = pygame.transform.scale(load_image("cosmos.jpg"), (settings.width, settings.height))

    while not turn_manager.is_game_over():
        settings.screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                hex_map.get_clicked_hex(event.pos)

            turn_manager.handle_input(event, hex_map)

        hex_map.draw(settings.screen, turn_manager)
        turn_manager.draw_turn_button(settings.screen)
        pygame.display.flip()
        settings.clock.tick(settings.fps)
    return


def end_screen():
    """Display end menu"""
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)

    title_text = title_font.render("Игра окончена!", True, settings.colors['white'])
    title_rect = title_text.get_rect(center=(settings.width // 2, settings.height // 3))

    restart_button_text = text_font.render("Играть заново", True, settings.colors['black'])
    restart_button_rect = restart_button_text.get_rect(center=(settings.width // 2, settings.height * 2 // 3))
    restart_button_cords = pygame.Rect(restart_button_rect.left - 10, restart_button_rect.top - 5,
                                       restart_button_rect.width + 20, restart_button_rect.height + 10)

    exit_button_text = text_font.render("Выход", True, settings.colors['black'])
    exit_button_rect = exit_button_text.get_rect(center=(settings.width // 2, settings.height * 5 // 6))
    exit_button_cords = pygame.Rect(exit_button_rect.left - 10, exit_button_rect.top - 5,
                                    exit_button_rect.width + 20, exit_button_rect.height + 10)

    background = pygame.transform.scale(load_image("cosmos.jpg"), (settings.width, settings.height))
    while True:
        settings.screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_cords.collidepoint(event.pos):
                    game()
                    return
                elif exit_button_cords.collidepoint(event.pos):
                    terminate()

        settings.screen.blit(title_text, title_rect)

        pygame.draw.rect(settings.screen, settings.colors['white'], restart_button_cords)
        settings.screen.blit(restart_button_text, restart_button_rect)

        pygame.draw.rect(settings.screen, settings.colors['white'], exit_button_cords)
        settings.screen.blit(exit_button_text, exit_button_rect)

        pygame.display.flip()
        settings.clock.tick(settings.fps)


def terminate():
    pygame.quit()
    sys.exit()


def main():
    start_screen()
    game()
    end_screen()


if __name__ == "__main__":
    sys.exit(main())
