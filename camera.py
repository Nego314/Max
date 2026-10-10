import pygame
import settings
from settings import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    CAMERA_SPEED_KEYS, CAMERA_SPEED_EDGE, CAMERA_EDGE_MARGIN,
    UI_PANEL_WIDTH,
)

class Camera:
    def __init__(self, map_width=MAP_WIDTH, map_height=MAP_HEIGHT):
        self.x = 0.0
        self.y = 0.0
        self.map_pixel_w = map_width * TILE_SIZE
        self.map_pixel_h = map_height * TILE_SIZE

        # Сдвиг и размеры viewport (игрового поля)
        self.viewport_x = UI_PANEL_WIDTH
        self.viewport_y = 0
        self.viewport_w = settings.SCREEN_WIDTH - 2 * UI_PANEL_WIDTH
        self.viewport_h = settings.SCREEN_HEIGHT

    def update(self, dt, keys, mouse_pos):
        dx = dy = 0.0

        # --- Клавиатура ---
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= CAMERA_SPEED_KEYS * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += CAMERA_SPEED_KEYS * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= CAMERA_SPEED_KEYS * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += CAMERA_SPEED_KEYS * dt

        # --- Мышь у краёв viewport ---
        mx, my = mouse_pos
        vx1 = self.viewport_x
        vx2 = self.viewport_x + self.viewport_w
        vy1 = self.viewport_y
        vy2 = self.viewport_y + self.viewport_h

        # Только если мышь внутри viewport (не над панелями)
        if vx1 <= mx < vx2 and vy1 <= my < vy2:
            if mx <= vx1 + CAMERA_EDGE_MARGIN:
                dx -= CAMERA_SPEED_EDGE * dt
            elif mx >= vx2 - CAMERA_EDGE_MARGIN:
                dx += CAMERA_SPEED_EDGE * dt
            if my <= vy1 + CAMERA_EDGE_MARGIN:
                dy -= CAMERA_SPEED_EDGE * dt
            elif my >= vy2 - CAMERA_EDGE_MARGIN:
                dy += CAMERA_SPEED_EDGE * dt

        self.x += dx
        self.y += dy
        self._clamp()

    def _clamp(self):
        """Камера не выезжает за карту (с учётом viewport, а не всего экрана)."""
        max_x = max(0, self.map_pixel_w - self.viewport_w)
        max_y = max(0, self.map_pixel_h - self.viewport_h)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def move_to(self, world_x, world_y):
        self.x = world_x - self.viewport_w / 2
        self.y = world_y - self.viewport_h / 2
        self._clamp()

    def screen_to_world(self, screen_x, screen_y):
        """
        Экранные пиксели → мировые.
        Учитывает сдвиг viewport (панели слева и справа).
        """
        return (screen_x - self.viewport_x + self.x,
                screen_y - self.viewport_y + self.y)

    def world_to_screen(self, world_x, world_y):
        """Мировые координаты → экранные (с учётом сдвига viewport)."""
        return (world_x - self.x + self.viewport_x,
                world_y - self.y + self.viewport_y)

    @property
    def offset(self):
        """Смещение для рендера тайлов (без учёта viewport, чистый мир)."""
        return int(self.x), int(self.y)