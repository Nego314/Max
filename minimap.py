"""
Миникарта: два режима — без ресурсов (по умолчанию) и с ресурсами.
"""
import numpy as np
import pygame

from settings import (
    TILE_SIZE, TILE_COLORS,
    TILE_REGOLITH, TILE_DUST, TILE_ROCK, TILE_CRATER,
    TILE_ICE, TILE_ILMENITE, TILE_ANORTHOSITE,
    MINIMAP_SIZE, MINIMAP_CAMERA_COLOR,
    MINIMAP_ALLY_COLOR, MINIMAP_ENEMY_COLOR,
    MINIMAP_MODE_PLAIN, MINIMAP_MODE_RESOURCES,
    MINIMAP_BUTTON_HEIGHT, MINIMAP_BUTTON_COLOR,
    MINIMAP_BUTTON_COLOR_HOVER, MINIMAP_BUTTON_TEXT_COLOR,
    UI_PANEL_WIDTH,
)


class Minimap:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.size = MINIMAP_SIZE

        self.scale_x = tilemap.width / self.size
        self.scale_y = tilemap.height / self.size

        # Режим: с ресурсами или без
        self.mode = MINIMAP_MODE_PLAIN

        # Две статичные картинки: без ресурсов и с ресурсами
        self.surface_plain = self._build_surface(include_resources=False)
        self.surface_resources = self._build_surface(include_resources=True)

        # Позиция на экране
        self.screen_x = 0
        self.screen_y = 0
        self.screen_rect = pygame.Rect(0, 0, self.size, self.size)

        # Кнопка переключения
        self.button_rect = pygame.Rect(0, 0, 0, 0)
        self.button_hover = False

        self._font = pygame.font.SysFont("consolas", 14)

    # --- Позиционирование ---

    def set_position(self, x, y):
        self.screen_x = x
        self.screen_y = y
        self.screen_rect = pygame.Rect(x, y, self.size, self.size)

        # Кнопка — под миникартой
        btn_y = y + self.size + 4
        self.button_rect = pygame.Rect(x, btn_y, self.size, MINIMAP_BUTTON_HEIGHT)

    # --- Генерация картинки ---

    def _build_surface(self, include_resources):
        """
        Создаёт уменьшенную карту.
        include_resources=False — ресурсы заменяются на базовый ландшафт.
        """
        tiles = self.tilemap.tiles

        # Если не хотим ресурсы — подменяем их на реголит
        if not include_resources:
            tiles = tiles.copy()
            for res in (TILE_ICE, TILE_ILMENITE, TILE_ANORTHOSITE):
                tiles[tiles == res] = TILE_REGOLITH

        # RGB через LUT
        max_tile = max(TILE_COLORS.keys()) + 1
        lut = np.zeros((max_tile, 3), dtype=np.uint8)
        for k, v in TILE_COLORS.items():
            lut[k] = v
        rgb = lut[tiles]   # (H, W, 3)

        # pygame.Surface из numpy
        rgb_wh = np.transpose(rgb, (1, 0, 2))
        big = pygame.Surface((self.tilemap.width, self.tilemap.height))
        pygame.surfarray.blit_array(big, rgb_wh)

        # Уменьшаем через smoothscale
        small = pygame.transform.smoothscale(big, (self.size, self.size))
        return small

    # --- Отрисовка ---

    def draw(self, screen, world, camera, fog):
        # Выбор поверхности по режиму
        if self.mode == MINIMAP_MODE_RESOURCES:
            surface = self.surface_resources
        else:
            surface = self.surface_plain

        screen.blit(surface, (self.screen_x, self.screen_y))

        # Юниты
        for u in world.units:
            if u.team != "player" and not fog.is_visible(u.tile_x, u.tile_y):
                continue

            mx = self.screen_x + int(u.tile_x / self.scale_x)
            my = self.screen_y + int(u.tile_y / self.scale_y)

            color = MINIMAP_ALLY_COLOR if u.team == "player" else MINIMAP_ENEMY_COLOR
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

        # Кнопка переключения режима
        self._draw_button(screen)

    def _draw_button(self, screen):
        """Кнопка переключения режима миникарты."""
        mouse_pos = pygame.mouse.get_pos()
        self.button_hover = self.button_rect.collidepoint(mouse_pos)

        color = (MINIMAP_BUTTON_COLOR_HOVER if self.button_hover
                 else MINIMAP_BUTTON_COLOR)

        pygame.draw.rect(screen, color, self.button_rect)
        pygame.draw.rect(screen, (80, 80, 100), self.button_rect, 1)

        # Текст
        if self.mode == MINIMAP_MODE_PLAIN:
            label = "Показать ресурсы"
        else:
            label = "Скрыть ресурсы"

        text = self._font.render(label, True, MINIMAP_BUTTON_TEXT_COLOR)
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)

    # --- Обработка событий ---

    def handle_click(self, mouse_pos):
        """
        Возвращает True, если клик был обработан (кнопка нажата).
        """
        if self.button_rect.collidepoint(mouse_pos):
            # Переключаем режим
            if self.mode == MINIMAP_MODE_PLAIN:
                self.mode = MINIMAP_MODE_RESOURCES
            else:
                self.mode = MINIMAP_MODE_PLAIN
            return True
        return False

    # --- Клик по миникарте ---

    def screen_to_world(self, mouse_x, mouse_y):
        local_x = mouse_x - self.screen_x
        local_y = mouse_y - self.screen_y
        tile_x = local_x * self.scale_x
        tile_y = local_y * self.scale_y
        return tile_x * TILE_SIZE, tile_y * TILE_SIZE

    def contains_point(self, mouse_pos):
        return self.screen_rect.collidepoint(mouse_pos)

    def button_contains_point(self, mouse_pos):
        return self.button_rect.collidepoint(mouse_pos)