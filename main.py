import pygame
import sys

import settings
from settings import (
    FPS, COLOR_BG, COLOR_TEXT,
    TILE_SIZE, FORMATION_SEARCH_RADIUS, SCREEN_MODE,
    UI_PANEL_WIDTH, SELECT_RECT_THICKNESS, DEBUG_FONT_SIZE,
)
from ui import UI
from settings import SELECT_RECT_THICKNESS
from tilemap import TileMap
from camera import Camera
from unit import Unit
from world import World
from fog import Fog

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
    """Создаём мир с юнитами."""
    world = World(tilemap)

    # Наши — синие
    player_tiles = [(10, 10), (11, 10), (12, 10), (10, 11), (11, 11)]
    for (tx, ty) in player_tiles:
        world.add_unit(Unit(tx, ty, team="player", unit_type="geologist"))

    # Враги — красные
    enemy_tiles = [(25, 15), (26, 15), (25, 16)]
    for (tx, ty) in enemy_tiles:
        world.add_unit(Unit(tx, ty, team="enemy", unit_type="soldier"))

    return world


def order_group_move(world, selected_units, click_tile):
    """
    Приказ группы на движение к click_tile с сохранением формации.
    Верхний левый юнит в группе встаёт в click_tile.
    Остальные сохраняют относительное положение.
    """
    if not selected_units:
        return

    # Находим верхний левый юнит (минимальные tile_y, tile_x)
    anchor = min(selected_units, key=lambda u: (u.tile_y, u.tile_x))

    # Относительные смещения от anchor
    offsets = {}
    for u in selected_units:
        offsets[u] = (u.tile_x - anchor.tile_x, u.tile_y - anchor.tile_y)

    # Идеальная целевая клетка для каждого
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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Клик по миникарте — телепорт камеры
                if ui.minimap.contains_point(event.pos):
                    wx, wy = ui.minimap.screen_to_world(*event.pos)
                    camera.move_to(wx, wy)
                    continue

                if ui.is_over_ui(event.pos):
                    continue  # клик по панели — игнорируем
                mx, my = event.pos
                wx, wy = camera.screen_to_world(mx, my)

                clicked = None
                for u in world.units:
                    if u.team == "player" and u.contains_point(wx, wy):
                        clicked = u
                        break

                shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT

                if clicked is not None:
                    if not shift_held:
                        for u in world.units:
                            u.selected = False
                    clicked.selected = (not clicked.selected) if shift_held else True
                else:
                    dragging = True
                    drag_start = (mx, my)
                    drag_end = (mx, my)
                    if not shift_held:
                        for u in world.units:
                            u.selected = False

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    dragging = False

                    x1, y1 = drag_start
                    x2, y2 = drag_end
                    rx1, ry1 = min(x1, x2), min(y1, y2)
                    rx2, ry2 = max(x1, x2), max(y1, y2)

                    # Слишком маленькая рамка = просто клик, ничего не делаем
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

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    drag_end = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if ui.is_over_ui(event.pos):
                    continue
                mx, my = event.pos
                click_tile = screen_to_tile(camera, mx, my)

                selected = [u for u in world.units
                            if u.selected and u.team == "player"]

                # Клик по непроходимой клетке — приказ не проходит
                if not world.is_tile_walkable(*click_tile):
                    continue

                # Клик по клетке с врагом — приказ не проходит
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

        for u in world.units:
            u.update(dt, world)

        # --- Отрисовка ---
        screen.fill(COLOR_BG)

        # Рисуем тайлы только в области viewport
        screen.set_clip(ui.viewport)
        cam_x, cam_y = camera.offset
        tilemap.draw(screen, cam_x, cam_y)
        for u in world.units:
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
        ui.draw(camera, pygame.mouse.get_pos(), world)
        ui.draw(camera, mouse_pos, world)

        # Debug
        selected_count = sum(1 for u in world.units
                             if u.selected and u.team == "player")
        debug = font.render(
            f"FPS: {int(clock.get_fps())}  Selected: {selected_count}  "
            f"Units: {len(world.units)}",
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