#SCREEN_WIDTH = 1280
SCREEN_WIDTH = 1920
#SCREEN_HEIGHT = 720
SCREEN_HEIGHT = 1080
FPS = 60

# --- Тайлы ---
TILE_SIZE = 64

# Размеры карты в тайлах
MAP_WIDTH = 40
MAP_HEIGHT = 25

# --- Цвета ---
COLOR_BG = (20, 20, 25)
COLOR_TEXT = (240, 240, 240)

# Типы местности (пока цвета, позже заменим на спрайты)
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

# --- Отладка ---
SHOW_GRID = True   # рисовать линии сетки
#SHOW_GRID = False

# --- Камера ---
CAMERA_SPEED_KEYS = 700        # пикселей в секунду (стрелки/WASD)
CAMERA_SPEED_EDGE = 900        # пикселей в секунду (у края экрана)
#CAMERA_EDGE_MARGIN = 40        # ширина "горячей зоны" у края, пикселей
CAMERA_EDGE_MARGIN = 80
CAMERA_ZOOM_STEP = 0.1         # шаг зума колёсиком (пока не используем)
CAMERA_ZOOM_MIN = 0.5
CAMERA_ZOOM_MAX = 2.0

# --- Проходимость тайлов ---
WALKABLE_TILES = {
    TILE_GRASS: True,
    TILE_SAND:  True,
    TILE_WATER: False,   # вода непроходима
    TILE_ROCK:  False,   # скалы непроходимы
}