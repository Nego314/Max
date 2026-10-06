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

    def update(self, dt):
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

        self.x += dx / dist * step
        self.y += dy / dist * step

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