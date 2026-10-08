"""
Поиск пути A* по клеткам.
"""
import heapq
import math


def heuristic(a, b):
    """Октальное расстояние — оптимально для 8-направленного движения."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)


def find_path(world, start_tile, goal_tile, ignore_unit=None):
    """
    A* от start_tile до goal_tile. Оба — (tx, ty) в клетках.
    Возвращает список клеток [(tx, ty), ...] БЕЗ стартовой, включая целевую.
    Или None, если пути нет.
    """
    if start_tile == goal_tile:
        return []

    if not world.is_tile_walkable(*goal_tile):
        return None

    open_set = []
    heapq.heappush(open_set, (0.0, start_tile))

    came_from = {}
    g_score = {start_tile: 0.0}

    neighbors = [
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
        (-1, -1, math.sqrt(2)), (1, -1, math.sqrt(2)),
        (-1, 1, math.sqrt(2)), (1, 1, math.sqrt(2)),
    ]

    visited = set()
    max_iterations = 8000
    iterations = 0

    while open_set:
        iterations += 1
        if iterations > max_iterations:
            return None

        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal_tile:
            return _reconstruct(came_from, current)

        cx, cy = current
        for dx, dy, cost in neighbors:
            nx, ny = cx + dx, cy + dy
            neighbor = (nx, ny)

            if not world.is_tile_walkable(nx, ny):
                continue

            # Клетка занята — можно войти только если это целевая (её обработаем отдельно)
            if neighbor != goal_tile:
                if world.unit_at(nx, ny) is not None and world.unit_at(nx, ny) is not ignore_unit:
                    continue

            # Диагональ: проверяем оба «прямых» соседа, чтобы не срезать угол
            if dx != 0 and dy != 0:
                if not world.is_tile_walkable(cx + dx, cy):
                    continue
                if not world.is_tile_walkable(cx, cy + dy):
                    continue

            tentative_g = g_score[current] + cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal_tile)
                heapq.heappush(open_set, (f, neighbor))

    return None


def _reconstruct(came_from, current):
    """Восстанавливает путь (без стартовой клетки)."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path[1:]  # убираем стартовую