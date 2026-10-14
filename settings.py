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

TILE_REGOLITH = 0      # Реголит — базовый ландшафт
TILE_DUST = 1          # Пыль — «лунные моря»
TILE_ROCK = 2          # Скалы — непроходимо
TILE_CRATER = 3        # Дно кратера — впадина
TILE_ICE = 4           # Лёд — ресурс (вода)
TILE_ILMENITE = 5      # Ильменит — ресурс (титан, железо)
TILE_ANORTHOSITE = 6   # Анортозит — ресурс (алюминий)
# Гелий-3 — НЕ тип карты, а продукт переработки

# --- Названия типов местности (для UI) ---
TILE_NAMES = {
    TILE_REGOLITH:    "Реголит",
    TILE_DUST:        "Пыль",
    TILE_ROCK:        "Скалы",
    TILE_CRATER:      "Кратер",
    TILE_ICE:         "Лёд",
    TILE_ILMENITE:    "Ильменит",
    TILE_ANORTHOSITE: "Анортозит",
}

TILE_COLORS = {
    TILE_REGOLITH:  (140, 130, 120),   # серо-коричневый
    TILE_DUST:      (110, 100, 95),    # темнее, пыльнее
    TILE_ROCK:      (70, 65, 60),      # тёмно-серый
    TILE_CRATER:    (30, 25, 35),
    TILE_ICE:       (170, 210, 230),   # светло-голубой
    TILE_ILMENITE:  (120, 60, 40),      # тёмно-коричневый
    TILE_ANORTHOSITE: (220, 210, 200), # светло-серый
}

WALKABLE_TILES = {
    TILE_REGOLITH:   True,
    TILE_DUST:       True,
    TILE_ROCK:       False,   # скалы — непроходимо
    TILE_CRATER:     True,
    TILE_ICE:        True,
    TILE_ILMENITE:   True,
    TILE_ANORTHOSITE: True,
}

SHOW_GRID = False

# --- Генерация карты ---
MAP_SEED = 12345                          # seed для воспроизводимости
MAP_SAVE_PATH = "map_cache"               # папка для сохранённых карт

# Параметры шума (для генерации ландшафта)
NOISE_SCALE_BASE = 0.0005                 # крупный шум — базовые зоны
NOISE_SCALE_DETAIL = 0.0015                # мелкий шум — детали
NOISE_SCALE_ROCK = 0.0008                 # шум для скал
NOISE_SCALE_DUST = 0.0008                 # шум для пылевых морей

# Пороги
THRESHOLD_DUST = 0.55                     # выше — пылевое море
THRESHOLD_ROCK = 0.68                     # выше — скалы
THRESHOLD_RESOURCE = 0.75                 # выше — ресурсная жила (редко)

# Плотность ресурсов (вероятность в подходящем регионе)
DENSITY_ICE = 0.15                         # лёд в кратерах
DENSITY_ILMENITE = 0.03                    # ильменит в реголите
DENSITY_ANORTHOSITE = 0.03                 # анортозит в реголите

# Кратеры
CRATER_COUNT = 500                        # сколько кратеров генерировать
CRATER_MIN_RADIUS = 20                    # минимальный радиус (клеток)
CRATER_MAX_RADIUS = 80                    # максимальный радиус

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

# --- UI: панель свойств ---
UI_STATS_ROW_HEIGHT = 24         # высота строки свойства
UI_PORTRAIT_HEIGHT = 240         # высота блока портрета (внизу левой панели)

# --- Ресурсы (значения захардкожены, потом подключим экономику) ---
RESOURCES = [
    # --- Жизнеобеспечение ---
    {"name": "Вода",       "value": 30,  "unit": "л",    "icon_color": (100, 180, 220)},
    {"name": "Кислород",   "value": 50,  "unit": "л",    "icon_color": (180, 220, 255)},
    {"name": "Еда",        "value": 50,  "unit": "кг",   "icon_color": (200, 180, 100)},

    # --- Энергия ---
    {"name": "Энергия",    "value": 100, "unit": "кВт",  "icon_color": (255, 220, 100)},
    {"name": "Ёмкость аккумуляторов", "value": 0, "unit": "кВт·ч", "icon_color": (150, 200, 150)},
    {"name": "Гелий-3", "value": 0, "unit": "кг", "icon_color": (255, 100, 200)},

    # --- Минералы (сырьё для металлов) ---
    {"name": "Ледяной реголит",  "value": 200, "unit": "кг", "icon_color": (200, 230, 255)},
    {"name": "Ильменит",         "value": 0,   "unit": "кг", "icon_color": (120, 100, 90)},
    {"name": "Анортозит",        "value": 0,   "unit": "кг", "icon_color": (170, 160, 140)},

    # --- Металлы ---
    {"name": "Железо",     "value": 0, "unit": "кг", "icon_color": (160, 160, 180)},
    {"name": "Алюминий",   "value": 0, "unit": "кг", "icon_color": (200, 200, 200)},
    {"name": "Титан",      "value": 0, "unit": "кг", "icon_color": (180, 200, 220)},
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

# --- Численность колонии ---
# Каждая специальность: буква (1 символ), имя, количество
COLONY_POPULATION = [
    {"letter": "Г", "name": "Геолог",   "count": 1},
    {"letter": "И", "name": "Инженер",  "count": 0},
    {"letter": "Ш", "name": "Шахтёр",   "count": 0},
]

# --- Типы юнитов ---
# Для каждого типа: буква (для портрета), имя, стартовые характеристики
UNIT_TYPES = {
     "geologist": {
        "letter": "Г",
        "name": "Сканер-геолог",
        "color": (180, 220, 180),
        "hp": 80,
        "armor": 2,
        "attack": 3,
        "vision": 6,
        "atk_range": 2,
        "shots": 1,
        "speed": 2.5,
    },
    "engineer": {
        "letter": "И",
        "name": "Инженер",
        "color": (180, 180, 220),
        "hp": 100,
        "armor": 5,
        "attack": 5,
        "vision": 5,
        "atk_range": 3,
        "shots": 1,
        "speed": 3.0,
    },
    "signal": {
        "letter": "С",
        "name": "Мобильный радар",
        "color": (220, 220, 180),
        "hp": 60,
        "armor": 1,
        "attack": 1,
        "vision": 15,  # глубокий обзор — радар
        "atk_range": 1,
        "shots": 0,
        "speed": 2.0,
    },
}

# --- UI: миникарта ---
MINIMAP_SIZE = 280           # размер миникарты (квадрат), пикс
MINIMAP_MARGIN = 10          # отступ от краёв панели, пикс
MINIMAP_CAMERA_COLOR = (255, 230, 80)   # цвет рамки камеры
MINIMAP_ALLY_COLOR = (80, 160, 255)     # цвет своих юнитов
MINIMAP_ENEMY_COLOR = (220, 70, 70)     # цвет врагов

# --- Миникарта: режимы ---
MINIMAP_MODE_PLAIN = 0        # без ресурсов
MINIMAP_MODE_RESOURCES = 1    # с ресурсами

# Кнопка переключения
MINIMAP_BUTTON_HEIGHT = 28
MINIMAP_BUTTON_COLOR = (50, 50, 70)
MINIMAP_BUTTON_COLOR_HOVER = (70, 70, 100)
MINIMAP_BUTTON_TEXT_COLOR = (230, 230, 230)

# --- Туман войны ---
FOG_EXPLORED_COLOR = (0, 0, 0, 140)   # RGBA — полупрозрачный чёрный для "исследовано, но не видно"
FOG_UNEXPLORED_COLOR = (0, 0, 0, 255) # RGBA — плотный чёрный для "не исследовано"

# --- Спавн баз ---
BASE_PLATFORM_SIZE = 12               # размер площадки под базу (клеток)
BASE_MIN_DISTANCE = 700              # минимум между базами (клеток)
BASE_RESOURCE_RADIUS = 40            # радиус поиска ресурсов вокруг базы
BASE_SEARCH_ATTEMPTS = 5000          # сколько попыток искать площадку

# --- Стартовые юниты ---
START_UNITS_PER_BASE = 3             # юнитов на старте
START_UNIT_TYPES = ["engineer", "geologist", "signal"]   # типы юнитов

# --- Типы зданий ---
# Каждое здание: буква, имя, размер (в клетках), цвет, характеристики
BUILDING_TYPES = {
    "habitat": {
        "letter": "Ж",
        "name": "Жилой модуль",
        "size": 2,
        "color": (180, 180, 220),
        "hp": 500,
        "max_hp": 500,
    },
    "lab": {
        "letter": "Л",
        "name": "Лаборатория",
        "size": 2,
        "color": (160, 200, 200),
        "hp": 300,
        "max_hp": 300,
    },
    "generator": {
        "letter": "Г",
        "name": "Генератор H₂O₂",
        "size": 2,
        "color": (220, 180, 120),
        "hp": 250,
        "max_hp": 250,
    },
    "battery": {
        "letter": "А",
        "name": "Аккумуляторная станция",
        "size": 2,
        "color": (200, 200, 140),
        "hp": 250,
        "max_hp": 250,
    },
    "solar": {
        "letter": "Б",
        "name": "Солнечная батарея",
        "size": 2,
        "color": (140, 180, 220),
        "hp": 150,
        "max_hp": 150,
    },
    "ice_storage": {
        "letter": "С",
        "name": "Склад льда",
        "size": 1,
        "color": (170, 210, 230),
        "hp": 100,
        "max_hp": 100,
    },
    "workshop": {
        "letter": "М",
        "name": "Мастерская",
        "size": 2,
        "color": (200, 160, 140),
        "hp": 300,
        "max_hp": 300,
    },
}

# --- Схема расстановки зданий (смещения от центра базы) ---
# (тип здания, смещение по X, смещение по Y)
# Смещение считается до ЛЕВОГО ВЕРХНЕГО угла здания.
BASE_LAYOUT = [
    ("habitat",    -1, -1),   # жилой модуль — в центре
    ("lab",         3, -5),   # лаборатория — справа вверху
    ("generator",  -5,  0),   # генератор — слева
    ("battery",     3,  0),   # аккумуляторы — справа
    ("solar",      -5,  4),   # солнечная батарея #1 — слева внизу
    ("ice_storage",-1,  4),   # склад льда (1×1) — по центру внизу
    ("workshop",    2,  4),   # мастерская — справа внизу
    ("solar",       3,  8),   # солнечная батарея #2 — справа внизу
]