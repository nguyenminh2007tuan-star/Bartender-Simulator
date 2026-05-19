<<<<<<< HEAD
# ui.py
"""
Toàn bộ giao diện Pygame.
Chỉ nhận data từ game_state, KHÔNG chứa logic game.
"""
import pygame
import random
import math
=======
# ui.py
"""
Toàn bộ giao diện Pygame.
Chỉ nhận data từ game_state, KHÔNG chứa logic game.
"""
import pygame
import random
import math
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
import time
import os

from settings import *
from sound_manager import sound_mgr
from algorithms import Trie

try:
    import cv2
except ImportError:
    cv2 = None
<<<<<<< HEAD

# ══════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════
def load_font(path, size):
    """
    Tải font từ file, fallback về Arial nếu file không tồn tại.

    Args:
        path (str): Đường dẫn đến file font (vd: ``"assets/pixel_font.ttf"``).
        size (int): Cỡ chữ (px).

    Returns:
        pygame.font.Font: Đối tượng font đã tải.
    """
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("Arial", size, bold=True)


def load_image(path, size, fallback_color=(80, 80, 100)):
    """
    Tải và scale ảnh từ file, fallback về hình chữ nhật màu nếu không tìm thấy.

    Args:
        path (str): Đường dẫn đến file ảnh.
        size (tuple): Kích thước đích ``(width, height)`` (px).
        fallback_color (tuple): Màu RGB dùng khi file không tồn tại. Mặc định ``(80, 80, 100)``.

    Returns:
        pygame.Surface: Surface đã scale về kích thước ``size``.
    """
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((*fallback_color, 200))
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 1, border_radius=4)
    return surf


def draw_text(surface, text, font, color, x, y, anchor="topleft"):
    """
    Vẽ chuỗi văn bản lên surface tại tọa độ cho trước.

    Args:
        surf (pygame.Surface): Surface đích.
        text (str): Chuỗi cần vẽ.
        font (pygame.font.Font): Font sử dụng.
        color (tuple): Màu RGB của chữ.
        x (int): Tọa độ X (pixel).
        y (int): Tọa độ Y (pixel).
        anchor (str): Điểm neo của rect, mặc định ``"topleft"``.
            Có thể là bất kỳ thuộc tính nào của ``pygame.Rect``
            (vd: ``"center"``, ``"midtop"``, ``"topright"``).

    Returns:
        pygame.Rect: Rect của văn bản vừa vẽ (dùng để hit-test nếu cần).
    """
    rendered = font.render(str(text), True, color)
    # Lấy tọa độ
    rect = rendered.get_rect(**{anchor: (x, y)})
    # Vẽ lên surface
    surface.blit(rendered, rect)

# ══════════════════════════════════════════════════════════
#  1. PARTICLE — hiệu ứng rót rượu
# ══════════════════════════════════════════════════════════
class Particle:
    """
    Hạt hiệu ứng rơi xuống mô phỏng chất lỏng chảy ra khi rót vào bình.

    Mỗi hạt có vận tốc ngẫu nhiên, chịu gia tốc trọng trường giả lập,
    và mờ dần (alpha giảm) cho đến khi biến mất.

    Attributes:
        x, y (float): Vị trí hiện tại.
        dx, dy (float): Vận tốc theo trục X và Y (pixel/frame).
        color (tuple): Màu RGB của hạt.
        life (int): Độ trong suốt hiện tại (255 → 0); hạt biến mất khi <= 0.
        size (int): Bán kính hạt (px).
    """
    def __init__(self, x, y, color):
        """
        Khởi tạo hạt tại vị trí ``(x, y)`` với màu ``color`` và thông số ngẫu nhiên.

        Args:
            x (float): Tọa độ X xuất phát.
            y (float): Tọa độ Y xuất phát.
            color (tuple): Màu RGB của hạt.
        """
        self.x, self.y = x, y
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(1, 5)
        self.color = color
        self.life = 255
        self.size = random.randint(3, 6)

    def update(self):
        """
        Cập nhật vị trí và trạng thái hạt cho một frame.

        Di chuyển theo vận tốc, áp dụng gia tốc rơi tự do giả lập
        (``dy += 0.3``), và giảm ``life`` đi 8 mỗi frame.
        """
        self.x  += self.dx
        self.y  += self.dy
        self.dy += 0.3
        self.life -= 8

    def draw(self, screen):
        if self.life <= 0:
            return
            
        # VẼ KHỐI VUÔNG PIXEL (Thay cho hình tròn)
        # Kích thước khối vuông dựa trên self.size
        rect_size = self.size * 2 
        s = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
        
        # Tô màu khối vuông
        s.fill((*self.color, max(0, self.life)))
        
        # Blit lên màn hình
        screen.blit(s, (int(self.x), int(self.y)))

# ══════════════════════════════════════════════════════════
#  2. BOTTLE — chai nguyên liệu có thể kéo thả
# ══════════════════════════════════════════════════════════
class Bottle:
    """
    Đại diện cho một chai nguyên liệu có thể kéo-thả (Drag & Drop) trong InventoryPanel.

    Khi đang kéo (``is_dragging = True``), chai di chuyển theo chuột và
    có thể được nghiêng để tạo hiệu ứng rót khi chuột nằm trên Shaker.

    Attributes:
        name (str): Tên nguyên liệu (vd: ``"Vodka"``).
        color (tuple): Màu RGB của nguyên liệu, dùng làm fallback khi thiếu ảnh.
        origin (tuple): Tọa độ ``(x, y)`` gốc trong InventoryPanel,
            dùng để reset về vị trí ban đầu khi nhả chuột.
        rect (pygame.Rect): Rect hiện tại của chai (110×95 px).
        is_dragging (bool): ``True`` nếu chai đang được kéo.
    """
    def __init__(self, x, y, name, color, asset_path):
        # KHAI BÁO CÁC BIẾN CƠ BẢN BỊ THIẾU
        self.name = name
        self.color = color
        self.origin = (x, y)
        self.rect = pygame.Rect(x, y, 110, 95) # Khung hit-box của chai
        self.is_dragging = False               # Khởi tạo trạng thái ban đầu là không bị kéo
        self.relative_y = 0

        # PHẦN LOAD ẢNH BÊN DƯỚI GIỮ NGUYÊN
        import os
        if os.path.exists(asset_path):
            orig_img = pygame.image.load(asset_path).convert_alpha()
            w, h = orig_img.get_size()
            
            max_w, max_h = 80, 55
            scale = min(max_w / w, max_h / h)
            
            new_w, new_h = int(w * scale), int(h * scale)
            self._image = pygame.transform.scale(orig_img, (new_w, new_h))
        else:
            self._image = pygame.Surface((30, 55))
            self._image.fill(self.color)

    def reset_position(self):
        """
        Trả chai về vị trí gốc trong InventoryPanel và tắt trạng thái kéo.

        Được gọi khi người chơi nhả chuột hoặc khi panel bị ẩn.
        """
        self.rect.topleft = self.origin
        self.is_dragging = False

    def draw(self, surface, font, is_pouring=False):
        """
        Vẽ chai lên surface theo trạng thái hiện tại.

        Khi đang kéo: chỉ vẽ ảnh (không có nền), xoay 120° nếu ``is_pouring``.
        Khi không kéo: vẽ khung nền tối, ảnh căn giữa, và tên bên dưới.

        Args:
            surface (pygame.Surface): Surface đích.
            font (pygame.font.Font): Font dùng để vẽ tên nguyên liệu.
            is_pouring (bool): ``True`` khi chuột đang nằm trên vùng Shaker,
                kích hoạt hiệu ứng nghiêng chai. Mặc định ``False``.
        """
        img = self._image
        if is_pouring:
            img = pygame.transform.rotate(self._image, 120)
            img_x = self.rect.centerx - img.get_width() // 2
            img_y = self.rect.centery - img.get_height() // 2
            surface.blit(img, (img_x, img_y))
        elif self.is_dragging:
            # NẾU ĐANG KÉO: Căn giữa chai rượu vào đúng lòng bàn tay (con trỏ chuột)
            img_x = self.rect.centerx - self._image.get_width() // 2
            img_y = self.rect.centery - self._image.get_height() // 2
            surface.blit(self._image, (img_x, img_y))  
            
            surface.blit(self._image, (img_x, img_y))
        else:
            # NẾU NẰM TRONG KHO: Vẽ nguyên box nền và chữ
            pygame.draw.rect(surface, (40, 45, 55), self.rect, border_radius=8)
            pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 1, border_radius=8)

            img_x = self.rect.centerx - self._image.get_width() // 2
            img_y = self.rect.y + 12
            surface.blit(self._image, (img_x, img_y))

            draw_text(surface, self.name, font, C_TEXT,
                      self.rect.centerx, self.rect.bottom - 22, anchor="center")


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
        # 1. Tính toán Word Wrap TRƯỚC để biết số dòng
        text_y = y + 34
        lines = []
        text_color = C_TEXT

        if customer.request_type == "direct":
            lines = [f"Order: {customer.request_data}"]
        else:
            text_color = (200, 200, 160) # Màu hơi vàng cho câu thoại
            mood_text = customer.request_data["text"]
            
            # Thuật toán tách từ và tự động xuống dòng
            words = mood_text.split(' ')
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if small_font.size(test_line)[0] <= self.CARD_W - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line: # Bỏ dòng cuối cùng vào mảng
                lines.append(' '.join(current_line))
                
        lines_drawn = len(lines)

        # 2. Tính toán chiều cao động (Dynamic Height)
        # Chiều cao = Y bắt đầu text (34) + (số dòng * line_height) + khoảng cách bar (8) + độ dày bar (14) + lề dưới (10)
        dynamic_h = 34 + (lines_drawn * 18) + 8 + 14 + 10
        # Đảm bảo chiều cao tối thiểu không bị ngắn hơn CARD_H mặc định (120)
        dynamic_h = max(dynamic_h, self.CARD_H) 

        # 3. Vẽ Nền card dựa trên chiều cao động vừa tính
        bg_color = (50, 40, 20) if customer.is_vip else C_PANEL
        pygame.draw.rect(surface, bg_color,
                         (x, y, self.CARD_W, dynamic_h), border_radius=10)
        border_color = C_GOLD if customer.is_vip else C_PANEL_BORDER
        pygame.draw.rect(surface, border_color,
                         (x, y, self.CARD_W, dynamic_h), 2, border_radius=10)

        # 4. Vẽ Tên + tag VIP
        tag = " [VIP]" if customer.is_vip else ""
        draw_text(surface, customer.name + tag, font,
                  C_GOLD if customer.is_vip else C_TEXT,
                  x + 10, y + 10)

        # 5. Vẽ chữ lên màn hình
        for i, line in enumerate(lines):
            draw_text(surface, line, small_font, text_color,
                      x + 10, text_y + i * 18)

        # 6. Vẽ Thanh kiên nhẫn ở vị trí linh hoạt
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
    Giao diện bình lắc: vẽ chất lỏng dâng lên, xử lý thao tác lắc chuột,
    và hiệu ứng flash khi phục vụ xong.

    Cơ chế lắc: người chơi giữ chuột trên bình và di trái/phải nhanh.
    Mỗi khi ``delta_x > 18 px`` giữa hai frame liên tiếp, ``shake_progress``
    tăng 1. Khi đạt ``SHAKE_THRESHOLD``, lắc hoàn thành.

    Attributes:
        shake_progress (int): Số nhịp lắc hiện tại.
        is_shaking (bool): ``True`` khi đang trong chế độ lắc (chuột đang giữ trên bình).
        RECT (pygame.Rect): Vùng hiển thị bình lắc trên màn hình (tĩnh, class-level).
    """
    # Cố định tọa độ góc trên bên trái của bình lắc
    RECT = pygame.Rect(530, 390, 140, 220)
    BASE_X = 530
    BASE_Y = 300

    def __init__(self):
        self.shake_progress = 0
        self._flash_timer   = 0
        self._flash_color   = None
        self.is_shaking     = False
        self.is_closed      = False
        self._last_mouse_x  = 0

        # --- LOAD ẢNH VÀ GIỮ NGUYÊN TỈ LỆ (KHÔNG BÓP MÉO) ---
        import os
        target_h = 280
        
        front_path = "assets/shaker_front.png"
        if os.path.exists(front_path):
            orig_img = pygame.image.load(front_path).convert_alpha()
            ratio = orig_img.get_width() / orig_img.get_height()
            target_w = int(target_h * ratio)
            self.img_front = pygame.transform.scale(orig_img, (target_w, target_h))
            self.RECT = pygame.Rect(self.BASE_X, self.BASE_Y, target_w, target_h)
        else:
            self.img_front = None
            self.RECT = pygame.Rect(self.BASE_X, self.BASE_Y, 140, 220)

        closed_path = "assets/shaker_closed.png"
        if os.path.exists(closed_path):
            orig_closed = pygame.image.load(closed_path).convert_alpha()
            # Tweak size of closed shaker to match open shaker
            scale_factor = 0.82
            target_h_c = int(target_h * scale_factor)
            ratio_c = orig_closed.get_width() / orig_closed.get_height()
            target_w_c = int(target_h_c * ratio_c)
            self.img_closed = pygame.transform.scale(orig_closed, (target_w_c, target_h_c))
        else:
            self.img_closed = None

        self.btn_lid_rect = pygame.Rect(self.RECT.right + 10, self.RECT.bottom - 40, 80, 40)

=======

# ══════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════
def load_font(path, size):
    """
    Tải font từ file, fallback về Arial nếu file không tồn tại.

    Args:
        path (str): Đường dẫn đến file font (vd: ``"assets/pixel_font.ttf"``).
        size (int): Cỡ chữ (px).

    Returns:
        pygame.font.Font: Đối tượng font đã tải.
    """
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("Arial", size, bold=True)


def load_image(path, size, fallback_color=(80, 80, 100)):
    """
    Tải và scale ảnh từ file, fallback về hình chữ nhật màu nếu không tìm thấy.

    Args:
        path (str): Đường dẫn đến file ảnh.
        size (tuple): Kích thước đích ``(width, height)`` (px).
        fallback_color (tuple): Màu RGB dùng khi file không tồn tại. Mặc định ``(80, 80, 100)``.

    Returns:
        pygame.Surface: Surface đã scale về kích thước ``size``.
    """
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((*fallback_color, 200))
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 1, border_radius=4)
    return surf


def draw_text(surface, text, font, color, x, y, anchor="topleft"):
    """
    Vẽ chuỗi văn bản lên surface tại tọa độ cho trước.

    Args:
        surf (pygame.Surface): Surface đích.
        text (str): Chuỗi cần vẽ.
        font (pygame.font.Font): Font sử dụng.
        color (tuple): Màu RGB của chữ.
        x (int): Tọa độ X (pixel).
        y (int): Tọa độ Y (pixel).
        anchor (str): Điểm neo của rect, mặc định ``"topleft"``.
            Có thể là bất kỳ thuộc tính nào của ``pygame.Rect``
            (vd: ``"center"``, ``"midtop"``, ``"topright"``).

    Returns:
        pygame.Rect: Rect của văn bản vừa vẽ (dùng để hit-test nếu cần).
    """
    rendered = font.render(str(text), True, color)
    # Lấy tọa độ
    rect = rendered.get_rect(**{anchor: (x, y)})
    # Vẽ lên surface
    surface.blit(rendered, rect)

# ══════════════════════════════════════════════════════════
#  1. PARTICLE — hiệu ứng rót rượu
# ══════════════════════════════════════════════════════════
class Particle:
    """
    Hạt hiệu ứng rơi xuống mô phỏng chất lỏng chảy ra khi rót vào bình.

    Mỗi hạt có vận tốc ngẫu nhiên, chịu gia tốc trọng trường giả lập,
    và mờ dần (alpha giảm) cho đến khi biến mất.

    Attributes:
        x, y (float): Vị trí hiện tại.
        dx, dy (float): Vận tốc theo trục X và Y (pixel/frame).
        color (tuple): Màu RGB của hạt.
        life (int): Độ trong suốt hiện tại (255 → 0); hạt biến mất khi <= 0.
        size (int): Bán kính hạt (px).
    """
    def __init__(self, x, y, color):
        """
        Khởi tạo hạt tại vị trí ``(x, y)`` với màu ``color`` và thông số ngẫu nhiên.

        Args:
            x (float): Tọa độ X xuất phát.
            y (float): Tọa độ Y xuất phát.
            color (tuple): Màu RGB của hạt.
        """
        self.x, self.y = x, y
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(1, 5)
        self.color = color
        self.life = 255
        self.size = random.randint(3, 6)

    def update(self):
        """
        Cập nhật vị trí và trạng thái hạt cho một frame.

        Di chuyển theo vận tốc, áp dụng gia tốc rơi tự do giả lập
        (``dy += 0.3``), và giảm ``life`` đi 8 mỗi frame.
        """
        self.x  += self.dx
        self.y  += self.dy
        self.dy += 0.3
        self.life -= 8

    def draw(self, screen):
        if self.life <= 0:
            return
            
        # VẼ KHỐI VUÔNG PIXEL (Thay cho hình tròn)
        # Kích thước khối vuông dựa trên self.size
        rect_size = self.size * 2 
        s = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
        
        # Tô màu khối vuông
        s.fill((*self.color, max(0, self.life)))
        
        # Blit lên màn hình
        screen.blit(s, (int(self.x), int(self.y)))

# ══════════════════════════════════════════════════════════
#  2. BOTTLE — chai nguyên liệu có thể kéo thả
# ══════════════════════════════════════════════════════════
class Bottle:
    """
    Đại diện cho một chai nguyên liệu có thể kéo-thả (Drag & Drop) trong InventoryPanel.

    Khi đang kéo (``is_dragging = True``), chai di chuyển theo chuột và
    có thể được nghiêng để tạo hiệu ứng rót khi chuột nằm trên Shaker.

    Attributes:
        name (str): Tên nguyên liệu (vd: ``"Vodka"``).
        color (tuple): Màu RGB của nguyên liệu, dùng làm fallback khi thiếu ảnh.
        origin (tuple): Tọa độ ``(x, y)`` gốc trong InventoryPanel,
            dùng để reset về vị trí ban đầu khi nhả chuột.
        rect (pygame.Rect): Rect hiện tại của chai (110×95 px).
        is_dragging (bool): ``True`` nếu chai đang được kéo.
    """
    def __init__(self, x, y, name, color, asset_path):
        # KHAI BÁO CÁC BIẾN CƠ BẢN BỊ THIẾU
        self.name = name
        self.color = color
        self.origin = (x, y)
        self.rect = pygame.Rect(x, y, 110, 95) # Khung hit-box của chai
        self.is_dragging = False               # Khởi tạo trạng thái ban đầu là không bị kéo
        self.relative_y = 0

        # PHẦN LOAD ẢNH BÊN DƯỚI GIỮ NGUYÊN
        import os
        if os.path.exists(asset_path):
            orig_img = pygame.image.load(asset_path).convert_alpha()
            w, h = orig_img.get_size()
            
            max_w, max_h = 80, 55
            scale = min(max_w / w, max_h / h)
            
            new_w, new_h = int(w * scale), int(h * scale)
            self._image = pygame.transform.scale(orig_img, (new_w, new_h))
        else:
            self._image = pygame.Surface((30, 55))
            self._image.fill(self.color)

    def reset_position(self):
        """
        Trả chai về vị trí gốc trong InventoryPanel và tắt trạng thái kéo.

        Được gọi khi người chơi nhả chuột hoặc khi panel bị ẩn.
        """
        self.rect.topleft = self.origin
        self.is_dragging = False

    def draw(self, surface, font, is_pouring=False):
        """
        Vẽ chai lên surface theo trạng thái hiện tại.

        Khi đang kéo: chỉ vẽ ảnh (không có nền), xoay 120° nếu ``is_pouring``.
        Khi không kéo: vẽ khung nền tối, ảnh căn giữa, và tên bên dưới.

        Args:
            surface (pygame.Surface): Surface đích.
            font (pygame.font.Font): Font dùng để vẽ tên nguyên liệu.
            is_pouring (bool): ``True`` khi chuột đang nằm trên vùng Shaker,
                kích hoạt hiệu ứng nghiêng chai. Mặc định ``False``.
        """
        img = self._image
        if is_pouring:
            img = pygame.transform.rotate(self._image, 120)
            img_x = self.rect.centerx - img.get_width() // 2
            img_y = self.rect.centery - img.get_height() // 2
            surface.blit(img, (img_x, img_y))
        elif self.is_dragging:
            # NẾU ĐANG KÉO: Căn giữa chai rượu vào đúng lòng bàn tay (con trỏ chuột)
            img_x = self.rect.centerx - self._image.get_width() // 2
            img_y = self.rect.centery - self._image.get_height() // 2
            surface.blit(self._image, (img_x, img_y))  
            
            surface.blit(self._image, (img_x, img_y))
        else:
            # NẾU NẰM TRONG KHO: Vẽ nguyên box nền và chữ
            pygame.draw.rect(surface, (40, 45, 55), self.rect, border_radius=8)
            pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 1, border_radius=8)

            img_x = self.rect.centerx - self._image.get_width() // 2
            img_y = self.rect.y + 12
            surface.blit(self._image, (img_x, img_y))

            draw_text(surface, self.name, font, C_TEXT,
                      self.rect.centerx, self.rect.bottom - 22, anchor="center")


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
        # 1. Tính toán Word Wrap TRƯỚC để biết số dòng
        text_y = y + 34
        lines = []
        text_color = C_TEXT

        if customer.request_type == "direct":
            lines = [f"Order: {customer.request_data}"]
        else:
            text_color = (200, 200, 160) # Màu hơi vàng cho câu thoại
            mood_text = customer.request_data["text"]
            
            # Thuật toán tách từ và tự động xuống dòng
            words = mood_text.split(' ')
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if small_font.size(test_line)[0] <= self.CARD_W - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line: # Bỏ dòng cuối cùng vào mảng
                lines.append(' '.join(current_line))
                
        lines_drawn = len(lines)

        # 2. Tính toán chiều cao động (Dynamic Height)
        # Chiều cao = Y bắt đầu text (34) + (số dòng * line_height) + khoảng cách bar (8) + độ dày bar (14) + lề dưới (10)
        dynamic_h = 34 + (lines_drawn * 18) + 8 + 14 + 10
        # Đảm bảo chiều cao tối thiểu không bị ngắn hơn CARD_H mặc định (120)
        dynamic_h = max(dynamic_h, self.CARD_H) 

        # 3. Vẽ Nền card dựa trên chiều cao động vừa tính
        bg_color = (50, 40, 20) if customer.is_vip else C_PANEL
        pygame.draw.rect(surface, bg_color,
                         (x, y, self.CARD_W, dynamic_h), border_radius=10)
        border_color = C_GOLD if customer.is_vip else C_PANEL_BORDER
        pygame.draw.rect(surface, border_color,
                         (x, y, self.CARD_W, dynamic_h), 2, border_radius=10)

        # 4. Vẽ Tên + tag VIP
        tag = " [VIP]" if customer.is_vip else ""
        draw_text(surface, customer.name + tag, font,
                  C_GOLD if customer.is_vip else C_TEXT,
                  x + 10, y + 10)

        # 5. Vẽ chữ lên màn hình
        for i, line in enumerate(lines):
            draw_text(surface, line, small_font, text_color,
                      x + 10, text_y + i * 18)

        # 6. Vẽ Thanh kiên nhẫn ở vị trí linh hoạt
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
    Giao diện bình lắc: vẽ chất lỏng dâng lên, xử lý thao tác lắc chuột,
    và hiệu ứng flash khi phục vụ xong.

    Cơ chế lắc: người chơi giữ chuột trên bình và di trái/phải nhanh.
    Mỗi khi ``delta_x > 18 px`` giữa hai frame liên tiếp, ``shake_progress``
    tăng 1. Khi đạt ``SHAKE_THRESHOLD``, lắc hoàn thành.

    Attributes:
        shake_progress (int): Số nhịp lắc hiện tại.
        is_shaking (bool): ``True`` khi đang trong chế độ lắc (chuột đang giữ trên bình).
        RECT (pygame.Rect): Vùng hiển thị bình lắc trên màn hình (tĩnh, class-level).
    """
    # Cố định tọa độ góc trên bên trái của bình lắc
    RECT = pygame.Rect(530, 390, 140, 220)
    BASE_X = 530
    BASE_Y = 300

    def __init__(self):
        self.shake_progress = 0
        self._flash_timer   = 0
        self._flash_color   = None
        self.is_shaking     = False
        self.is_closed      = False
        self._last_mouse_x  = 0

        # --- LOAD ẢNH VÀ GIỮ NGUYÊN TỈ LỆ (KHÔNG BÓP MÉO) ---
        import os
        target_h = 280
        
        front_path = "assets/shaker_front.png"
        if os.path.exists(front_path):
            orig_img = pygame.image.load(front_path).convert_alpha()
            ratio = orig_img.get_width() / orig_img.get_height()
            target_w = int(target_h * ratio)
            self.img_front = pygame.transform.scale(orig_img, (target_w, target_h))
            self.RECT = pygame.Rect(self.BASE_X, self.BASE_Y, target_w, target_h)
        else:
            self.img_front = None
            self.RECT = pygame.Rect(self.BASE_X, self.BASE_Y, 140, 220)

        closed_path = "assets/shaker_closed.png"
        if os.path.exists(closed_path):
            orig_closed = pygame.image.load(closed_path).convert_alpha()
            # Tweak size of closed shaker to match open shaker
            scale_factor = 0.82
            target_h_c = int(target_h * scale_factor)
            ratio_c = orig_closed.get_width() / orig_closed.get_height()
            target_w_c = int(target_h_c * ratio_c)
            self.img_closed = pygame.transform.scale(orig_closed, (target_w_c, target_h_c))
        else:
            self.img_closed = None

        self.btn_lid_rect = pygame.Rect(self.RECT.right + 10, self.RECT.bottom - 40, 80, 40)

>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def handle_shake(self, event):
        if not self.is_closed:
            return False

        self.RECT.center = event.pos

        delta = abs(event.pos[0] - self._last_mouse_x)
        if delta > 18:
            self.shake_progress += 1
            self._last_mouse_x = event.pos[0]
            
        if self.shake_progress >= SHAKE_THRESHOLD:
            self.shake_progress = 0
            self.stop_shake()
            return True
<<<<<<< HEAD
        return False

=======
        return False

>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def start_shake(self, mouse_x):
        if self.is_closed:
            self.is_shaking    = True
            self._last_mouse_x = mouse_x
            sound_mgr.start_shaking()

    def stop_shake(self):
        self.is_shaking = False
        sound_mgr.stop_shaking()
        self.RECT.topleft = (self.BASE_X, self.BASE_Y)
<<<<<<< HEAD

    def flash(self, color):
        self._flash_color = color
        self._flash_timer = 400

    def update(self, dt_ms):
        if self._flash_timer > 0:
            self._flash_timer -= dt_ms

    def draw(self, surface, current_volume, max_volume, mixed_color, font):
        # 1. NẾU CHƯA CÓ ẢNH THÌ MỚI VẼ CÁI HỘP ĐEN CŨ
        if not self.img_front:
            pygame.draw.rect(surface, (20, 25, 30), self.RECT, border_radius=14)

        # 2. VẼ DÒNG NƯỚC (Ép cho lọt thỏm vào ruột ly)
        if current_volume > 0 and mixed_color is not None and not self.is_shaking:
            ratio = min(1.0, current_volume / max_volume)
            
            # ---> BẢNG ĐIỀU KHIỂN NƯỚC CỦA M Ở ĐÂY <---
            # Nếu nước bị lòi ra ngoài, m tăng/giảm 4 con số này vài pixel cho nó khít
            pad_left = 30    # Cách mép trái bao nhiêu?
            pad_right = 30   # Cách mép phải bao nhiêu?
            pad_bottom = 20  # Cách đáy ly bao nhiêu?
            pad_top = 120    # Cách miệng ly bao nhiêu (để rót đầy ko bị trào)?
            
            water_max_h = self.RECT.h - pad_top - pad_bottom
            liquid_h = int(water_max_h * ratio)
            
            if liquid_h > 0:
                chunk_size = 4 
                start_x = self.RECT.x + pad_left
                end_x = self.RECT.right - pad_right
                base_y = self.RECT.bottom - pad_bottom

                for cx in range(start_x, end_x, chunk_size):
                    # Cắt gọn pixel dư để ko đâm thủng vách ly bên phải
                    w = min(chunk_size, end_x - cx) 
                    
                    wave = math.sin(time.time() * 12 + cx * 0.5) * 3
                    noise = random.randint(-1, 1) if current_volume < max_volume else 0
                    
                    col_h = liquid_h + int(wave) + noise
                    if col_h < 0: col_h = 0 
                    
                    col_rect = pygame.Rect(cx, base_y - col_h, w, col_h)
                    pygame.draw.rect(surface, mixed_color, col_rect)

        # 3. VẼ CÁI LY ĐÈ LÊN DÒNG NƯỚC
        current_img = self.img_closed if self.is_closed else self.img_front
        if current_img:
            # Nếu đang lắc, xoay ngang bình shaker
            if self.is_shaking:
                current_img = pygame.transform.rotate(current_img, -90)
                
            img_rect = current_img.get_rect(center=self.RECT.center)
            if self.is_closed:
                # Tăng X thì dịch sang phải, Giảm X thì dịch sang trái
                img_rect.x += -5    
                
                # Tăng Y thì dịch xuống dưới, Giảm Y thì dịch lên trên
                img_rect.y -= -15
            surface.blit(current_img, img_rect.topleft)
            # Hiệu ứng flash
            if self._flash_timer > 0 and self._flash_color:
                flash_surf = pygame.Surface(current_img.get_size(), pygame.SRCALPHA)
                flash_surf.blit(current_img, (0, 0))
                flash_surf.fill((*self._flash_color, 100), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(flash_surf, img_rect.topleft)
        else:
            border_color = self._flash_color if self._flash_timer > 0 else C_TEXT_DIM
            pygame.draw.rect(surface, border_color, self.RECT, 3, border_radius=14)
            if self.is_closed:
                pygame.draw.rect(surface, (100, 100, 100), (self.RECT.x, self.RECT.y - 20, self.RECT.w, 30), border_radius=5)

        # Nút Đóng nắp
        if not self.is_shaking:
            self.btn_lid_rect.topleft = (self.RECT.right + 10, self.RECT.bottom - 40)
            btn_color = C_SUCCESS if self.is_closed else C_PANEL
            pygame.draw.rect(surface, btn_color, self.btn_lid_rect, border_radius=6)
            pygame.draw.rect(surface, C_PANEL_BORDER, self.btn_lid_rect, 2, border_radius=6)
            draw_text(surface, "LID", font, C_TEXT, self.btn_lid_rect.centerx, self.btn_lid_rect.centery, anchor="center")

        # 4. CHỮ VÀ UI
        draw_text(surface, "SHAKER", font, C_TEXT_DIM, self.RECT.centerx, self.RECT.y - 20, anchor="center")

        vol_text = f"{int(current_volume)}/{int(max_volume)} ml"
        text_color = (255, 255, 255) if current_volume > 0 else C_TEXT_DIM
        
        # Đổ bóng chữ viền đen
        draw_text(surface, vol_text, font, (0, 0, 0), self.RECT.centerx + 2, self.RECT.centery + 2, anchor="center") 
        draw_text(surface, vol_text, font, text_color, self.RECT.centerx, self.RECT.centery, anchor="center") 

        # Thanh lắc
        if self.is_shaking or self.shake_progress > 0:
            bar_x = self.RECT.x
            bar_y = self.RECT.bottom + 15
            bar_w = self.RECT.w
            pygame.draw.rect(surface, C_PANEL_BORDER, (bar_x, bar_y, bar_w, 12), border_radius=5)
            fill = int(bar_w * self.shake_progress / SHAKE_THRESHOLD)
            pygame.draw.rect(surface, C_SUCCESS, (bar_x, bar_y, fill, 12), border_radius=5)

# ══════════════════════════════════════════════════════════
#  5. SEARCH BAR — Trie autocomplete
# ══════════════════════════════════════════════════════════
class SearchBar:
    """
    Giao diện thanh tìm kiếm thông minh (Search Bar).
    Hỗ trợ gõ phím, bôi đen (Ctrl+A), cuộn danh sách (Scroll) và tự động 
    đề xuất (Autocomplete) công thức dựa trên thuật toán Trie.
    """
    RECT  = pygame.Rect(30, 140, 500, 36)
    MAX_SUGGESTIONS = 5

=======

    def flash(self, color):
        self._flash_color = color
        self._flash_timer = 400

    def update(self, dt_ms):
        if self._flash_timer > 0:
            self._flash_timer -= dt_ms

    def draw(self, surface, current_volume, max_volume, mixed_color, font):
        # 1. NẾU CHƯA CÓ ẢNH THÌ MỚI VẼ CÁI HỘP ĐEN CŨ
        if not self.img_front:
            pygame.draw.rect(surface, (20, 25, 30), self.RECT, border_radius=14)

        # 2. VẼ DÒNG NƯỚC (Ép cho lọt thỏm vào ruột ly)
        if current_volume > 0 and mixed_color is not None and not self.is_shaking:
            ratio = min(1.0, current_volume / max_volume)
            
            # ---> BẢNG ĐIỀU KHIỂN NƯỚC CỦA M Ở ĐÂY <---
            # Nếu nước bị lòi ra ngoài, m tăng/giảm 4 con số này vài pixel cho nó khít
            pad_left = 30    # Cách mép trái bao nhiêu?
            pad_right = 30   # Cách mép phải bao nhiêu?
            pad_bottom = 20  # Cách đáy ly bao nhiêu?
            pad_top = 120    # Cách miệng ly bao nhiêu (để rót đầy ko bị trào)?
            
            water_max_h = self.RECT.h - pad_top - pad_bottom
            liquid_h = int(water_max_h * ratio)
            
            if liquid_h > 0:
                chunk_size = 4 
                start_x = self.RECT.x + pad_left
                end_x = self.RECT.right - pad_right
                base_y = self.RECT.bottom - pad_bottom

                for cx in range(start_x, end_x, chunk_size):
                    # Cắt gọn pixel dư để ko đâm thủng vách ly bên phải
                    w = min(chunk_size, end_x - cx) 
                    
                    wave = math.sin(time.time() * 12 + cx * 0.5) * 3
                    noise = random.randint(-1, 1) if current_volume < max_volume else 0
                    
                    col_h = liquid_h + int(wave) + noise
                    if col_h < 0: col_h = 0 
                    
                    col_rect = pygame.Rect(cx, base_y - col_h, w, col_h)
                    pygame.draw.rect(surface, mixed_color, col_rect)

        # 3. VẼ CÁI LY ĐÈ LÊN DÒNG NƯỚC
        current_img = self.img_closed if self.is_closed else self.img_front
        if current_img:
            # Nếu đang lắc, xoay ngang bình shaker
            if self.is_shaking:
                current_img = pygame.transform.rotate(current_img, -90)
                
            img_rect = current_img.get_rect(center=self.RECT.center)
            if self.is_closed:
                # Tăng X thì dịch sang phải, Giảm X thì dịch sang trái
                img_rect.x += -5    
                
                # Tăng Y thì dịch xuống dưới, Giảm Y thì dịch lên trên
                img_rect.y -= -15
            surface.blit(current_img, img_rect.topleft)
            # Hiệu ứng flash
            if self._flash_timer > 0 and self._flash_color:
                flash_surf = pygame.Surface(current_img.get_size(), pygame.SRCALPHA)
                flash_surf.blit(current_img, (0, 0))
                flash_surf.fill((*self._flash_color, 100), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(flash_surf, img_rect.topleft)
        else:
            border_color = self._flash_color if self._flash_timer > 0 else C_TEXT_DIM
            pygame.draw.rect(surface, border_color, self.RECT, 3, border_radius=14)
            if self.is_closed:
                pygame.draw.rect(surface, (100, 100, 100), (self.RECT.x, self.RECT.y - 20, self.RECT.w, 30), border_radius=5)

        # Nút Đóng nắp
        if not self.is_shaking:
            self.btn_lid_rect.topleft = (self.RECT.right + 10, self.RECT.bottom - 40)
            btn_color = C_SUCCESS if self.is_closed else C_PANEL
            pygame.draw.rect(surface, btn_color, self.btn_lid_rect, border_radius=6)
            pygame.draw.rect(surface, C_PANEL_BORDER, self.btn_lid_rect, 2, border_radius=6)
            draw_text(surface, "LID", font, C_TEXT, self.btn_lid_rect.centerx, self.btn_lid_rect.centery, anchor="center")

        # 4. CHỮ VÀ UI
        draw_text(surface, "SHAKER", font, C_TEXT_DIM, self.RECT.centerx, self.RECT.y - 20, anchor="center")

        vol_text = f"{int(current_volume)}/{int(max_volume)} ml"
        text_color = (255, 255, 255) if current_volume > 0 else C_TEXT_DIM
        
        # Đổ bóng chữ viền đen
        draw_text(surface, vol_text, font, (0, 0, 0), self.RECT.centerx + 2, self.RECT.centery + 2, anchor="center") 
        draw_text(surface, vol_text, font, text_color, self.RECT.centerx, self.RECT.centery, anchor="center") 

        # Thanh lắc
        if self.is_shaking or self.shake_progress > 0:
            bar_x = self.RECT.x
            bar_y = self.RECT.bottom + 15
            bar_w = self.RECT.w
            pygame.draw.rect(surface, C_PANEL_BORDER, (bar_x, bar_y, bar_w, 12), border_radius=5)
            fill = int(bar_w * self.shake_progress / SHAKE_THRESHOLD)
            pygame.draw.rect(surface, C_SUCCESS, (bar_x, bar_y, fill, 12), border_radius=5)

# ══════════════════════════════════════════════════════════
#  5. SEARCH BAR — Trie autocomplete
# ══════════════════════════════════════════════════════════
class SearchBar:
    """
    Giao diện thanh tìm kiếm thông minh (Search Bar).
    Hỗ trợ gõ phím, bôi đen (Ctrl+A), cuộn danh sách (Scroll) và tự động 
    đề xuất (Autocomplete) công thức dựa trên thuật toán Trie.
    """
    RECT  = pygame.Rect(30, 140, 500, 36)
    MAX_SUGGESTIONS = 5

>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def __init__(self):
        """Khởi tạo các thông số hình học và trạng thái mặc định của thanh tìm kiếm."""
        self.text          = ""
        self.active        = False
        self.results       = []   
<<<<<<< HEAD
        self.scroll_offset = 0    
        self.select_all    = False  # ---> THÊM CỜ BÔI ĐEN
        self.close_btn_rect = pygame.Rect(self.RECT.right + 10, self.RECT.y, 36, 36)
        
=======
        self.scroll_offset = 0    
        self.select_all    = False  # ---> THÊM CỜ BÔI ĐEN
        self.close_btn_rect = pygame.Rect(self.RECT.right + 10, self.RECT.y, 36, 36)
        
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        # Thêm khung cho nút Đóng (Nằm bên phải thanh search)
        self.close_btn_rect = pygame.Rect(self.RECT.right + 10, self.RECT.y, 36, 36)

    def _get_dropdown_rect(self):
        drop_h = min(len(self.results), self.MAX_SUGGESTIONS) * 48
        return pygame.Rect(self.RECT.x, self.RECT.bottom, self.RECT.w, drop_h)
<<<<<<< HEAD

    def handle_event(self, event, search_fn):
        """
        Bắt sự kiện bàn phím và chuột cho thanh tìm kiếm.

        Args:
            event (pygame.event.Event): Sự kiện từ Pygame.
            search_fn (callable): Hàm callback truyền vào từ khóa và trả về kết quả tìm kiếm.

        Returns:
            dict | None: Trả về dict chứa lệnh ghim công thức (vd: {"action": "pin", ...}) nếu click chọn, ngược lại trả về None.
        """
=======

    def handle_event(self, event, search_fn):
        """
        Bắt sự kiện bàn phím và chuột cho thanh tìm kiếm.

        Args:
            event (pygame.event.Event): Sự kiện từ Pygame.
            search_fn (callable): Hàm callback truyền vào từ khóa và trả về kết quả tìm kiếm.

        Returns:
            dict | None: Trả về dict chứa lệnh ghim công thức (vd: {"action": "pin", ...}) nếu click chọn, ngược lại trả về None.
        """
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Click chuột trái
                # Click vào thanh Search để bật
                if self.RECT.collidepoint(event.pos):
                    if not self.active:
                        self.active = True
                        self.text = ""
                        self.results = sorted(search_fn(""), key=lambda x: x[0])
                        self.scroll_offset = 0
                    self.select_all = False
                
                # Click vào nút X để Đóng
                elif self.active and self.close_btn_rect.collidepoint(event.pos):
                    self.active = False
                    self.results = []
                    self.text = ""
                    self.select_all = False
                    
                # --- CHỨC NĂNG MỚI: CLICK VÀO CÔNG THỨC ĐỂ GHIM ---
                elif self.active and self.results:
                    drop_y = self.RECT.bottom + 4
                    visible_results = self.results[self.scroll_offset : self.scroll_offset + self.MAX_SUGGESTIONS]
<<<<<<< HEAD
                    for i, (name, data) in enumerate(visible_results):
=======
                    for i, (name, data) in enumerate(visible_results):
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
                        row = pygame.Rect(self.RECT.x, drop_y + i * 48, self.RECT.w, 44)
                        if row.collidepoint(event.pos):
                            self.active = False # Tự đóng thanh search
                            self.text = ""
                            self.select_all = False
                            # Trả về tín hiệu yêu cầu ghim công thức
                            return {"action": "pin", "name": name, "data": data}

                    # Click ra ngoài toàn bộ vùng search/dropdown thì thoát tìm kiếm ngay
                    if not self._get_dropdown_rect().collidepoint(event.pos):
                        self.active = False
                        self.results = []
                        self.select_all = False
                elif self.active:
                    self.active = False
                    self.results = []
                    self.select_all = False

            # --- FIX SCROLL: Chỉ cuộn khi trỏ chuột vào danh sách ---
            elif event.button in (4, 5) and self.active:
                drop_rect = self._get_dropdown_rect()
                
                # CHỈ cuộn nếu chuột nằm trên thanh search hoặc danh sách xổ xuống
                if self.RECT.collidepoint(event.pos) or drop_rect.collidepoint(event.pos):
                    if event.button == 4: # Cuộn lên
                        self.scroll_offset = max(0, self.scroll_offset - 1)
<<<<<<< HEAD
                    elif event.button == 5: # Cuộn xuống
                        max_scroll = max(0, len(self.results) - self.MAX_SUGGESTIONS)
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self.active:
                    self.active = True
                    self.text = ""
                    self.results = sorted(search_fn(""), key=lambda x: x[0])
                    self.scroll_offset = 0
            
            elif self.active:
                mods = pygame.key.get_mods()
                
                # ---> BẮT TỔ HỢP CTRL + A
                if event.key == pygame.K_a and (mods & pygame.KMOD_CTRL):
                    self.select_all = bool(self.text)
                    return None

                # ---> XỬ LÝ GÕ / XÓA PHÍM KHI ĐANG BÔI ĐEN HOẶC BÌNH THƯỜNG
                if event.key == pygame.K_BACKSPACE:
                    if self.select_all:
                        self.text = ""
                        self.select_all = False
                    else:
                        self.text = self.text[:-1]
                elif event.unicode.isprintable() and not (mods & pygame.KMOD_CTRL):
                    if self.select_all:
                        self.text = ""  # Gõ đè lên chỗ bôi đen
                        self.select_all = False
                    self.text += event.unicode
                
                self.results = sorted(search_fn(self.text), key=lambda x: x[0])
                self.scroll_offset = 0
                
        return None

    def draw(self, surface, font, small_font):
        """
        Vẽ thanh tìm kiếm, con trỏ nhấp nháy và danh sách xổ xuống (nếu đang active).

        Args:
            surface (pygame.Surface): Surface đích để vẽ.
            font (pygame.font.Font): Font chữ lớn cho thanh gõ.
            small_font (pygame.font.Font): Font chữ nhỏ cho danh sách kết quả.
        """
        border = C_SUCCESS if self.active else C_PANEL_BORDER
        pygame.draw.rect(surface, C_PANEL, self.RECT, border_radius=6)
        pygame.draw.rect(surface, border, self.RECT, 2, border_radius=6)

        display = self.text
        if not self.text and self.active:
            display = "Type name or #tag..."
        elif not self.text and not self.active:
            display = "RECIPE..."
            
        color   = C_TEXT if self.active and self.text else C_TEXT_DIM
        cursor  = "|" if self.active and time.time() % 1 > 0.5 and not self.select_all else ""
        
        # ---> VẼ KHUNG NỀN XANH DƯƠNG NẾU ĐANG BÔI ĐEN (Ctrl+A)
        if self.select_all and self.active and self.text:
            text_surf = font.render(self.text, True, C_TEXT)
            bg_rect = pygame.Rect(self.RECT.x + 8, self.RECT.y + 8, text_surf.get_width(), text_surf.get_height())
            pygame.draw.rect(surface, (50, 100, 200), bg_rect) # Xanh bôi đen

        draw_text(surface, display + cursor, font, color, self.RECT.x + 8, self.RECT.y + 8)

        # Vẽ nút X nếu bảng đang mở
        if self.active:
            pygame.draw.rect(surface, C_ALERT, self.close_btn_rect, border_radius=6)
            draw_text(surface, "X", font, C_TEXT, 
                      self.close_btn_rect.centerx + 1, self.close_btn_rect.centery, anchor="center")

        if self.results and self.active:
            drop_y = self.RECT.bottom + 4
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

class InventoryPanel:
    """
    Giao diện kho chứa nguyên liệu (Inventory).
    Hỗ trợ phân loại qua các Tab, thanh cuộn (Scrollbar) dọc và ô tìm kiếm nội bộ.
    """
    RECT = pygame.Rect(940, 150, 300, 460)

    def __init__(self, sorted_inventory):
        """
        Khởi tạo kho nguyên liệu.

        Args:
            sorted_inventory (list[dict]): Danh sách nguyên liệu đã được sắp xếp sẵn.
        """
        self.full_inventory = sorted_inventory
        self.search_trie = Trie()
        self.current_filter = "All"
        self.filters = ["All", "base", "mixer", "modifier", "garnish"] 
        self.tab_rects = []
        self.tab_font = load_font(FONT_PATH, 14)
        
        # --- Khai báo thanh tìm kiếm nguyên liệu ---
=======
                    elif event.button == 5: # Cuộn xuống
                        max_scroll = max(0, len(self.results) - self.MAX_SUGGESTIONS)
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self.active:
                    self.active = True
                    self.text = ""
                    self.results = sorted(search_fn(""), key=lambda x: x[0])
                    self.scroll_offset = 0
            
            elif self.active:
                mods = pygame.key.get_mods()
                
                # ---> BẮT TỔ HỢP CTRL + A
                if event.key == pygame.K_a and (mods & pygame.KMOD_CTRL):
                    self.select_all = bool(self.text)
                    return None

                # ---> XỬ LÝ GÕ / XÓA PHÍM KHI ĐANG BÔI ĐEN HOẶC BÌNH THƯỜNG
                if event.key == pygame.K_BACKSPACE:
                    if self.select_all:
                        self.text = ""
                        self.select_all = False
                    else:
                        self.text = self.text[:-1]
                elif event.unicode.isprintable() and not (mods & pygame.KMOD_CTRL):
                    if self.select_all:
                        self.text = ""  # Gõ đè lên chỗ bôi đen
                        self.select_all = False
                    self.text += event.unicode
                
                self.results = sorted(search_fn(self.text), key=lambda x: x[0])
                self.scroll_offset = 0
                
        return None

    def draw(self, surface, font, small_font):
        """
        Vẽ thanh tìm kiếm, con trỏ nhấp nháy và danh sách xổ xuống (nếu đang active).

        Args:
            surface (pygame.Surface): Surface đích để vẽ.
            font (pygame.font.Font): Font chữ lớn cho thanh gõ.
            small_font (pygame.font.Font): Font chữ nhỏ cho danh sách kết quả.
        """
        border = C_SUCCESS if self.active else C_PANEL_BORDER
        pygame.draw.rect(surface, C_PANEL, self.RECT, border_radius=6)
        pygame.draw.rect(surface, border, self.RECT, 2, border_radius=6)

        display = self.text
        if not self.text and self.active:
            display = "Type name or #tag..."
        elif not self.text and not self.active:
            display = "RECIPE..."
            
        color   = C_TEXT if self.active and self.text else C_TEXT_DIM
        cursor  = "|" if self.active and time.time() % 1 > 0.5 and not self.select_all else ""
        
        # ---> VẼ KHUNG NỀN XANH DƯƠNG NẾU ĐANG BÔI ĐEN (Ctrl+A)
        if self.select_all and self.active and self.text:
            text_surf = font.render(self.text, True, C_TEXT)
            bg_rect = pygame.Rect(self.RECT.x + 8, self.RECT.y + 8, text_surf.get_width(), text_surf.get_height())
            pygame.draw.rect(surface, (50, 100, 200), bg_rect) # Xanh bôi đen

        draw_text(surface, display + cursor, font, color, self.RECT.x + 8, self.RECT.y + 8)

        # Vẽ nút X nếu bảng đang mở
        if self.active:
            pygame.draw.rect(surface, C_ALERT, self.close_btn_rect, border_radius=6)
            draw_text(surface, "X", font, C_TEXT, 
                      self.close_btn_rect.centerx + 1, self.close_btn_rect.centery, anchor="center")

        if self.results and self.active:
            drop_y = self.RECT.bottom + 4
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

class InventoryPanel:
    """
    Giao diện kho chứa nguyên liệu (Inventory).
    Hỗ trợ phân loại qua các Tab, thanh cuộn (Scrollbar) dọc và ô tìm kiếm nội bộ.
    """
    RECT = pygame.Rect(940, 150, 300, 460)

    def __init__(self, sorted_inventory):
        """
        Khởi tạo kho nguyên liệu.

        Args:
            sorted_inventory (list[dict]): Danh sách nguyên liệu đã được sắp xếp sẵn.
        """
        self.full_inventory = sorted_inventory
        self.search_trie = Trie()
        self.current_filter = "All"
        self.filters = ["All", "base", "mixer", "modifier", "garnish"] 
        self.tab_rects = []
        self.tab_font = load_font(FONT_PATH, 14)
        
        # --- Khai báo thanh tìm kiếm nguyên liệu ---
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        self.search_text = ""
        self.search_active = False
        self.search_select_all = False
        # Thanh tìm kiếm nằm ngay dưới chữ INGREDIENTS
        self.search_rect = pygame.Rect(self.RECT.x + 12, self.RECT.y + 35, self.RECT.w - 24, 25)
<<<<<<< HEAD
        
        padding = 12       
        spacing = 4        
        tab_w = (self.RECT.w - 2 * padding - spacing * (len(self.filters) - 1)) / len(self.filters)
        
        for i, f in enumerate(self.filters):
            tx = self.RECT.x + padding + i * (tab_w + spacing)
            # Dời vị trí tab xuống Y + 68 để chừa chỗ cho search box
            rect = pygame.Rect(tx, self.RECT.y + 68, tab_w, 22)
            self.tab_rects.append((f, rect))

=======
        
        padding = 12       
        spacing = 4        
        tab_w = (self.RECT.w - 2 * padding - spacing * (len(self.filters) - 1)) / len(self.filters)
        
        for i, f in enumerate(self.filters):
            tx = self.RECT.x + padding + i * (tab_w + spacing)
            # Dời vị trí tab xuống Y + 68 để chừa chỗ cho search box
            rect = pygame.Rect(tx, self.RECT.y + 68, tab_w, 22)
            self.tab_rects.append((f, rect))

>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        self.bottles = []
        self.scroll_offset = 0
        self.max_scroll = 0
        self._rebuild_search_trie()
        self._build()

    def _rebuild_search_trie(self):
        self.search_trie = Trie()
        for item in self.full_inventory:
            self.search_trie.insert(item["name"], item)

    def _build(self, sorted_inventory=None):
<<<<<<< HEAD
        """
        Xây dựng lại danh sách chai (bottles) hiển thị dựa trên bộ lọc Tab và thanh tìm kiếm.
        
        Args:
            sorted_inventory (list[dict] | None): Cập nhật danh sách mới (nếu có).
        """
=======
        """
        Xây dựng lại danh sách chai (bottles) hiển thị dựa trên bộ lọc Tab và thanh tìm kiếm.
        
        Args:
            sorted_inventory (list[dict] | None): Cập nhật danh sách mới (nếu có).
        """
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        if sorted_inventory is not None:
            self.full_inventory = sorted_inventory
            self._rebuild_search_trie()
            
        self.bottles.clear()
        self.scroll_offset = 0 
        
        if self.search_text:
            candidate_items = [item for _, item in self.search_trie.autocomplete(self.search_text)]
        else:
            candidate_items = self.full_inventory

        filtered_items = []
        for item in candidate_items:
            if self.current_filter == "All" or item.get("type") == self.current_filter:
                filtered_items.append(item)
<<<<<<< HEAD
        
        box_w = 110       
        box_h = 95        
        col_spacing = 30  
        row_spacing = 15  
        
        base_x = self.RECT.x + 25 
        current_y = 0

        for i, item in enumerate(filtered_items):
            col = i % 2
            row = i // 2
            bx = base_x + col * (box_w + col_spacing)
            by = current_y + row * (box_h + row_spacing)
            
            b = Bottle(bx, by, item["name"], item["color"], item["asset"])
            b.relative_y = by
            self.bottles.append(b)
            
        total_rows = (len(filtered_items) + 1) // 2
        total_height = total_rows * (box_h + row_spacing)
        # Thu nhỏ clip_h lại do nhường không gian cho search box
        clip_h = self.RECT.h - 100 
        
        self.max_scroll = max(0, total_height - clip_h + 10)

    def handle_event(self, event):
        """
        Xử lý sự kiện click chuyển Tab, cuộn chuột và gõ phím tìm kiếm nguyên liệu.

        Args:
            event (pygame.event.Event): Sự kiện từ Pygame.
        """
=======
        
        box_w = 110       
        box_h = 95        
        col_spacing = 30  
        row_spacing = 15  
        
        base_x = self.RECT.x + 25 
        current_y = 0

        for i, item in enumerate(filtered_items):
            col = i % 2
            row = i // 2
            bx = base_x + col * (box_w + col_spacing)
            by = current_y + row * (box_h + row_spacing)
            
            b = Bottle(bx, by, item["name"], item["color"], item["asset"])
            b.relative_y = by
            self.bottles.append(b)
            
        total_rows = (len(filtered_items) + 1) // 2
        total_height = total_rows * (box_h + row_spacing)
        # Thu nhỏ clip_h lại do nhường không gian cho search box
        clip_h = self.RECT.h - 100 
        
        self.max_scroll = max(0, total_height - clip_h + 10)

    def handle_event(self, event):
        """
        Xử lý sự kiện click chuyển Tab, cuộn chuột và gõ phím tìm kiếm nguyên liệu.

        Args:
            event (pygame.event.Event): Sự kiện từ Pygame.
        """
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.search_rect.collidepoint(event.pos):
                self.search_active = True
                self.search_select_all = False
                return
            else:
                self.search_active = False
                self.search_select_all = False

        if event.type == pygame.MOUSEBUTTONDOWN and self.RECT.collidepoint(event.pos):
            for f, rect in self.tab_rects:
                if rect.collidepoint(event.pos):
                    if self.current_filter != f:
                        self.current_filter = f
                        self._build() 
<<<<<<< HEAD
                    return 
            
            if event.button == 4: 
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.button == 5: 
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                
=======
                    return 
            
            if event.button == 4: 
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.button == 5: 
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        # Xử lý gõ phím khi đang active trong thanh search kho đồ
        elif event.type == pygame.KEYDOWN and self.search_active:
            mods = pygame.key.get_mods()
            if event.key == pygame.K_a and (mods & pygame.KMOD_CTRL):
                self.search_select_all = bool(self.search_text)
                return
            if event.key == pygame.K_BACKSPACE:
                if self.search_select_all:
                    self.search_text = ""
                    self.search_select_all = False
                else:
                    self.search_text = self.search_text[:-1]
            elif event.unicode.isprintable() and not (mods & pygame.KMOD_CTRL):
                if self.search_select_all:
                    self.search_text = ""
                    self.search_select_all = False
                self.search_text += event.unicode
            self._build() # Gọi lại build để filter ngay lập tức
<<<<<<< HEAD

    def draw(self, surface, font, small_font):
        """
        Vẽ toàn bộ kho, bao gồm khung, tab, ô search, thanh cuộn và các chai rượu.
        Dùng kỹ thuật surface.set_clip() để không vẽ tràn ra ngoài khung.

        Args:
            surface (pygame.Surface): Surface đích.
            font (pygame.font.Font): Font chữ dùng cho Tab và tiêu đề.
            small_font (pygame.font.Font): Font chữ dùng cho tên chai rượu.
        """
        pygame.draw.rect(surface, C_PANEL, self.RECT, border_radius=12)
        pygame.draw.rect(surface, C_PANEL_BORDER, self.RECT, 2, border_radius=12)
        
        draw_text(surface, "INGREDIENTS", font, C_TEXT_DIM,
                  self.RECT.centerx, self.RECT.y + 12, anchor="midtop")
                  
        # Vẽ thanh search của kho
        search_color = C_SUCCESS if self.search_active else C_PANEL_BORDER
        pygame.draw.rect(surface, (20, 24, 30), self.search_rect, border_radius=4)
        pygame.draw.rect(surface, search_color, self.search_rect, 1, border_radius=4)
        
=======

    def draw(self, surface, font, small_font):
        """
        Vẽ toàn bộ kho, bao gồm khung, tab, ô search, thanh cuộn và các chai rượu.
        Dùng kỹ thuật surface.set_clip() để không vẽ tràn ra ngoài khung.

        Args:
            surface (pygame.Surface): Surface đích.
            font (pygame.font.Font): Font chữ dùng cho Tab và tiêu đề.
            small_font (pygame.font.Font): Font chữ dùng cho tên chai rượu.
        """
        pygame.draw.rect(surface, C_PANEL, self.RECT, border_radius=12)
        pygame.draw.rect(surface, C_PANEL_BORDER, self.RECT, 2, border_radius=12)
        
        draw_text(surface, "INGREDIENTS", font, C_TEXT_DIM,
                  self.RECT.centerx, self.RECT.y + 12, anchor="midtop")
                  
        # Vẽ thanh search của kho
        search_color = C_SUCCESS if self.search_active else C_PANEL_BORDER
        pygame.draw.rect(surface, (20, 24, 30), self.search_rect, border_radius=4)
        pygame.draw.rect(surface, search_color, self.search_rect, 1, border_radius=4)
        
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        display_txt = self.search_text + ("|" if self.search_active and time.time() % 1 > 0.5 and not self.search_select_all else "")
        if not self.search_text and not self.search_active:
            display_txt = "Search..."

        if self.search_select_all and self.search_active and self.search_text:
            text_surf = self.tab_font.render(self.search_text, True, C_TEXT)
            bg_rect = pygame.Rect(self.search_rect.x + 6, self.search_rect.y + 4, text_surf.get_width(), text_surf.get_height())
            pygame.draw.rect(surface, (50, 100, 200), bg_rect)
            
        draw_text(surface, display_txt, self.tab_font, C_TEXT if self.search_text or self.search_active else C_TEXT_DIM,
                  self.search_rect.x + 6, self.search_rect.centery, anchor="midleft")
<<<<<<< HEAD

        for f, rect in self.tab_rects:
            is_active = (f == self.current_filter)
            color = C_SUCCESS if is_active else C_PANEL_BORDER
            pygame.draw.rect(surface, color, rect, border_radius=4)
            display_text = "MODS" if f == "modifier" else f.upper()
            draw_text(surface, display_text, self.tab_font, C_TEXT if is_active else C_TEXT_DIM,
                      rect.centerx, rect.centery, anchor="center")

        # Cắt clip rect thụt xuống Y + 95
        clip_rect = pygame.Rect(self.RECT.x, self.RECT.y + 95, self.RECT.w, self.RECT.h - 100)
        surface.set_clip(clip_rect)

        dragging_bottle = None

        for b in self.bottles:
            if not b.is_dragging:
                # Cộng b.rect.y thêm để vừa với khung clip_rect mới
                b.rect.y = self.RECT.y + 100 + b.relative_y - self.scroll_offset
                b.origin = (b.rect.x, b.rect.y)
                
                if b.rect.bottom > clip_rect.top and b.rect.top < clip_rect.bottom:
                    b.draw(surface, small_font)
            else:
                dragging_bottle = b

        surface.set_clip(None)

        if self.max_scroll > 0:
            bar_x = self.RECT.right - 12
            bar_y = clip_rect.y + 5
            bar_h = clip_rect.h - 10
            pygame.draw.rect(surface, C_PANEL_BORDER, (bar_x, bar_y, 6, bar_h), border_radius=3)
            thumb_h = max(20, (clip_rect.h / (self.max_scroll + clip_rect.h)) * bar_h)
            thumb_y = bar_y + (self.scroll_offset / self.max_scroll) * (bar_h - thumb_h)
            pygame.draw.rect(surface, C_TEXT_DIM, (bar_x, thumb_y, 6, thumb_h), border_radius=3)

       

    def get_dragging(self):
        """
        Lấy đối tượng chai rượu đang được người chơi nhấc lên (kéo thả).

        Returns:
            Bottle | None: Đối tượng chai đang bị kéo, hoặc None.
        """
        return next((b for b in self.bottles if b.is_dragging), None)

# ══════════════════════════════════════════════════════════
#  7. DISCOVERY BANNER — thông báo khám phá công thức mới
# ══════════════════════════════════════════════════════════
class DiscoveryBanner:
    def __init__(self):
        self._msg   = None
        self._timer = 0   # ms

    def show(self, drink_name):
        self._msg   = f"DISCOVERED: {drink_name}!"
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
# ui.py

class Button:
    """Nút bấm UI cơ bản hỗ trợ đổi màu khi di chuột vào (hover) và bắt sự kiện click."""
    def __init__(self, x, y, w, h, text, color, hover_color):
        """Khởi tạo thông số hình học, màu sắc và text hiển thị của nút."""
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface, font):
        """Vẽ nút bấm và chữ căn giữa, tự đổi màu theo trạng thái hover."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 2, border_radius=8)
        draw_text(surface, self.text, font, C_TEXT, 
                  self.rect.centerx, self.rect.centery, anchor="center")

    def handle_event(self, event):
        """
        Xử lý sự kiện di chuột và click.

        Returns:
            bool: True nếu nút được nhấn chuột trái.
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
# ══════════════════════════════════════════════════════════
#  Thanh trượt âm lượng (Volume Slider)
# ══════════════════════════════════════════════════════════
class VolumeSlider:
    """Thanh trượt UI để điều chỉnh giá trị từ 0.0 đến 1.0 (âm lượng)."""
    def __init__(self, x, y, w, h, label, initial_val):
        """Khởi tạo kích thước, nhãn dán và giá trị ban đầu."""
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.val = initial_val  # Giá trị từ 0.0 đến 1.0
        self.is_dragging = False

    def draw(self, surface, font, small_font):
        """Vẽ thanh trượt, nút kéo (knob) và giá trị % hiện tại."""
        # Vẽ nhãn (MUSIC / SFX)
        draw_text(surface, self.label, font, C_TEXT, self.rect.x - 90, self.rect.centery, anchor="midleft")
        
        # Vẽ rãnh trượt
        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, border_radius=self.rect.h//2)
        
        # Vẽ phần đã làm đầy (màu xanh lá)
        fill_w = int(self.rect.w * self.val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
        pygame.draw.rect(surface, C_SUCCESS, fill_rect, border_radius=self.rect.h//2)
        
        # Vẽ nút kéo
        knob_x = self.rect.x + fill_w
        pygame.draw.circle(surface, C_TEXT, (knob_x, self.rect.centery), self.rect.h + 2)
        
        # Vẽ text phần trăm (%)
        draw_text(surface, f"{int(self.val * 100)}%", small_font, C_TEXT_DIM, self.rect.right + 20, self.rect.centery, anchor="midleft")

    def handle_event(self, event):
        """
        Xử lý kéo thả chuột (Drag & Drop) để thay đổi giá trị.

        Returns:
            bool: True nếu thanh trượt đang bị tác động.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Mở rộng vùng hit-box một chút cho dễ bấm
            hit_rect = self.rect.inflate(0, 20)
            if hit_rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_val(event.pos[0])
                return True
        return False

    def _update_val(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        self.val = max(0.0, min(1.0, rel_x / self.rect.w))
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
=======

        for f, rect in self.tab_rects:
            is_active = (f == self.current_filter)
            color = C_SUCCESS if is_active else C_PANEL_BORDER
            pygame.draw.rect(surface, color, rect, border_radius=4)
            display_text = "MODS" if f == "modifier" else f.upper()
            draw_text(surface, display_text, self.tab_font, C_TEXT if is_active else C_TEXT_DIM,
                      rect.centerx, rect.centery, anchor="center")

        # Cắt clip rect thụt xuống Y + 95
        clip_rect = pygame.Rect(self.RECT.x, self.RECT.y + 95, self.RECT.w, self.RECT.h - 100)
        surface.set_clip(clip_rect)

        dragging_bottle = None

        for b in self.bottles:
            if not b.is_dragging:
                # Cộng b.rect.y thêm để vừa với khung clip_rect mới
                b.rect.y = self.RECT.y + 100 + b.relative_y - self.scroll_offset
                b.origin = (b.rect.x, b.rect.y)
                
                if b.rect.bottom > clip_rect.top and b.rect.top < clip_rect.bottom:
                    b.draw(surface, small_font)
            else:
                dragging_bottle = b

        surface.set_clip(None)

        if self.max_scroll > 0:
            bar_x = self.RECT.right - 12
            bar_y = clip_rect.y + 5
            bar_h = clip_rect.h - 10
            pygame.draw.rect(surface, C_PANEL_BORDER, (bar_x, bar_y, 6, bar_h), border_radius=3)
            thumb_h = max(20, (clip_rect.h / (self.max_scroll + clip_rect.h)) * bar_h)
            thumb_y = bar_y + (self.scroll_offset / self.max_scroll) * (bar_h - thumb_h)
            pygame.draw.rect(surface, C_TEXT_DIM, (bar_x, thumb_y, 6, thumb_h), border_radius=3)

       

    def get_dragging(self):
        """
        Lấy đối tượng chai rượu đang được người chơi nhấc lên (kéo thả).

        Returns:
            Bottle | None: Đối tượng chai đang bị kéo, hoặc None.
        """
        return next((b for b in self.bottles if b.is_dragging), None)

# ══════════════════════════════════════════════════════════
#  7. DISCOVERY BANNER — thông báo khám phá công thức mới
# ══════════════════════════════════════════════════════════
class DiscoveryBanner:
    def __init__(self):
        self._msg   = None
        self._timer = 0   # ms

    def show(self, drink_name):
        self._msg   = f"DISCOVERED: {drink_name}!"
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
# ui.py

class Button:
    """Nút bấm UI cơ bản hỗ trợ đổi màu khi di chuột vào (hover) và bắt sự kiện click."""
    def __init__(self, x, y, w, h, text, color, hover_color):
        """Khởi tạo thông số hình học, màu sắc và text hiển thị của nút."""
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface, font):
        """Vẽ nút bấm và chữ căn giữa, tự đổi màu theo trạng thái hover."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, 2, border_radius=8)
        draw_text(surface, self.text, font, C_TEXT, 
                  self.rect.centerx, self.rect.centery, anchor="center")

    def handle_event(self, event):
        """
        Xử lý sự kiện di chuột và click.

        Returns:
            bool: True nếu nút được nhấn chuột trái.
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
# ══════════════════════════════════════════════════════════
#  Thanh trượt âm lượng (Volume Slider)
# ══════════════════════════════════════════════════════════
class VolumeSlider:
    """Thanh trượt UI để điều chỉnh giá trị từ 0.0 đến 1.0 (âm lượng)."""
    def __init__(self, x, y, w, h, label, initial_val):
        """Khởi tạo kích thước, nhãn dán và giá trị ban đầu."""
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.val = initial_val  # Giá trị từ 0.0 đến 1.0
        self.is_dragging = False

    def draw(self, surface, font, small_font):
        """Vẽ thanh trượt, nút kéo (knob) và giá trị % hiện tại."""
        # Vẽ nhãn (MUSIC / SFX)
        draw_text(surface, self.label, font, C_TEXT, self.rect.x - 90, self.rect.centery, anchor="midleft")
        
        # Vẽ rãnh trượt
        pygame.draw.rect(surface, C_PANEL_BORDER, self.rect, border_radius=self.rect.h//2)
        
        # Vẽ phần đã làm đầy (màu xanh lá)
        fill_w = int(self.rect.w * self.val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
        pygame.draw.rect(surface, C_SUCCESS, fill_rect, border_radius=self.rect.h//2)
        
        # Vẽ nút kéo
        knob_x = self.rect.x + fill_w
        pygame.draw.circle(surface, C_TEXT, (knob_x, self.rect.centery), self.rect.h + 2)
        
        # Vẽ text phần trăm (%)
        draw_text(surface, f"{int(self.val * 100)}%", small_font, C_TEXT_DIM, self.rect.right + 20, self.rect.centery, anchor="midleft")

    def handle_event(self, event):
        """
        Xử lý kéo thả chuột (Drag & Drop) để thay đổi giá trị.

        Returns:
            bool: True nếu thanh trượt đang bị tác động.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Mở rộng vùng hit-box một chút cho dễ bấm
            hit_rect = self.rect.inflate(0, 20)
            if hit_rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_val(event.pos[0])
                return True
        return False

    def _update_val(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        self.val = max(0.0, min(1.0, rel_x / self.rect.w))
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
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def __init__(self, screen, sorted_inventory):
        """Khởi tạo tất cả các thành phần UI, font chữ, hình ảnh và hoạt ảnh."""
        self.screen   = screen
        self.mouse_pos = (0, 0)
        self.font      = load_font(FONT_PATH, 32)
        self.small     = load_font(FONT_PATH, 24)
        self.bg        = load_image(BG_PATH, (WINDOW_WIDTH, WINDOW_HEIGHT), C_BG)
        self.start_bg  = load_image(BG_PATH, (WINDOW_WIDTH, WINDOW_HEIGHT), (18, 20, 28))
        self.start_logo = self._load_start_logo()
        self.start_video_cap = None
        self.start_video_frame = None
        self.start_video_last_tick = 0
        self.start_video_frame_ms = 41
        self._init_start_video()
<<<<<<< HEAD

        self.body_x = 420 
        self.body_y = 200

        self.shaker_ui    = ShakerUI()
        self.search_bar   = SearchBar()
        self.inventory    = InventoryPanel(sorted_inventory)
        self.cust_card    = CustomerCard()
        self.banner       = DiscoveryBanner()
        self.pinned_recipe = None  # Biến lưu công thức đang ghim
        self.particles    = []
        self.show_tools = False
        # (Tìm chỗ khai báo các UI cũ)
        self.banner       = DiscoveryBanner()
        self.pinned_recipe = None  
        self.particles    = []
        self.show_tools = False
        
        # ---> THÊM KHỞI TẠO THANH TRƯỢT
        self.bgm_slider = VolumeSlider(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT//2 + 20, 200, 10, "MUSIC", 0.5)
        self.sfx_slider = VolumeSlider(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT//2 + 70, 200, 10, "EFFECTS", 0.8)
        self.mood_btn = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 120, 200, 40, "", (70, 120, 80), (90, 145, 100))
        self.end_btn = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 175, 200, 45, "END GAME", C_ALERT, (200, 40, 40))
        # --- CODE THÊM VÀO CHO NHÂN VẬT ---
        # Hệ số thu nhỏ toàn bộ nhân vật (0.4 = 40% kích thước gốc)
        self.char_scale = 0.4 
        self.shake_anim_scale = 0.4
        if os.path.exists(SPRITE_PROC_PATH):
            orig_body = pygame.image.load(SPRITE_PROC_PATH).convert_alpha()
            new_w = int(orig_body.get_width() * self.char_scale)
            new_h = int(orig_body.get_height() * self.char_scale)
            self.body_img = pygame.transform.scale(orig_body, (new_w, new_h))
        else:
            self.body_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.anchor_x = self.body_x + self.body_img.get_width() // 2   # tâm ngang
        self.anchor_y = self.body_y + self.body_img.get_height()
       # ── SPRITESHEET ANIMATION ──────────────────────────────
        SHEET_COLS   = 8          
        self.anim_scale = 1.2  # Nhớ giữ nguyên thông số độ to của m

        # --- BẢNG ĐIỀU KHIỂN DAO CẮT ---
        STRIDE = 172    # Bước nhảy: Giữ nguyên 172 để nó nhảy đúng khung
        OFFSET_X = 4       # Dịch lưỡi dao sang phải 4 pixel để né cái vệt bên trái
        CROP_W = 165       # Bóp khung cắt nhỏ lại (172 - 4 trái - 4 phải) để an toàn tuyệt đối
        # -------------------------------

        self.anim_frames   = []   
        self.anim_index    = 0    
        self.anim_timer    = 0    
        self.ANIM_FPS      = 12   
        self.anim_playing  = False

        sheet_path = SPRITE_RAW_PATH   
        if os.path.exists(sheet_path):
            sheet = pygame.image.load(sheet_path).convert_alpha()
            FRAME_H = sheet.get_height()

            for col in range(SHEET_COLS):
                # Tọa độ nhát cắt = Vị trí khung + Dịch vào trong né viền
                cut_x = (col * STRIDE) + OFFSET_X
                
                # Cắt gọn gàng
                frame_surf = sheet.subsurface(
                    pygame.Rect(cut_x, 0, CROP_W, FRAME_H)
                )
                
                # Scale ảnh
                fw = int(CROP_W * self.anim_scale)
                fh = int(FRAME_H * self.anim_scale)
                self.anim_frames.append(
                    pygame.transform.scale(frame_surf, (fw, fh))
                )
                # Load ảnh cánh tay (giữ nguyên gốc, mình sẽ scale lúc vẽ)
        arm_path = "assets/arm.png" 
        if os.path.exists(arm_path):
            self.arm_img = pygame.image.load(arm_path).convert_alpha()
        else:
            self.arm_img = pygame.Surface((50, 20), pygame.SRCALPHA)
            
        # Tọa độ đặt ông bartender lên màn hình
        # Chỉnh X, Y ở đây để dịch ông ấy vào đúng giữa quầy bar
        

        # ----------------------------------
    # ── Particles ─────────────────────────────────────────
=======

        self.body_x = 420 
        self.body_y = 200

        self.shaker_ui    = ShakerUI()
        self.search_bar   = SearchBar()
        self.inventory    = InventoryPanel(sorted_inventory)
        self.cust_card    = CustomerCard()
        self.banner       = DiscoveryBanner()
        self.pinned_recipe = None  # Biến lưu công thức đang ghim
        self.particles    = []
        self.show_tools = False
        # (Tìm chỗ khai báo các UI cũ)
        self.banner       = DiscoveryBanner()
        self.pinned_recipe = None  
        self.particles    = []
        self.show_tools = False
        
        # ---> THÊM KHỞI TẠO THANH TRƯỢT
        self.bgm_slider = VolumeSlider(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT//2 + 20, 200, 10, "MUSIC", 0.5)
        self.sfx_slider = VolumeSlider(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT//2 + 70, 200, 10, "EFFECTS", 0.8)
        self.mood_btn = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 120, 200, 40, "", (70, 120, 80), (90, 145, 100))
        self.end_btn = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 175, 200, 45, "END GAME", C_ALERT, (200, 40, 40))
        # --- CODE THÊM VÀO CHO NHÂN VẬT ---
        # Hệ số thu nhỏ toàn bộ nhân vật (0.4 = 40% kích thước gốc)
        self.char_scale = 0.4 
        self.shake_anim_scale = 0.4
        if os.path.exists(SPRITE_PROC_PATH):
            orig_body = pygame.image.load(SPRITE_PROC_PATH).convert_alpha()
            new_w = int(orig_body.get_width() * self.char_scale)
            new_h = int(orig_body.get_height() * self.char_scale)
            self.body_img = pygame.transform.scale(orig_body, (new_w, new_h))
        else:
            self.body_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.anchor_x = self.body_x + self.body_img.get_width() // 2   # tâm ngang
        self.anchor_y = self.body_y + self.body_img.get_height()
       # ── SPRITESHEET ANIMATION ──────────────────────────────
        SHEET_COLS   = 8          
        self.anim_scale = 1.2  # Nhớ giữ nguyên thông số độ to của m

        # --- BẢNG ĐIỀU KHIỂN DAO CẮT ---
        STRIDE = 172    # Bước nhảy: Giữ nguyên 172 để nó nhảy đúng khung
        OFFSET_X = 4       # Dịch lưỡi dao sang phải 4 pixel để né cái vệt bên trái
        CROP_W = 165       # Bóp khung cắt nhỏ lại (172 - 4 trái - 4 phải) để an toàn tuyệt đối
        # -------------------------------

        self.anim_frames   = []   
        self.anim_index    = 0    
        self.anim_timer    = 0    
        self.ANIM_FPS      = 12   
        self.anim_playing  = False

        sheet_path = SPRITE_RAW_PATH   
        if os.path.exists(sheet_path):
            sheet = pygame.image.load(sheet_path).convert_alpha()
            FRAME_H = sheet.get_height()

            for col in range(SHEET_COLS):
                # Tọa độ nhát cắt = Vị trí khung + Dịch vào trong né viền
                cut_x = (col * STRIDE) + OFFSET_X
                
                # Cắt gọn gàng
                frame_surf = sheet.subsurface(
                    pygame.Rect(cut_x, 0, CROP_W, FRAME_H)
                )
                
                # Scale ảnh
                fw = int(CROP_W * self.anim_scale)
                fh = int(FRAME_H * self.anim_scale)
                self.anim_frames.append(
                    pygame.transform.scale(frame_surf, (fw, fh))
                )
                # Load ảnh cánh tay (giữ nguyên gốc, mình sẽ scale lúc vẽ)
        arm_path = "assets/arm.png" 
        if os.path.exists(arm_path):
            self.arm_img = pygame.image.load(arm_path).convert_alpha()
        else:
            self.arm_img = pygame.Surface((50, 20), pygame.SRCALPHA)
            
        # Tọa độ đặt ông bartender lên màn hình
        # Chỉnh X, Y ở đây để dịch ông ấy vào đúng giữa quầy bar
        

        # ----------------------------------
    # ── Particles ─────────────────────────────────────────
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def toggle_tools(self):
        """Bật/tắt hiển thị của thanh kho nguyên liệu và bình shaker (Phím TAB)."""
        self.show_tools = not self.show_tools
        # Nếu đang kéo chai hoặc lắc bình mà tắt đi thì phải reset lại
        if not self.show_tools:
            self.shaker_ui.stop_shake()
            for b in self.inventory.bottles:
                b.reset_position()

    def _load_start_logo(self):
        logo_path = os.path.join("assets", "start", "title_logo.png")
        if not os.path.exists(logo_path):
            return None

        logo = pygame.image.load(logo_path).convert_alpha()
        max_w = int(WINDOW_WIDTH * 0.82)
        max_h = int(WINDOW_HEIGHT * 0.34)
        ratio = min(max_w / logo.get_width(), max_h / logo.get_height())
        new_size = (int(logo.get_width() * ratio), int(logo.get_height() * ratio))
        return pygame.transform.scale(logo, new_size)

    def _init_start_video(self):
        video_path = os.path.join("assets", "start", "intro.mp4")
        if cv2 is None or not os.path.exists(video_path):
            return

        cap = cv2.VideoCapture(video_path)
        if not cap or not cap.isOpened():
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps and fps > 1:
            self.start_video_frame_ms = max(16, int(1000 / fps))

        self.start_video_cap = cap
        self._advance_start_video(force=True)

    def _advance_start_video(self, force=False):
        if not self.start_video_cap:
            return

        now = pygame.time.get_ticks()
        if not force and now - self.start_video_last_tick < self.start_video_frame_ms:
            return

        ok, frame = self.start_video_cap.read()
        if not ok:
            self.start_video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self.start_video_cap.read()
        if not ok:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_AREA)
        surf = pygame.image.frombuffer(frame.tobytes(), (WINDOW_WIDTH, WINDOW_HEIGHT), "RGB")
        self.start_video_frame = surf.convert()
        self.start_video_last_tick = now

    def _draw_start_screen_base(self):
        self._advance_start_video()
        if self.start_video_frame:
            self.screen.blit(self.start_video_frame, (0, 0))
        else:
            self.screen.blit(self.start_bg, (0, 0))

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 18, 132))
        self.screen.blit(overlay, (0, 0))

        if self.start_logo:
            logo_rect = self.start_logo.get_rect(center=(WINDOW_WIDTH // 2, 150))
            self.screen.blit(self.start_logo, logo_rect)
<<<<<<< HEAD
    def spawn_particles(self, x, y, color):
        """
        Tạo ra một loạt hạt hiệu ứng (Particle) tại tọa độ cụ thể.
        
        Args:
            x, y (int): Tọa độ trung tâm phát sinh.
            color (tuple): Màu sắc của hạt.
        """
        for _ in range(20):
            self.particles.append(Particle(x, y, color))

    def _update_particles(self):

        # Update vòng đời của toàn bộ hạt trước
        for p in self.particles:
            p.update()
        # Xong rồi mới dọn dẹp những hạt đã chết (life <= 0)
        self.particles = [p for p in self.particles if p.life > 0]
    def draw_rubber_arm(self, mouse_pos):
        """
        Vẽ cánh tay "cao su" co dãn theo vị trí chuột.
        Sử dụng kỹ thuật chia cắt sprite và gradient mask để giấu vết nối.

        Args:
            mouse_pos (tuple): Tọa độ (x, y) hiện tại của con trỏ chuột.

        Returns:
            tuple: Tọa độ thực tế (x, y) của đầu bàn tay sau khi tính toán chống co rúm.
        """
        if not hasattr(self, 'arm_img') or not hasattr(self, 'body_img'):
            return

        # 1. Tọa độ khớp vai
        offset_x = -10 
        offset_y = 0

        shoulder_x = self.body_x + int(833 * self.char_scale) + offset_x
        shoulder_y = self.body_y + int(436 * self.char_scale) + offset_y
        
        mx, my = mouse_pos
        dx = mx - shoulder_x
        dy = my - shoulder_y
        distance = math.hypot(dx, dy)
        
        # 2. Tính toán thông số kích thước
        arm_thickness_scale = 0.6 * self.char_scale
        orig_w = self.arm_img.get_width()
        orig_h = self.arm_img.get_height()
        
        new_height = int(orig_h * arm_thickness_scale)
        base_length = int(orig_w * arm_thickness_scale)

        # Chống co rúm
        if distance < base_length:
            distance = base_length

        # ==============================================================
        # THAY ĐỔI TỈ LỆ: ÉP VÙNG GIÃN VỀ SÁT VAI
        # ==============================================================
        # static_ratio = 0.75: 75% cánh tay (từ ngón tay lùi về cùi chỏ) sẽ đứng yên.
        # Bạn có thể tăng lên 0.8 hoặc 0.85 nếu muốn vùng dãn càng nhỏ (càng sát nách).
        static_ratio = 0.75 
        static_orig_w = int(orig_w * static_ratio)
        stretch_orig_w = orig_w - static_orig_w

        # Cắt 2 mảnh: mảnh sát vai (bị giãn) và mảnh cẳng tay (đứng yên)
        stretch_img = self.arm_img.subsurface((0, 0, stretch_orig_w, orig_h))
        static_img = self.arm_img.subsurface((stretch_orig_w, 0, static_orig_w, orig_h))

        static_new_w = int(static_orig_w * arm_thickness_scale)
        
        # Vùng mờ để giấu vết nối
        overlap_w = min(30, static_new_w) 
        
        # Bắp tay gánh toàn bộ độ giãn + chừa 1 khoảng để lót xuống dưới cẳng tay
        stretch_new_w = int((distance - static_new_w) + overlap_w)

        scaled_stretch = pygame.transform.scale(stretch_img, (stretch_new_w, new_height))
        scaled_static = pygame.transform.scale(static_img, (static_new_w, new_height))

        # Tạo mặt nạ gradient alpha
        gradient_mask = pygame.Surface((overlap_w, new_height), pygame.SRCALPHA)
        for x in range(overlap_w):
            alpha = int((x / overlap_w) * 255)
            pygame.draw.line(gradient_mask, (255, 255, 255, alpha), (x, 0), (x, new_height))

        # Áp dụng mặt nạ lên rìa trái của cẳng tay
        blended_static = scaled_static.copy()
        blended_static.blit(gradient_mask, (0, 0), area=pygame.Rect(0, 0, overlap_w, new_height), special_flags=pygame.BLEND_RGBA_MULT)

        # Ghép lại thành cánh tay hoàn chỉnh
        full_arm = pygame.Surface((int(distance), new_height), pygame.SRCALPHA)
        full_arm.blit(scaled_stretch, (0, 0)) # Vẽ bắp tay dãn ở dưới
        
        static_x_pos = int(distance - static_new_w)
        full_arm.blit(blended_static, (static_x_pos, 0)) # Đắp cẳng tay không dãn lên trên

        # 3. Tính góc và Xoay
        angle_rad = math.atan2(-dy, dx)
        angle_deg = math.degrees(angle_rad)

        rotated_arm = pygame.transform.rotate(full_arm, angle_deg)

        center_x = shoulder_x + (distance / 2) * math.cos(angle_rad)
        center_y = shoulder_y - (distance / 2) * math.sin(angle_rad) 

        arm_rect = rotated_arm.get_rect(center=(center_x, center_y))

        # 4. Vẽ lên màn hình
        self.screen.blit(rotated_arm, arm_rect.topleft)
        hand_x = shoulder_x + distance * math.cos(angle_rad)
        hand_y = shoulder_y - distance * math.sin(angle_rad)
        
        return (int(hand_x), int(hand_y))
    # ── Main draw ─────────────────────────────────────────
    def draw_pinned_recipe(self):
        """Vẽ bảng công thức đang được ghim ngay bên dưới thanh Search Bar."""
        if not self.pinned_recipe:
            return
            
        name = self.pinned_recipe["name"]
        ings = self.pinned_recipe["data"]["ingredients"]
        
        # Tạo bảng nằm ngay dưới thanh Search
        box_x = 30
        box_y = self.search_bar.RECT.bottom + 15
        box_w = 260
        box_h = 36 + len(ings) * 24 # Độ cao co giãn theo số nguyên liệu
        
        rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (30, 40, 50), rect, border_radius=8)
        pygame.draw.rect(self.screen, C_GOLD, rect, 2, border_radius=8)
        
        # Vẽ tên công thức
        draw_text(self.screen, f"PINNED: {name}", self.small, C_GOLD, box_x + 10, box_y + 8)
        
        # Vẽ danh sách nguyên liệu
        y_offset = box_y + 35
        for ing_name, ratio in ings.items():
            # Chuyển ratio (tỉ lệ) sang % cho dễ hình dung
            perc = int(ratio * 100)
            draw_text(self.screen, f"- {ing_name}: {perc}%", self.small, C_TEXT, box_x + 15, y_offset)
            y_offset += 24
=======
    def spawn_particles(self, x, y, color):
        """
        Tạo ra một loạt hạt hiệu ứng (Particle) tại tọa độ cụ thể.
        
        Args:
            x, y (int): Tọa độ trung tâm phát sinh.
            color (tuple): Màu sắc của hạt.
        """
        for _ in range(20):
            self.particles.append(Particle(x, y, color))

    def _update_particles(self):

        # Update vòng đời của toàn bộ hạt trước
        for p in self.particles:
            p.update()
        # Xong rồi mới dọn dẹp những hạt đã chết (life <= 0)
        self.particles = [p for p in self.particles if p.life > 0]
    def draw_rubber_arm(self, mouse_pos):
        """
        Vẽ cánh tay "cao su" co dãn theo vị trí chuột.
        Sử dụng kỹ thuật chia cắt sprite và gradient mask để giấu vết nối.

        Args:
            mouse_pos (tuple): Tọa độ (x, y) hiện tại của con trỏ chuột.

        Returns:
            tuple: Tọa độ thực tế (x, y) của đầu bàn tay sau khi tính toán chống co rúm.
        """
        if not hasattr(self, 'arm_img') or not hasattr(self, 'body_img'):
            return

        # 1. Tọa độ khớp vai
        offset_x = -10 
        offset_y = 0

        shoulder_x = self.body_x + int(833 * self.char_scale) + offset_x
        shoulder_y = self.body_y + int(436 * self.char_scale) + offset_y
        
        mx, my = mouse_pos
        dx = mx - shoulder_x
        dy = my - shoulder_y
        distance = math.hypot(dx, dy)
        
        # 2. Tính toán thông số kích thước
        arm_thickness_scale = 0.6 * self.char_scale
        orig_w = self.arm_img.get_width()
        orig_h = self.arm_img.get_height()
        
        new_height = int(orig_h * arm_thickness_scale)
        base_length = int(orig_w * arm_thickness_scale)

        # Chống co rúm
        if distance < base_length:
            distance = base_length

        # ==============================================================
        # THAY ĐỔI TỈ LỆ: ÉP VÙNG GIÃN VỀ SÁT VAI
        # ==============================================================
        # static_ratio = 0.75: 75% cánh tay (từ ngón tay lùi về cùi chỏ) sẽ đứng yên.
        # Bạn có thể tăng lên 0.8 hoặc 0.85 nếu muốn vùng dãn càng nhỏ (càng sát nách).
        static_ratio = 0.75 
        static_orig_w = int(orig_w * static_ratio)
        stretch_orig_w = orig_w - static_orig_w

        # Cắt 2 mảnh: mảnh sát vai (bị giãn) và mảnh cẳng tay (đứng yên)
        stretch_img = self.arm_img.subsurface((0, 0, stretch_orig_w, orig_h))
        static_img = self.arm_img.subsurface((stretch_orig_w, 0, static_orig_w, orig_h))

        static_new_w = int(static_orig_w * arm_thickness_scale)
        
        # Vùng mờ để giấu vết nối
        overlap_w = min(30, static_new_w) 
        
        # Bắp tay gánh toàn bộ độ giãn + chừa 1 khoảng để lót xuống dưới cẳng tay
        stretch_new_w = int((distance - static_new_w) + overlap_w)

        scaled_stretch = pygame.transform.scale(stretch_img, (stretch_new_w, new_height))
        scaled_static = pygame.transform.scale(static_img, (static_new_w, new_height))

        # Tạo mặt nạ gradient alpha
        gradient_mask = pygame.Surface((overlap_w, new_height), pygame.SRCALPHA)
        for x in range(overlap_w):
            alpha = int((x / overlap_w) * 255)
            pygame.draw.line(gradient_mask, (255, 255, 255, alpha), (x, 0), (x, new_height))

        # Áp dụng mặt nạ lên rìa trái của cẳng tay
        blended_static = scaled_static.copy()
        blended_static.blit(gradient_mask, (0, 0), area=pygame.Rect(0, 0, overlap_w, new_height), special_flags=pygame.BLEND_RGBA_MULT)

        # Ghép lại thành cánh tay hoàn chỉnh
        full_arm = pygame.Surface((int(distance), new_height), pygame.SRCALPHA)
        full_arm.blit(scaled_stretch, (0, 0)) # Vẽ bắp tay dãn ở dưới
        
        static_x_pos = int(distance - static_new_w)
        full_arm.blit(blended_static, (static_x_pos, 0)) # Đắp cẳng tay không dãn lên trên

        # 3. Tính góc và Xoay
        angle_rad = math.atan2(-dy, dx)
        angle_deg = math.degrees(angle_rad)

        rotated_arm = pygame.transform.rotate(full_arm, angle_deg)

        center_x = shoulder_x + (distance / 2) * math.cos(angle_rad)
        center_y = shoulder_y - (distance / 2) * math.sin(angle_rad) 

        arm_rect = rotated_arm.get_rect(center=(center_x, center_y))

        # 4. Vẽ lên màn hình
        self.screen.blit(rotated_arm, arm_rect.topleft)
        hand_x = shoulder_x + distance * math.cos(angle_rad)
        hand_y = shoulder_y - distance * math.sin(angle_rad)
        
        return (int(hand_x), int(hand_y))
    # ── Main draw ─────────────────────────────────────────
    def draw_pinned_recipe(self):
        """Vẽ bảng công thức đang được ghim ngay bên dưới thanh Search Bar."""
        if not self.pinned_recipe:
            return
            
        name = self.pinned_recipe["name"]
        ings = self.pinned_recipe["data"]["ingredients"]
        
        # Tạo bảng nằm ngay dưới thanh Search
        box_x = 30
        box_y = self.search_bar.RECT.bottom + 15
        box_w = 260
        box_h = 36 + len(ings) * 24 # Độ cao co giãn theo số nguyên liệu
        
        rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (30, 40, 50), rect, border_radius=8)
        pygame.draw.rect(self.screen, C_GOLD, rect, 2, border_radius=8)
        
        # Vẽ tên công thức
        draw_text(self.screen, f"PINNED: {name}", self.small, C_GOLD, box_x + 10, box_y + 8)
        
        # Vẽ danh sách nguyên liệu
        y_offset = box_y + 35
        for ing_name, ratio in ings.items():
            # Chuyển ratio (tỉ lệ) sang % cho dễ hình dung
            perc = int(ratio * 100)
            draw_text(self.screen, f"- {ing_name}: {perc}%", self.small, C_TEXT, box_x + 15, y_offset)
            y_offset += 24
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def draw_menu(self):
        self._draw_start_screen_base()

        title_y = 310 if self.start_logo else 230
        subtitle_y = title_y + 54
        prompt_y = subtitle_y + 72

        draw_text(self.screen, "THE MIXOLOGIST", self.font, (130, 242, 255),
                  WINDOW_WIDTH // 2, title_y, anchor="center")
        draw_text(self.screen, "Shake fast. Serve smart. Keep the bar alive.", self.small, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, subtitle_y, anchor="center")

        prompt_box = pygame.Rect(WINDOW_WIDTH // 2 - 190, prompt_y - 18, 380, 54)
        pygame.draw.rect(self.screen, (255, 170, 70), prompt_box, border_radius=12)
        pygame.draw.rect(self.screen, (78, 40, 20), prompt_box, 3, border_radius=12)
        draw_text(self.screen, "PRESS ENTER TO START", self.small, (38, 18, 12),
                  prompt_box.centerx, prompt_box.centery, anchor="center")

    def draw_guide(self):
        """Vẽ màn hình hướng dẫn điều khiển khi mới mở game."""
        self._draw_start_screen_base()

        panel_w = 760
        panel_h = 470
        panel = pygame.Rect(
            (WINDOW_WIDTH - panel_w) // 2,
            210,
            panel_w,
            panel_h,
        )
        pygame.draw.rect(self.screen, (20, 22, 30), panel, border_radius=18)
        pygame.draw.rect(self.screen, (255, 190, 70), panel, 3, border_radius=18)

        draw_text(self.screen, "HOW TO PLAY", self.font, C_GOLD,
                  WINDOW_WIDTH // 2, panel.y + 34, anchor="center")
        draw_text(self.screen, "Nắm nhanh các nút trước khi mở quán.", self.small, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, panel.y + 90, anchor="center")

        controls = [
            ("ENTER", "Đi tiếp sang menu và bắt đầu game"),
            ("TAB", "Ẩn / hiện khu vực tools và shaker"),
            ("DRAG + HOLD", "Kéo chai vào shaker để rót nguyên liệu"),
            ("CLICK SHAKER", "Bắt đầu lắc khi đã đậy nắp"),
            ("SPACE", "Phục vụ vị khách gấp nhất"),
            ("C", "Đổ bỏ toàn bộ nguyên liệu trong shaker"),
            ("ESC", "Tạm dừng hoặc quay lại game"),
        ]

        key_x = panel.x + 48
        text_x = panel.x + 250
        start_y = panel.y + 145
        row_gap = 38

        for i, (key, desc) in enumerate(controls):
            y = start_y + i * row_gap
            key_box = pygame.Rect(key_x, y - 8, 150, 28)
            pygame.draw.rect(self.screen, (52, 60, 78), key_box, border_radius=8)
            pygame.draw.rect(self.screen, C_PANEL_BORDER, key_box, 2, border_radius=8)
            draw_text(self.screen, key, self.small, C_TEXT, key_box.centerx, y + 6, anchor="center")
            draw_text(self.screen, desc, self.small, C_TEXT_DIM, text_x, y)

        draw_text(self.screen, "ENTER", self.small, C_GOLD,
                  WINDOW_WIDTH // 2, panel.bottom - 64, anchor="center")
        draw_text(self.screen, "Press Enter to continue", self.small, C_TEXT,
                  WINDOW_WIDTH // 2, panel.bottom - 34, anchor="center")
<<<<<<< HEAD

    def load_glass_image(self, name):
        """
        Tải và cache hình ảnh ly thành phẩm (Glass).

        Args:
            name (str): Tên công thức để map với file ảnh.

        Returns:
            pygame.Surface | None: Hình ảnh ly đã được resize, hoặc None nếu không có file.
        """
        if not hasattr(self, '_glass_cache'):
            self._glass_cache = {}
        if name in self._glass_cache:
            return self._glass_cache[name]
            
        img_name = name.replace(" ", "") + ".png"
        path = os.path.join("assets", img_name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            # Cố định chiều cao ly khoảng 150px
            target_h = 150
            ratio = img.get_width() / img.get_height()
            target_w = int(target_h * ratio)
            surf = pygame.transform.scale(img, (target_w, target_h))
            self._glass_cache[name] = surf
            return surf
        return None

    def draw_playing(self, game_state, dt_ms):
        """Vẽ toàn bộ giao diện trong trạng thái PLAYING (quầy, khách, shaker, UI)."""
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.body_img, (self.body_x, self.body_y))

        # 1. Vẽ Customers và tính toán chiều cao lớn nhất
        customers = game_state.get_active_customers()
        max_card_bottom = 140 # Vị trí Y mặc định ban đầu của Search Bar
        
        for i, c in enumerate(customers):
            cx = 30 + i * (CustomerCard.CARD_W + 12)
            cy = 10
            self.cust_card.draw(self.screen, c, cx, cy, self.font, self.small)
            
            # Tính toán xem thẻ này kết thúc ở đâu (Dynamic Height)
            # Dựa trên logic tính dynamic_h trong CustomerCard.draw
            mood_text = c.request_data["text"] if c.request_type == "mood" else ""
            words = mood_text.split(' ')
            line_count = 1
            if mood_text:
                curr_line = []
                temp_lines = []
                for w in words:
                    if self.small.size(' '.join(curr_line + [w]))[0] <= CustomerCard.CARD_W - 20:
                        curr_line.append(w)
                    else:
                        temp_lines.append(' '.join(curr_line))
                        curr_line = [w]
                temp_lines.append(' '.join(curr_line))
                line_count = len(temp_lines)
            
            card_h = max(120, 34 + (line_count * 18) + 8 + 14 + 10)
            max_card_bottom = max(max_card_bottom, cy + card_h + 20) # +20px khoảng cách an toàn

        # 2. Cập nhật vị trí Search Bar theo max_card_bottom
        self.search_bar.RECT.y = max_card_bottom
        # Cập nhật luôn vị trí nút Close của Search Bar
        self.search_bar.close_btn_rect.y = max_card_bottom

        # 3. Vẽ Shaker & Inventory
        self.shaker_ui.update(dt_ms)
        if self.show_tools:
            vol, max_vol, color = game_state.get_shaker_state()
            self.shaker_ui.draw(self.screen, vol, max_vol, color, self.small)
            self.inventory.draw(self.screen, self.font, self.small)
            
            # --- VẼ LY THÀNH PHẨM TRÊN BÀN ---
            if getattr(game_state, "finished_drink_name", None):
                glass_surf = self.load_glass_image(game_state.finished_drink_name)
                if glass_surf:
                    # FIX: Cố định vị trí ly dựa trên tọa độ gốc (BASE_X, BASE_Y) thay vì RECT (tọa độ chuột)
                    shaker_base_bottom = self.shaker_ui.BASE_Y + self.shaker_ui.RECT.height
                    
                    glass_x = self.shaker_ui.BASE_X - glass_surf.get_width() - 120
                    glass_y = shaker_base_bottom - glass_surf.get_height() - 80
                    self.screen.blit(glass_surf, (glass_x, glass_y))

        # --- CODE DỜI XUỐNG ĐÂY ---
        # 4. Vẽ cái tay SAU CÙNG để nó đè lên tất cả UI
        mouse_pos = self.mouse_pos
        
        # ---> SỬA DÒNG NÀY: Hứng tọa độ thực tế của bàn tay
        actual_hand_pos = self.draw_rubber_arm(mouse_pos)

        # 5. Vẽ chai rượu ĐÈ LÊN TRÊN CÁI TAY
        if self.show_tools:
            dragging_bottle = self.inventory.get_dragging()
            if dragging_bottle:
                is_pouring = self.shaker_ui.RECT.collidepoint(mouse_pos)
                
                # ---> THÊM 2 DÒNG NÀY: Khóa chết tâm chai rượu vào bàn tay
                if actual_hand_pos:
                    dragging_bottle.rect.center = actual_hand_pos
                    
                dragging_bottle.draw(self.screen, self.small, is_pouring=is_pouring)

        # Vẽ bảng ghim 
        self.draw_pinned_recipe()
        
        # Search bar
        self.search_bar.draw(self.screen, self.font, self.small)
        # Search bar
        self.search_bar.draw(self.screen, self.font, self.small)

        # Particles
        self._update_particles()
        for p in self.particles:
            p.draw(self.screen)

        # Score
        draw_text(self.screen, f"SCORE: {game_state.score}",
                  self.font, C_GOLD,
                  WINDOW_WIDTH - 20, 20, anchor="topright")

        
        # Khách gấp nhất — hint order to giữa màn
        next_c = game_state.get_next_customer()
        if next_c and next_c.request_type == "mood":
            hint_tags = ", ".join(next_c.request_data["tags"])
            draw_text(self.screen, f"HINT: [{hint_tags}]",
                      self.small, (200, 200, 160),
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30, anchor="center")

=======

    def load_glass_image(self, name):
        """
        Tải và cache hình ảnh ly thành phẩm (Glass).

        Args:
            name (str): Tên công thức để map với file ảnh.

        Returns:
            pygame.Surface | None: Hình ảnh ly đã được resize, hoặc None nếu không có file.
        """
        if not hasattr(self, '_glass_cache'):
            self._glass_cache = {}
        if name in self._glass_cache:
            return self._glass_cache[name]
            
        img_name = name.replace(" ", "") + ".png"
        path = os.path.join("assets", img_name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            # Cố định chiều cao ly khoảng 150px
            target_h = 150
            ratio = img.get_width() / img.get_height()
            target_w = int(target_h * ratio)
            surf = pygame.transform.scale(img, (target_w, target_h))
            self._glass_cache[name] = surf
            return surf
        return None

    def draw_playing(self, game_state, dt_ms):
        """Vẽ toàn bộ giao diện trong trạng thái PLAYING (quầy, khách, shaker, UI)."""
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.body_img, (self.body_x, self.body_y))

        # 1. Vẽ Customers và tính toán chiều cao lớn nhất
        customers = game_state.get_active_customers()
        max_card_bottom = 140 # Vị trí Y mặc định ban đầu của Search Bar
        
        for i, c in enumerate(customers):
            cx = 30 + i * (CustomerCard.CARD_W + 12)
            cy = 10
            self.cust_card.draw(self.screen, c, cx, cy, self.font, self.small)
            
            # Tính toán xem thẻ này kết thúc ở đâu (Dynamic Height)
            # Dựa trên logic tính dynamic_h trong CustomerCard.draw
            mood_text = c.request_data["text"] if c.request_type == "mood" else ""
            words = mood_text.split(' ')
            line_count = 1
            if mood_text:
                curr_line = []
                temp_lines = []
                for w in words:
                    if self.small.size(' '.join(curr_line + [w]))[0] <= CustomerCard.CARD_W - 20:
                        curr_line.append(w)
                    else:
                        temp_lines.append(' '.join(curr_line))
                        curr_line = [w]
                temp_lines.append(' '.join(curr_line))
                line_count = len(temp_lines)
            
            card_h = max(120, 34 + (line_count * 18) + 8 + 14 + 10)
            max_card_bottom = max(max_card_bottom, cy + card_h + 20) # +20px khoảng cách an toàn

        # 2. Cập nhật vị trí Search Bar theo max_card_bottom
        self.search_bar.RECT.y = max_card_bottom
        # Cập nhật luôn vị trí nút Close của Search Bar
        self.search_bar.close_btn_rect.y = max_card_bottom

        # 3. Vẽ Shaker & Inventory
        self.shaker_ui.update(dt_ms)
        if self.show_tools:
            vol, max_vol, color = game_state.get_shaker_state()
            self.shaker_ui.draw(self.screen, vol, max_vol, color, self.small)
            self.inventory.draw(self.screen, self.font, self.small)
            
            # --- VẼ LY THÀNH PHẨM TRÊN BÀN ---
            if getattr(game_state, "finished_drink_name", None):
                glass_surf = self.load_glass_image(game_state.finished_drink_name)
                if glass_surf:
                    # FIX: Cố định vị trí ly dựa trên tọa độ gốc (BASE_X, BASE_Y) thay vì RECT (tọa độ chuột)
                    shaker_base_bottom = self.shaker_ui.BASE_Y + self.shaker_ui.RECT.height
                    
                    glass_x = self.shaker_ui.BASE_X - glass_surf.get_width() - 120
                    glass_y = shaker_base_bottom - glass_surf.get_height() - 80
                    self.screen.blit(glass_surf, (glass_x, glass_y))

        # --- CODE DỜI XUỐNG ĐÂY ---
        # 4. Vẽ cái tay SAU CÙNG để nó đè lên tất cả UI
        mouse_pos = self.mouse_pos
        
        # ---> SỬA DÒNG NÀY: Hứng tọa độ thực tế của bàn tay
        actual_hand_pos = self.draw_rubber_arm(mouse_pos)

        # 5. Vẽ chai rượu ĐÈ LÊN TRÊN CÁI TAY
        if self.show_tools:
            dragging_bottle = self.inventory.get_dragging()
            if dragging_bottle:
                is_pouring = self.shaker_ui.RECT.collidepoint(mouse_pos)
                
                # ---> THÊM 2 DÒNG NÀY: Khóa chết tâm chai rượu vào bàn tay
                if actual_hand_pos:
                    dragging_bottle.rect.center = actual_hand_pos
                    
                dragging_bottle.draw(self.screen, self.small, is_pouring=is_pouring)

        # Vẽ bảng ghim 
        self.draw_pinned_recipe()
        
        # Search bar
        self.search_bar.draw(self.screen, self.font, self.small)
        # Search bar
        self.search_bar.draw(self.screen, self.font, self.small)

        # Particles
        self._update_particles()
        for p in self.particles:
            p.draw(self.screen)

        # Score
        draw_text(self.screen, f"SCORE: {game_state.score}",
                  self.font, C_GOLD,
                  WINDOW_WIDTH - 20, 20, anchor="topright")

        
        # Khách gấp nhất — hint order to giữa màn
        next_c = game_state.get_next_customer()
        if next_c and next_c.request_type == "mood":
            hint_tags = ", ".join(next_c.request_data["tags"])
            draw_text(self.screen, f"HINT: [{hint_tags}]",
                      self.small, (200, 200, 160),
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30, anchor="center")

>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    def draw_paused(self):
        """Vẽ lớp phủ mờ đục và menu Pause đè lên giao diện chính."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
<<<<<<< HEAD
        draw_text(self.screen, "PAUSED", self.font, C_GOLD,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, anchor="center")
                  
=======
        draw_text(self.screen, "PAUSED", self.font, C_GOLD,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, anchor="center")
                  
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        # Đặt dòng hướng dẫn xuống dưới cụm nút/slider để tránh đè UI.
        draw_text(self.screen, "PRESS ESC TO CONTINUE", self.small, C_TEXT_DIM, 
                  WINDOW_WIDTH // 2, self.end_btn.rect.bottom + 22, anchor="center")
                  
        self.bgm_slider.draw(self.screen, self.small, self.small)
        self.sfx_slider.draw(self.screen, self.small, self.small)
        self.mood_btn.text = f"MOOD VOICE: {'ON' if sound_mgr.mood_dialogue_enabled else 'OFF'}"
        self.mood_btn.color = (70, 120, 80) if sound_mgr.mood_dialogue_enabled else (110, 70, 70)
        self.mood_btn.hover_color = (90, 145, 100) if sound_mgr.mood_dialogue_enabled else (145, 90, 90)
        self.mood_btn.draw(self.screen, self.small)
        self.end_btn.draw(self.screen, self.small)
<<<<<<< HEAD
    def draw_gameover(self, game_state):
        """Vẽ màn hình Game Over và danh sách bảng xếp hạng Leaderboard."""
        self.screen.fill(C_BG)
        draw_text(self.screen, "GAME OVER!", self.font, C_ALERT,
                  WINDOW_WIDTH // 2, 80, anchor="center")
        draw_text(self.screen, f"SCORE: {game_state.score}",
                  self.font, C_GOLD,
                  WINDOW_WIDTH // 2, 130, anchor="center")
=======
    def draw_gameover(self, game_state):
        """Vẽ màn hình Game Over và danh sách bảng xếp hạng Leaderboard."""
        self.screen.fill(C_BG)
        draw_text(self.screen, "GAME OVER!", self.font, C_ALERT,
                  WINDOW_WIDTH // 2, 80, anchor="center")
        draw_text(self.screen, f"SCORE: {game_state.score}",
                  self.font, C_GOLD,
                  WINDOW_WIDTH // 2, 130, anchor="center")
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        draw_text(self.screen, "LEADERBOARD", self.font, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, 190, anchor="center")
        current_entry = getattr(game_state, "last_saved_entry", None)
        for i, entry in enumerate(game_state.leaderboard[:5]):
            row_color = C_GOLD if entry is current_entry else C_TEXT
            draw_text(self.screen,
<<<<<<< HEAD
                      f"#{i+1}  {entry['name']}  —  {entry['score']}",
                      self.small, row_color,
                      WINDOW_WIDTH // 2, 230 + i * 36, anchor="center")
=======
                      f"#{i+1}  {entry['name']}  —  {entry['score']}",
                      self.small, row_color,
                      WINDOW_WIDTH // 2, 230 + i * 36, anchor="center")
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
        current_rank = getattr(game_state, "last_saved_rank", None)
        if current_rank is not None:
            draw_text(self.screen, "THIS RUN SAVED",
                      self.small, C_SUCCESS,
                      WINDOW_WIDTH // 2, 430, anchor="center")
            draw_text(self.screen,
                      f"#{current_rank}  Player  -  {game_state.score}",
                      self.small, C_GOLD,
                      WINDOW_WIDTH // 2, 462, anchor="center")
        elif len(game_state.leaderboard) > 5:
            tail_rank = len(game_state.leaderboard)
            tail_entry = game_state.leaderboard[-1]
            draw_text(self.screen, "LOWEST SAVED",
                      self.small, C_SUCCESS,
                      WINDOW_WIDTH // 2, 430, anchor="center")
            draw_text(self.screen,
                      f"#{tail_rank}  {tail_entry['name']}  -  {tail_entry['score']}",
                      self.small, C_GOLD,
                      WINDOW_WIDTH // 2, 462, anchor="center")

        if game_state.leaderboard:
            draw_text(self.screen, f"TOTAL SAVES: {len(game_state.leaderboard)}",
                      self.small, C_TEXT_DIM,
                      WINDOW_WIDTH // 2, 510, anchor="center")

        draw_text(self.screen, "PRESS R TO RETRY",
                  self.small, C_TEXT_DIM,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, anchor="center")
<<<<<<< HEAD

    # ── Event forwarding ──────────────────────────────────
    def handle_event(self, event, game_state):
        """
        Điều phối các sự kiện Pygame đến đúng thành phần UI tương ứng 
        (SearchBar, Inventory, Shaker, Bottles).

        Returns:
            dict: Hành động được kích hoạt (ví dụ: {"shake_done": True}).
        """
        action = {}

        # Kiểm tra trước mọi event: hễ có click chuột là phân xử ngay
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_tools:
                # Nếu click trúng thanh Recipe -> Bắt thanh Kho phải tắt
                if self.search_bar.RECT.collidepoint(event.pos):
                    self.inventory.search_active = False
                
                # Nếu click trúng thanh Kho -> Bắt thanh Recipe phải tắt
                elif self.inventory.search_rect.collidepoint(event.pos):
                    self.search_bar.active = False
        # -----------------------------------

        search_action = self.search_bar.handle_event(
            event,
            lambda query: game_state.search_recipes(query)  
        )
        if search_action and search_action.get("action") == "pin":
            self.pinned_recipe = search_action
        if self.show_tools:
            self.inventory.handle_event(event)

            # Bắt sự kiện Click chuột xuống (Khởi động kéo thả / Lắc)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Kiểm tra click nút đậy nắp
                if self.shaker_ui.btn_lid_rect.collidepoint(event.pos):
                    self.shaker_ui.is_closed = not self.shaker_ui.is_closed

                # 1. Kiểm tra kéo chai rượu
                # 1. Kiểm tra kéo chai rượu
                for b in self.inventory.bottles:
                    if b.rect.collidepoint(event.pos):
                        b.is_dragging = True
                        sound_mgr.play("pickup") # <--- PHẬP! TIẾNG NHẤC CHAI LÊN
                        break
                
                # 2. Kiểm tra click vào bình lắc để bắt đầu Shake
                # Phải check xem có đang KHÔNG cầm chai nào thì mới cho lắc
                if not any(b.is_dragging for b in self.inventory.bottles):
                    if self.shaker_ui.RECT.collidepoint(event.pos):
                        self.shaker_ui.start_shake(event.pos[0])

            # Bắt sự kiện Di chuột (Đang kéo thả / Đang lắc)
            elif event.type == pygame.MOUSEMOTION:
                # 1. Xử lý kéo thả chai
                for b in self.inventory.bottles:
                    if b.is_dragging:
                        b.rect.center = event.pos
                        # Hiệu ứng particle khi kéo qua shaker
                        if self.shaker_ui.RECT.collidepoint(event.pos):
                            color = INGREDIENTS_DATA.get(b.name, {}).get("color", (200, 200, 200))
                            self.spawn_particles(*event.pos, color)
                            
                # 2. Xử lý lắc bình
                # CHỈ gọi hàm đếm nhịp lắc khi cờ is_shaking đang Bật (tức là đã click chuột xuống)
                if self.shaker_ui.is_shaking:
                    done = self.shaker_ui.handle_shake(event)
                    if done:
                        action["shake_done"] = True

            # Bắt sự kiện Nhả chuột (Dừng kéo thả / Dừng lắc)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Dừng lắc
                self.shaker_ui.stop_shake()
                # Thả tất cả các chai về kho
                for b in self.inventory.bottles:
                    if b.is_dragging:
                        b.reset_position()

        return action

=======

    # ── Event forwarding ──────────────────────────────────
    def handle_event(self, event, game_state):
        """
        Điều phối các sự kiện Pygame đến đúng thành phần UI tương ứng 
        (SearchBar, Inventory, Shaker, Bottles).

        Returns:
            dict: Hành động được kích hoạt (ví dụ: {"shake_done": True}).
        """
        action = {}

        # Kiểm tra trước mọi event: hễ có click chuột là phân xử ngay
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_tools:
                # Nếu click trúng thanh Recipe -> Bắt thanh Kho phải tắt
                if self.search_bar.RECT.collidepoint(event.pos):
                    self.inventory.search_active = False
                
                # Nếu click trúng thanh Kho -> Bắt thanh Recipe phải tắt
                elif self.inventory.search_rect.collidepoint(event.pos):
                    self.search_bar.active = False
        # -----------------------------------

        search_action = self.search_bar.handle_event(
            event,
            lambda query: game_state.search_recipes(query)  
        )
        if search_action and search_action.get("action") == "pin":
            self.pinned_recipe = search_action
        if self.show_tools:
            self.inventory.handle_event(event)

            # Bắt sự kiện Click chuột xuống (Khởi động kéo thả / Lắc)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Kiểm tra click nút đậy nắp
                if self.shaker_ui.btn_lid_rect.collidepoint(event.pos):
                    self.shaker_ui.is_closed = not self.shaker_ui.is_closed

                # 1. Kiểm tra kéo chai rượu
                # 1. Kiểm tra kéo chai rượu
                for b in self.inventory.bottles:
                    if b.rect.collidepoint(event.pos):
                        b.is_dragging = True
                        sound_mgr.play("pickup") # <--- PHẬP! TIẾNG NHẤC CHAI LÊN
                        break
                
                # 2. Kiểm tra click vào bình lắc để bắt đầu Shake
                # Phải check xem có đang KHÔNG cầm chai nào thì mới cho lắc
                if not any(b.is_dragging for b in self.inventory.bottles):
                    if self.shaker_ui.RECT.collidepoint(event.pos):
                        self.shaker_ui.start_shake(event.pos[0])

            # Bắt sự kiện Di chuột (Đang kéo thả / Đang lắc)
            elif event.type == pygame.MOUSEMOTION:
                # 1. Xử lý kéo thả chai
                for b in self.inventory.bottles:
                    if b.is_dragging:
                        b.rect.center = event.pos
                        # Hiệu ứng particle khi kéo qua shaker
                        if self.shaker_ui.RECT.collidepoint(event.pos):
                            color = INGREDIENTS_DATA.get(b.name, {}).get("color", (200, 200, 200))
                            self.spawn_particles(*event.pos, color)
                            
                # 2. Xử lý lắc bình
                # CHỈ gọi hàm đếm nhịp lắc khi cờ is_shaking đang Bật (tức là đã click chuột xuống)
                if self.shaker_ui.is_shaking:
                    done = self.shaker_ui.handle_shake(event)
                    if done:
                        action["shake_done"] = True

            # Bắt sự kiện Nhả chuột (Dừng kéo thả / Dừng lắc)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Dừng lắc
                self.shaker_ui.stop_shake()
                # Thả tất cả các chai về kho
                for b in self.inventory.bottles:
                    if b.is_dragging:
                        b.reset_position()

        return action

>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
    
