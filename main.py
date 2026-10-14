import pygame
import sys

import settings
from settings import (
    FPS, COLOR_BG, COLOR_TEXT,
    TILE_SIZE, FORMATION_SEARCH_RADIUS, SCREEN_MODE,
    UI_PANEL_WIDTH, SELECT_RECT_THICKNESS, DEBUG_FONT_SIZE,
)
from ui import UI
from tilemap import TileMap
from camera import Camera
from unit import Unit
from world import World
from fog import Fog
from spawn import find_all_base_locations
from settings import START_UNIT_TYPES
from building import Building
from settings import BUILDING_TYPES


# --- Инициализация Pygame ---
pygame.init()

if SCREEN_MODE == "fullscreen":
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        pygame.SCALED | pygame.FULLSCREEN,
    )
elif SCREEN_MODE == "window":
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )

pygame.display.set_caption("MyRTS — прототип")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", DEBUG_FONT_SIZE)


def screen_to_tile(camera, mx, my):
    """Экранные пиксели → координаты клетки."""
    wx, wy = camera.screen_to_world(mx, my)
    return int(wx // TILE_SIZE), int(wy // TILE_SIZE)


def create_world(tilemap):
    """Создаём мир: ищем базы, ставим здание, спавним юнитов."""
    world = World(tilemap)

    base_locations = find_all_base_locations(
        tilemap.tiles, count=4, seed=settings.MAP_SEED
    )

    if not base_locations:
        print("[ERROR] Не удалось найти базы")
        return world

    for i, (bx, by) in enumerate(base_locations):
        team = "player" if i == 0 else "enemy"

        size = BUILDING_TYPES["habitat"]["size"]
        half = size // 2
        bld = Building(bx - half, by - half, building_type="habitat", team=team)

        if not world.can_place_building(bld):
            print(f"[World] Не могу поставить здание в {bx},{by} для {team}")
            placed = False
            for (dx, dy) in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
                bld.tile_x = bx - half + dx
                bld.tile_y = by - half + dy
                if world.can_place_building(bld):
                    placed = True
                    break
            if not placed:
                print(f"[World] Не смог поставить здание для {team}, пропускаю")
                continue

        world.add_building(bld)
        print(f"[World] Здание ({team}) поставлено в ({bld.tile_x}, {bld.tile_y})")

        _spawn_units_for_base(world, (bx, by), team, exclude=bld.get_occupied_tiles())

    world.base_locations = base_locations
    return world


def _spawn_units_for_base(world, base_pos, team, exclude=None):
    """Спавнит юнитов рядом с базой, не на клетках здания."""
    bx, by = base_pos
    exclude = set(exclude) if exclude else set()

    offsets = [
        (-3, 0), (-2, 0), (-1, 0), (2, 0), (3, 0), (0, -3), (0, -2),
        (0, 2), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2),
    ]

    spawned = 0
    for (dx, dy) in offsets:
        if spawned >= len(START_UNIT_TYPES):
            break

        tx = bx + dx
        ty = by + dy

        if (tx, ty) in exclude:
            continue

        if not world.is_tile_free(tx, ty):
            continue

        unit_type = START_UNIT_TYPES[spawned]
        u = Unit(tx, ty, team=team, unit_type=unit_type)
        world.add_unit(u)
        spawned += 1

    if spawned < len(START_UNIT_TYPES):
        print(f"[World] Заспавнено юнитов для {team}: {spawned}/{len(START_UNIT_TYPES)}")


def order_group_move(world, selected_units, click_tile):
    """Приказ группы на движение с сохранением формации."""
    if not selected_units:
        return

    anchor = min(selected_units, key=lambda u: (u.tile_y, u.tile_x))
    offsets = {}
    for u in selected_units:
        offsets[u] = (u.tile_x - anchor.tile_x, u.tile_y - anchor.tile_y)

    for u in selected_units:
        dx, dy = offsets[u]
        want_x = click_tile[0] + dx
        want_y = click_tile[1] + dy

        if world.is_tile_free(want_x, want_y, ignore_unit=u):
            goal = (want_x, want_y)
        else:
            goal = world.find_nearest_free_tile(
                want_x, want_y, FORMATION_SEARCH_RADIUS, ignore_unit=u
            )

        if goal is None:
            u.goal_tile = None
            u.path = []
            continue

        u.order_move_to_tile(world, goal)


def order_single_move(world, unit, click_tile):
    """Приказ одиночному юниту: встать в клик-клетку или рядом."""
    if world.is_tile_free(click_tile[0], click_tile[1], ignore_unit=unit):
        goal = click_tile
    else:
        goal = world.find_nearest_free_tile(
            click_tile[0], click_tile[1],
            FORMATION_SEARCH_RADIUS, ignore_unit=unit
        )
        if goal is None:
            unit.goal_tile = None
            unit.path = []
            return
    unit.order_move_to_tile(world, goal)


def main():
    tilemap = TileMap()
    camera = Camera()
    world = create_world(tilemap)
    ui = UI(screen, tilemap)
    fog = Fog(tilemap.width, tilemap.height)

    dragging = False
    drag_start = (0, 0)
    drag_end = (0, 0)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- События ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # --- ЛКМ ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Кнопка переключения режима миникарты
                if ui.minimap.button_contains_point(event.pos):
                    ui.minimap.handle_click(event.pos)
                    continue

                # Клик по миникарте — телепорт камеры
                if ui.minimap.contains_point(event.pos):
                    wx, wy = ui.minimap.screen_to_world(*event.pos)
                    camera.move_to(wx, wy)
                    continue

                # Клик по UI — игнорируем
                if ui.is_over_ui(event.pos):
                    continue

                # Клик по игровому полю — выделение
                mx, my = event.pos
                wx, wy = camera.screen_to_world(mx, my)

                shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT

                # 1. Сначала проверяем клик по зданию
                clicked_building = None
                for b in world.buildings:
                    if b.team == "player" and b.contains_point(wx, wy):
                        clicked_building = b
                        break

                if clicked_building is not None:
                    if not shift_held:
                        for b in world.buildings:
                            b.selected = False
                        for u in world.units:
                            u.selected = False
                    clicked_building.selected = True
                    continue

                # 2. Проверяем клик по юниту
                clicked_unit = None
                for u in world.units:
                    if u.team == "player" and u.contains_point(wx, wy):
                        clicked_unit = u
                        break

                if clicked_unit is not None:
                    if not shift_held:
                        for u in world.units:
                            u.selected = False
                        for b in world.buildings:
                            b.selected = False
                    clicked_unit.selected = (not clicked_unit.selected) if shift_held else True
                else:
                    # 3. Клик по пустому месту — начало drag
                    dragging = True
                    drag_start = (mx, my)
                    drag_end = (mx, my)
                    if not shift_held:
                        for u in world.units:
                            u.selected = False
                        for b in world.buildings:
                            b.selected = False

            # --- Отпускание ЛКМ (конец drag) ---
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    dragging = False

                    x1, y1 = drag_start
                    x2, y2 = drag_end
                    rx1, ry1 = min(x1, x2), min(y1, y2)
                    rx2, ry2 = max(x1, x2), max(y1, y2)

                    if (rx2 - rx1) < 5 and (ry2 - ry1) < 5:
                        pass
                    else:
                        wx1, wy1 = camera.screen_to_world(rx1, ry1)
                        wx2, wy2 = camera.screen_to_world(rx2, ry2)

                        for u in world.units:
                            if u.team != "player":
                                continue
                            if wx1 <= u.x <= wx2 and wy1 <= u.y <= wy2:
                                u.selected = True

            # --- Движение мыши (обновление рамки) ---
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    drag_end = event.pos

            # --- ПКМ (приказ) ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if ui.is_over_ui(event.pos):
                    continue
                mx, my = event.pos
                click_tile = screen_to_tile(camera, mx, my)

                selected = [u for u in world.units
                            if u.selected and u.team == "player"]

                if not world.is_tile_walkable(*click_tile):
                    continue

                occupant = world.unit_at(*click_tile)
                if occupant is not None and occupant.team != "player":
                    continue

                if len(selected) == 1:
                    order_single_move(world, selected[0], click_tile)
                elif len(selected) > 1:
                    order_group_move(world, selected, click_tile)

        # --- Логика ---
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        camera.update(dt, keys, mouse_pos)

        # Все юниты обновляются, даже скрытые
        for u in world.units:
            u.update(dt, world)

        # --- Отрисовка ---
        screen.fill(COLOR_BG)

        # Рисуем тайлы только в области viewport
        screen.set_clip(ui.viewport)
        cam_x, cam_y = camera.offset
        tilemap.draw(screen, cam_x, cam_y)

        # Отрисовка зданий (под юнитами)
        for b in world.buildings:
            if b.team == "player" or fog.is_visible(b.tile_x, b.tile_y):
                b.draw(screen, camera)

        # Отрисовка юнитов
        for u in world.units:
            if u.team == "player" or fog.is_visible(u.tile_x, u.tile_y):
                u.draw(screen, camera)

        fog.update(world)

        # Туман поверх карты и юнитов
        fog.draw(screen, camera)

        screen.set_clip(None)

        # Рамка выделения — рисуем поверх поля
        if dragging:
            x1, y1 = drag_start
            x2, y2 = drag_end
            rx, ry = min(x1, x2), min(y1, y2)
            rw, rh = abs(x2 - x1), abs(y2 - y1)
            pygame.draw.rect(
                screen, (255, 230, 80),
                (rx, ry, rw, rh), SELECT_RECT_THICKNESS
            )

        # UI поверх всего
        mouse_pos = pygame.mouse.get_pos()
        ui.draw(camera, mouse_pos, world, fog)

        # Debug
        selected_count = sum(1 for u in world.units
                             if u.selected and u.team == "player")
        debug = font.render(
            f"FPS: {int(clock.get_fps())}  Selected: {selected_count}  "
            f"Units: {len(world.units)}  Buildings: {len(world.buildings)}",
            True, COLOR_TEXT,
        )
        screen.blit(debug, (ui.viewport.x + 10, 10))

        hint = font.render(
            "LMB - select, RMB - move, ESC - exit",
            True, COLOR_TEXT,
        )
        screen.blit(hint, (ui.viewport.x + 10, 35))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()