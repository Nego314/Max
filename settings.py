# =============================================================
#                      НАСТРОЙКИ ИГРЫ
# =============================================================
# Всё, что зависит от размера тайла, задаётся через TILE_SIZE.
# Меняешь TILE_SIZE — всё остальное пересчитывается автоматически.
# =============================================================

# --- Базовая единица ---
TILE_SIZE = 32

# --- Экран ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Режим окна:
#   "window"     — обычное окно с рамкой
#   "fullscreen" — безрамочный фуллскрин с масштабированием
SCREEN_MODE = "fullscreen"

# --- Карта ---
MAP_WIDTH = 5000
MAP_HEIGHT = 5000

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
CAMERA_SPEED_KEYS_FACTOR = 11.0     # × TILE_SIZE, пикс/сек (клавиатура)
CAMERA_SPEED_EDGE_FACTOR = 14.0     # × TILE_SIZE, пикс/сек (у края экрана)
CAMERA_SPEED_KEYS = CAMERA_SPEED_KEYS_FACTOR * TILE_SIZE
CAMERA_SPEED_EDGE = CAMERA_SPEED_EDGE_FACTOR * TILE_SIZE
CAMERA_EDGE_MARGIN = 80             # пикселей, не зависит от TILE_SIZE

# --- Юниты (в долях от TILE_SIZE) ---
UNIT_RADIUS_FACTOR = 0.28       # радиус юнита / TILE_SIZE
UNIT_SPEED_FACTOR = 2.8         # скорость юнита × TILE_SIZE (пикс/сек)
UNIT_SELECT_FACTOR = 0.078      # доп. радиус кольца выделения / TILE_SIZE

UNIT_RADIUS = max(2, int(UNIT_RADIUS_FACTOR * TILE_SIZE))
UNIT_SPEED = UNIT_SPEED_FACTOR * TILE_SIZE
UNIT_RADIUS_SELECT = max(1, int(UNIT_SELECT_FACTOR * TILE_SIZE))

# Цвета команд
UNIT_COLOR_PLAYER = (80, 160, 255)
UNIT_COLOR_ENEMY = (220, 70, 70)

# --- Формации ---
FORMATION_SEARCH_RADIUS = 3     # радиус поиска свободной клетки (в клетках)
FORMATION_SPACING = 1           # шаг формации (в клетках)

# --- Перестроение маршрута ---
REPATH_INTERVAL = 0.5           # секунд между попытками
REPATH_MAX_ATTEMPTS = 10        # после скольких попыток сдаться

# --- UI ---
SELECT_RECT_THICKNESS = max(1, TILE_SIZE // 16)   # толщина рамки выделения
DEBUG_FONT_SIZE = 16                               # шрифт debug-строки