import random
import pygame
from settings import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT,
    TILE_GRASS, TILE_WATER, TILE_ROCK, TILE_SAND,
    TILE_COLORS, SHOW_GRID,
)


class TileMap:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        # Двумерный список: self.tiles[y][x] = тип тайла
        self.tiles = [[TILE_GRASS for _ in range(width)] for _ in range(height)]
        self._generate()

    def _generate(self):
        """Простая генерация: пятна воды, камня, песка."""
        # Вода — пятно в центре-слева
        for y in range(8, 15):
            for x in range(5, 13):
                if random.random() < 0.85:
                    self.tiles[y][x] = TILE_WATER

        # Камень — пятно справа-сверху
        for y in range(3, 9):
            for x in range(25, 33):
                if random.random() < 0.75:
                    self.tiles[y][x] = TILE_ROCK

        # Песок — полоса вдоль воды
        for y in range(7, 16):
            for x in range(4, 14):
                if self.tiles[y][x] == TILE_GRASS and random.random() < 0.5:
                    self.tiles[y][x] = TILE_SAND

    def draw(self, surface, camera_x=0, camera_y=0):
        """Рисует только те тайлы, что попадают в экран (culling)."""
        screen_w, screen_h = surface.get_size()

        # Индексы тайлов, которые видны на экране
        start_x = max(0, camera_x // TILE_SIZE)
        start_y = max(0, camera_y // TILE_SIZE)
        end_x = min(self.width, (camera_x + screen_w) // TILE_SIZE + 2)
        end_y = min(self.height, (camera_y + screen_h) // TILE_SIZE + 2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                color = TILE_COLORS[tile_type]

                # Экранные координаты тайла
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y

                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, color, rect)

                if SHOW_GRID:
                    pygame.draw.rect(surface, (0, 0, 0), rect, 1)

    def is_walkable_world(self, world_x, world_y):
        """Проверяет, проходим ли тайл в мировых координатах."""
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        # За пределами карты — непроходимо
        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return False

        tile_type = self.tiles[tile_y][tile_x]
        from settings import WALKABLE_TILES
        return WALKABLE_TILES.get(tile_type, False)

    def is_walkable_circle(self, world_x, world_y, radius):
        """
        Проверяет, что круг целиком лежит на проходимых тайлах.
        Сэмплируем 8 точек по окружности + центр — дёшево и достаточно.
        """
        import math

        # Центр
        if not self.is_walkable_world(world_x, world_y):
            return False

        # 8 точек по окружности
        for i in range(8):
            angle = i * math.pi / 4
            px = world_x + math.cos(angle) * radius
            py = world_y + math.sin(angle) * radius
            if not self.is_walkable_world(px, py):
                return False

        return True