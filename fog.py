"""
Туман войны: explored + visible массивы.
"""
import numpy as np
import pygame

from settings import (
    FOG_EXPLORED_COLOR, FOG_UNEXPLORED_COLOR,
    TILE_SIZE,
)

class Fog:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # explored: клетки, которые мы когда-либо видели (навсегда)
        # visible: клетки, видимые прямо сейчас
        self.explored = np.zeros((height, width), dtype=bool)
        self.visible = np.zeros((height, width), dtype=bool)

        # Кэш для маски (чтобы не создавать Surface каждый кадр)
        self._mask_surface = None

    # --- Обновление видимости ---

    def update(self, world, player_team="player"):
        """
        Обходит всех юнитов игрока, добавляет их зону обзора
        в visible и explored.
        """
        # Обнуляем visible каждый кадр
        self.visible.fill(False)

        for u in world.units:
            if u.team != player_team:
                continue
            self._reveal(u.tile_x, u.tile_y, u.vision)

        # explored накапливается
        self.explored |= self.visible

    def _reveal(self, cx, cy, radius):
        """Помечает клетки в радиусе как видимые."""
        x1 = max(0, cx - radius)
        x2 = min(self.width, cx + radius + 1)
        y1 = max(0, cy - radius)
        y2 = min(self.height, cy + radius + 1)

        if x2 <= x1 or y2 <= y1:
            return

        # Локальный кусок
        yy, xx = np.ogrid[y1:y2, x1:x2]
        dist_sq = (yy - cy) ** 2 + (xx - cx) ** 2
        mask = dist_sq <= radius * radius

        self.visible[y1:y2, x1:x2] |= mask

    # --- Проверки ---

    def is_visible(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return False
        return bool(self.visible[ty, tx])

    def is_explored(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return False
        return bool(self.explored[ty, tx])

    # --- Отрисовка маски ---

    def draw(self, screen, camera):
        """
        Рисует туман поверх игрового поля.
        Работает по видимым клеткам на экране (viewport).
        """
        # Координаты viewport в клетках
        # camera.x/y — мировые пиксели левого верхнего угла viewport
        start_tx = max(0, int(camera.x // 32))   # 32 = TILE_SIZE
        start_ty = max(0, int(camera.y // 32))
        end_tx = min(self.width, int((camera.x + camera.viewport_w) // 32) + 2)
        end_ty = min(self.height, int((camera.y + camera.viewport_h) // 32) + 2)

        # Временный surface для маски (один раз в кадр)
        # Размер — весь viewport
        vw = camera.viewport_w
        vh = camera.viewport_h

        if self._mask_surface is None \
                or self._mask_surface.get_width() != vw \
                or self._mask_surface.get_height() != vh:
            self._mask_surface = pygame.Surface((vw, vh), pygame.SRCALPHA)

        self._mask_surface.fill((0, 0, 0, 0))   # полностью прозрачный

        # Проходим по видимым клеткам и рисуем затемнение для "невидимых"
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                if self.visible[ty, tx]:
                    continue   # видно — ничего не рисуем

                # Координаты клетки в экранных пикселях (относительно viewport)
                sx = tx * 32 - int(camera.x)
                sy = ty * 32 - int(camera.y)

                if self.explored[ty, tx]:
                    color = FOG_EXPLORED_COLOR
                else:
                    color = FOG_UNEXPLORED_COLOR

                pygame.draw.rect(
                    self._mask_surface, color,
                    (sx, sy, 32, 32)
                )

        # Накладываем маску на viewport
        screen.blit(self._mask_surface, (camera.viewport_x, camera.viewport_y))