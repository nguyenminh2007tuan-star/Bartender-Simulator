# ui.py
"""
Toàn bộ giao diện Pygame.
Chỉ nhận data từ game_state, KHÔNG chứa logic game.
"""

import pygame
import random
import math
import time
import os

from settings import *


# ══════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════
def load_font(path, size):
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("Arial", size, bold=True)


def load_image(path, size, fallback_color=(80, 80, 100)):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((*fallback_color, 200))
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 1, border_radius=4)
    return surf


def draw_text(surf, text, font, color, x, y, anchor="topleft"):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(**{anchor: (x, y)})
    surf.blit(rendered, rect)
    return rect


# ══════════════════════════════════════════════════════════
#  1. PARTICLE — hiệu ứng rót rượu
# ══════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(1, 5)
        self.color = color
        self.life = 255
        self.size = random.randint(3, 6)

    def update(self):
        self.x  += self.dx
        self.y  += self.dy
        self.dy += 0.3
        self.life -= 8

    def draw(self, screen):
        if self.life > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life),
                               (self.size, self.size), self.size)
            screen.blit(s, (int(self.x), int(self.y)))


# ══════════════════════════════════════════════════════════
#  2. BOTTLE — chai nguyên liệu có thể kéo thả
# ══════════════════════════════════════════════════════════
class Bottle:
    def __init__(self, x, y, name, color, asset_path):
        self.name = name
        self.color = color
        self.origin = (x, y)
        self.rect = pygame.Rect(x, y, 130, 38)
        self.is_dragging = False
        self._image = None
        self._load_image(asset_path)

    def _load_image(self, path):
        self._image = load_image(path, (130, 38), self.color)

    def reset_position(self):
        self.rect.topleft = self.origin
        self.is_dragging = False

    def draw(self, surface, font):
        surface.blit(self._image, self.rect.topleft)
        # Tên nguyên liệu đè lên ảnh
        label = font.render(self.name, True, C_TEXT)
        surface.blit(label, (self.rect.x + 6, self.rect.y + 10))


# ══════════════════════════════════════════════════════════
#  3. CUSTOMER CARD — vẽ thông tin 1 khách tại quầy
# ══════════════════════════════════════════════════════════
class CustomerCard:
    """
    Đại diện cho thẻ hiển thị thông tin và yêu cầu của một khách hàng.
    
    Phương thức chính:
        draw(surface, customer, x, y, font, small_font): Vẽ thẻ khách hàng, tự động ngắt dòng 
            văn bản (Word Wrap) và hiển thị thanh kiên nhẫn (Patience Bar).
        _draw_patience_bar(...): Vẽ thanh thời gian giảm dần dựa trên tỉ lệ kiên nhẫn còn lại.
    """
    CARD_W, CARD_H = 240, 120

    def draw(self, surface, customer, x, y, font, small_font):
        # Nền card
        bg_color = (50, 40, 20) if customer.is_vip else C_PANEL
        pygame.draw.rect(surface, bg_color,
                         (x, y, self.CARD_W, self.CARD_H), border_radius=10)
        border_color = C_GOLD if customer.is_vip else C_PANEL_BORDER
        pygame.draw.rect(surface, border_color,
                         (x, y, self.CARD_W, self.CARD_H), 2, border_radius=10)

        # Tên + tag VIP
        tag = " [VIP]" if customer.is_vip else ""
        draw_text(surface, customer.name + tag, font,
                  C_GOLD if customer.is_vip else C_TEXT,
                  x + 10, y + 10)

        # Order & Tự động ngắt dòng
        text_y = y + 34
        lines_drawn = 1

        if customer.request_type == "direct":
            draw_text(surface, f"Order: {customer.request_data}", small_font, C_TEXT,
                      x + 10, text_y)
        else:
            mood_text = customer.request_data["text"]
            # Thuật toán tách từ và tự động xuống dòng (Word Wrap)
            words = mood_text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                # Kiểm tra nếu chiều dài chữ hiện tại vượt qua chiều ngang thẻ (trừ 20px lề 2 bên)
                if small_font.size(test_line)[0] <= self.CARD_W - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line)) # Thêm dòng cuối cùng

            # Vẽ từng dòng text lên màn hình
            for i, line in enumerate(lines):
                draw_text(surface, line, small_font, (200, 200, 160),
                          x + 10, text_y + i * 18)  # 18 là khoảng cách (line-height) giữa các dòng
            
            lines_drawn = len(lines)

        # Thanh kiên nhẫn (Đẩy tọa độ y xuống dưới linh hoạt dựa theo số dòng chữ)
        bar_y = text_y + (lines_drawn * 18) + 8
        self._draw_patience_bar(surface, customer, x + 10, bar_y,
                                self.CARD_W - 20, 14)

    def _draw_patience_bar(self, surface, customer, x, y, w, h):
        # ... (Phần hàm này giữ nguyên không cần sửa) ...
        ratio = customer.patience_ratio
        bar_color = (
            C_SUCCESS if ratio > 0.5
            else C_GOLD if ratio > 0.25
            else C_ALERT
        )
        pygame.draw.rect(surface, C_PANEL_BORDER, (x, y, w, h), border_radius=6)
        pygame.draw.rect(surface, bar_color,
                         (x, y, int(w * ratio), h), border_radius=6)
        pygame.draw.rect(surface, C_TEXT_DIM, (x, y, w, h), 1, border_radius=6)

# ══════════════════════════════════════════════════════════
#  4. SHAKER UI — vẽ bình lắc + thanh tiến trình
# ══════════════════════════════════════════════════════════

class ShakerUI:
    """
    Mô phỏng hình ảnh và trạng thái của bình lắc (Shaker).
    
    Thuộc tính:
        RECT (pygame.Rect): Vị trí cố định của bình lắc trên quầy bar.
        is_shaking (bool): Trạng thái xác định bình có đang được lắc hay không.
        shake_offset (int): Giá trị độ lệch để tạo hiệu ứng rung lắc (vibration).
    
    Phương thức chính:
        update(dt): Cập nhật hiệu ứng rung dựa trên thời gian thực.
        draw(surface, contents, font): Vẽ bình lắc và danh sách các nguyên liệu đang có bên trong.
        flash(color): Tạo hiệu ứng lóe sáng khi thêm nguyên liệu hoặc phục vụ.
    """
    RECT = pygame.Rect(530, 390, 140, 220)

    def __init__(self):
        self.shake_progress = 0
        self._flash_timer   = 0   # ms
        self._flash_color   = None
        self.is_shaking     = False
        self._last_mouse_x  = 0

    def handle_shake(self, event):
        """Gọi từ event loop khi MOUSEMOTION. Trả về True khi lắc xong."""
        if event.type == pygame.MOUSEMOTION and self.is_shaking:
            delta = abs(event.pos[0] - self._last_mouse_x)
            if delta > 18:
                self.shake_progress += 1
                self._last_mouse_x = event.pos[0]
            if self.shake_progress >= SHAKE_THRESHOLD:
                self.shake_progress = 0
                self.is_shaking     = False
                return True
        return False

    def start_shake(self, mouse_x):
        self.is_shaking    = True
        self._last_mouse_x = mouse_x

    def stop_shake(self):
        self.is_shaking = False

    def flash(self, color):
        self._flash_color = color
        self._flash_timer = 400   # ms

    def update(self, dt_ms):
        if self._flash_timer > 0:
            self._flash_timer -= dt_ms

    def draw(self, surface, contents, font):
        # Bình lắc
        color = self._flash_color if self._flash_timer > 0 else C_SHAKER
        pygame.draw.rect(surface, color, self.RECT, border_radius=14)
        pygame.draw.rect(surface, C_TEXT_DIM, self.RECT, 2, border_radius=14)

        # Nguyên liệu trong bình
        for i, name in enumerate(reversed(contents)):
            ing_color = INGREDIENTS_DATA.get(name, {}).get("color", (150, 150, 150))
            bar_y = self.RECT.bottom - 20 - i * 28
            pygame.draw.rect(surface, ing_color,
                             (self.RECT.x + 8, bar_y, self.RECT.w - 16, 22),
                             border_radius=5)
            label = font.render(name, True, (0, 0, 0))
            surface.blit(label, (self.RECT.x + 10, bar_y + 3))

        # Label SHAKER
        draw_text(surface, "SHAKER", font, C_TEXT_DIM,
                  self.RECT.centerx, self.RECT.y - 18, anchor="center")

        # Thanh lắc (chỉ hiện khi đang lắc)
        if self.is_shaking or self.shake_progress > 0:
            bar_x = self.RECT.x
            bar_y = self.RECT.bottom + 10
            bar_w = self.RECT.w
            pygame.draw.rect(surface, C_PANEL_BORDER, (bar_x, bar_y, bar_w, 12), border_radius=5)
            fill = int(bar_w * self.shake_progress / SHAKE_THRESHOLD)
            pygame.draw.rect(surface, C_SUCCESS, (bar_x, bar_y, fill, 12), border_radius=5)


# ══════════════════════════════════════════════════════════
#  5. SEARCH BAR — Trie autocomplete
# ══════════════════════════════════════════════════════════
class SearchBar:
    """
    Thanh tìm kiếm công thức thông minh tích hợp cấu trúc dữ liệu Trie.
    
    Thuộc tính:
        text (str): Chuỗi ký tự người chơi đang nhập.
        active (bool): Trạng thái thanh tìm kiếm có đang được mở/focus hay không.
        results (list): Danh sách các công thức gợi ý khớp với tiền tố đã nhập.
        scroll_offset (int): Vị trí cuộn hiện tại để hiển thị danh sách kết quả dài.
    
    Phương thức chính:
        handle_event(event, autocomplete_fn): Xử lý nhập liệu từ bàn phím và cuộn chuột.
        draw(surface, font, small_font): Hiển thị thanh nhập liệu và danh sách kết quả xổ xuống (Dropdown).
    """
    RECT  = pygame.Rect(30, 140, 500, 36) # Đã kéo dài khung như bạn muốn
    MAX_SUGGESTIONS = 5 # Số lượng món hiển thị cùng lúc

    def __init__(self):
        self.text          = ""
        self.active        = False
        self.results       = []   # Danh sách (name, data)
        self.scroll_offset = 0    # Vị trí bắt đầu của "cửa sổ" hiển thị

    def handle_event(self, event, autocomplete_fn):
        # 1. Xử lý bàn phím
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.active = not self.active
                if self.active:
                    self.text = ""
                    # Khi vừa mở, lấy TOÀN BỘ danh sách và sắp xếp A-Z
                    self.results = sorted(autocomplete_fn(""), key=lambda x: x[0])
                    self.scroll_offset = 0
                else:
                    self.results = []
            
            elif self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isprintable():
                    self.text += event.unicode
                
                # Cập nhật kết quả tìm kiếm và luôn sắp xếp A-Z
                self.results = sorted(autocomplete_fn(self.text), key=lambda x: x[0])
                self.scroll_offset = 0 # Reset cuộn khi gõ chữ mới

        # 2. Xử lý lăn chuột (Mouse Wheel)
        if self.active and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: # Lăn lên (Scroll Up)
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5: # Lăn xuống (Scroll Down)
                # Không cho cuộn quá danh sách (trừ đi số lượng hiển thị tối đa)
                max_scroll = max(0, len(self.results) - self.MAX_SUGGESTIONS)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

    def draw(self, surface, font, small_font):
        border = C_SUCCESS if self.active else C_PANEL_BORDER
        pygame.draw.rect(surface, C_PANEL, self.RECT, border_radius=6)
        pygame.draw.rect(surface, border, self.RECT, 2, border_radius=6)

        display = self.text if self.active else "ENTER để tìm công thức..."
        color   = C_TEXT if self.active else C_TEXT_DIM
        cursor  = "|" if self.active and time.time() % 1 > 0.5 else ""
        draw_text(surface, display + cursor, font, color,
                  self.RECT.x + 8, self.RECT.y + 8)

        # Vẽ danh sách kết quả xổ xuống
        if self.results:
            drop_y = self.RECT.bottom + 4
            
            # CHỈ LẤY MỘT ĐOẠN kết quả dựa trên scroll_offset để vẽ
            visible_results = self.results[self.scroll_offset : self.scroll_offset + self.MAX_SUGGESTIONS]
            
            for i, (name, data) in enumerate(visible_results):
                row = pygame.Rect(self.RECT.x, drop_y + i * 48, self.RECT.w, 44)
                pygame.draw.rect(surface, C_PANEL, row, border_radius=4)
                pygame.draw.rect(surface, C_PANEL_BORDER, row, 1, border_radius=4)
                
                ings = ", ".join(data["ingredients"])
                tags = ", ".join(data["tags"])
                
                draw_text(surface, f"{name}: {ings}", small_font, C_TEXT,
                          row.x + 6, row.y + 5)
                draw_text(surface, f"Tags: [{tags}]", small_font, (150, 200, 255),
                          row.x + 6, row.y + 24)


# ══════════════════════════════════════════════════════════
#  6. INVENTORY PANEL — danh sách nguyên liệu (MergeSort)
# ══════════════════════════════════════════════════════════
"""
    Quản lý và hiển thị danh sách nguyên liệu (Kho đồ) lên màn hình.
    
    Thuộc tính:
        bottles (list): Danh sách các đối tượng Bottle đại diện cho từng loại rượu/mixer.
        RECT (pygame.Rect): Khung vị trí của bảng nguyên liệu trên màn hình.
    
    Phương thức chính:
        draw(surface, font, small_font): Vẽ bảng nền và các chai rượu lên màn hình.
        handle_event(event): Xử lý tương tác kéo-thả (Drag & Drop) từng chai rượu.
    """
class InventoryPanel:
    RECT = pygame.Rect(940, 150, 300, 460)

    def __init__(self, sorted_inventory):
        self.bottles = []
        self._build(sorted_inventory)

    def _build(self, sorted_inventory):
        self.bottles.clear()
        start_x = self.RECT.x + 10
        start_y = self.RECT.y + 40
        for i, item in enumerate(sorted_inventory):
            b = Bottle(
                start_x,
                start_y + i * 52,
                item["name"],
                item["color"],
                item["asset"],
            )
            self.bottles.append(b)

    def draw(self, surface, font, small_font):
        pygame.draw.rect(surface, C_PANEL, self.RECT, border_radius=12)
        pygame.draw.rect(surface, C_PANEL_BORDER, self.RECT, 2, border_radius=12)
        draw_text(surface, "NGUYÊN LIỆU", font, C_TEXT_DIM,
                  self.RECT.centerx, self.RECT.y + 12, anchor="center")
        for b in self.bottles:
            b.draw(surface, small_font)

    def get_dragging(self):
        return next((b for b in self.bottles if b.is_dragging), None)


# ══════════════════════════════════════════════════════════
#  7. DISCOVERY BANNER — thông báo khám phá công thức mới
# ══════════════════════════════════════════════════════════
class DiscoveryBanner:
    def __init__(self):
        self._msg   = None
        self._timer = 0   # ms

    def show(self, drink_name):
        self._msg   = f"Đã khám phá: {drink_name}!"
        self._timer = 3000

    def update(self, dt_ms):
        if self._timer > 0:
            self._timer -= dt_ms

    def draw(self, surface, font):
        if self._timer > 0 and self._msg:
            alpha = min(255, self._timer)
            s = font.render(self._msg, True, C_GOLD)
            s.set_alpha(alpha)
            x = WINDOW_WIDTH  // 2 - s.get_width()  // 2
            y = WINDOW_HEIGHT // 2 - 40
            surface.blit(s, (x, y))


# ══════════════════════════════════════════════════════════
#  8. RENDERER — lớp tổng hợp, vẽ toàn bộ game
# ══════════════════════════════════════════════════════════
class Renderer:
    """
    Lớp điều phối (Manager) chịu trách nhiệm vẽ toàn bộ các thành phần lên màn hình.
    
    Thuộc tính:
        show_tools (bool): Biến kiểm soát việc ẩn/hiện quầy pha chế (Toggle Tools).
    
    Phương thức chính:
        draw_playing(game_state, dt_ms): Hàm chính vẽ giao diện trong trạng thái đang chơi.
        handle_event(event, game_state): Chuyển tiếp các sự kiện chuột/phím đến đúng thành phần UI.
        toggle_tools(): Chuyển đổi trạng thái hiển thị của bình lắc và kho nguyên liệu.
    """
    def __init__(self, screen, sorted_inventory):
        self.screen   = screen
        self.font      = load_font(FONT_PATH, 20)
        self.small     = load_font(FONT_PATH, 14)
        self.bg        = load_image(BG_PATH, (WINDOW_WIDTH, WINDOW_HEIGHT), C_BG)

        self.shaker_ui    = ShakerUI()
        self.search_bar   = SearchBar()
        self.inventory    = InventoryPanel(sorted_inventory)
        self.cust_card    = CustomerCard()
        self.banner       = DiscoveryBanner()
        self.particles    = []
        self.show_tools = False
    # ── Particles ─────────────────────────────────────────
    def toggle_tools(self):
        self.show_tools = not self.show_tools
        # Nếu đang kéo chai hoặc lắc bình mà tắt đi thì phải reset lại
        if not self.show_tools:
            self.shaker_ui.stop_shake()
            for b in self.inventory.bottles:
                b.reset_position()
    def spawn_particles(self, x, y, color):
        for _ in range(20):
            self.particles.append(Particle(x, y, color))

    def _update_particles(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    # ── Main draw ─────────────────────────────────────────
    def draw_menu(self):
        self.screen.fill(C_BG)
        draw_text(self.screen, TITLE, self.font, C_GOLD,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40, anchor="center")
        draw_text(self.screen, "Press Enter", self.font, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10, anchor="center")

    def draw_playing(self, game_state, dt_ms):
        self.screen.blit(self.bg, (0, 0))

        # Customers
        customers = game_state.get_active_customers()
        for i, c in enumerate(customers):
            cx = 30 + i * (CustomerCard.CARD_W + 12)
            self.cust_card.draw(self.screen, c, cx, 10,
                                self.font, self.small)

        # Shaker
        self.shaker_ui.update(dt_ms)
        if self.show_tools:
            self.shaker_ui.draw(self.screen,
                                game_state.get_shaker_contents(),
                                self.small)

        # Inventory
            self.inventory.draw(self.screen, self.font, self.small)

        # Search bar
        self.search_bar.draw(self.screen, self.font, self.small)

        # Particles
        self._update_particles()
        for p in self.particles:
            p.draw(self.screen)

        # Score
        draw_text(self.screen, f"ĐIỂM: {game_state.score}",
                  self.font, C_GOLD,
                  WINDOW_WIDTH - 20, 20, anchor="topright")

        # Discovery banner
        self.banner.update(dt_ms)
        self.banner.draw(self.screen, self.font)

        # Khách gấp nhất — hint order to giữa màn
        next_c = game_state.get_next_customer()
        if next_c and next_c.request_type == "mood":
            hint_tags = ", ".join(next_c.request_data["tags"])
            draw_text(self.screen, f"Gợi ý tag: [{hint_tags}]",
                      self.small, (200, 200, 160),
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30, anchor="center")

    def draw_paused(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, "PAUSED", self.font, C_GOLD,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, anchor="center")
        draw_text(self.screen, "Nhấn P để tiếp tục", self.small, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 36, anchor="center")

    def draw_gameover(self, game_state):
        self.screen.fill(C_BG)
        draw_text(self.screen, "KẾT THÚC!", self.font, C_ALERT,
                  WINDOW_WIDTH // 2, 80, anchor="center")
        draw_text(self.screen, f"Điểm của bạn: {game_state.score}",
                  self.font, C_GOLD,
                  WINDOW_WIDTH // 2, 130, anchor="center")
        draw_text(self.screen, "TOP ĐIỂM CAO", self.font, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, 190, anchor="center")
        for i, entry in enumerate(game_state.leaderboard[:5]):
            draw_text(self.screen,
                      f"#{i+1}  {entry['name']}  —  {entry['score']}",
                      self.small, C_TEXT,
                      WINDOW_WIDTH // 2, 230 + i * 36, anchor="center")
        draw_text(self.screen, "Nhấn R để chơi lại",
                  self.small, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, anchor="center")

    # ── Event forwarding ──────────────────────────────────
    def handle_event(self, event, game_state):
        """
        Xử lý tất cả event liên quan đến UI.
        Trả về action dict để game_state xử lý nếu cần.
        """
        action = {}

        # Search bar
        self.search_bar.handle_event(
            event,
            lambda prefix: game_state.autocomplete(prefix)
        )
        if self.show_tools:
            # Drag & drop chai
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in self.inventory.bottles:
                    if b.rect.collidepoint(event.pos):
                        b.is_dragging = True
                        break
                # Bắt đầu lắc nếu click vào shaker
                if ShakerUI.RECT.collidepoint(event.pos):
                    self.shaker_ui.start_shake(event.pos[0])

            elif event.type == pygame.MOUSEMOTION:
                for b in self.inventory.bottles:
                    if b.is_dragging:
                        b.rect.center = event.pos
                        # Hiệu ứng particle khi kéo qua shaker
                        if ShakerUI.RECT.collidepoint(event.pos):
                            color = INGREDIENTS_DATA.get(b.name, {}).get("color", (200, 200, 200))
                            self.spawn_particles(*event.pos, color)
                # Xử lý lắc
                done = self.shaker_ui.handle_shake(event)
                if done:
                    action["shake_done"] = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.shaker_ui.stop_shake()
                for b in self.inventory.bottles:
                    if b.is_dragging:
                        if ShakerUI.RECT.colliderect(b.rect):
                            action["add_ingredient"] = b.name
                            color = INGREDIENTS_DATA.get(b.name, {}).get("color", (200, 200, 200))
                            self.shaker_ui.flash(color)
                        b.reset_position()

        return action

    def show_discovery(self, drink_name):
        self.banner.show(drink_name)