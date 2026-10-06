import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    CAMERA_SPEED_KEYS, CAMERA_SPEED_EDGE, CAMERA_EDGE_MARGIN,
)


class Camera:
    def __init__(self, map_width=MAP_WIDTH, map_height=MAP_HEIGHT):
        self.x = 0.0          # мировые координаты левого верхнего угла вида
        self.y = 0.0
        self.map_pixel_w = map_width * TILE_SIZE
        self.map_pixel_h = map_height * TILE_SIZE

    def update(self, dt, keys, mouse_pos):
        """Двигает камеру по стрелкам/WASD и у краёв экрана."""
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

        # --- Мышь у краёв экрана ---
        mx, my = mouse_pos
        if mx <= CAMERA_EDGE_MARGIN:
            dx -= CAMERA_SPEED_EDGE * dt
        elif mx >= SCREEN_WIDTH - CAMERA_EDGE_MARGIN:
            dx += CAMERA_SPEED_EDGE * dt
        if my <= CAMERA_EDGE_MARGIN:
            dy -= CAMERA_SPEED_EDGE * dt
        elif my >= SCREEN_HEIGHT - CAMERA_EDGE_MARGIN:
            dy += CAMERA_SPEED_EDGE * dt

        # --- Применяем и ограничиваем ---
        self.x += dx
        self.y += dy
        self._clamp()

    def _clamp(self):
        """Не даём камере выехать за карту."""
        max_x = max(0, self.map_pixel_w - SCREEN_WIDTH)
        max_y = max(0, self.map_pixel_h - SCREEN_HEIGHT)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def move_to(self, world_x, world_y):
        """Центрировать камеру на точке (пригодится для миникарты)."""
        self.x = world_x - SCREEN_WIDTH / 2
        self.y = world_y - SCREEN_HEIGHT / 2
        self._clamp()

    def screen_to_world(self, screen_x, screen_y):
        """Преобразовать координаты экрана в мировые (для клика по карте)."""
        return screen_x + self.x, screen_y + self.y

    def world_to_screen(self, world_x, world_y):
        """Мировые координаты → экранные."""
        return world_x - self.x, world_y - self.y

    @property
    def offset(self):
        """Возвращает целочисленное смещение — для отрисовки без дрожания."""
        return int(self.x), int(self.y)