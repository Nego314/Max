"""
Поиск стартовых позиций для баз (игрока и врагов).
"""
import random

import numpy as np

from settings import (
    BASE_PLATFORM_SIZE, BASE_MIN_DISTANCE,
    BASE_RESOURCE_RADIUS, BASE_SEARCH_ATTEMPTS,
    TILE_REGOLITH, TILE_ICE, TILE_ILMENITE, TILE_ANORTHOSITE,
)

def _check_platform(tiles, cx, cy, size):
    """
    Проверяет, что площадка size × size вокруг (cx, cy)
    состоит из «строительных» тайлов: реголит, пыль, кратер.
    """
    from settings import TILE_DUST, TILE_CRATER

    h, w = tiles.shape
    half = size // 2
    x1 = cx - half
    x2 = cx + half + (size % 2)
    y1 = cy - half
    y2 = cy + half + (size % 2)

    if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
        return False

    sub = tiles[y1:y2, x1:x2]

    # Разрешённые тайлы
    allowed = (sub == TILE_REGOLITH) | (sub == TILE_DUST) | (sub == TILE_CRATER)
    return bool(np.all(allowed))

def _check_resources_nearby(tiles, cx, cy, radius):
    """
    Проверяет, что в радиусе radius клеток есть лёд и хотя бы один минерал.
    """
    h, w = tiles.shape
    x1 = max(0, cx - radius)
    x2 = min(w, cx + radius + 1)
    y1 = max(0, cy - radius)
    y2 = min(h, cy + radius + 1)

    sub = tiles[y1:y2, x1:x2]

    has_ice = bool(np.any(sub == TILE_ICE))
    has_ilmenite = bool(np.any(sub == TILE_ILMENITE))
    has_anorthosite = bool(np.any(sub == TILE_ANORTHOSITE))

    return has_ice and (has_ilmenite or has_anorthosite)


def _far_enough(cx, cy, existing, min_dist):
    """Проверяет, что точка далеко от всех существующих баз."""
    for (bx, by) in existing:
        dx = bx - cx
        dy = by - cy
        if dx * dx + dy * dy < min_dist * min_dist:
            return False
    return True


def find_base_location(tiles, existing_bases, rng):
    """
    Ищет одну стартовую позицию для базы.
    Возвращает (cx, cy) или None.

    Условия:
      - площадка BASE_PLATFORM_SIZE × BASE_PLATFORM_SIZE из реголита;
      - в радиусе BASE_RESOURCE_RADIUS есть лёд + минерал;
      - расстояние до всех existing_bases >= BASE_MIN_DISTANCE.
    """
    h, w = tiles.shape
    half = BASE_PLATFORM_SIZE // 2 + 1   # небольшой отступ от края карты

    # Этап 1: строгий поиск
    for attempt in range(BASE_SEARCH_ATTEMPTS):
        cx = rng.integers(half, w - half)
        cy = rng.integers(half, h - half)

        if not _far_enough(cx, cy, existing_bases, BASE_MIN_DISTANCE):
            continue

        if not _check_platform(tiles, cx, cy, BASE_PLATFORM_SIZE):
            continue

        if not _check_resources_nearby(tiles, cx, cy, BASE_RESOURCE_RADIUS):
            continue

        print(f"[Spawn] Найдена база за {attempt+1} попыток: ({cx}, {cy})")
        return (int(cx), int(cy))

    # Этап 2: ослабленные условия — без проверки ресурсов
    print("[Spawn] Не нашли идеальную базу — ослабляю условия")
    for attempt in range(BASE_SEARCH_ATTEMPTS):
        cx = rng.integers(half, w - half)
        cy = rng.integers(half, h - half)

        if not _far_enough(cx, cy, existing_bases, BASE_MIN_DISTANCE):
            continue

        if not _check_platform(tiles, cx, cy, BASE_PLATFORM_SIZE):
            continue

        print(f"[Spawn] Найдена база (ослабленные условия): ({cx}, {cy})")
        return (int(cx), int(cy))

    # Этап 3: совсем отчаянный поиск — только далеко
    print("[Spawn] Совсем не нашли — ещё ослабляю")
    for attempt in range(BASE_SEARCH_ATTEMPTS):
        cx = rng.integers(half, w - half)
        cy = rng.integers(half, h - half)

        if not _far_enough(cx, cy, existing_bases, BASE_MIN_DISTANCE // 2):
            continue

        print(f"[Spawn] Найдена база (отчаянно): ({cx}, {cy})")
        return (int(cx), int(cy))

    print("[Spawn] Не удалось найти базу совсем")
    return None


def find_all_base_locations(tiles, count, seed=42):
    """
    Ищет count баз.
    Возвращает список (cx, cy).
    """
    rng = np.random.default_rng(seed)
    bases = []

    for i in range(count):
        loc = find_base_location(tiles, bases, rng)
        if loc is None:
            print(f"[Spawn] Не смог найти базу #{i+1}")
            break
        bases.append(loc)

    return bases