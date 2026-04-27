# main.py
"""
Điểm khởi chạy duy nhất.
Chỉ chứa vòng lặp Pygame + kết nối game_state ↔ renderer.
"""

import pygame
import sys

from settings import *
from game_logic import GameState
from ui import Renderer


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_state = GameState()

    # Renderer cần sorted_inventory để dựng InventoryPanel
    renderer = Renderer(screen, game_state.get_sorted_inventory())

    while True:
        dt_ms = clock.tick(FPS)   # ms kể từ frame trước

        # ── Event loop ────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Global keys (hoạt động mọi state)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            # ── MENU ──────────────────────────────────────
            if game_state.state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state.start_game()
                    # Rebuild inventory panel với data mới
                    renderer.inventory._build(game_state.get_sorted_inventory())

            # ── PLAYING ───────────────────────────────────
            elif game_state.state == "PLAYING":
                # Forward event cho UI, nhận lại action
                action = renderer.handle_event(event, game_state)

                # Xử lý action từ UI
                if "add_ingredient" in action:
                    success = game_state.add_ingredient(action["add_ingredient"])
                    if not success:
                        pass  # TODO: hiệu ứng "bình đầy"

                if "shake_done" in action:
                    pass  # lắc xong → người chơi nhấn SPACE để serve

                # Keyboard shortcuts
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        renderer.toggle_tools()
                    if event.key == pygame.K_SPACE:
                        result = game_state.serve_current_customer()
                        if result:
                            color = (100, 255, 100) if result["correct"] else (255, 80, 80)
                            renderer.shaker_ui.flash(color)
                            if result.get("discovered"):
                                renderer.show_discovery(result["discovered"])

                    elif event.key == pygame.K_z:
                        removed = game_state.undo_ingredient()
                        # TODO: hiệu ứng undo

                    elif event.key == pygame.K_c:
                        game_state.clear_shaker()

                    elif event.key == pygame.K_p:
                        game_state.toggle_pause()

            # ── PAUSED ────────────────────────────────────
            elif game_state.state == "PAUSED":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state.toggle_pause()

            # ── GAMEOVER ──────────────────────────────────
            elif game_state.state == "GAMEOVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_state.start_game()
                    renderer.inventory._build(game_state.get_sorted_inventory())

        # ── Update logic ──────────────────────────────────
        if game_state.state == "PLAYING":
            game_state.update()

            # Lấy discovery message (nếu có) để hiển thị banner
            msg = game_state.get_discovery_message()
            if msg:
                renderer.show_discovery(msg)

        # ── Render ────────────────────────────────────────
        if game_state.state == "MENU":
            renderer.draw_menu()
        elif game_state.state == "PLAYING":

            renderer.draw_playing(game_state, dt_ms)
        elif game_state.state == "PAUSED":
            renderer.draw_playing(game_state, dt_ms)   # vẽ game phía sau
            renderer.draw_paused()
        elif game_state.state == "GAMEOVER":
            renderer.draw_gameover(game_state)

        pygame.display.flip()


if __name__ == "__main__":
    main()