"""
Поиск пути A* по тайловой сетке.
"""
import heapq
import math


def world_to_tile(world_x, world_y, tile_size):
    """Мировые координаты → координаты тайла."""
    return int(world_x // tile_size), int(world_y // tile_size)


def tile_to_world_center(tile_x, tile_y, tile_size):
    """Центр тайла в мировых координатах."""
    return tile_x * tile_size + tile_size / 2, tile_y * tile_size + tile_size / 2


def heuristic(a, b):
    """Октальное расстояние — хорошо для 8-направленного движения."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)


def find_path(tilemap, start_world, goal_world, tile_size):
    """
    Ищет путь A* от start_world до goal_world (мировые координаты).
    Возвращает список мировых точек [(x, y), ...] или None, если пути нет.
    """
    start = world_to_tile(*start_world, tile_size)
    goal = world_to_tile(*goal_world, tile_size)

    # Если цель непроходима — попробуем найти ближайший проходимый тайл
    if not tilemap.is_walkable_world(*goal_world):
        goal = _find_nearest_walkable(tilemap, goal, tile_size)
        if goal is None:
            return None

    # Если старт непроходим (застряли) — тоже ищем ближайший
    if not tilemap.is_walkable_world(*start_world):
        start = _find_nearest_walkable(tilemap, start, tile_size)
        if start is None:
            return None

    # --- A* ---
    open_set = []
    heapq.heappush(open_set, (0.0, start))

    came_from = {}
    g_score = {start: 0.0}
    f_score = {start: heuristic(start, goal)}

    # 8 направлений: 4 прямых + 4 диагональных
    neighbors = [
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
        (-1, -1, math.sqrt(2)), (1, -1, math.sqrt(2)),
        (-1, 1, math.sqrt(2)), (1, 1, math.sqrt(2)),
    ]

    visited = set()
    max_iterations = 5000  # защита от зацикливания
    iterations = 0

    while open_set:
        iterations += 1
        if iterations > max_iterations:
            return None

        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        # Дошли до цели
        if current == goal:
            return _reconstruct_path(came_from, current, tile_size)

        cx, cy = current
        for dx, dy, cost in neighbors:
            nx, ny = cx + dx, cy + dy

            # За пределами карты
            if nx < 0 or ny < 0 or nx >= tilemap.width or ny >= tilemap.height:
                continue

            # Непроходимый тайл
            wx, wy = tile_to_world_center(nx, ny, tile_size)
            if not tilemap.is_walkable_world(wx, wy):
                continue

            # Диагональный ход: проверяем, что оба «соседа по сторонам» проходимы
            # (иначе юнит «срежет угол» сквозь стену)
            if dx != 0 and dy != 0:
                wx1, wy1 = tile_to_world_center(cx + dx, cy, tile_size)
                wx2, wy2 = tile_to_world_center(cx, cy + dy, tile_size)
                if not tilemap.is_walkable_world(wx1, wy1):
                    continue
                if not tilemap.is_walkable_world(wx2, wy2):
                    continue

            neighbor = (nx, ny)
            tentative_g = g_score[current] + cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))

    # Путь не найден
    return None


def _reconstruct_path(came_from, current, tile_size):
    """Восстанавливает путь от старта к цели."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()

    # Преобразуем тайлы в мировые центры
    return [tile_to_world_center(tx, ty, tile_size) for tx, ty in path]


def _find_nearest_walkable(tilemap, tile, tile_size, max_radius=5):
    """Ищет ближайший проходимый тайл вокруг заданного (для случая, если цель в стене)."""
    tx, ty = tile
    for r in range(1, max_radius + 1):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if abs(dx) != r and abs(dy) != r:
                    continue  # только «кольцо» радиуса r
                nx, ny = tx + dx, ty + dy
                if nx < 0 or ny < 0 or nx >= tilemap.width or ny >= tilemap.height:
                    continue
                wx, wy = tile_to_world_center(nx, ny, tile_size)
                if tilemap.is_walkable_world(wx, wy):
                    return (nx, ny)
    return None


def smooth_path(path):
    """
    Простое сглаживание: если между двумя точками можно провести прямую
    (без препятствий), убираем промежуточные.
    Пока без проверки препятствий — минимальный вариант.
    """
    if not path or len(path) < 3:
        return path

    smoothed = [path[0]]
    for i in range(1, len(path) - 1):
        # Оставляем точки на «поворотах» (где меняется направление)
        prev = smoothed[-1]
        nxt = path[i + 1]
        # Вектор prev→path[i] и path[i]→nxt
        v1x = path[i][0] - prev[0]
        v1y = path[i][1] - prev[1]
        v2x = nxt[0] - path[i][0]
        v2y = nxt[1] - path[i][1]
        # Если направление изменилось — точка важная
        if abs(v1x - v2x) > 1 or abs(v1y - v2y) > 1:
            smoothed.append(path[i])
    smoothed.append(path[-1])
    return smoothed