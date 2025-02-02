import os
import sys
import pygame

pygame.init()
pygame.display.set_caption("Перемещение героя")
size = WIDTH, HEIGHT = 550, 550
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
FPS = 60
clock = pygame.time.Clock()

player = None


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


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.world_x = tile_width * pos_x
        self.world_y = tile_height * pos_y
        self.rect.topleft = (self.world_x, self.world_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.world_x = tile_width * pos_x + 15
        self.world_y = tile_height * pos_y + 5
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.world_x, self.world_y)

    def move(self, pos_x, pos_y):
        self.world_x = tile_width * pos_x + 15
        self.world_y = tile_height * pos_y + 5
        self.rect.topleft = (self.world_x, self.world_y)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.topleft = (obj.world_x + self.dx, obj.world_y + self.dy)

    def update(self, target):
        self.dx = -(target.world_x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.world_y + target.rect.h // 2 - HEIGHT // 2)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    lst = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    return [list(x) for x in lst]


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def move(player, movement, level):
    x, y = player.world_x // tile_width, player.world_y // tile_height
    if movement == "up" and y > 0 and level[y - 1][x] == ".":
        level[y][x] = '.'
        player.move(x, y - 1)
        level[y - 1][x] = '@'
    elif movement == "down" and y < len(level) - 1 and level[y + 1][x] == ".":
        level[y][x] = '.'
        player.move(x, y + 1)
        level[y + 1][x] = '@'
    elif movement == "left" and x > 0 and level[y][x - 1] == ".":
        level[y][x] = '.'
        player.move(x - 1, y)
        level[y][x - 1] = '@'
    elif movement == "right" and x < len(level[0]) - 1 and level[y][x + 1] == ".":
        level[y][x] = '.'
        player.move(x + 1, y)
        level[y][x + 1] = '@'


def level_1():
    level = load_level("map.map")
    player, level_x, level_y = generate_level(level)
    camera = Camera()

    while True:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    move(player, "up", level)
                elif event.key == pygame.K_DOWN:
                    move(player, "down", level)
                elif event.key == pygame.K_LEFT:
                    move(player, "left", level)
                elif event.key == pygame.K_RIGHT:
                    move(player, "right", level)

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        tiles_group.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    start_screen()
    level_1()


if __name__ == "__main__":
    sys.exit(main())
