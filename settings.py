# --- Экран ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# --- Тайлы ---
TILE_SIZE = 64
MAP_WIDTH = 40
MAP_HEIGHT = 25

# --- Цвета ---
COLOR_BG = (20, 20, 25)
COLOR_TEXT = (240, 240, 240)

# Типы местности
TILE_GRASS = 0
TILE_WATER = 1
TILE_ROCK = 2
TILE_SAND = 3

TILE_COLORS = {
    TILE_GRASS: (60, 130, 60),
    TILE_WATER: (40, 80, 160),
    TILE_ROCK:  (110, 110, 110),
    TILE_SAND:  (200, 180, 120),
}

WALKABLE_TILES = {
    TILE_GRASS: True,
    TILE_SAND:  True,
    TILE_WATER: False,
    TILE_ROCK:  False,
}

SHOW_GRID = True

# --- Камера ---
CAMERA_SPEED_KEYS = 700
CAMERA_SPEED_EDGE = 900
CAMERA_EDGE_MARGIN = 80

# --- Юниты (все параметры тут) ---
UNIT_RADIUS = 18           # радиус круга
UNIT_SPEED = 180.0         # пикселей в секунду
UNIT_COLOR_PLAYER = (80, 160, 255)
UNIT_COLOR_ENEMY = (220, 70, 70)
UNIT_RADIUS_SELECT = 5     # на сколько радиус выделения больше юнита

# --- Игровые константы ---
# Радиус поиска свободной клетки для формации (в клетках, 3 = 3x3)
FORMATION_SEARCH_RADIUS = 3

# Разброс формации: минимальное расстояние между юнитами в формации (в клетках)
FORMATION_SPACING = 1

# Тайминг перестроения маршрута при блокировке (в секундах)
REPATH_INTERVAL = 0.5
REPATH_MAX_ATTEMPTS = 10