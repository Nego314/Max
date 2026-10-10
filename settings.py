# =============================================================
#                      НАСТРОЙКИ ИГРЫ
# =============================================================
# Всё, что зависит от размера тайла, задаётся через TILE_SIZE.
# Меняешь TILE_SIZE — всё остальное пересчитывается автоматически.
# =============================================================

# --- Базовая единица ---
TILE_SIZE = 32

# --- Экран ---
SCREEN_WIDTH = 3840/2
SCREEN_HEIGHT = 2160/2
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

SHOW_GRID = False

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
UI_PANEL_WIDTH = 300                            # ширина каждой панели (левой и правой)
UI_PANEL_COLOR = (25, 25, 35)                   # фон панелей
UI_BORDER_COLOR = (60, 60, 80)                  # рамки блоков
UI_TEXT_COLOR = (230, 230, 230)                 # обычный текст
UI_HEADER_COLOR = (255, 255, 255)               # заголовки
UI_FONT_SIZE = 16                               # шрифт UI

SELECT_RECT_THICKNESS = max(1, TILE_SIZE // 16) # толщина рамки выделения
SELECT_CIRCLE_THICKNESS = 1                     # толщина кольца выделения юнита
DEBUG_FONT_SIZE = 16                            # шрифт debug-строки

# --- Ресурсы (значения захардкожены, потом подключим экономику) ---
RESOURCES = [
    {"name": "Еда",       "value": 50,  "unit": "",     "icon_color": (200, 180, 100)},
    {"name": "Вода",      "value": 30,  "unit": "л",    "icon_color": (100, 180, 220)},
    {"name": "Энергия",   "value": 100, "unit": "кВт",  "icon_color": (255, 220, 100)},
    {"name": "Ёмкость аккумуляторов", "value": 0, "unit": "кВт·ч", "icon_color": (150, 200, 150)},

    {"name": "Железная руда", "value": 200, "unit": "кг", "icon_color": (150, 100, 80)},
    {"name": "Медная руда",   "value": 0,   "unit": "кг", "icon_color": (200, 120, 60)},

    {"name": "Сталь",    "value": 0, "unit": "кг", "icon_color": (160, 160, 180)},
    {"name": "Алюминий", "value": 0, "unit": "кг", "icon_color": (200, 200, 200)},
]

# --- Свойства юнита (показ в левой панели) ---
UNIT_STATS = [
    {"key": "hp",        "name": "Жизнь",             "value": 100, "unit": ""},
    {"key": "armor",     "name": "Броня",             "value": 5,   "unit": ""},
    {"key": "attack",    "name": "Атака",             "value": 10,  "unit": ""},
    {"key": "vision",    "name": "Дальность обзора",  "value": 8,   "unit": "кл."},
    {"key": "atk_range", "name": "Дальность атаки",   "value": 5,   "unit": "кл."},
    {"key": "shots",     "name": "Кол-во выстрелов",  "value": 1,   "unit": ""},
    {"key": "speed",     "name": "Скорость хода",     "value": 3,   "unit": "кл./с"},
]