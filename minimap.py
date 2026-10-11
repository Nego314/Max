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
        Каждый пиксель миникарты = усреднённый цвет региона.
        """
        surface = pygame.Surface((self.size, self.size))

        for my in range(self.size):
            for mx in range(self.size):
                # Диапазон клеток карты, которые попадают в этот пиксель
                tx_start = int(mx * self.scale_x)
                tx_end = int((mx + 1) * self.scale_x)
                ty_start = int(my * self.scale_y)
                ty_end = int((my + 1) * self.scale_y)

                # Защита от выхода за границы
                tx_end = max(tx_end, tx_start + 1)
                ty_end = max(ty_end, ty_start + 1)

                r_total = g_total = b_total = 0
                count = 0

                for ty in range(ty_start, ty_end):
                    row = self.tilemap.tiles[ty]
                    for tx in range(tx_start, tx_end):
                        if 0 <= tx < self.tilemap.width:
                            color = TILE_COLORS[row[tx]]
                            r_total += color[0]
                            g_total += color[1]
                            b_total += color[2]
                            count += 1

                if count > 0:
                    avg = (r_total // count, g_total // count, b_total // count)
                else:
                    avg = (0, 0, 0)

                surface.set_at((mx, my), avg)

        return surface

    # --- Отрисовка ---

    def draw(self, screen, world, camera):
        """Рисует миникарту: статичную карту, юнитов, рамку камеры."""
        # Копируем статичную картинку
        screen.blit(self.static_surface, (self.screen_x, self.screen_y))

        # Юниты точками
        for u in world.units:
            mx = self.screen_x + int(u.tile_x / self.scale_x)
            my = self.screen_y + int(u.tile_y / self.scale_y)

            if u.team == "player":
                color = MINIMAP_ALLY_COLOR
            else:
                color = MINIMAP_ENEMY_COLOR

            # 2×2, чтобы точки было видно
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