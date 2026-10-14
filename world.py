"""
Игровой мир: карта, юниты, занятость клеток.
"""


class World:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.units = []
        self.buildings = []
        # Словарь: (tile_x, tile_y) -> unit или None.
        # Заполняется при спавне юнита и обновляется при движении.
        self.occupied = {}

    # --- Юниты ---

    def add_unit(self, unit):
        """
        Добавить юнита в мир.
        Если его стартовая клетка занята или непроходима — молча
        переносим на ближайшую свободную в радиусе FORMATION_SEARCH_RADIUS.
        """
        # Проверяем стартовую клетку
        if not self.is_tile_free(unit.tile_x, unit.tile_y, ignore_unit=unit):
            # Ищем ближайшую свободную
            free = self.find_nearest_free_tile(
                unit.tile_x, unit.tile_y,
                self._spawn_search_radius(),
                ignore_unit=unit,
            )
            if free is not None:
                # Молча переносим юнита
                unit.tile_x, unit.tile_y = free
                unit.x, unit.y = unit._tile_center(free[0], free[1])

        # Добавляем
        self.units.append(unit)
        self.occupied[(unit.tile_x, unit.tile_y)] = unit

    def _spawn_search_radius(self):
        """Радиус поиска свободной клетки при спавне."""
        from settings import FORMATION_SEARCH_RADIUS
        return FORMATION_SEARCH_RADIUS

    def remove_unit(self, unit):
        """Убрать юнита (смерть, выход)."""
        if unit in self.units:
            self.units.remove(unit)
        key = (unit.tile_x, unit.tile_y)
        if self.occupied.get(key) is unit:
            del self.occupied[key]

    def unit_at(self, tile_x, tile_y):
        """Юнит на клетке или None."""
        return self.occupied.get((tile_x, tile_y))

    def move_unit_on_grid(self, unit, new_tx, new_ty):
        """
        Обновляет запись в occupied при переходе юнита между клетками.
        Проверяет, что:
          - юнит действительно владеет старой клеткой (иначе — рассинхрон);
          - новая клетка не занята другим юнитом;
          - новая клетка проходима.
        Если проверки не проходят — ничего не меняем (юнит остаётся на месте).
        """
        old_key = (unit.tile_x, unit.tile_y)
        new_key = (new_tx, new_ty)

        # Проверка 1: юнит должен владеть своей старой клеткой
        if self.occupied.get(old_key) is not unit:
            # Рассинхрон: occupied не знает про этого юнита на этой клетке.
            # Исправляем: удаляем любую запись на old_key и ставим юнита обратно.
            if old_key in self.occupied:
                del self.occupied[old_key]
            self.occupied[old_key] = unit
            # Всё равно не двигаем — сначала пусть мир придёт в согласованное состояние
            return False

        # Проверка 2: новая клетка в границах
        if new_tx < 0 or new_ty < 0 \
           or new_tx >= self.tilemap.width or new_ty >= self.tilemap.height:
            return False

        # Проверка 3: новая клетка проходима
        if not self.is_tile_walkable(new_tx, new_ty):
            return False

        # Проверка 4: новая клетка не занята другим юнитом
        occupant = self.occupied.get(new_key)
        if occupant is not None and occupant is not unit:
            return False

        # Все проверки пройдены — перемещаем
        del self.occupied[old_key]
        unit.tile_x = new_tx
        unit.tile_y = new_ty
        self.occupied[new_key] = unit
        return True

    # --- Проверки клеток ---

    def is_tile_walkable(self, tx, ty):
        """Проходима ли клетка по типу местности (без учёта юнитов)."""
        if tx < 0 or ty < 0 or tx >= self.tilemap.width or ty >= self.tilemap.height:
            return False
        tile_type = int(self.tilemap.tiles[ty, tx])
        from settings import WALKABLE_TILES
        return WALKABLE_TILES.get(tile_type, False)

    def is_tile_free(self, tx, ty, for_team=None, ignore_unit=None):
        """
        Свободна ли клетка: проходима И не занята юнитом.
        Параметры:
          for_team — если задан, клетки врагов считаются занятыми (нельзя вставать)
          ignore_unit — юнит, которого игнорируем (обычно сам движущийся)
        """
        if not self.is_tile_walkable(tx, ty):
            return False

        occupant = self.occupied.get((tx, ty))
        if occupant is None or occupant is ignore_unit:
            return True

        # Клетка занята. Если указана команда — юниты других команд всегда блокируют.
        # Свои юниты тоже блокируют, но приказы строятся с их учётом.
        return False

    def find_nearest_free_tile(self, tx, ty, radius, for_team=None, ignore_unit=None):
        """
        Ищет ближайшую свободную клетку в квадрате (2*radius+1)x(2*radius+1).
        Возвращает (x, y) или None.
        """
        if self.is_tile_free(tx, ty, for_team, ignore_unit):
            return (tx, ty)

        # Ищем по «кольцам» радиуса 1, 2, 3...
        for r in range(1, radius + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) != r and abs(dy) != r:
                        continue
                    nx, ny = tx + dx, ty + dy
                    if self.is_tile_free(nx, ny, for_team, ignore_unit):
                        return (nx, ny)
        return None

    def reserve_tile(self, unit, tx, ty):
        """
        Бронирует клетку (tx, ty) за юнитом, не перемещая его туда физически.
        Если клетка уже занята кем-то другим — возвращает False.
        """
        key = (tx, ty)
        occupant = self.occupied.get(key)
        if occupant is not None and occupant is not unit:
            return False

        self.occupied[key] = unit
        return True

    def release_tile(self, unit, tx, ty):
        """Снимает бронь с клетки, если она принадлежит юниту."""
        key = (tx, ty)
        if self.occupied.get(key) is unit:
            del self.occupied[key]

    def release_all_except_current(self, unit):
        """
        Снимает все брони юнита, кроме его текущей клетки (tile_x, tile_y).
        Полезно при отмене пути или переприказе.
        """
        current_key = (unit.tile_x, unit.tile_y)
        to_release = []
        for key, u in self.occupied.items():
            if u is unit and key != current_key:
                to_release.append(key)
        for key in to_release:
            del self.occupied[key]

    # --- Здания ---

    def add_building(self, building):
        """
        Добавляет здание в мир.
        Занимает все свои клетки в occupied.
        """
        self.buildings.append(building)

        # Занимаем все клетки здания
        for (tx, ty) in building.get_occupied_tiles():
            self.occupied[(tx, ty)] = building

    def building_at(self, tx, ty):
        """Здание, занимающее клетку (tx, ty), или None."""
        obj = self.occupied.get((tx, ty))
        if obj is not None and hasattr(obj, "get_occupied_tiles"):
            return obj
        return None

    def can_place_building(self, building, ignore_walls=False):
        """
        Проверяет, можно ли поставить здание в его текущем положении.
        Все клетки должны быть:
          - в границах карты,
          - проходимы по типу местности,
          - не заняты другим юнитом или зданием.
        """
        for (tx, ty) in building.get_occupied_tiles():
            # Границы карты
            if tx < 0 or ty < 0 or tx >= self.tilemap.width or ty >= self.tilemap.height:
                return False
            # Тип местности
            if not self.is_tile_walkable(tx, ty):
                return False
            # Занятость
            if (tx, ty) in self.occupied:
                return False
        return True