"""
Игровой интерфейс (HUD): левая панель свойств и правая панель
с миникартой, ресурсами и координатами курсора.
"""
import pygame
from minimap import Minimap
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_PANEL_WIDTH, UI_PANEL_COLOR, UI_BORDER_COLOR,
    UI_TEXT_COLOR, UI_HEADER_COLOR, UI_FONT_SIZE,
    TILE_SIZE, RESOURCES, COLONY_POPULATION,
    UNIT_STATS, UI_STATS_ROW_HEIGHT, UI_PORTRAIT_HEIGHT,
    MINIMAP_SIZE, MINIMAP_MARGIN, MINIMAP_BUTTON_HEIGHT,
    TILE_NAMES,
)


class UI:
    def __init__(self, screen, tilemap):
        self.screen = screen

        # Геометрия панелей
        self.left_panel = pygame.Rect(0, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT)
        self.right_panel = pygame.Rect(
            SCREEN_WIDTH - UI_PANEL_WIDTH, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT
        )
        self.viewport = pygame.Rect(
            UI_PANEL_WIDTH, 0,
            SCREEN_WIDTH - 2 * UI_PANEL_WIDTH, SCREEN_HEIGHT,
        )

        self.font = pygame.font.SysFont("consolas", UI_FONT_SIZE)

        # Миникарта
        self.minimap = Minimap(tilemap)
        mm_x = self.right_panel.x + MINIMAP_MARGIN
        mm_y = 40
        self.minimap.set_position(mm_x, mm_y)

    # --- Геометрия ---

    def is_over_ui(self, mouse_pos):
        return self.left_panel.collidepoint(mouse_pos) \
            or self.right_panel.collidepoint(mouse_pos)

    def is_over_viewport(self, mouse_pos):
        return self.viewport.collidepoint(mouse_pos)

    # --- Отрисовка ---

    def draw(self, camera, mouse_pos, world, fog):
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

        # Свойства (левая панель)
        self.draw_properties(world)

        # Заголовок + миникарта
        text = self.font.render("МИНИКАРТА", True, UI_HEADER_COLOR)
        self.screen.blit(text, (self.right_panel.x + 12, 12))
        self.minimap.draw(self.screen, world, camera, fog)

        # Панель населения
        self.draw_population()

        # Панель ресурсов
        self.draw_resources()

        # Блок координат
        self.draw_cursor_coords(camera, mouse_pos, self.minimap.tilemap)

    # --- Правая панель ---

    def draw_population(self):
        block_w = UI_PANEL_WIDTH - 20
        block_h = 60
        block_x = self.right_panel.x + 10
        block_y = 40 + MINIMAP_SIZE + MINIMAP_BUTTON_HEIGHT + 20

        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        pygame.draw.rect(self.screen, (35, 35, 48), block_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, block_rect, 1)

        header = self.font.render("НАСЕЛЕНИЕ", True, UI_HEADER_COLOR)
        self.screen.blit(header, (block_x + 10, block_y + 8))

        parts = []
        for pop in COLONY_POPULATION:
            parts.append(f"{pop['letter']}:{pop['count']}")
        text_str = "   ".join(parts)
        text = self.font.render(text_str, True, UI_TEXT_COLOR)
        self.screen.blit(text, (block_x + 10, block_y + 32))

    def draw_resources(self):
        block_w = UI_PANEL_WIDTH - 20
        block_x = self.right_panel.x + 10
        block_y = 40 + MINIMAP_SIZE + MINIMAP_BUTTON_HEIGHT + 20 + 60 + 10
        block_h = SCREEN_HEIGHT - block_y - 80

        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        pygame.draw.rect(self.screen, (35, 35, 48), block_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, block_rect, 1)

        header = self.font.render("РЕСУРСЫ", True, UI_HEADER_COLOR)
        self.screen.blit(header, (block_x + 10, block_y + 8))

        row_h = 24
        y = block_y + 34
        icon_size = 12

        for res in RESOURCES:
            if y + row_h > block_rect.bottom - 4:
                break

            icon_rect = pygame.Rect(block_x + 10, y + 4, icon_size, icon_size)
            pygame.draw.rect(self.screen, res["icon_color"], icon_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), icon_rect, 1)

            unit = res.get("unit", "")
            value = res["value"]
            text_str = f"{res['name']}: {value} {unit}".rstrip()
            text = self.font.render(text_str, True, UI_TEXT_COLOR)
            self.screen.blit(text, (block_x + 10 + icon_size + 8, y + 2))

            y += row_h

    def draw_cursor_coords(self, camera, mouse_pos, tilemap):
        block_w = UI_PANEL_WIDTH - 20
        block_h = 60
        block_x = self.right_panel.x + 10
        block_y = SCREEN_HEIGHT - block_h - 10

        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        pygame.draw.rect(self.screen, (35, 35, 48), block_rect)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, block_rect, 1)

        header = self.font.render("КУРСОР", True, UI_HEADER_COLOR)
        self.screen.blit(header, (block_x + 10, block_y + 8))

        if self.is_over_viewport(mouse_pos):
            wx, wy = camera.screen_to_world(*mouse_pos)
            tx = int(wx // TILE_SIZE)
            ty = int(wy // TILE_SIZE)

            if 0 <= tx < tilemap.width and 0 <= ty < tilemap.height:
                tile_type = int(tilemap.tiles[ty, tx])
                tile_name = TILE_NAMES.get(tile_type, "?")
                text_str = f"X: {tx}  Y: {ty}  [{tile_name}]"
            else:
                text_str = f"X: {tx}  Y: {ty}  [вне карты]"
        else:
            text_str = "X: ---  Y: ---"

        text = self.font.render(text_str, True, UI_TEXT_COLOR)
        self.screen.blit(text, (block_x + 10, block_y + 30))

    # --- Левая панель: свойства + портрет ---

    def draw_properties(self, world):
        panel = self.left_panel

        header = self.font.render("СВОЙСТВА", True, UI_HEADER_COLOR)
        self.screen.blit(header, (panel.x + 12, 12))

        # Определяем выделение — СНАЧАЛА здания, ПОТОМ юниты
        selected_buildings = [b for b in world.buildings
                              if b.selected and b.team == "player"]
        selected_units = [u for u in world.units
                          if u.selected and u.team == "player"]

        stats_y = 45
        stats_x = panel.x + 12
        row_h = UI_STATS_ROW_HEIGHT

        # --- Приоритет: здание > одиночный юнит > группа юнитов ---
        if selected_buildings:
            b = selected_buildings[0]
            type_text = self.font.render(f"{b.type_name}", True, UI_HEADER_COLOR)
            self.screen.blit(type_text, (stats_x, stats_y))
            stats_y += row_h + 6

            hp_text = self.font.render(f"Прочность: {b.hp} / {b.max_hp}",
                                       True, UI_TEXT_COLOR)
            self.screen.blit(hp_text, (stats_x, stats_y))
            stats_y += row_h

            size_text = self.font.render(f"Размер: {b.size}×{b.size}",
                                         True, UI_TEXT_COLOR)
            self.screen.blit(size_text, (stats_x, stats_y))
            stats_y += row_h

        elif not selected_units:
            text = self.font.render("Ничего не выделено", True, UI_TEXT_COLOR)
            self.screen.blit(text, (stats_x, stats_y))

        elif len(selected_units) == 1:
            u = selected_units[0]
            type_text = self.font.render(f"{u.type_name}", True, UI_HEADER_COLOR)
            self.screen.blit(type_text, (stats_x, stats_y))
            stats_y += row_h + 6

            for stat in UNIT_STATS:
                value = u.get_stat(stat["key"])
                unit_str = stat["unit"]
                line = f"{stat['name']}: {value} {unit_str}".rstrip()
                text = self.font.render(line, True, UI_TEXT_COLOR)
                self.screen.blit(text, (stats_x, stats_y))
                stats_y += row_h

        else:
            text = self.font.render(f"Выделено: {len(selected_units)} юнитов",
                                    True, UI_HEADER_COLOR)
            self.screen.blit(text, (stats_x, stats_y))

        # Портрет
        self.draw_portrait(selected_buildings, selected_units)

    def draw_portrait(self, selected_buildings, selected_units):
        panel = self.left_panel
        block_h = UI_PORTRAIT_HEIGHT
        block_y = SCREEN_HEIGHT - block_h
        block_rect = pygame.Rect(panel.x, block_y, panel.width, block_h)

        pygame.draw.rect(self.screen, (35, 35, 48), block_rect)
        pygame.draw.line(self.screen, UI_BORDER_COLOR,
                         (panel.x, block_y),
                         (panel.x + panel.width, block_y), 1)

        header = self.font.render("ПОРТРЕТ", True, UI_HEADER_COLOR)
        self.screen.blit(header, (panel.x + 12, block_y + 8))

        center_x = panel.x + panel.width // 2
        center_y = block_y + block_h // 2 + 10

        # --- Приоритет: здание > одиночный юнит > группа ---
        if selected_buildings:
            b = selected_buildings[0]
            self._draw_portrait_icon(center_x, center_y, b.color, b.letter)
        elif len(selected_units) == 1:
            u = selected_units[0]
            self._draw_portrait_icon(center_x, center_y, u.color, u.letter)
        elif len(selected_units) > 1:
            self._draw_portrait_icon(center_x, center_y,
                                     (100, 100, 120), f"{len(selected_units)}")

    def _draw_portrait_icon(self, cx, cy, color, letter):
        radius = 60
        pygame.draw.circle(self.screen, color, (cx, cy), radius)
        pygame.draw.circle(self.screen, (20, 30, 50), (cx, cy), radius, 3)

        big_font = pygame.font.SysFont("consolas", 48, bold=True)
        letter_surf = big_font.render(letter, True, (255, 255, 255))
        rect = letter_surf.get_rect(center=(cx, cy))
        self.screen.blit(letter_surf, rect)