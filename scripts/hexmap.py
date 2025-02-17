import pygame
import os
import json
import random

from scripts.settings import settings
from scripts.utils import hex_distance, get_hex_points
from scripts.constants import hex_images, planet_types


def generate_hex_map(center_cords, radius):
    """Generating a map and assigning values to hexagons"""
    hex_map = []

    for map_q in range(-radius, radius + 1):
        for map_r in range(max(-radius, -map_q - radius), min(radius, -map_q + radius) + 1):
            x = center_cords[0] + (map_q * settings.x_offset) + (map_r * settings.x_offset / 2)
            y = center_cords[1] + (map_r * settings.y_offset)
            if 0 <= x <= settings.width and 0 <= y <= settings.height:
                hex_map.append({"q": map_q, "r": map_r, "value": 0, "x": x, "y": y})

    # creating sun with value 1
    sun_hex_coords = [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    for one_hex in hex_map:
        if (one_hex["q"], one_hex["r"]) in sun_hex_coords:
            one_hex["value"] = 1

    empty_hex = [one_hex for one_hex in hex_map if one_hex["value"] == 0]

    # creating planets with value 2
    planet_types_list = list(planet_types.keys())
    random.shuffle(planet_types_list)
    for i in range(random.randint(5, 6)):
        chosen_hex = random.choice(empty_hex)
        chosen_hex["value"] = 2
        chosen_hex["planet_type"] = planet_types_list[i % len(planet_types_list)]
        chosen_hex["population"] = random.randint(1000, 2000)
        chosen_hex["specialization"] = None
        chosen_hex["is_planet_active"] = True
        empty_hex.remove(chosen_hex)

    # creating spaceship with value 3
    chosen_hex = random.choice(empty_hex)
    chosen_hex["value"] = 3
    chosen_hex["fuel"] = 100
    chosen_hex["population"] = 0
    chosen_hex["production"] = 0
    empty_hex.remove(chosen_hex)

    # creating spaceship with value 4
    possible_locations = [hex_tile for hex_tile in empty_hex if
                          (hex_tile["r"] == settings.map_radius or hex_tile["r"] == -settings.map_radius or
                           hex_tile["q"] == settings.map_radius or hex_tile["q"] == -settings.map_radius) or
                          -hex_tile["q"] - hex_tile["r"] == settings.map_radius or
                          -hex_tile["q"] - hex_tile["r"] == -settings.map_radius]
    chosen_hex = random.choice(possible_locations)
    chosen_hex["value"] = 4
    chosen_hex["population"] = 0
    empty_hex.remove(chosen_hex)

    return hex_map


class HexMap:
    """Responsible for the map in the main game"""

    def __init__(self, center_cords, radius):
        self.hex_map = generate_hex_map(center_cords, radius)
        self.selected_spaceship = None
        self.movement_hex = []
        self.selected_planet = None
        self.selected_transport = None
        self.spaceship_moved_this_turn = False
        self.font = pygame.font.Font(None, 30)
        self.save_map()

        # Status
        self.planet_menu_active = False
        self.transport_menu_active = False

        # Planet menu buttons
        self.exit_button_rect = None

        # Planet resources buttons
        self.fuel_button_100_rect = None
        self.population_button_100_rect = None
        self.production_button_100_rect = None
        self.fuel_button_10_rect = None
        self.population_button_10_rect = None
        self.production_button_10_rect = None

        # Planet specialization buttons
        self.specialize_fuel_rect = None
        self.specialize_population_rect = None
        self.specialize_production_rect = None

    def save_map(self):
        file_path = os.path.join(settings.save_dir, "map.json")
        with open(file_path, "w") as file:
            json.dump(self.hex_map, file, indent=4)

    def get_clicked_hex(self, pos):
        mouse_x, mouse_y = pos

        # Planet menu buttons
        if self.planet_menu_active:
            # Exit button click
            if self.exit_button_rect and self.exit_button_rect.collidepoint(pos):
                self.planet_menu_active = False
                self.selected_planet = None
                return

            # Fuel buttons click
            elif (self.fuel_button_100_rect and self.fuel_button_100_rect.collidepoint(pos) and
                  self.selected_planet['is_planet_active']):
                self.add_resource_to_spaceship("fuel", 100)
                self.selected_planet['is_planet_active'] = False
                return
            elif (self.fuel_button_10_rect and self.fuel_button_10_rect.collidepoint(pos) and
                  self.selected_planet['is_planet_active']):
                self.add_resource_to_spaceship("fuel", 10)
                self.selected_planet['is_planet_active'] = False
                return

            # Population buttons click
            elif (self.population_button_100_rect and self.population_button_100_rect.collidepoint(pos) and
                  self.selected_planet['is_planet_active']):
                self.transfer_population_to_ship(100)
                self.selected_planet['is_planet_active'] = False
                return
            elif (self.population_button_10_rect and self.population_button_10_rect.collidepoint(pos) and
                  self.selected_planet['is_planet_active']):
                self.transfer_population_to_ship(10)
                self.selected_planet['is_planet_active'] = False
                return

            # Production buttons click
            elif (self.production_button_100_rect and self.production_button_100_rect.collidepoint(pos) and
                 self.selected_planet['is_planet_active']):
                self.add_resource_to_spaceship("production", 100)
                self.selected_planet['is_planet_active'] = False
                return
            elif (self.production_button_10_rect and self.production_button_10_rect.collidepoint(pos) and
                 self.selected_planet['is_planet_active']):
                self.add_resource_to_spaceship("production", 10)
                self.selected_planet['is_planet_active'] = False
                return

            # Specialization buttons click
            elif self.specialize_fuel_rect and self.specialize_fuel_rect.collidepoint(pos):
                self.set_planet_specialization("fuel")
                return
            elif self.specialize_population_rect and self.specialize_population_rect.collidepoint(pos):
                self.set_planet_specialization("population")
                return
            elif self.specialize_production_rect and self.specialize_production_rect.collidepoint(pos):
                self.set_planet_specialization("production")
                return

            # If none of the buttons were clicked, exit the function
            return

        # Transport menu buttons
        if self.transport_menu_active:
            if self.exit_button_rect and self.exit_button_rect.collidepoint(pos):
                self.transport_menu_active = False
                self.selected_transport = None
            return

        nearest_hex = min(self.hex_map, key=lambda h: (mouse_x - h["x"]) ** 2 + (mouse_y - h["y"]) ** 2)
        # Selected hexagon
        if self.selected_spaceship and nearest_hex in self.movement_hex and not self.spaceship_moved_this_turn:
            self.move_spaceship(nearest_hex)
        elif nearest_hex["value"] == 3 and not self.spaceship_moved_this_turn:
            self.select_spaceship(nearest_hex)
        elif nearest_hex["value"] == 2 and self.can_select_object(nearest_hex):
            self.select_planet(nearest_hex)
        elif nearest_hex["value"] == 4 and self.can_select_object(nearest_hex):
            self.select_transport_spaceship(nearest_hex)
        else:
            self.deselect_all()

    def move_spaceship(self, target_hex):
        target_hex["value"] = 3
        target_hex["fuel"] = self.selected_spaceship["fuel"] - 5
        target_hex["population"] = self.selected_spaceship["population"]
        target_hex["production"] = self.selected_spaceship["production"]
        self.selected_spaceship["value"] = 0
        del self.selected_spaceship["fuel"]
        del self.selected_spaceship["population"]
        del self.selected_spaceship["production"]
        self.deselect_all()
        self.spaceship_moved_this_turn = True

    def select_spaceship(self, hex):
        self.selected_spaceship = hex
        self.movement_area(hex)
        self.selected_planet = None

    def select_planet(self, hex):
        self.selected_planet = hex
        self.planet_menu_active = True
        self.selected_spaceship = None
        self.movement_hex = []

    def select_transport_spaceship(self, hex):
        self.selected_transport = hex
        for other_hex in self.hex_map:
            if other_hex["value"] == 2:
                other_hex["is_planet_active"] = True
        self.transport_menu_active = True
        self.selected_spaceship = None
        self.movement_hex = []

    def deselect_all(self):
        self.selected_spaceship = None
        self.movement_hex = []
        self.selected_planet = None
        self.planet_menu_active = False
        self.transport_menu_active = False

    def can_select_object(self, object_hex):
        for other_hex in self.hex_map:
            if other_hex["value"] == 3 and hex_distance(object_hex, other_hex) == 1:
                return True
        return False

    def movement_area(self, start_hex):
        self.movement_hex = [h for h in self.hex_map if hex_distance(start_hex, h) == 1 and h["value"] == 0]

    def set_planet_specialization(self, specialization):
        """Sets the planet's specialization and updates the hex_map."""
        if self.selected_planet:
            self.selected_planet["specialization"] = specialization
            self.save_map()

    def transfer_population_to_ship(self, amount):
        """Transfers population from the selected planet to the nearest spaceship."""
        nearest_spaceship = None

        for other_hex in self.hex_map:
            if other_hex["value"] == 3:
                nearest_spaceship = other_hex

        if nearest_spaceship is None:
            return

        if self.selected_planet["population"] >= amount:
            self.selected_planet["population"] -= amount
            nearest_spaceship["population"] += amount
        else:
            amount = self.selected_planet["population"]
            nearest_spaceship["population"] += amount
            self.selected_planet["population"] = 0

    def draw(self, screen, turn):
        # Draw info bar
        self.draw_info_bar(screen, turn)

        # Draw hexes
        for one_hex in self.hex_map:
            self.draw_hex(screen, one_hex)

        # Draw possible movement
        if self.selected_spaceship:
            self.draw_movement_area(screen)

        # Draw objects (sun и spaceship)
        self.draw_hex_image(screen, 'sun', 2.5)
        self.draw_hex_image(screen, 'spaceship', 1)
        self.draw_hex_image(screen, 'transport_spaceship', 1)

        # Draw planet menu
        if self.planet_menu_active and self.selected_planet:
            self.draw_planet_menu(screen)

        # Draw transport menu
        if self.transport_menu_active and self.selected_transport:
            self.draw_transport_menu(screen)

    def draw_info_bar(self, screen, turn):
        pygame.draw.rect(screen, settings.colors['black'], (0, 0, settings.width, settings.info_bar_height))
        total_population = sum(one_hex.get("population", 0) for one_hex in self.hex_map if one_hex.get("value") == 3)
        total_production = sum(one_hex.get("production", 0) for one_hex in self.hex_map)
        total_fuel = sum(one_hex.get("fuel", 0) for one_hex in self.hex_map)

        info_bar_x_offset = 5
        info_bar_y_offset = 5

        # Draw Population
        population_icon = pygame.transform.scale(hex_images['population'], (settings.icon_size, settings.icon_size))
        screen.blit(population_icon, (info_bar_x_offset, info_bar_y_offset))
        population_text = self.font.render(f" {total_population}", True, settings.colors['white'])
        screen.blit(population_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + population_text.get_width() + 10

        # Draw Production
        production_icon = pygame.transform.scale(hex_images['production'], (settings.icon_size, settings.icon_size))
        screen.blit(production_icon, (info_bar_x_offset, info_bar_y_offset))
        production_text = self.font.render(f" {total_production}", True, settings.colors['white'])
        screen.blit(production_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + production_text.get_width() + 10

        # Draw Power
        power_icon = pygame.transform.scale(hex_images['fuel'], (settings.icon_size, settings.icon_size))
        screen.blit(power_icon, (info_bar_x_offset, info_bar_y_offset))
        power_text = self.font.render(f" {total_fuel}", True, settings.colors['white'])
        screen.blit(power_text, (info_bar_x_offset + settings.icon_size, info_bar_y_offset))
        info_bar_x_offset += settings.icon_size + power_text.get_width() + 10

        # Draw turn counter
        turn_text = self.font.render(f"{turn.turn_count}/{turn.max_turns}", True, settings.colors['white'])
        text_rect = turn_text.get_rect(topright=(settings.width - 10, settings.info_bar_height - 23))
        screen.blit(turn_text, text_rect)

    def draw_hex(self, screen, one_hex):
        hex_points = get_hex_points(one_hex["x"], one_hex["y"], settings.hex_radius)
        width = 1

        if self.selected_spaceship == one_hex:
            color = settings.colors['red']
            width = 3
        elif self.selected_planet == one_hex or self.selected_transport == one_hex:
            color = settings.colors['green']
            width = 3
        else:
            color = settings.colors['white']

        pygame.draw.polygon(screen, color, hex_points, width)

        if one_hex["value"] == 2:
            planet_type = one_hex.get('planet_type')
            planet_image_key = planet_types[planet_type]['image']
            scaled_planet_image = pygame.transform.scale(hex_images[planet_image_key],
                                                         (int(settings.hex_width) - settings.indent,
                                                          int(settings.hex_width) - settings.indent))
            screen.blit(scaled_planet_image, scaled_planet_image.get_rect(center=(one_hex["x"], one_hex["y"])))

    def draw_movement_area(self, screen):
        for one_hex in self.movement_hex:
            hex_points = get_hex_points(one_hex["x"], one_hex["y"], settings.hex_radius)
            pygame.draw.polygon(screen, settings.colors['blue'], hex_points, 3)

    def draw_hex_image(self, screen, image, size):
        scaled_image = pygame.transform.scale(hex_images[image],
                                              (int(settings.hex_width) * size - settings.indent * size,
                                               int(settings.hex_width) * size - settings.indent * size))
        rect = scaled_image.get_rect()

        # Draw sun with value 1 (Always in the center)
        if image == 'sun':
            rect.center = (settings.width // 2, settings.height // 2)
            screen.blit(scaled_image, rect)
        # Draw spaceship with value 3
        if image == 'spaceship':
            for one_hex in self.hex_map:
                if one_hex["value"] == 3:
                    rect = scaled_image.get_rect(center=(one_hex["x"], one_hex["y"]))
                    screen.blit(scaled_image, rect)
                    break
        # Draw transport_spaceship with value 4
        if image == 'transport_spaceship':
            for one_hex in self.hex_map:
                if one_hex["value"] == 4:
                    rect = scaled_image.get_rect(center=(one_hex["x"], one_hex["y"]))
                    screen.blit(scaled_image, rect)
                    break

    def draw_planet_menu(self, screen):
        # Draw menu background
        menu_x = settings.width // 2 - settings.menu_width // 2
        menu_y = settings.height // 2 - settings.menu_height // 2
        pygame.draw.rect(screen, settings.colors['black'], (menu_x, menu_y, settings.menu_width, settings.menu_height))
        pygame.draw.rect(screen, settings.colors['white'],
                         (menu_x - settings.menu_outline, menu_y - settings.menu_outline,
                          settings.menu_width + settings.menu_outline * 2,
                          settings.menu_height + settings.menu_outline * 2), settings.menu_outline)

        # Draw planet image area
        planet_area_x = menu_x + settings.menu_padding
        planet_area_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['white'], (planet_area_x, planet_area_y,
                                                            settings.planet_image_size, settings.planet_image_size), 2)

        # Draw planet image
        planet_type = self.selected_planet.get('planet_type')
        planet_image_key = planet_types[planet_type]['image']
        planet_image = pygame.transform.scale(hex_images[planet_image_key],
                                              (settings.planet_image_size - 2 * settings.menu_padding,
                                               settings.planet_image_size - 2 * settings.menu_padding))
        screen.blit(planet_image, (planet_area_x + settings.menu_padding, planet_area_y + settings.menu_padding))

        stats_x = planet_area_x + settings.planet_image_size + settings.menu_padding
        stats_y = planet_area_y

        # Icons
        population_icon = pygame.transform.scale(hex_images['population'], (settings.menu_icon_size,
                                                                            settings.menu_icon_size))
        production_icon = pygame.transform.scale(hex_images['production'], (settings.menu_icon_size,
                                                                            settings.menu_icon_size))
        fuel_icon = pygame.transform.scale(hex_images['fuel'], (settings.menu_icon_size,
                                                                settings.menu_icon_size))

        # Mini icons
        mini_population_icon = pygame.transform.scale(hex_images['population'], (settings.resource_button_height,
                                                                                 settings.resource_button_height))
        mini_production_icon = pygame.transform.scale(hex_images['production'], (settings.resource_button_height,
                                                                                 settings.resource_button_height))
        mini_fuel_icon = pygame.transform.scale(hex_images['fuel'], (settings.resource_button_height,
                                                                     settings.resource_button_height))

        # Population
        population_text = self.font.render(f"{self.selected_planet.get('population')}", True, settings.colors['white'])
        screen.blit(population_text, (stats_x, stats_y + (settings.menu_icon_size // 4)))
        screen.blit(population_icon, (stats_x + population_text.get_width(), stats_y))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Specialization
        specialization = self.selected_planet.get('specialization')
        specialization_icon = None

        if specialization == "fuel":
            specialization_icon = fuel_icon
        elif specialization == "population":
            specialization_icon = population_icon
        elif specialization == "production":
            specialization_icon = production_icon

        specialization_text = self.font.render(f"Специализация:", True, settings.colors['white'])
        screen.blit(specialization_text, (stats_x, stats_y + (settings.menu_icon_size // 4)))

        if specialization_icon:
            screen.blit(specialization_icon, (stats_x + specialization_text.get_width(), stats_y))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Draw separation lines
        separator_y = planet_area_y + settings.planet_image_size + settings.menu_padding
        pygame.draw.line(screen, settings.colors['white'], (planet_area_x, separator_y),
                         (menu_x + settings.menu_width - settings.menu_padding, separator_y), settings.menu_line_width)

        # Resource Buttons
        button_x = menu_x + settings.menu_padding
        button_y = separator_y + settings.menu_padding

        # Are the buttons active depending on the specialization
        fuel_100_active = False
        population_100_active = False
        production_100_active = False
        fuel_10_active = False
        population_10_active = False
        production_10_active = False

        if specialization and self.selected_planet.get('is_planet_active'):
            fuel_100_active = specialization == "fuel"
            population_100_active = specialization == "population"
            production_100_active = specialization == "production"
            fuel_10_active = specialization != "fuel"
            population_10_active = specialization != "population"
            production_10_active = specialization != "production"

        # Resources buttons row 1
        self.fuel_button_100_rect = self.draw_resource_button(screen, button_x, button_y, mini_fuel_icon, "+100",
                                                              settings.colors['white'] if fuel_100_active
                                                              else settings.colors['black'],
                                                              settings.colors['black'] if fuel_100_active
                                                              else settings.colors['grey'],
                                                              fuel_100_active)
        button_x += settings.resource_button_width + settings.resource_button_padding
        self.population_button_100_rect = self.draw_resource_button(screen, button_x, button_y, mini_population_icon,
                                                                    "+100",
                                                                    settings.colors['white'] if population_100_active
                                                                    else settings.colors['black'],
                                                                    settings.colors['black'] if population_100_active
                                                                    else settings.colors['grey'],
                                                                    population_100_active)
        button_x += settings.resource_button_width + settings.resource_button_padding
        self.production_button_100_rect = self.draw_resource_button(screen, button_x, button_y, mini_production_icon,
                                                                    "+100",
                                                                    settings.colors['white'] if production_100_active
                                                                    else settings.colors['black'],
                                                                    settings.colors['black'] if production_100_active
                                                                    else settings.colors['grey'],
                                                                    production_100_active)

        # Resources buttons row 2
        button_x = menu_x + settings.menu_padding
        button_y += settings.resource_button_height + settings.resource_button_padding

        self.fuel_button_10_rect = self.draw_resource_button(screen, button_x, button_y, mini_fuel_icon, "+10",
                                                             settings.colors['white'] if fuel_10_active
                                                             else settings.colors['black'],
                                                             settings.colors['black'] if fuel_10_active
                                                             else settings.colors['grey'],
                                                             fuel_10_active)
        button_x += settings.resource_button_width + settings.resource_button_padding
        self.population_button_10_rect = self.draw_resource_button(screen, button_x, button_y, mini_population_icon,
                                                                   "+10",
                                                                   settings.colors['white'] if population_10_active
                                                                   else settings.colors['black'],
                                                                   settings.colors['black'] if population_10_active
                                                                   else settings.colors['grey'],
                                                                   population_10_active)
        button_x += settings.resource_button_width + settings.resource_button_padding
        self.production_button_10_rect = self.draw_resource_button(screen, button_x, button_y, mini_production_icon,
                                                                   "+10",
                                                                   settings.colors['white'] if production_10_active
                                                                   else settings.colors['black'],
                                                                   settings.colors['black'] if production_10_active
                                                                   else settings.colors['grey'],
                                                                   production_10_active)

        # Draw separation lines
        separator_y = button_y + settings.resource_button_height + settings.menu_padding
        pygame.draw.line(screen, settings.colors['white'], (planet_area_x, separator_y),
                         (menu_x + settings.menu_width - settings.menu_padding, separator_y), settings.menu_line_width)

        # Specialization buttons row 3
        specialize_button_y = separator_y + settings.menu_padding

        specialize_fuel_x = menu_x + settings.menu_padding
        self.specialize_fuel_rect = self.draw_specialization_button(screen, specialize_fuel_x,
                                                                    specialize_button_y, mini_fuel_icon, True)

        specialize_population_x = specialize_fuel_x + settings.resource_button_width + settings.resource_button_padding
        self.specialize_population_rect = self.draw_specialization_button(screen, specialize_population_x,
                                                                          specialize_button_y, mini_population_icon, True)

        specialize_production_x = (specialize_population_x + settings.resource_button_width +
                                   settings.resource_button_padding)
        self.specialize_production_rect = self.draw_specialization_button(screen, specialize_production_x,
                                                                          specialize_button_y, mini_production_icon, True)

        # Draw exit button
        button_x = menu_x + settings.menu_width - settings.exit_button_size - settings.menu_padding
        button_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['red'],
                         (button_x, button_y, settings.exit_button_size, settings.exit_button_size))
        pygame.draw.rect(screen, settings.colors['white'],
                         (button_x - settings.exit_btn_outline, button_y - settings.exit_btn_outline,
                         settings.exit_button_size + settings.exit_btn_outline * 2,
                         settings.exit_button_size + settings.exit_btn_outline * 2),
                         settings.exit_btn_outline)
        exit_text = self.font.render('X', True, settings.colors['white'])
        screen.blit(exit_text, (button_x + 9, button_y + 7))
        self.exit_button_rect = pygame.Rect(button_x, button_y, settings.exit_button_size, settings.exit_button_size)

    def draw_resource_button(self, screen, x, y, icon, text, text_color, button_color, is_active):
        """Draws a resource button and returns its rect"""
        pygame.draw.rect(screen, button_color, (x, y, settings.resource_button_width, settings.resource_button_height))
        pygame.draw.rect(screen, settings.colors['white'],
                         (x, y, settings.resource_button_width, settings.resource_button_height), 1)

        text_surface = self.font.render(text, True, text_color)
        text_width, text_height = text_surface.get_size()
        icon_width, icon_height = icon.get_size()
        total_width = text_width + icon_width

        text_x = x + (settings.resource_button_width - total_width) // 2
        text_y = y + (settings.resource_button_height - text_height) // 2
        icon_x = text_x + text_width
        icon_y = y + (settings.resource_button_height - icon_height) // 2

        screen.blit(text_surface, (text_x, text_y))
        screen.blit(icon, (icon_x, icon_y))

        return pygame.Rect(x, y, settings.resource_button_width, settings.resource_button_height) if is_active else None

    def draw_specialization_button(self, screen, x, y, icon, is_active):
        """Draws a specialization button (only icon) and returns its rect"""
        pygame.draw.rect(screen, settings.colors['black'],
                         (x, y, settings.resource_button_width, settings.resource_button_height))
        pygame.draw.rect(screen, settings.colors['white'],
                         (x, y, settings.resource_button_сwidth, settings.resource_button_height), 1)
        screen.blit(icon, (x + settings.resource_button_width // 2 - icon.get_width() // 2, y))
        return pygame.Rect(x, y, settings.resource_button_width, settings.resource_button_height) if is_active else None

    def draw_transport_menu(self, screen):
        # Draw menu background
        menu_x = settings.width // 2 - settings.menu_width // 2
        menu_y = settings.height // 2 - settings.menu_height // 2
        pygame.draw.rect(screen, settings.colors['black'], (menu_x, menu_y, settings.menu_width, settings.menu_height))
        pygame.draw.rect(screen, settings.colors['white'],
                         (menu_x - settings.menu_outline, menu_y - settings.menu_outline,
                         settings.menu_width + settings.menu_outline * 2,
                         settings.menu_height + settings.menu_outline * 2), settings.menu_outline)

        # Draw planet image area
        planet_area_x = menu_x + settings.menu_padding
        planet_area_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['white'], (planet_area_x, planet_area_y,
                                                            settings.planet_image_size, settings.planet_image_size), 2)

        # Draw planet image
        transport_image = pygame.transform.scale(hex_images['transport_spaceship'],
                                                 (settings.planet_image_size - 2 * settings.menu_padding,
                                                  settings.planet_image_size - 2 * settings.menu_padding))
        screen.blit(transport_image, (planet_area_x + settings.menu_padding, planet_area_y + settings.menu_padding))

        stats_x = planet_area_x + settings.planet_image_size + settings.menu_padding
        stats_y = planet_area_y

        # Population
        pop_icon = pygame.transform.scale(hex_images['population'], (settings.menu_icon_size, settings.menu_icon_size))
        screen.blit(pop_icon, (stats_x, stats_y))
        pop_text = self.font.render(f": {self.selected_transport.get('population')}", True, settings.colors['white'])
        screen.blit(pop_text, (stats_x + settings.menu_icon_size, stats_y + (settings.menu_icon_size // 4)))
        stats_y += settings.menu_icon_size + settings.menu_padding

        # Draw separation lines
        separator_y = planet_area_y + settings.planet_image_size + settings.menu_padding
        pygame.draw.line(screen, settings.colors['white'], (planet_area_x, separator_y),
                         (menu_x + settings.menu_width - settings.menu_padding, separator_y), settings.menu_line_width)

        # Draw exit button
        button_x = menu_x + settings.menu_width - settings.exit_button_size - settings.menu_padding
        button_y = menu_y + settings.menu_padding
        pygame.draw.rect(screen, settings.colors['red'], (button_x, button_y,
                                                          settings.exit_button_size, settings.exit_button_size))
        pygame.draw.rect(screen, settings.colors['white'],
                         (button_x - settings.exit_btn_outline, button_y - settings.exit_btn_outline,
                         settings.exit_button_size + settings.exit_btn_outline * 2,
                         settings.exit_button_size + settings.exit_btn_outline * 2),
                         settings.exit_btn_outline)
        exit_text = self.font.render('X', True, settings.colors['white'])
        screen.blit(exit_text, (button_x + 9, button_y + 7))
        self.exit_button_rect = pygame.Rect(button_x, button_y, settings.exit_button_size, settings.exit_button_size)

    def add_resource_to_spaceship(self, resource_type, amount):
        """Adds resources to the nearest spaceship."""
        for other_hex in self.hex_map:
            if other_hex["value"] == 3:
                if resource_type in other_hex:
                    other_hex[resource_type] += amount
