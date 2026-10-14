"""
Здания: статичные многоклеточные объекты.
"""
import pygame

from settings import (
    TILE_SIZE, BUILDING_TYPES,
)


class Building:
    def __init__(self, tile_x, tile_y, building_type="habitat", team="player"):
        self.team = team
        self.building_type = building_type

        tpl = BUILDING_TYPES[building_type]
        self.letter = tpl["letter"]
        self.type_name = tpl["name"]
        self.size = tpl["size"]         # 2 для 2×2
        self.color = tpl["color"]

        self.hp = tpl["hp"]
        self.max_hp = tpl["max_hp"]

        # Левый верхний угол здания (в клетках)
        self.tile_x = tile_x
        self.tile_y = tile_y

        self.selected = False

    def get_occupied_tiles(self):
        """
        Возвращает список всех клеток, которые занимает здание.
        Для 2×2 это 4 клетки.
        """
        tiles = []
        for dy in range(self.size):
            for dx in range(self.size):
                tiles.append((self.tile_x + dx, self.tile_y + dy))
        return tiles

    def contains_tile(self, tx, ty):
        """Проверяет, занимает ли здание клетку (tx, ty)."""
        return (self.tile_x <= tx < self.tile_x + self.size and
                self.tile_y <= ty < self.tile_y + self.size)

    def contains_point(self, world_x, world_y):
        """Проверяет попадание точки (в мировых координатах) в здание."""
        px = self.tile_x * TILE_SIZE
        py = self.tile_y * TILE_SIZE
        pw = self.size * TILE_SIZE
        ph = self.size * TILE_SIZE
        return px <= world_x < px + pw and py <= world_y < py + ph

    def get_center_world(self):
        """Центр здания в мировых координатах."""
        px = self.tile_x * TILE_SIZE
        py = self.tile_y * TILE_SIZE
        pw = self.size * TILE_SIZE
        ph = self.size * TILE_SIZE
        return px + pw / 2, py + ph / 2

    def draw(self, surface, camera):
        """Рисует здание."""
        # Левый верхний угол в экранных координатах
        sx, sy = camera.world_to_screen(
            self.tile_x * TILE_SIZE,
            self.tile_y * TILE_SIZE,
        )
        sx, sy = int(sx), int(sy)

        size_px = self.size * TILE_SIZE

        # Основной прямоугольник
        rect = pygame.Rect(sx, sy, size_px, size_px)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (20, 30, 50), rect, 2)

        # Буква типа в центре
        big_font = pygame.font.SysFont("consolas", size_px // 2, bold=True)
        letter_surf = big_font.render(self.letter, True, (30, 30, 40))
        letter_rect = letter_surf.get_rect(center=(sx + size_px // 2, sy + size_px // 2))
        surface.blit(letter_surf, letter_rect)

        # Кольцо выделения — жёлтая рамка вокруг
        if self.selected:
            pygame.draw.rect(surface, (255, 230, 80), rect, 2)