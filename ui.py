"""
Игровой интерфейс (HUD): левая панель свойств и правая панель
с миникартой, ресурсами и координатами курсора.
"""
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_PANEL_WIDTH, UI_PANEL_COLOR, UI_BORDER_COLOR,
    UI_TEXT_COLOR, UI_HEADER_COLOR, UI_FONT_SIZE,
    TILE_SIZE,   # ← добавь
)


class UI:
    def __init__(self, screen):
        self.screen = screen

        # Геометрия панелей
        self.left_panel = pygame.Rect(
            0, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT
        )
        self.right_panel = pygame.Rect(
            SCREEN_WIDTH - UI_PANEL_WIDTH, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT
        )

        # Игровое поле — область между панелями
        self.viewport = pygame.Rect(
            UI_PANEL_WIDTH, 0,
            SCREEN_WIDTH - 2 * UI_PANEL_WIDTH, SCREEN_HEIGHT,
        )

        # Шрифты
        self.font = pygame.font.SysFont("consolas", UI_FONT_SIZE)

    # --- Геометрия ---

    def is_over_ui(self, mouse_pos):
        """True, если точка над одной из панелей."""
        return self.left_panel.collidepoint(mouse_pos) \
            or self.right_panel.collidepoint(mouse_pos)

    def is_over_viewport(self, mouse_pos):
        return self.viewport.collidepoint(mouse_pos)

    # --- Отрисовка ---

    def draw(self, camera, mouse_pos):
        # Левая панель
        pygame.draw.rect(self.screen, UI_PANEL_COLOR, self.left_panel)
        pygame.draw.line(
            self.screen, UI_BORDER_COLOR,
            (self.left_panel.right - 1, 0),
            (self.left_panel.right - 1, SCREEN_HEIGHT), 1
        )

        # Правая панель
        pygame.draw.rect(self.screen, UI_PANEL_COLOR, self.right_panel)
        pygame.draw.line(
            self.screen, UI_BORDER_COLOR,
            (self.right_panel.left, 0),
            (self.right_panel.left, SCREEN_HEIGHT), 1
        )

        # Временные заголовки (потом заменим)
        text = self.font.render("СВОЙСТВА", True, UI_HEADER_COLOR)
        self.screen.blit(text, (self.left_panel.x + 12, 12))

        text = self.font.render("МИНИКАРТА", True, UI_HEADER_COLOR)
        self.screen.blit(text, (self.right_panel.x + 12, 12))

        text = self.font.render("РЕСУРСЫ", True, UI_HEADER_COLOR)
        self.screen.blit(text, (self.right_panel.x + 12, 320))

        # Блок координат курсора — внизу правой панели
        self.draw_cursor_coords(camera, mouse_pos)

    def draw_cursor_coords(self, camera, mouse_pos):
        """Рисует блок с координатами клетки под курсором."""
        # Геометрия блока
        block_w = UI_PANEL_WIDTH - 20
        block_h = 60
        block_x = self.right_panel.x + 10
        block_y = SCREEN_HEIGHT - block_h - 10

        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        pygame.draw.rect(self.screen, (35, 35, 48), block_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, block_rect, 1)

        # Заголовок
        header = self.font.render("КУРСОР", True, UI_HEADER_COLOR)
        self.screen.blit(header, (block_x + 10, block_y + 8))

        # Координаты
        if self.is_over_viewport(mouse_pos):
            wx, wy = camera.screen_to_world(*mouse_pos)
            tx = int(wx // TILE_SIZE)
            ty = int(wy // TILE_SIZE)
            text_str = f"X: {tx}   Y: {ty}"
        else:
            text_str = "X: ---   Y: ---"

        text = self.font.render(text_str, True, UI_TEXT_COLOR)
        self.screen.blit(text, (block_x + 10, block_y + 30))