import pygame  # Основная библиотека для графики
from pygame.locals import *  # Импорт констант для событий и клавиш

# Определение цветов в формате RGB
BLACK = (0, 0, 0)  # Чёрный цвет для фона и линий
ORANGE = (255, 120, 0)  # Оранжевый цвет для выделенных шестиугольников
YELLOW = (255, 255, 0)  # Жёлтый цвет для обычных шестиугольников
CYAN = (0, 255, 255)  # Голубой цвет для текста


class Hexagon:
    """
    Класс для расчётов, связанных с геометрией шестиугольников.
    """
    # Вершины шестиугольника относительно его верхнего левого угла
    VERTEXES = ((1, 0), (3, 0), (4, 1), (3, 2), (1, 2), (0, 1))

    def __init__(self, size):
        # Размеры шестиугольника
        self.SIZE = size
        self.HALF = size // 2  # Половина высоты
        self.QUARTER = size // 4  # Четверть высоты
        self.WIDTH = size * 3 // 4  # Ширина (с учётом перекрытий)
        self.HEIGHT = size  # Полная высота

    def index_at(self, pixel_x, pixel_y):
        """Вычисляет координаты (x, y) шестиугольника по пиксельным координатам."""
        x = pixel_x // self.WIDTH  # Индекс столбца
        x0 = pixel_x % self.WIDTH  # Смещение внутри столбца
        if x0 < self.QUARTER:  # Если пиксель находится в перекрывающейся зоне
            y0 = (pixel_y - (x % 2) * self.HALF) % self.HEIGHT
            if y0 >= self.HALF:  # Нижняя половина шестиугольника
                y0 = self.SIZE - y0
            is_leftarea = x0 < self.QUARTER - y0 * self.QUARTER // self.HALF
            if is_leftarea:
                x -= 1
        y = (pixel_y - (x % 2) * self.HALF) // self.HEIGHT  # Индекс строки
        return x, y

    def origin_of(self, x, y):
        """Возвращает пиксельные координаты верхнего левого угла шестиугольника."""
        return x * self.WIDTH, y * self.HEIGHT + (x % 2) * self.HALF

    def vertexes_of(self, x, y):
        """Возвращает координаты вершин шестиугольника с индексами (x, y)."""
        origin_x, origin_y = self.origin_of(x, y)
        return [(origin_x + vx * self.QUARTER, origin_y + vy * self.HALF) for vx, vy in self.VERTEXES]


class HexMap:
    """
    Класс для управления картой из шестиугольников.
    """

    def __init__(self, columns, rows, hexagon_size):
        self.COLUMNS = columns  # Количество столбцов
        self.ROWS = rows  # Количество строк
        self.hexagon = Hexagon(hexagon_size)  # Экземпляр шестиугольника
        width, height = self.hexagon.origin_of(self.COLUMNS, self.ROWS)
        width += self.hexagon.QUARTER  # Учитываем ширину для последнего шестиугольника
        self.size = width + 1, height + 1  # Размер карты в пикселях
        self.clear_clicked()  # Инициализация состояния шестиугольников

    def clear_clicked(self):
        """Сбрасывает состояния всех шестиугольников (не кликнуты)."""
        self.clicked = [[False] * self.ROWS for _ in range(self.COLUMNS)]

    def click_at(self, pixel_x, pixel_y):
        """Переключает состояние шестиугольника, на который кликнули."""
        x, y = self.hexagon.index_at(pixel_x, pixel_y)
        if 0 <= x < self.COLUMNS and 0 <= y < self.ROWS:
            self.clicked[x][y] = not self.clicked[x][y]

    def is_clicked_on(self, x, y):
        """Проверяет, был ли шестиугольник с координатами (x, y) кликнут."""
        return 0 <= x < self.COLUMNS and 0 <= y < self.ROWS and self.clicked[x][y]

    def hexagons(self):
        """Генерирует все шестиугольники на карте."""
        for x in range(self.COLUMNS):
            for y in range(self.ROWS - (x % 2)):
                yield self.hexagon, x, y


class HexCanvas:
    """
    Класс для визуализации карты шестиугольников.
    """
    LINE_WIDTH = 1  # Толщина линий
    CURSOR_SIZE = 5  # Размер курсора

    def __init__(self, hexmap):
        self.hexmap = hexmap  # Экземпляр карты
        self.canvas = pygame.display.set_mode(hexmap.size)  # Поверхность для рисования
        self.font = pygame.font.SysFont(None, 17)  # Шрифт для текста
        self.cursor = None  # Координаты курсора

    def cursor_at(self, pixel_x, pixel_y):
        """Обновляет положение курсора."""
        self.cursor = pixel_x, pixel_y

    def draw(self):
        """Рисует карту и элементы интерфейса."""
        self.canvas.fill(BLACK)  # Очистка экрана
        for hexagon, x, y in self.hexmap.hexagons_points():
            vertexes = hexagon.vertexes_of(x, y)
            color = ORANGE if self.hexmap.is_clicked_on(x, y) else YELLOW
            pygame.draw.polygon(self.canvas, color, vertexes)  # Рисуем шестиугольник
            for v1, v2 in zip(vertexes, vertexes[1:] + vertexes[:1]):
                pygame.draw.line(self.canvas, BLACK, v1, v2, self.LINE_WIDTH)  # Границы
            tag = f"{x}, {y}"  # Текст с координатами
            text = self.font.render(tag, True, CYAN)
            origin_x, origin_y = hexagon.origin_of(x, y)
            text_area = text.get_rect(center=(origin_x + hexagon.HALF, origin_y + hexagon.HALF))
            self.canvas.blit(text, text_area)  # Выводим текст
        if self.cursor:
            pygame.draw.circle(self.canvas, BLACK, self.cursor, self.CURSOR_SIZE, 0)  # Курсор


# Главная функция

def main():
    pygame.init()  # Инициализация Pygame
    FPSCLOCK = pygame.time.Clock()  # Таймер для управления FPS

    hexmap = HexMap(15, 15, 50)  # Создаём карту
    canvas = HexCanvas(hexmap)  # Создаём холст для карты

    while True:  # Основной цикл программы
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                pygame.quit()
                return
            if event.type == MOUSEMOTION:  # Движение мыши
                x, y = pygame.mouse.get_pos()
                canvas.cursor_at(x, y)
            elif event.type == MOUSEBUTTONDOWN:  # Клик мыши
                x, y = pygame.mouse.get_pos()
                hexmap.click_at(x, y)

        canvas.draw()  # Отрисовка
        pygame.display.update()  # Обновление экрана
        FPSCLOCK.tick(30)  # Ограничение FPS


if __name__ == '__main__':
    main()
