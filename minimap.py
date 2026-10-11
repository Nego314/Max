"""
Миникарта: статичная картинка карты + динамические элементы
(юниты, рамка камеры) + обработка клика.
"""
import pygame
from settings import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT,
    TILE_COLORS,
    MINIMAP_SIZE, MINIMAP_CAMERA_COLOR,
    MINIMAP_ALLY_COLOR, MINIMAP_ENEMY_COLOR,
)


class Minimap:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.size = MINIMAP_SIZE

        # Масштаб: сколько клеток на 1 пиксель миникарты
        self.scale_x = tilemap.width / self.size
        self.scale_y = tilemap.height / self.size

        # Статичная картинка карты (один раз при старте)
        self.static_surface = self._build_static_surface()

        # Экранная позиция миникарты (по умолчанию — верх правой панели)
        self.screen_x = 0
        self.screen_y = 0
        self.screen_rect = pygame.Rect(0, 0, self.size, self.size)

    # --- Позиционирование ---

    def set_position(self, x, y):
        """Устанавливает экранную позицию миникарты."""
        self.screen_x = x
        self.screen_y = y
        self.screen_rect = pygame.Rect(x, y, self.size, self.size)

    # --- Статичная поверхность ---

    def _build_static_surface(self):
        """
        Создаёт уменьшенную картинку карты.
        Использует numpy для подготовки массива + pygame.smoothscale для сжатия.
        Время генерации: ~0.2-0.5 сек вместо 5-10 сек.
        """
        import numpy as np
        from settings import TILE_COLORS

        # 1. Карта → numpy (H, W)
        tiles_np = np.array(self.tilemap.tiles, dtype=np.int8)

        # 2. Таблица цветов
        max_tile = max(TILE_COLORS.keys()) + 1
        color_lut = np.zeros((max_tile, 3), dtype=np.uint8)
        for tile_type, color in TILE_COLORS.items():
            color_lut[tile_type] = color

        # 3. RGB (H, W, 3)
        rgb = color_lut[tiles_np]

        # 4. pygame.Surface из numpy
        #    pygame.surfarray ожидает (W, H, 3) → транспонируем
        rgb_wh = np.transpose(rgb, (1, 0, 2))
        big_surface = pygame.Surface((self.tilemap.width, self.tilemap.height))
        pygame.surfarray.blit_array(big_surface, rgb_wh)

        # 5. Уменьшение через smoothscale
        small = pygame.transform.smoothscale(big_surface, (self.size, self.size))
        return small

    # --- Отрисовка ---

    def draw(self, screen, world, camera, fog):
        """Рисует миникарту: статичную карту, юнитов, рамку камеры."""
        # Копируем статичную картинку
        screen.blit(self.static_surface, (self.screen_x, self.screen_y))

        # Юниты точками
        for u in world.units:
            # Врагов — только если видимы
            if u.team != "player" and not fog.is_visible(u.tile_x, u.tile_y):
                continue

            mx = self.screen_x + int(u.tile_x / self.scale_x)
            my = self.screen_y + int(u.tile_y / self.scale_y)

            if u.team == "player":
                color = MINIMAP_ALLY_COLOR
            else:
                color = MINIMAP_ENEMY_COLOR

            pygame.draw.rect(screen, color, (mx, my, 2, 2))

        # Рамка камеры
        cam_x1 = self.screen_x + int(camera.x / self.scale_x / TILE_SIZE)
        cam_y1 = self.screen_y + int(camera.y / self.scale_y / TILE_SIZE)
        cam_w = int(camera.viewport_w / self.scale_x / TILE_SIZE)
        cam_h = int(camera.viewport_h / self.scale_y / TILE_SIZE)

        pygame.draw.rect(
            screen, MINIMAP_CAMERA_COLOR,
            (cam_x1, cam_y1, cam_w, cam_h), 1
        )

        # Рамка миникарты
        pygame.draw.rect(screen, (80, 80, 100), self.screen_rect, 1)

    # --- Обработка клика ---

    def screen_to_world(self, mouse_x, mouse_y):
        """
        Преобразует экранные координаты клика по миникарте
        в мировые координаты (для центрирования камеры).
        """
        # Локальные координаты внутри миникарты
        local_x = mouse_x - self.screen_x
        local_y = mouse_y - self.screen_y

        # В клетки карты
        tile_x = local_x * self.scale_x
        tile_y = local_y * self.scale_y

        # В мировые пиксели
        world_x = tile_x * TILE_SIZE
        world_y = tile_y * TILE_SIZE

        return world_x, world_y

    def contains_point(self, mouse_pos):
        return self.screen_rect.collidepoint(mouse_pos)

    def _update_fog_surface(self, fog):
        """Пересчитывает туман миникарты через numpy."""
        import numpy as np

        # explored (height, width) → bool
        # уменьшить до (size, size)
        # используем reshape + any()

        block_x = self.tilemap.width // self.size  # ~17
        block_y = self.tilemap.height // self.size

        usable_w = block_x * self.size
        usable_h = block_y * self.size

        # Режем explored до кратного
        explored = fog.explored[:usable_h, :usable_w]

        # Решейп: (size, block_y, size, block_x)
        reshaped = explored.reshape(self.size, block_y, self.size, block_x)

        # «Хоть одна explored-клетка в блоке?»
        any_explored = reshaped.any(axis=(1, 3))  # (size, size)

        # Создаём маску
        mask = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        mask[~any_explored] = (0, 0, 0)  # не исследовано → чёрный
        # explored → прозрачный (не рисуем)

        # На Surface
        ...