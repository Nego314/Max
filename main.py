import math
import pygame
import sys

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_TEXT
from tilemap import TileMap
from camera import Camera
#from unit import Unit
from unit import Unit, resolve_unit_collisions


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MyRTS — прототип")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)


def create_units():
    """Создаём группу наших юнитов и пару врагов."""
    units = []

    # Наши — синие
    for i in range(5):
        units.append(Unit(
            x=10 * 64 + 32 + i * 50,
            y=10 * 64 + 32,
            color=(80, 160, 255),
            team="player",
        ))

    # Враги — красные (пока просто стоят)
    for i in range(3):
        units.append(Unit(
            x=25 * 64 + 32 + i * 50,
            y=15 * 64 + 32,
            color=(220, 70, 70),
            team="enemy",
        ))

    return units


def main():
    tilemap = TileMap()
    camera = Camera()
    units = create_units()

    # Рамка выделения (drag-box)
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

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            # ЛКМ — старт выделения или клик
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                world_x, world_y = camera.screen_to_world(mx, my)

                # Ищем юнита под курсором (только наших)
                clicked_unit = None
                for u in units:
                    if u.team == "player" and u.contains_point(world_x, world_y):
                        clicked_unit = u
                        break

                shift_held = pygame.key.get_mods() & pygame.KMOD_SHIFT

                if clicked_unit is not None:
                    # Клик по юниту — выделяем его
                    if not shift_held:
                        for u in units:
                            u.selected = False
                    clicked_unit.selected = not clicked_unit.selected \
                        if shift_held else True
                else:
                    # Клик по пустому месту — начинаем рамку
                    dragging = True
                    drag_start = (mx, my)
                    drag_end = (mx, my)
                    if not shift_held:
                        for u in units:
                            u.selected = False

            # ЛКМ отпущена — завершаем рамку
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    dragging = False

                    # Прямоугольник рамки в экранных координатах
                    x1, y1 = drag_start
                    x2, y2 = drag_end
                    rx1, ry1 = min(x1, x2), min(y1, y2)
                    rx2, ry2 = max(x1, x2), max(y1, y2)

                    # Если рамка слишком маленькая — считаем это просто кликом
                    if (rx2 - rx1) < 5 and (ry2 - ry1) < 5:
                        pass

                    # Переводим углы рамки в мировые координаты
                    wx1, wy1 = camera.screen_to_world(rx1, ry1)
                    wx2, wy2 = camera.screen_to_world(rx2, ry2)

                    for u in units:
                        if u.team != "player":
                            continue
                        # Проверяем: центр юнита внутри прямоугольника
                        if wx1 <= u.x <= wx2 and wy1 <= u.y <= wy2:
                            u.selected = True

            # Движение мыши — обновляем конец рамки
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    drag_end = event.pos

            # ПКМ — приказ идти выделенным
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mx, my = event.pos
                world_x, world_y = camera.screen_to_world(mx, my)

                selected = [u for u in units if u.selected and u.team == "player"]
                if selected:
                    # Разброс целей, чтобы юниты не слипались в одну точку
                    n = len(selected)
                    cols = max(1, int(math.ceil(math.sqrt(n))))
                    spacing = 50  # пикселей между юнитами

                    for i, u in enumerate(selected):
                        row = i // cols
                        col = i % cols
                        offset_x = (col - (cols - 1) / 2) * spacing
                        offset_y = (row - (cols - 1) / 2) * spacing
                        u.move_to(world_x + offset_x, world_y + offset_y, tilemap)

        # --- Логика ---
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        camera.update(dt, keys, mouse_pos)

        for u in units:
            u.update(dt, tilemap)

        # Расталкивание юнитов (несколько итераций для стабильности)
        for _ in range(3):
            resolve_unit_collisions(units)

        # --- Отрисовка ---
        screen.fill(COLOR_BG)
        cam_x, cam_y = camera.offset
        tilemap.draw(screen, cam_x, cam_y)

        # Сначала враги, потом наши — чтобы наши были сверху
        for u in [u for u in units if u.team != "player"]:
            u.draw(screen, camera)
        for u in [u for u in units if u.team == "player"]:
            u.draw(screen, camera)

        # Рамка выделения
        if dragging:
            x1, y1 = drag_start
            x2, y2 = drag_end
            rx, ry = min(x1, x2), min(y1, y2)
            rw, rh = abs(x2 - x1), abs(y2 - y1)
            pygame.draw.rect(screen, (255, 230, 80), (rx, ry, rw, rh), 1)

        # Debug
        selected_count = sum(1 for u in units if u.selected and u.team == "player")
        debug = font.render(
            f"FPS: {int(clock.get_fps())}  Selected: {selected_count}/{len([u for u in units if u.team == 'player'])}",
            True, COLOR_TEXT,
        )
        screen.blit(debug, (10, 10))
        hint = font.render(
            "LMB - select / drag, Shift+LMB - add, RMB - move, ESC - exit",
            True, COLOR_TEXT,
        )
        screen.blit(hint, (10, 35))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()