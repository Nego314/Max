import math
import pygame
import pathfinding
from settings import TILE_SIZE


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
        self.path = []


    def contains_point(self, world_x, world_y):
        dx = world_x - self.x
        dy = world_y - self.y
        return dx * dx + dy * dy <= self.radius * self.radius

    def move_to(self, world_x, world_y, tilemap=None):
        """
        Приказ: идти в точку (мировые координаты).
        Если передан tilemap — строим путь A*.
        """
        self.target_x = float(world_x)
        self.target_y = float(world_y)

        if tilemap is None:
            # Простая прямая (на случай, если карты нет)
            self.path = [(self.target_x, self.target_y)]
            return

        # Пробуем A*
        path = pathfinding.find_path(
            tilemap,
            (self.x, self.y),
            (self.target_x, self.target_y),
            TILE_SIZE,
        )
        if path:
            self.path = pathfinding.smooth_path(path)
        else:
            # Путь не найден — пробуем прямую (юнит дойдёт «как сможет»)
            self.path = [(self.target_x, self.target_y)]

    def update(self, dt, tilemap):
        """Движение по пути с учётом препятствий."""
        # Если пути нет — идём к target напрямую (старое поведение)
        if not self.path:
            if self.target_x is None:
                return
            self.path = [(self.target_x, self.target_y)]

        # Берём первую точку пути
        tx, ty = self.path[0]

        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        # Дошли до точки пути — убираем её и берём следующую
        if dist < 4.0:
            self.path.pop(0)
            if not self.path:
                # Путь закончился
                self.target_x = None
                self.target_y = None
            return

        step = self.speed * dt
        if step > dist:
            step = dist

        nx = self.x + dx / dist * step
        ny = self.y + dy / dist * step

        # Проверка коллизии (страховка)
        if tilemap.is_walkable_circle(nx, ny, self.radius):
            self.x, self.y = nx, ny
        else:
            # Путь сломался — перестроим
            if self.target_x is not None:
                self.move_to(self.target_x, self.target_y, tilemap)


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
    Двигающиеся юниты уступают стоящим: стоящий остаётся на месте,
    движущийся берёт на себя полный сдвиг.
    Если оба движутся — расталкиваются поровну.
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
                angle = random.random() * 6.28318
                dx = math.cos(angle)
                dy = math.sin(angle)
                dist = 0.001

            nx = dx / dist
            ny = dy / dist

            overlap = min_dist - dist

            # Определяем, кто движется (у кого есть цель)
            a_moving = a.target_x is not None
            b_moving = b.target_x is not None

            if a_moving and b_moving:
                # Оба движутся — сдвиг пополам
                push_a = overlap / 2.0
                push_b = overlap / 2.0
            elif a_moving and not b_moving:
                # Движется только A — он и уступает полностью
                push_a = overlap
                push_b = 0.0
            elif b_moving and not a_moving:
                # Движется только B — он и уступает полностью
                push_a = 0.0
                push_b = overlap
            else:
                # Оба стоят — не трогаем (не должны пересекаться, но на всякий случай)
                continue

            a.x -= nx * push_a
            a.y -= ny * push_a
            b.x += nx * push_b
            b.y += ny * push_b