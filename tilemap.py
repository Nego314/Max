"""
Карта Луны: генерация через процедурный шум + сохранение в файл.
"""
import os
import random

import numpy as np
import pygame
from perlin_noise import PerlinNoise

from settings import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT,
    TILE_REGOLITH, TILE_DUST, TILE_ROCK, TILE_CRATER,
    TILE_ICE, TILE_ILMENITE, TILE_ANORTHOSITE,
    TILE_COLORS, SHOW_GRID,
    MAP_SEED, MAP_SAVE_PATH,
    NOISE_SCALE_BASE, NOISE_SCALE_DETAIL,
    NOISE_SCALE_ROCK, NOISE_SCALE_DUST,
    THRESHOLD_DUST, THRESHOLD_ROCK, THRESHOLD_RESOURCE,
    DENSITY_ICE, DENSITY_ILMENITE, DENSITY_ANORTHOSITE,
    CRATER_COUNT, CRATER_MIN_RADIUS, CRATER_MAX_RADIUS,
)


class TileMap:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height

        # Пробуем загрузить карту из кэша
        loaded = self._try_load()
        if loaded is None:
            # Генерируем
            self.tiles = self._generate()
            self._save()
        else:
            self.tiles = loaded

    # --- Сохранение / загрузка ---

    def _cache_path(self):
        """Путь к файлу кэша карты (с учётом seed и размера)."""
        if not os.path.exists(MAP_SAVE_PATH):
            os.makedirs(MAP_SAVE_PATH, exist_ok=True)
        filename = f"map_{self.width}x{self.height}_seed{MAP_SEED}.npy"
        return os.path.join(MAP_SAVE_PATH, filename)

    def _try_load(self):
        path = self._cache_path()
        if not os.path.exists(path):
            return None
        print(f"[TileMap] Загружаю карту из {path}")
        return np.load(path)

    def _save(self):
        path = self._cache_path()
        np.save(path, self.tiles)
        print(f"[TileMap] Карта сохранена в {path}")

    # --- Генерация ---

    def _generate(self):
        """
        Генерация карты Луны через многослойный шум.
        Возвращает numpy-массив формы (height, width), dtype=int8.
        """
        print(f"[TileMap] Генерирую карту {self.width}×{self.height} (seed={MAP_SEED})...")

        w, h = self.width, self.height
        rng = np.random.default_rng(MAP_SEED)

        # --- 1. Базовый шум: определяет "реголит vs пыль" ---
        base_noise = self._generate_noise(
            w, h, NOISE_SCALE_BASE, octaves=4, seed=MAP_SEED
        )

        # --- 2. Шум для скал ---
        rock_noise = self._generate_noise(
            w, h, NOISE_SCALE_ROCK, octaves=3, seed=MAP_SEED + 1
        )

        # --- 3. Начинаем с реголита везде ---
        tiles = np.full((h, w), TILE_REGOLITH, dtype=np.int8)

        # --- 4. Пылевые моря (большие области) ---
        dust_mask = base_noise > THRESHOLD_DUST
        tiles[dust_mask] = TILE_DUST

        # --- 5. Скалы ---
        rock_mask = rock_noise > THRESHOLD_ROCK
        tiles[rock_mask] = TILE_ROCK

        # --- 6. Кратеры (круглые впадины) ---
        self._add_craters(tiles, rng)

        # --- 7. Ресурсы ---
        # Лёд — в кратерах
        self._add_resource_in_region(
            tiles, rng, region_mask=(tiles == TILE_CRATER),
            resource=TILE_ICE, density=DENSITY_ICE
        )

        # Ильменит — в реголите И пыли
        ilmenite_region = (tiles == TILE_REGOLITH) | (tiles == TILE_DUST)
        self._add_resource_in_region(
            tiles, rng, region_mask=ilmenite_region,
            resource=TILE_ILMENITE, density=DENSITY_ILMENITE
        )

        # Анортозит — в реголите И пыли
        anorth_region = (tiles == TILE_REGOLITH) | (tiles == TILE_DUST)
        self._add_resource_in_region(
            tiles, rng, region_mask=anorth_region,
            resource=TILE_ANORTHOSITE, density=DENSITY_ANORTHOSITE
        )

        print(f"[TileMap] Готово.")
        return tiles

    def _generate_noise(self, w, h, scale, octaves=1, seed=0):
        """
        Генерирует шумовое поле size (h, w) через perlin-noise.
        Генерируем на маленькой сетке и масштабируем через numpy.
        """
        step = 24
        small_w = max(2, w // step)
        small_h = max(2, h // step)

        # Создаём PerlinNoise с нужным seed
        noise_gen = PerlinNoise(octaves=octaves, seed=seed)

        small = np.zeros((small_h, small_w), dtype=np.float32)
        for y in range(small_h):
            for x in range(small_w):
                small[y, x] = noise_gen([x * step * scale, y * step * scale])

        # Нормализация по факту (у perlin-noise диапазон не фиксирован)
        s_min = float(small.min())
        s_max = float(small.max())
        if s_max - s_min > 1e-6:
            small = (small - s_min) / (s_max - s_min)
        else:
            small = np.zeros_like(small)

        # Отладка
        print(f"[noise] scale={scale:.4f} step={step} octaves={octaves} seed={seed} "
              f"min={small.min():.3f} max={small.max():.3f} mean={small.mean():.3f}")

        # Масштабирование до полного размера
        big = np.repeat(np.repeat(small, step, axis=0), step, axis=1)
        big = big[:h, :w]

        if big.shape != (h, w):
            padded = np.zeros((h, w), dtype=np.float32)
            padded[:big.shape[0], :big.shape[1]] = big
            big = padded

        return big

    def _add_craters(self, tiles, rng):
        """Добавляет круглые кратеры по всей карте."""
        h, w = tiles.shape
        for _ in range(CRATER_COUNT):
            cx = rng.integers(0, w)
            cy = rng.integers(0, h)
            radius = rng.integers(CRATER_MIN_RADIUS, CRATER_MAX_RADIUS)

            y1 = max(0, cy - radius)
            y2 = min(h, cy + radius + 1)
            x1 = max(0, cx - radius)
            x2 = min(w, cx + radius + 1)

            if y2 <= y1 or x2 <= x1:
                continue

            yy, xx = np.ogrid[y1:y2, x1:x2]
            dist_sq = (yy - cy) ** 2 + (xx - cx) ** 2
            mask = dist_sq <= radius ** 2

            # Внутри кратера — меняем на TILE_CRATER
            sub = tiles[y1:y2, x1:x2]
            sub[mask] = TILE_CRATER

    def _add_resource_in_region(self, tiles, rng, region_mask, resource, density):
        """Разбрасывает ресурс в регионе с заданной плотностью."""
        if density <= 0:
            return
        random_mask = rng.random(tiles.shape) < density
        mask = region_mask & random_mask
        tiles[mask] = resource

    # --- Отрисовка ---

    def draw(self, surface, camera_x=0, camera_y=0):
        """Рисует видимые тайлы через pygame.surfarray (быстро)."""
        screen_w, screen_h = surface.get_size()

        start_x = max(0, camera_x // TILE_SIZE)
        start_y = max(0, camera_y // TILE_SIZE)
        end_x = min(self.width, (camera_x + screen_w) // TILE_SIZE + 2)
        end_y = min(self.height, (camera_y + screen_h) // TILE_SIZE + 2)

        # Если регион пустой — выходим
        if end_x <= start_x or end_y <= start_y:
            return

        # Срез тайлов на видимой области (numpy)
        sub = self.tiles[start_y:end_y, start_x:end_x]   # (H, W)

        # Преобразуем индексы тайлов в RGB через таблицу
        max_tile = max(TILE_COLORS.keys()) + 1
        lut = np.zeros((max_tile, 3), dtype=np.uint8)
        for k, v in TILE_COLORS.items():
            lut[k] = v
        rgb = lut[sub]   # (H, W, 3)

        # Масштабируем: каждая клетка = TILE_SIZE × TILE_SIZE пикселей
        # np.kron — быстрое «размножение» массива
        big = np.kron(rgb, np.ones((TILE_SIZE, TILE_SIZE, 1), dtype=np.uint8))

        # Отрисовываем как Surface
        sub_h, sub_w = big.shape[:2]

        # Экранные координаты верхнего левого угла этого региона
        screen_x = start_x * TILE_SIZE - camera_x
        screen_y = start_y * TILE_SIZE - camera_y

        # Создаём pygame.Surface из numpy
        # pygame.surfarray ожидает форму (W, H, 3) → транспонируем
        big_wh = np.transpose(big, (1, 0, 2))
        sub_surface = pygame.Surface((sub_w, sub_h))
        pygame.surfarray.blit_array(sub_surface, big_wh)

        # Блитим на экран
        surface.blit(sub_surface, (screen_x, screen_y))

    # --- Проверки ---

    def is_walkable_world(self, world_x, world_y):
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return False

        tile_type = int(self.tiles[tile_y, tile_x])
        from settings import WALKABLE_TILES
        return WALKABLE_TILES.get(tile_type, False)

    def is_walkable_circle(self, world_x, world_y, radius):
        """Проверка круга на проходимость (для юнитов)."""
        import math

        if not self.is_walkable_world(world_x, world_y):
            return False

        for i in range(8):
            angle = i * math.pi / 4
            px = world_x + math.cos(angle) * radius
            py = world_y + math.sin(angle) * radius
            if not self.is_walkable_world(px, py):
                return False
        return True