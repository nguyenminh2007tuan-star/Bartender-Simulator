# main.py
"""
Diem khoi chay duy nhat.
Chi chua vong lap Pygame + ket noi game_state <-> renderer.
"""

import pygame
import sys

from settings import *
from game_logic import GameState
from ui import Renderer
from sound_manager import sound_mgr


def _create_display():
    return pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)


def _compute_viewport(screen_size):
    sw, sh = screen_size
    scale = min(sw / WINDOW_WIDTH, sh / WINDOW_HEIGHT)
    view_w = max(1, int(WINDOW_WIDTH * scale))
    view_h = max(1, int(WINDOW_HEIGHT * scale))
    return pygame.Rect((sw - view_w) // 2, (sh - view_h) // 2, view_w, view_h)


def _to_game_pos(pos, viewport):
    x = (pos[0] - viewport.x) * WINDOW_WIDTH / viewport.width
    y = (pos[1] - viewport.y) * WINDOW_HEIGHT / viewport.height
    return int(x), int(y)


def _to_game_rel(rel, viewport):
    x = rel[0] * WINDOW_WIDTH / viewport.width
    y = rel[1] * WINDOW_HEIGHT / viewport.height
    return int(x), int(y)


def _translate_event(event, viewport):
    if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
        return event

    data = dict(event.dict)
    if "pos" in data:
        data["pos"] = _to_game_pos(data["pos"], viewport)
    if event.type == pygame.MOUSEMOTION and "rel" in data:
        data["rel"] = _to_game_rel(data["rel"], viewport)
    return pygame.event.Event(event.type, data)


def main():
    pygame.init()
    pygame.key.set_repeat(300, 40)
    sound_mgr.init()
    sound_mgr.play_bgm()

    screen = _create_display()
    game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert()
    scaled_surface = None
    scaled_surface_size = None
    viewport = _compute_viewport(screen.get_size())
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_state = GameState()
    renderer = Renderer(game_surface, game_state.get_sorted_inventory())

    while True:
        dt_ms = clock.tick(FPS)
        renderer.mouse_pos = _to_game_pos(pygame.mouse.get_pos(), viewport)

        for raw_event in pygame.event.get():
            if raw_event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if raw_event.type == pygame.WINDOWSIZECHANGED:
                viewport = _compute_viewport((raw_event.x, raw_event.y))
                scaled_surface = None
                scaled_surface_size = None

            event = _translate_event(raw_event, viewport)

            if game_state.state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state.open_guide()

            elif game_state.state == "GUIDE":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state.start_game()
                    renderer.inventory._build(game_state.get_sorted_inventory())

            elif game_state.state == "PLAYING":
                action = renderer.handle_event(event, game_state)
                if "shake_done" in action:
                    game_state.finish_shaking()

                if event.type == pygame.KEYDOWN:
                    is_repeat = event.dict.get("is_repeating", False)
                    is_typing = renderer.search_bar.active or renderer.inventory.search_active

                    if not is_typing and not is_repeat:
                        if event.key == pygame.K_TAB:
                            renderer.toggle_tools()
                        elif event.key == pygame.K_SPACE:
                            result = game_state.serve_current_customer()
                            if result:
                                renderer.pinned_recipe = None
                                sound_mgr.play("serve")
                                if result["correct"]:
                                    color = (100, 255, 100)
                                    sound_mgr.play("score_up")
                                    sound_mgr.play("khen")
                                else:
                                    color = (255, 80, 80)
                                    sound_mgr.play("che")

                                renderer.shaker_ui.flash(color)
                                renderer.shaker_ui.is_closed = False
                        elif event.key == pygame.K_c:
                            game_state.clear_shaker()
                            renderer.shaker_ui.is_closed = False
                        elif event.key == pygame.K_ESCAPE:
                            game_state.toggle_pause()

            elif game_state.state == "PAUSED":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state.toggle_pause()
                    elif event.key == pygame.K_k:
                        game_state._end_game()

                if renderer.bgm_slider.handle_event(event):
                    sound_mgr.set_bgm_volume(renderer.bgm_slider.val)
                if renderer.sfx_slider.handle_event(event):
                    sound_mgr.set_sfx_volume(renderer.sfx_slider.val)
                if renderer.mood_btn.handle_event(event):
                    sound_mgr.set_mood_dialogue_enabled(not sound_mgr.mood_dialogue_enabled)
                if renderer.end_btn.handle_event(event):
                    game_state._end_game()

            elif game_state.state == "GAMEOVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_state.start_game()

        if game_state.state == "PLAYING":
            game_state.update()

            if renderer.show_tools:
                mouse_pressed = pygame.mouse.get_pressed()[0]
                dragging_bottle = renderer.inventory.get_dragging()
                mouse_pos = renderer.mouse_pos

                if dragging_bottle and mouse_pressed and renderer.shaker_ui.RECT.collidepoint(mouse_pos):
                    game_state.pour_ingredient(dragging_bottle.name, POUR_RATE)
                    color = INGREDIENTS_DATA.get(dragging_bottle.name, {}).get("color", (200, 200, 200))
                    renderer.spawn_particles(mouse_pos[0] - 15, mouse_pos[1] + 15, color)
                    sound_mgr.start_pouring()
                else:
                    sound_mgr.stop_pouring()
            else:
                sound_mgr.stop_pouring()
        else:
            sound_mgr.stop_pouring()

        if game_state.state == "GUIDE":
            renderer.draw_guide()
        elif game_state.state == "MENU":
            renderer.draw_menu()
        elif game_state.state == "PLAYING":
            renderer.draw_playing(game_state, dt_ms)
        elif game_state.state == "PAUSED":
            renderer.draw_playing(game_state, dt_ms)
            renderer.draw_paused()
        elif game_state.state == "GAMEOVER":
            renderer.draw_gameover(game_state)

        screen.fill((0, 0, 0))
        if viewport.size == (WINDOW_WIDTH, WINDOW_HEIGHT):
            screen.blit(game_surface, viewport.topleft)
        else:
            if scaled_surface is None or scaled_surface_size != viewport.size:
                scaled_surface = pygame.Surface(viewport.size).convert()
                scaled_surface_size = viewport.size
            pygame.transform.scale(game_surface, viewport.size, scaled_surface)
            screen.blit(scaled_surface, viewport.topleft)

        pygame.display.flip()


if __name__ == "__main__":
    main()
