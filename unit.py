import math
import pygame

import pathfinding
from settings import (
    TILE_SIZE, UNIT_RADIUS, UNIT_SPEED,
    UNIT_COLOR_PLAYER, UNIT_COLOR_ENEMY, UNIT_RADIUS_SELECT,
    REPATH_INTERVAL, REPATH_MAX_ATTEMPTS,
)


class Unit:
    def __init__(self, tile_x, tile_y, team="player"):
        self.team = team

        # Сеточная позиция (текущая клетка)
        self.tile_x = tile_x
        self.tile_y = tile_y

        # Пиксельные координаты = центр клетки
        self.x, self.y = self._tile_center(tile_x, tile_y)

        # Параметры (из settings)
        self.radius = UNIT_RADIUS
        self.speed = UNIT_SPEED
        self.color = UNIT_COLOR_PLAYER if team == "player" else UNIT_COLOR_ENEMY

        self.selected = False

        # Путь: список клеток (tx, ty) БЕЗ текущей
        self.path = []
        # Целевая клетка (для переприказа и пересчёта)
        self.goal_tile = None

        # Тайминг перестроения
        self.repath_timer = 0.0
        self.repath_attempts = 0

    # --- Вспомогательное ---

    @staticmethod
    def _tile_center(tx, ty):
        return tx * TILE_SIZE + TILE_SIZE / 2, ty * TILE_SIZE + TILE_SIZE / 2

    def is_idle(self):
        return not self.path

    def contains_point(self, world_x, world_y):
        dx = world_x - self.x
        dy = world_y - self.y
        return dx * dx + dy * dy <= self.radius * self.radius

    # --- Приказы ---

    def order_move_to_tile(self, world, goal_tile):
        """
        Приказ идти в клетку goal_tile.
        Если цель вне карты, непроходима или занята — приказ игнорируется.
        """
        # Проверка 1: цель — корректный кортеж из двух чисел
        if not goal_tile or len(goal_tile) != 2:
            return

        tx, ty = goal_tile

        # Проверка 2: в границах карты
        if tx < 0 or ty < 0 or tx >= world.tilemap.width or ty >= world.tilemap.height:
            return

        # Проверка 3: цель проходима (вода/скалы — нельзя)
        if not world.is_tile_walkable(tx, ty):
            return

        # Проверка 4: цель не занята другим юнитом
        occupant = world.unit_at(tx, ty)
        if occupant is not None and occupant is not self:
            return

        # Все проверки пройдены — ставим цель и строим путь
        self.goal_tile = (tx, ty)
        self.repath_attempts = 0
        self.repath_timer = 0.0
        self._build_path(world)

    def _build_path(self, world):
        """Пересчитывает self.path от текущей клетки к goal_tile."""
        if self.goal_tile is None:
            self.path = []
            return

        start = (self.tile_x, self.tile_y)
        goal = self.goal_tile

        if start == goal:
            self.path = []
            return

        # Целевая клетка должна быть свободна (кроме случая, когда юнит уже «едет»)
        if not world.is_tile_free(goal[0], goal[1], ignore_unit=self):
            # Пробуем найти рядом
            alt = world.find_nearest_free_tile(
                goal[0], goal[1], 3, ignore_unit=self
            )
            if alt is None:
                self.path = []
                return
            goal = alt
            self.goal_tile = goal

        path = pathfinding.find_path(world, start, goal, ignore_unit=self)
        self.path = path if path else []

    # --- Обновление ---

    def update(self, dt, world):
        """Движение по пути. Если путь оборвался — попытка перестроить."""
        if not self.path:
            return

        # Целевая клетка следующего шага
        next_tile = self.path[0]
        tx, ty = next_tile
        cx, cy = self._tile_center(tx, ty)

        dx = cx - self.x
        dy = cy - self.y
        dist = math.hypot(dx, dy)

        # Дошли до центра клетки
        if dist < 2.0:
            # Проверяем: не занята ли клетка другим юнитом (кроме нас)
            occupant = world.unit_at(tx, ty)
            if occupant is not None and occupant is not self:
                # Клетка занята — ждём и пытаемся перестроить
                self._wait_and_repath(dt, world)
                return

            # Перемещаем юнита в новую клетку (с проверкой)
            moved = world.move_unit_on_grid(self, tx, ty)
            if not moved:
                # Не смогли перейти — пробуем перестроить путь
                self._wait_and_repath(dt, world)
                return

            self.x, self.y = cx, cy
            self.path.pop(0)

            if not self.path:
                self.goal_tile = None
            return

        # Двигаемся к центру следующей клетки
        step = self.speed * dt
        if step > dist:
            step = dist

        self.x += dx / dist * step
        self.y += dy / dist * step

    def _wait_and_repath(self, dt, world):
        """Юнит стоит и раз в REPATH_INTERVAL пробует перестроить путь."""
        self.repath_timer += dt
        if self.repath_timer < REPATH_INTERVAL:
            return

        self.repath_timer = 0.0
        self.repath_attempts += 1

        self._build_path(world)

        if not self.path:
            if self.repath_attempts >= REPATH_MAX_ATTEMPTS:
                # Сдаёмся — окончательно стоим
                self.goal_tile = None

    # --- Отрисовка ---

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        sx, sy = int(sx), int(sy)

        pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
        pygame.draw.circle(surface, (20, 30, 50), (sx, sy), self.radius, 2)

        if self.selected:
            pygame.draw.circle(
                surface, (255, 230, 80),
                (sx, sy), self.radius + UNIT_RADIUS_SELECT, 3
            )

        # Маркер цели — центр конечной клетки
        if self.goal_tile is not None:
            gx, gy = self._tile_center(*self.goal_tile)
            gx, gy = camera.world_to_screen(gx, gy)
            gx, gy = int(gx), int(gy)
            size = 8
            pygame.draw.line(surface, (255, 230, 80),
                             (gx - size, gy), (gx + size, gy), 2)
            pygame.draw.line(surface, (255, 230, 80),
                             (gx, gy - size), (gx, gy + size), 2)