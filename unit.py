import math
import pygame


class Unit:
    def __init__(self, x, y, color=(80, 160, 255), radius=18,
                 speed=180.0, team="player"):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color
        self.selected = False
        self.speed = speed
        self.team = team  # "player" или "enemy"

        self.target_x = None
        self.target_y = None

    def contains_point(self, world_x, world_y):
        dx = world_x - self.x
        dy = world_y - self.y
        return dx * dx + dy * dy <= self.radius * self.radius

    def move_to(self, world_x, world_y):
        self.target_x = float(world_x)
        self.target_y = float(world_y)

    def update(self, dt, tilemap):
        """Движение к цели с учётом препятствий (простая версия — без A*)."""
        if self.target_x is None or self.target_y is None:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 2.0:
            self.x = self.target_x
            self.y = self.target_y
            self.target_x = None
            self.target_y = None
            return

        step = self.speed * dt
        if step > dist:
            step = dist

        # Куда хотим сдвинуться
        nx = self.x + dx / dist * step
        ny = self.y + dy / dist * step

        # Пробуем полное смещение
        if tilemap.is_walkable_circle(nx, ny, self.radius):
            self.x, self.y = nx, ny
            return

        # Не получилось — пробуем только по X
        if tilemap.is_walkable_circle(nx, self.y, self.radius):
            self.x = nx
            return

        # Только по Y
        if tilemap.is_walkable_circle(self.x, ny, self.radius):
            self.y = ny
            return

        # Всё заблокировано — стоим (позже заменим на A*)
        # Пока просто сбрасываем цель, чтобы юнит не «дрожал» у стены
        # (раскомментируй, если хочешь, чтобы юнит останавливался)
        # self.target_x = None
        # self.target_y = None

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        sx, sy = int(sx), int(sy)

        pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
        pygame.draw.circle(surface, (20, 30, 50), (sx, sy), self.radius, 2)

        if self.selected:
            pygame.draw.circle(surface, (255, 230, 80), (sx, sy), self.radius + 5, 3)

        if self.target_x is not None:
            tx, ty = camera.world_to_screen(self.target_x, self.target_y)
            tx, ty = int(tx), int(ty)
            size = 8
            pygame.draw.line(surface, (255, 230, 80),
                             (tx - size, ty), (tx + size, ty), 2)
            pygame.draw.line(surface, (255, 230, 80),
                             (tx, ty - size), (tx, ty + size), 2)

def resolve_unit_collisions(units):
    """
    Раздвигает пересекающихся юнитов.
    Простая физика: если два круга пересекаются — расталкиваем их поровну.
    Вызывается раз в кадр после update() всех юнитов.
    """
    n = len(units)
    for i in range(n):
        a = units[i]
        for j in range(i + 1, n):
            b = units[j]

            dx = b.x - a.x
            dy = b.y - a.y
            dist_sq = dx * dx + dy * dy
            min_dist = a.radius + b.radius

            # Не пересекаются — пропускаем
            if dist_sq >= min_dist * min_dist:
                continue

            dist = dist_sq ** 0.5

            # Случай «ровно в одной точке» — раздвигаем в случайном направлении
            if dist < 0.001:
                import random
                angle = random.random() * 6.28318
                import math as _m
                dx = _m.cos(angle)
                dy = _m.sin(angle)
                dist = 0.001

            # Нормализованный вектор от A к B
            nx = dx / dist
            ny = dy / dist

            # Насколько нужно раздвинуть, чтобы они коснулись
            overlap = min_dist - dist
            push = overlap / 2.0

            a.x -= nx * push
            a.y -= ny * push
            b.x += nx * push
            b.y += ny * push
