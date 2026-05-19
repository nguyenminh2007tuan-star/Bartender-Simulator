# game_logic.py
"""
Toàn bộ logic game — KHÔNG import pygame.

Module này hoạt động như tầng model/business-logic thuần túy.
Giao tiếp với ``ui.py`` chỉ qua data thuần (dict, list, string),
không bao giờ trả về đối tượng pygame.

Các lớp chính:
    - Customer        : Model dữ liệu một khách hàng.
    - CustomerManager : Quản lý vòng đời khách (spawn, seat, timeout, serve).
    - MixingEngine    : Xử lý shaker, kiểm tra công thức, khám phá món mới.
    - GameState       : Máy trạng thái tổng thể của một ván chơi.

Luồng phụ thuộc:
    ``main.py`` → ``GameState`` → ``CustomerManager`` + ``MixingEngine``
                                → ``algorithms.py`` (MinHeap, WaitingQueue, ActionStack, Trie, InvertedIndex)
                                → ``settings.py``  (hằng số, dữ liệu)
"""

import time
import random
import json # <--- THÊM
import os   # <--- THÊM
from algorithms import (
    MinHeap, WaitingQueue, LiquidShaker,
    Trie, InvertedIndex,
    quick_sort_leaderboard, merge_sort_inventory,
)
from settings import *
from sound_manager import sound_mgr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_PATH = os.path.join(BASE_DIR, "leaderboard.json")

# ══════════════════════════════════════════════════════════
#  1. MODEL: Khách hàng
# ══════════════════════════════════════════════════════════
class Customer:
    """
    Model dữ liệu đại diện cho một khách hàng trong game.

    Mỗi khách có hai kiểu gọi món:
        - ``"direct"`` : Gọi thẳng tên món (vd: "Cho tôi Martini").
          ``request_data`` là tên món (str).
        - ``"mood"``   : Mô tả tâm trạng (vd: "Tôi cần thứ gì đó đắng và mạnh").
          ``request_data`` là dict ``{text: str, tags: list[str]}``.

    Thời gian kiên nhẫn được tính real-time bằng ``time.time()``.
    Khách VIP ít kiên nhẫn hơn nhưng cho nhiều điểm hơn.

    Attributes:
        id (int): ID duy nhất tăng dần, dùng làm key trong MinHeap.
        name (str): Tên hiển thị của khách (lấy ngẫu nhiên từ ``CUSTOMER_NAMES``).
        is_vip (bool): ``True`` nếu là khách VIP.
        request_type (str): ``"direct"`` hoặc ``"mood"``.
        request_data (str | dict): Nội dung yêu cầu tương ứng với ``request_type``.
        patience (float): Tổng thời gian kiên nhẫn (giây).
        start_time (float): Timestamp lúc khách xuất hiện (``time.time()``).
    """

    def __init__(self, c_id, name, is_vip, request_type, request_data, voice_key=None):
        """
        Khởi tạo một khách hàng mới.

        Args:
            c_id (int): ID duy nhất của khách.
            name (str): Tên hiển thị.
            is_vip (bool): ``True`` nếu là khách VIP.
            request_type (str): ``"direct"`` hoặc ``"mood"``.
            request_data (str | dict): Nội dung yêu cầu.
            voice_key (str | None): Key âm thanh lời thoại, hoặc ``None`` nếu gọi trực tiếp.
        """
        self.id           = c_id
        self.name         = name
        self.is_vip       = is_vip
        self.request_type = request_type
        self.request_data = request_data
        
        # ---> 2. THÊM DÒNG NÀY ĐỂ LƯU VÀO TÚI KHÁCH
        self.voice_key    = voice_key    
        
        self.patience     = VIP_PATIENCE if is_vip else BASE_PATIENCE
        self.start_time   = time.time()

    @property
    def time_left(self):
        """
        Thời gian còn lại (giây) trước khi khách bỏ đi.

        Được tính real-time từ ``time.time()`` nên không cần cập nhật thủ công.

        Returns:
            float: Giá trị trong khoảng ``[0.0, patience]``.
        """
        return max(0.0, self.patience - (time.time() - self.start_time))

    @property
    def patience_ratio(self):
        """
        Tỉ lệ kiên nhẫn còn lại, dùng để vẽ thanh màu trong UI.

        Returns:
            float: ``1.0`` (đầy kiên nhẫn) → ``0.0`` (hết kiên nhẫn).
        """
        return self.time_left / self.patience

    def is_expired(self):
        """
        Kiểm tra khách đã hết kiên nhẫn và bỏ đi chưa.

        Returns:
            bool: ``True`` nếu ``time_left <= 0``.
        """
        return self.time_left <= 0


# ══════════════════════════════════════════════════════════
#  2. CUSTOMER MANAGER — spawn, heap, queue ngoài cửa
# ══════════════════════════════════════════════════════════
class CustomerManager:
    """
    Quản lý toàn bộ vòng đời khách hàng trong một ván chơi.

    Hai cấu trúc dữ liệu chính:
        - ``active`` (MinHeap)     : Khách đang ngồi tại quầy,
          sắp xếp theo ``time_left`` tăng dần.
        - ``waiting`` (WaitingQueue): Khách đứng chờ ngoài cửa (FIFO).

    Khi ``active`` chưa đầy (< ``MAX_CUSTOMERS_ON_SCREEN``), khách mới được
    ngồi thẳng vào quầy. Ngược lại, họ vào hàng đợi bên ngoài.
    """

    def __init__(self):
        """Khởi tạo manager với heap và queue rỗng."""
        self.active   = MinHeap()       # khách đang ngồi tại quầy
        self.waiting  = WaitingQueue()  # khách đứng ngoài cửa
        self._counter = 0               # bộ đếm ID khách, tăng dần

    def spawn(self):
        """
        Tạo một khách mới ngẫu nhiên và đưa vào quầy hoặc hàng chờ.

        Xác suất 50% gọi trực tiếp tên món, 50% mô tả tâm trạng.
        Nếu quầy còn chỗ trống, khách ngồi vào ngay; ngược lại xếp hàng ngoài cửa.
        """
        name   = random.choice(CUSTOMER_NAMES)
        is_vip = random.random() < VIP_SPAWN_CHANCE

        if random.random() < 0.5:
            drink_name   = random.choice([k for k, v in RECIPES_DATA.items() if not v["hidden"]])
            request_type = "direct"
            request_data = drink_name
            voice_key    = None  # ---> Không có voice order, gán bằng None cho nó câm
        else:
            mood         = random.choice(MOOD_DIALOGUES)
            request_type = "mood"
            request_data = mood
            voice_key    = mood.get("audio")  # Đồng bộ trực tiếp với id audio đã khai báo

        # Nhét voice_key vào túi khách
        customer = Customer(self._counter, name, is_vip, request_type, request_data, voice_key)

        if len(self.active) < MAX_CUSTOMERS_ON_SCREEN:
            self._seat(customer)
        else:
            self.waiting.enqueue(customer)

    def _seat(self, customer):
        """
        Đưa khách vào MinHeap (ngồi vào ghế tại quầy).

        Key của heap là ``time_left`` hiện tại của khách.
        Key này sẽ được cập nhật mỗi frame trong ``update()``.

        Args:
            customer (Customer): Khách cần cho ngồi.
        """
        if customer.voice_key:
            sound_mgr.play(customer.voice_key)

        # 2. Reset lại start_time để tính patience từ giây phút này
        customer.start_time = time.time()

        # 3. Đưa vào quầy (MinHeap)
        self.active.push([customer.time_left, customer.id, customer])

    def update(self):
        """
        Cập nhật trạng thái toàn bộ khách mỗi frame.

        Các bước thực hiện:
            1. Đồng bộ lại key ``time_left`` trong heap theo thời gian thực.
            2. Rebuild heap để đảm bảo heap property sau khi key thay đổi.
            3. Pop các khách ở đỉnh heap đã hết kiên nhẫn (``time_left <= 0``).
            4. Với mỗi khách timeout, thử đưa người tiếp theo từ hàng chờ vào.

        Lý do chỉ check đỉnh heap:
            MinHeap đảm bảo phần tử nhỏ nhất ở đỉnh. Nếu đỉnh chưa hết
            kiên nhẫn, các phần tử bên dưới chắc chắn cũng chưa hết.

        Returns:
            list[Customer]: Danh sách khách vừa timeout trong frame này.
                ``GameState`` dùng list này để trừ điểm.
        """
        for item in self.active.heap:
            item[0] = item[2].time_left
        self.active._build_heap()

        expired = []
        while not self.active.is_empty():
            top = self.active.peek()
            if top[2].is_expired():
                gone = self.active.pop()[2]
                expired.append(gone)
                self._fill_from_waiting()
            else:
                break

        return expired

    def serve(self, customer_id):
        """
        Xóa khách đã được phục vụ khỏi heap và điền chỗ trống từ hàng chờ.

        Args:
            customer_id (int): ID của khách vừa được phục vụ.
        """
        self.active.remove_by_id(customer_id)
        self._fill_from_waiting()

    def get_active_list(self):
        """
        Trả về danh sách tất cả khách đang ngồi tại quầy.

        Returns:
            list[Customer]: Dùng bởi ``Renderer`` để vẽ CustomerCard.
        """
        return [item[2] for item in self.active.heap]

    def get_next_customer(self):
        """
        Lấy khách gấp nhất hiện tại (đỉnh MinHeap) mà không xóa họ.

        Returns:
            Customer | None: Khách sắp hết kiên nhẫn nhất,
            hoặc ``None`` nếu quầy trống.
        """
        top = self.active.peek()
        return top[2] if top else None

    def _fill_from_waiting(self):
        """
        Đưa khách tiếp theo từ hàng chờ vào quầy nếu còn chỗ trống.

        Được gọi tự động sau mỗi lần ``serve()`` hoặc timeout.
        """
        if not self.waiting.is_empty() and len(self.active) < MAX_CUSTOMERS_ON_SCREEN:
            self._seat(self.waiting.dequeue())


# ══════════════════════════════════════════════════════════
#  3. MIXING ENGINE — shaker, undo, kiểm tra công thức
# ══════════════════════════════════════════════════════════
class MixingEngine:
    """
    Xử lý toàn bộ logic pha chế: quản lý bình lắc, kiểm tra công thức,
    và xử lý việc khám phá các món ẩn.

    Sử dụng ba cấu trúc dữ liệu từ ``algorithms.py``:
        - ``LiquidShaker`` : Lưu trữ và trộn nguyên liệu theo thể tích.
        - ``Trie``          : Hỗ trợ autocomplete tên công thức.
        - ``InvertedIndex`` : Gợi ý công thức theo tag tâm trạng khách.

    Attributes:
        shaker (LiquidShaker): Bình lắc hiện tại.
        recipe_trie (Trie): Cây tiền tố chứa các công thức đã mở khóa.
        inv_index (InvertedIndex): Chỉ mục đảo ngược tag → công thức.
    """
    def __init__(self, recipes_data):
        """
        Khởi tạo engine với dữ liệu công thức và callback khám phá.

        Args:
            recipes_data (dict): Dữ liệu công thức từ ``settings.RECIPES_DATA``.
            discovered_cb (callable | None): Hàm callback nhận ``drink_name`` (str)
                được gọi khi người chơi khám phá công thức ẩn lần đầu tiên.
        """
        self.shaker = LiquidShaker(capacity=SHAKER_MAX_VOLUME)
        

        self.recipe_trie = Trie()
        self.inv_index = InvertedIndex()

        self._recipes    = {}
        
        self._load_recipes(recipes_data)

    def _load_recipes(self, recipes_data):
        """
        Nạp dữ liệu công thức vào Trie và InvertedIndex khi khởi tạo.

        Chỉ chèn vào Trie các công thức chưa ẩn (``hidden=False``).
        Công thức ẩn sẽ được thêm sau qua ``InvertedIndex.unlock_drink()``
        khi người chơi khám phá ra.

        Args:
            recipes_data (dict): Dữ liệu từ ``settings.RECIPES_DATA``.
        """
        for name, info in recipes_data.items():
            self._recipes[name] = info
            self.recipe_trie.insert(name, info)
        self.inv_index.build(recipes_data)

    # ── Thao tác bình lắc ──────────────────────────────────
    def pour(self, ingredient_name, amount):
        """
        Rót nguyên liệu vào bình lắc, tự tra màu từ ``INGREDIENTS_DATA``.

        Args:
            ingredient_name (str): Tên nguyên liệu cần rót.
            amount (float): Lượng rót (ml).

        Returns:
            bool: ``True`` nếu rót thành công, ``False`` nếu bình đầy.
        """
        color = INGREDIENTS_DATA.get(ingredient_name, {}).get("color", (255, 255, 255))
        return self.shaker.pour(ingredient_name, amount, color)

    def clear_shaker(self):
        """Đổ bỏ toàn bộ nội dung bình lắc về trạng thái rỗng."""
        self.shaker.clear()

    def get_shaker_state(self):
        """
        Trả về trạng thái hiện tại của bình lắc để Renderer vẽ.

        Returns:
            tuple: ``(current_volume, capacity, mixed_color)`` —
            thể tích hiện tại (float), dung tích tối đa (float),
            và màu RGB hỗn hợp (tuple | None).
        """

    # ── Kiểm tra & phục vụ ────────────────────────────────
    def identify_drink(self):
        """
        Nhận diện món đồ uống hiện tại trong bình lắc (không chấm điểm).
        Trả về (drink_name, error_margin). Nếu lỗi > 30% thì drink_name = None.
        """
        proportions = self.shaker.get_proportions()
        if not proportions:
            return None, float('inf')

        best_match = None
        lowest_error = float('inf')

        # 1. Thuật toán tìm món khớp nhất dựa trên sai số % (Margin of Error)
        for name, info in self._recipes.items():
            recipe_props = info["ingredients"]
            error = 0.0
            
            # Tính độ lệch của các nguyên liệu CÓ trong công thức
            for ing, expected_ratio in recipe_props.items():
                actual_ratio = proportions.get(ing, 0.0)
                error += abs(expected_ratio - actual_ratio)
            
            # Cộng thêm sai số nếu người chơi lỡ tay bỏ nguyên liệu RÁC
            for ing, actual_ratio in proportions.items():
                if ing not in recipe_props:
                    error += actual_ratio
            
            if error < lowest_error:
                lowest_error = error
                best_match = name

        # Nếu sai số tổng quá 0.3 (30%) -> Pha quá tệ
        if lowest_error > 0.3:
            return None, lowest_error
            
        return best_match, lowest_error

    def check_and_serve(self, customer):
        """
        Kiểm tra nội dung bình lắc, xác định món pha, và tính điểm.
        """
        result = {"correct": False, "drink_name": None, "score_delta": 0, "discovered": None}

        best_match, lowest_error = self.identify_drink()

        if not best_match:
            result["score_delta"] = SCORE_WRONG_PENALTY
            return result

        # 2. Hệ số điểm: Pha càng chuẩn điểm càng cao
        if lowest_error <= 0.10:     # Lệch <= 10%
            accuracy_multiplier = 1.5  # PERFECT!
        elif lowest_error <= 0.20:   # Lệch <= 20%
            accuracy_multiplier = 1.0  # GOOD
        else:                        # Lệch <= 30%
            accuracy_multiplier = 0.7  # OK, tạm chấp nhận

        matched_drink = best_match
        result["drink_name"] = matched_drink

        # 3. Chấm điểm theo order của khách
        base_score = 0
        if customer.request_type == "direct":
            if matched_drink.lower() == customer.request_data.lower():
                result["correct"] = True
                base_score = SCORE_CORRECT_VIP if customer.is_vip else SCORE_CORRECT_NORMAL
            else:
                result["score_delta"] = SCORE_WRONG_PENALTY
                return result
        else:
            suggested = self.inv_index.suggest(customer.request_data["tags"])
            if matched_drink in suggested:
                result["correct"] = True
                base_score = SCORE_CORRECT_VIP if customer.is_vip else SCORE_CORRECT_NORMAL
            else:
                result["score_delta"] = SCORE_WRONG_PENALTY
                return result

        # Tính điểm cuối cùng
        result["score_delta"] = int(base_score * accuracy_multiplier)


        return result

    def suggest_by_tags(self, tags):
        """
        Gợi ý công thức phù hợp với danh sách tag.

        Ủy quyền cho ``InvertedIndex.suggest()``.

        Args:
            tags (list[str]): Danh sách tag cần tra cứu.

        Returns:
            list[str]: Tên các công thức sắp xếp theo độ phù hợp giảm dần.
        """
        return self.inv_index.suggest(tags)

    def search_recipes(self, query):
        """
        Tìm kiếm thông minh: Trả về công thức khớp tên (Trie) HOẶC khớp tag.
        Hỗ trợ gõ dấu '#' ở đầu để tập trung tìm tag.
        """
        query = query.lower()
        if not query:
            return self.recipe_trie.autocomplete("")

        # Gõ bình thường -> chỉ autocomplete theo tên món.
        if not query.startswith("#"):
            return self.recipe_trie.autocomplete(query)

        # Gõ # -> chuyển sang chế độ tìm theo tag.
        tag_query = query[1:]
        if not tag_query:
            return []

        results = []
        for name, info in self._recipes.items():
            if not info.get("hidden") and any(tag_query in t.lower() for t in info["tags"]):
                results.append((name, info))
        return results


# ══════════════════════════════════════════════════════════
#  4. GAME STATE — máy trạng thái + điểm + leaderboard
# ══════════════════════════════════════════════════════════
class GameState:
    """
    Máy trạng thái tổng thể điều phối toàn bộ một ván chơi.

    Quản lý:
        - Chuyển tiếp giữa các trạng thái: MENU → PLAYING ↔ PAUSED → GAMEOVER.
        - Spawn khách theo interval thời gian thực.
        - Cộng/trừ điểm và cập nhật bảng điểm.
        - Điều phối ``CustomerManager`` và ``MixingEngine``.
        - Cung cấp các getter thuần để ``Renderer`` lấy data cần vẽ.

    States:
        - ``"GUIDE"``   : Màn hình hướng dẫn phím bấm khi mới mở game.
        - ``"MENU"``    : Màn hình chờ, chưa bắt đầu chơi.
        - ``"PLAYING"`` : Đang chơi, ``update()`` được gọi mỗi frame.
        - ``"PAUSED"``  : Tạm dừng, logic đóng băng, UI vẫn vẽ.
        - ``"GAMEOVER"``: Kết thúc, hiển thị điểm và bảng xếp hạng.

    Attributes:
        state (str): Trạng thái hiện tại, một trong ``STATES``.
        score (int): Điểm số hiện tại của người chơi (không âm).
        customers_total (int): Tổng số khách đã xử lý (phục vụ + timeout).
        leaderboard (list[dict]): Bảng điểm cao, sắp xếp giảm dần.
    """

    STATES = ("GUIDE", "MENU", "PLAYING", "PAUSED", "GAMEOVER")

    def __init__(self):
        """
        Khởi tạo GameState về trạng thái ban đầu (MENU).

        Tạo mới ``CustomerManager``, ``MixingEngine``, và đặt lại
        toàn bộ biến theo dõi game.
        """
        self.state           = "MENU"
        self.score           = 0
        self.customers_total = 0
        self.leaderboard     = self._load_leaderboard()
        self.last_saved_entry = None
        self.last_saved_rank  = None

        self.customer_manager = CustomerManager()
        self.mixing_engine    = MixingEngine(
            RECIPES_DATA,
        )

        self._last_spawn_time = time.time()
        self._spawn_interval  = CUSTOMER_SPAWN_INTERVAL
        self._discovery_msg   = None
        self.finished_drink_name = None

    # ── Vòng lặp chính ────────────────────────────────────
    def update(self):
        """
        Cập nhật game logic cho một frame.

        Chỉ thực thi khi ``state == "PLAYING"``. Các bước:
            1. Kiểm tra interval spawn → gọi ``customer_manager.spawn()`` nếu đến giờ
               và chưa đạt ``MAX_CUSTOMERS_PER_GAME``.
            2. Cập nhật heap khách, nhận về danh sách khách timeout → trừ điểm.
            3. Kiểm tra điều kiện kết thúc game:
               đã xử lý đủ khách VÀ quầy không còn ai.

        Được gọi bởi ``main.py`` mỗi iteration của game loop.
        """
        if self.state != "PLAYING":
            return

        now = time.time()
        if (now - self._last_spawn_time >= self._spawn_interval
                and self.customers_total < MAX_CUSTOMERS_PER_GAME):
            self.customer_manager.spawn()
            sound_mgr.play("bell")        # Kính koong!
            self._last_spawn_time = now

        expired = self.customer_manager.update()
        for c in expired:
            self.score += SCORE_TIMEOUT_PENALTY
            self.customers_total += 1

        if (self.customers_total >= MAX_CUSTOMERS_PER_GAME
                and self.customer_manager.active.is_empty()):
            self._end_game()

    # ── Hành động người chơi ──────────────────────────────
    def serve_current_customer(self):
        """
        Xử lý hành động phục vụ khi người chơi nhấn SPACE hoặc nút Serve.

        Lấy khách gấp nhất (đỉnh MinHeap), kiểm tra công thức trong bình lắc,
        cộng/trừ điểm, xóa khách khỏi heap, tăng đếm khách, và reset bình.

        Returns:
            dict | None: Kết quả phục vụ từ ``MixingEngine.check_and_serve()``
                để ``Renderer`` hiển thị feedback (flash, banner).
                ``None`` nếu quầy không có khách.
        """
        customer = self.customer_manager.get_next_customer()
        if not customer:
            return None

        result = self.mixing_engine.check_and_serve(customer)
        self.score += result["score_delta"]
        self.score  = max(0, self.score)

        self.customer_manager.serve(customer.id)
        self.customers_total += 1
        self.mixing_engine.clear_shaker()
        self.finished_drink_name = None

        return result

    def pour_ingredient(self, name, amount):
        """
        Rót nguyên liệu vào bình lắc. Được gọi mỗi frame khi người chơi
        kéo chai vào vùng Shaker và giữ chuột.

        Args:
            name (str): Tên nguyên liệu.
            amount (float): Lượng rót mỗi frame (ml), lấy từ ``POUR_RATE``.

        Returns:
            bool: ``True`` nếu rót thành công, ``False`` nếu bình đầy.
        """
        return self.mixing_engine.pour(name, amount)

    def clear_shaker(self):
        """Xóa toàn bộ bình lắc (phím C)."""
        self.mixing_engine.clear_shaker()
        self.finished_drink_name = None
        
    def finish_shaking(self):
        """Gọi khi lắc xong để nhận diện món."""
        drink_name, _ = self.mixing_engine.identify_drink()
        self.finished_drink_name = drink_name

    def search_recipes(self, query):
        """
        Gọi hàm tìm kiếm thông minh từ MixingEngine (dùng cho SearchBar).
        """
        return self.mixing_engine.search_recipes(query)

    def suggest_by_tags(self, tags):
        """
        Gợi ý công thức theo tag (dùng để hiển thị hint cho order "mood").

        Args:
            tags (list[str]): Danh sách tag cần gợi ý.

        Returns:
            list[str]: Danh sách tên công thức theo độ phù hợp.
        """
        return self.mixing_engine.suggest_by_tags(tags)

    # ── State transitions ─────────────────────────────────
    def start_game(self):
        """
        Reset hoàn toàn và bắt đầu một ván chơi mới.

        Gọi ``__init__()`` để reset state, sau đó chuyển sang ``"PLAYING"``
        và spawn khách đầu tiên ngay lập tức (không chờ interval).
        """
        self.__init__()
        self.state = "PLAYING"
        self.customer_manager.spawn()
        sound_mgr.play("bell")        # Kính koong! # Khách: "A hèm... cho ly nước coi"

    def open_guide(self):
        """Chuyển từ start screen sang màn hình hướng dẫn."""
        self.state = "GUIDE"

    def toggle_pause(self):
        """
        Chuyển đổi qua lại giữa trạng thái ``"PLAYING"`` và ``"PAUSED"`` (phím P).

        Không làm gì nếu state không phải PLAYING hoặc PAUSED.
        """
        if self.state == "PLAYING":
            self.state = "PAUSED"
        elif self.state == "PAUSED":
            self.state = "PLAYING"

    def _end_game(self):
        """
        Kết thúc ván chơi: chuyển sang ``"GAMEOVER"`` và cập nhật bảng điểm.

        Thêm điểm hiện tại vào ``leaderboard`` rồi sắp xếp lại
        bằng ``quick_sort_leaderboard``.
        """
        if self.state == "GAMEOVER":
            return

        self.state = "GAMEOVER"
        entry = {"name": "Player", "score": self.score}
        self.leaderboard.append(entry)
        self.leaderboard = quick_sort_leaderboard(self.leaderboard)
        self.last_saved_entry = entry
        self.last_saved_rank = next(
            (i + 1 for i, saved_entry in enumerate(self.leaderboard) if saved_entry is entry),
            None
        )
        self._save_leaderboard()
    def _save_leaderboard(self):
        """Ghi bảng điểm ra file JSON"""
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(self.leaderboard, f, ensure_ascii=False, indent=2)

    def _load_leaderboard(self):
        """Đọc bảng điểm từ file JSON (nếu có)"""
        if os.path.exists(LEADERBOARD_PATH):
            try:
                with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    # ── Getters cho UI ────────────────────────────────────
    def get_active_customers(self):
        """
        Trả về danh sách khách đang ngồi tại quầy để UI vẽ CustomerCard.

        Returns:
            list[Customer]: Danh sách khách theo thứ tự trong heap.
        """
        return self.customer_manager.get_active_list()

    def get_next_customer(self):
        """
        Trả về khách gấp nhất (đỉnh MinHeap) để UI hiển thị hint.

        Returns:
            Customer | None: Khách sắp hết kiên nhẫn nhất, hoặc ``None``.
        """
        return self.customer_manager.get_next_customer()

    def get_shaker_state(self):
        """
        Trả về trạng thái hiện tại của bình lắc để Renderer vẽ.

        Returns:
            tuple: ``(current_volume, capacity, mixed_color)`` —
            thể tích hiện tại (float), dung tích tối đa (float),
            và màu RGB hỗn hợp (tuple), hoặc ``None`` nếu bình rỗng.
        """
        shaker = self.mixing_engine.shaker
        vol = getattr(shaker, 'current_volume', 0)
        max_vol = getattr(shaker, 'capacity', 300) 
        
        if vol > 0:
            if hasattr(shaker, 'get_mixed_color'):
                color = shaker.get_mixed_color()
            else:
                color = getattr(shaker, 'mixed_color', (220, 80, 80)) 
        else:
            color = None
            
        return vol, max_vol, color
    

    def get_sorted_inventory(self):
        """
        Trả về danh sách nguyên liệu đã sắp xếp để ``InventoryPanel`` vẽ.

        Sắp xếp 2 lần (stable sort):
            1. Theo ``name`` (A–Z) — tiêu chí phụ.
            2. Theo ``type`` (A–Z) — tiêu chí chính.

        Kết quả: trong cùng ``type``, nguyên liệu được sắp theo ``name``.

        Returns:
            list[dict]: Danh sách nguyên liệu (name, color, asset, price, type).
        """
        items = [{"name": k, **v} for k, v in INGREDIENTS_DATA.items()]
        items = merge_sort_inventory(items, "name")
        items = merge_sort_inventory(items, "type")
        return items

    # ── Callback ─────────────────────────────────────────
    
