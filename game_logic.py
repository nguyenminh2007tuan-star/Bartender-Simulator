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

from algorithms import (
    MinHeap, WaitingQueue, ActionStack,
    Trie, InvertedIndex,
    quick_sort_leaderboard, merge_sort_inventory,
)
from settings import *


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

    def __init__(self, c_id, name, is_vip, request_type, request_data):
        """
        Khởi tạo khách hàng mới.

        Args:
            c_id (int): ID duy nhất của khách.
            name (str): Tên hiển thị.
            is_vip (bool): Là VIP hay không.
            request_type (str): ``"direct"`` hoặc ``"mood"``.
            request_data (str | dict): Nội dung yêu cầu.
        """
        self.id           = c_id
        self.name         = name
        self.is_vip       = is_vip
        self.request_type = request_type
        self.request_data = request_data
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
        Tạo một khách mới với thông tin ngẫu nhiên và đưa vào game.

        Logic sinh:
            - Tên: chọn ngẫu nhiên từ ``CUSTOMER_NAMES``.
            - VIP: xác suất ``VIP_SPAWN_CHANCE`` (30%).
            - Kiểu order: 50% "direct" (gọi tên món đã mở khóa),
              50% "mood" (tâm trạng từ ``MOOD_DIALOGUES``).

        Khách được ngồi vào quầy nếu còn chỗ, ngược lại xếp hàng chờ.
        """
        self._counter += 1
        name   = random.choice(CUSTOMER_NAMES)
        is_vip = random.random() < VIP_SPAWN_CHANCE

        if random.random() < 0.5:
            drink_name   = random.choice([k for k, v in RECIPES_DATA.items() if not v["hidden"]])
            request_type = "direct"
            request_data = drink_name
        else:
            mood         = random.choice(MOOD_DIALOGUES)
            request_type = "mood"
            request_data = mood

        customer = Customer(self._counter, name, is_vip, request_type, request_data)

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
    Xử lý toàn bộ logic pha chế: bình lắc, kiểm tra công thức, khám phá món mới.

    Quản lý ba cấu trúc dữ liệu liên quan đến công thức:
        - ``shaker`` (ActionStack)   : Bình lắc có giới hạn dung lượng, hỗ trợ undo.
        - ``recipe_trie`` (Trie)     : Tìm kiếm và autocomplete tên công thức.
        - ``inv_index`` (InvertedIndex): Gợi ý món theo tag cho order kiểu "mood".

    Khi người chơi phục vụ thành công một "hidden recipe" lần đầu,
    engine tự động mở khóa và cập nhật cả Trie lẫn InvertedIndex.

    Args:
        recipes_data (dict): Dữ liệu công thức từ ``settings.RECIPES_DATA``.
        discovered_cb (callable | None): Callback nhận tên món khi khám phá.
            Dùng bởi ``GameState`` để lưu discovery message cho UI.
    """

    def __init__(self, recipes_data, discovered_cb=None):
        """
        Khởi tạo engine, load toàn bộ công thức và build các cấu trúc tìm kiếm.

        Args:
            recipes_data (dict): Dữ liệu từ ``settings.RECIPES_DATA``.
            discovered_cb (callable | None): Hàm gọi khi có khám phá mới.
        """
        self.shaker = ActionStack(capacity=SHAKER_CAPACITY)
        self._discovered_cb = discovered_cb

        self.recipe_trie = Trie()
        self.inv_index = InvertedIndex()

        self._recipes    = {}
        self._discovered = set()

        self._load_recipes(recipes_data)

    def _load_recipes(self, recipes_data):
        """
        Nạp dữ liệu công thức vào engine.

        Chỉ insert các công thức không ẩn vào Trie.
        Toàn bộ công thức (kể cả ẩn) được lưu trong ``_recipes`` để tra cứu.
        InvertedIndex cũng chỉ index công thức đã mở khóa ban đầu.

        Args:
            recipes_data (dict): Dữ liệu từ ``settings.RECIPES_DATA``.
        """
        for name, info in recipes_data.items():
            self._recipes[name] = info
            if not info["hidden"]:
                self.recipe_trie.insert(name, info)
        self.inv_index.build(recipes_data)

    # ── Thao tác bình lắc ──────────────────────────────────
    def add_ingredient(self, ingredient_name):
        """
        Thêm một nguyên liệu vào bình lắc.

        Args:
            ingredient_name (str): Tên nguyên liệu cần thêm.

        Returns:
            bool: ``True`` nếu thêm thành công, ``False`` nếu bình đầy.
        """
        return self.shaker.push(ingredient_name)

    def undo(self):
        """
        Lấy nguyên liệu cuối cùng ra khỏi bình (undo thao tác thêm).

        Returns:
            str | None: Tên nguyên liệu vừa lấy ra, hoặc ``None`` nếu bình rỗng.
        """
        return self.shaker.pop()

    def clear_shaker(self):
        """Xóa toàn bộ nguyên liệu trong bình lắc."""
        self.shaker.clear()

    def get_shaker_contents(self):
        """
        Trả về danh sách nguyên liệu hiện có trong bình lắc.

        Returns:
            list[str]: Danh sách tên nguyên liệu theo thứ tự thêm vào.
        """
        return self.shaker.to_list()

    # ── Kiểm tra & phục vụ ────────────────────────────────
    def check_and_serve(self, customer):
        """
        Kiểm tra bình lắc có tạo thành công thức đúng với order của ``customer`` không.

        Logic kiểm tra:
            1. Lấy danh sách nguyên liệu trong bình (đã sort để so sánh).
            2. Tìm xem có công thức nào khớp với tập nguyên liệu đó không.
            3. Nếu không khớp → sai, trừ điểm.
            4. Nếu khớp:
                - Order ``"direct"``: so sánh tên món với tên yêu cầu.
                - Order ``"mood"``: kiểm tra món có trong danh sách gợi ý theo tag.
            5. Nếu là công thức ẩn chưa khám phá → mở khóa, thưởng điểm bonus,
               cập nhật Trie và InvertedIndex, gọi ``discovered_cb``.

        Args:
            customer (Customer): Khách đang được phục vụ.

        Returns:
            dict: Kết quả phục vụ với các key:
                - ``correct`` (bool): Pha đúng hay sai.
                - ``drink_name`` (str | None): Tên công thức đã pha (nếu khớp).
                - ``score_delta`` (int): Điểm thêm/trừ cho lần phục vụ này.
                - ``discovered`` (str | None): Tên công thức ẩn vừa khám phá,
                  hoặc ``None`` nếu không có.
        """
        mixed = sorted(self.shaker.to_list())
        result = {"correct": False, "drink_name": None,
                  "score_delta": 0,  "discovered": None}

        matched_drink = self._find_recipe_by_ingredients(mixed)

        if matched_drink is None:
            result["score_delta"] = SCORE_WRONG_PENALTY
            return result

        result["drink_name"] = matched_drink

        if customer.request_type == "direct":
            if matched_drink.lower() == customer.request_data.lower():
                result["correct"]     = True
                result["score_delta"] = SCORE_CORRECT_VIP if customer.is_vip else SCORE_CORRECT_NORMAL
            else:
                result["score_delta"] = SCORE_WRONG_PENALTY

        else:
            suggested = self.inv_index.suggest(customer.request_data["tags"])
            if matched_drink in suggested:
                result["correct"]     = True
                result["score_delta"] = SCORE_CORRECT_VIP if customer.is_vip else SCORE_CORRECT_NORMAL
            else:
                result["score_delta"] = SCORE_WRONG_PENALTY

        info = self._recipes.get(matched_drink)
        if info and info["hidden"] and matched_drink not in self._discovered:
            self._discovered.add(matched_drink)
            self.recipe_trie.insert(matched_drink, info)
            self.inv_index.unlock_drink(matched_drink, info["tags"])
            self._recipes[matched_drink]["hidden"] = False
            result["discovered"]   = matched_drink
            result["score_delta"] += SCORE_DISCOVERY_BONUS
            if self._discovered_cb:
                self._discovered_cb(matched_drink)

        return result

    # ── Gợi ý theo tag (đọc vị) ───────────────────────────
    def suggest_by_tags(self, tags):
        """
        Gợi ý công thức phù hợp với danh sách tag từ lời nói của khách.

        Delegate cho ``InvertedIndex.suggest()``.

        Args:
            tags (list[str]): Danh sách tag cần tìm kiếm.

        Returns:
            list[str]: Danh sách tên công thức sắp xếp theo độ phù hợp.
        """
        return self.inv_index.suggest(tags)

    # ── Autocomplete ──────────────────────────────────────
    def autocomplete(self, prefix):
        """
        Tìm kiếm công thức bắt đầu bằng ``prefix`` (dùng cho SearchBar).

        Delegate cho ``Trie.autocomplete()``.

        Args:
            prefix (str): Chuỗi tiền tố người chơi đang gõ.

        Returns:
            list[tuple[str, dict]]: Danh sách ``(tên_món, dữ_liệu)`` khớp.
        """
        return self.recipe_trie.autocomplete(prefix)

    # ── Nội bộ ───────────────────────────────────────────
    def _find_recipe_by_ingredients(self, sorted_ingredients):
        """
        Tìm tên công thức khớp với danh sách nguyên liệu đã được sort.

        So sánh ``sorted_ingredients`` với ``sorted(info["ingredients"])``
        của từng công thức trong ``_recipes``.

        Args:
            sorted_ingredients (list[str]): Danh sách nguyên liệu đã sort.

        Returns:
            str | None: Tên công thức khớp, hoặc ``None`` nếu không tìm thấy.
        """
        for name, info in self._recipes.items():
            if sorted(info["ingredients"]) == sorted_ingredients:
                return name
        return None

    def get_discovered(self):
        """
        Trả về danh sách tên các công thức ẩn đã được khám phá.

        Returns:
            list[str]: Danh sách tên công thức.
        """
        return list(self._discovered)


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

    STATES = ("MENU", "PLAYING", "PAUSED", "GAMEOVER")

    def __init__(self):
        """
        Khởi tạo GameState về trạng thái ban đầu (MENU).

        Tạo mới ``CustomerManager``, ``MixingEngine``, và đặt lại
        toàn bộ biến theo dõi game.
        """
        self.state           = "MENU"
        self.score           = 0
        self.customers_total = 0
        self.leaderboard     = []

        self.customer_manager = CustomerManager()
        self.mixing_engine    = MixingEngine(
            RECIPES_DATA,
            discovered_cb=self._on_discovery,
        )

        self._last_spawn_time = time.time()
        self._spawn_interval  = 8.0
        self._discovery_msg   = None

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

        return result

    def add_ingredient(self, name):
        """
        Thêm một nguyên liệu vào bình lắc.

        Args:
            name (str): Tên nguyên liệu.

        Returns:
            bool: ``True`` nếu thêm thành công, ``False`` nếu bình đầy.
        """
        return self.mixing_engine.add_ingredient(name)

    def undo_ingredient(self):
        """
        Lấy nguyên liệu cuối ra khỏi bình lắc (undo, phím Z).

        Returns:
            str | None: Tên nguyên liệu vừa lấy ra, hoặc ``None``.
        """
        return self.mixing_engine.undo()

    def clear_shaker(self):
        """Xóa toàn bộ bình lắc (phím C)."""
        self.mixing_engine.clear_shaker()

    def autocomplete(self, prefix):
        """
        Gọi autocomplete từ MixingEngine (dùng cho SearchBar).

        Args:
            prefix (str): Chuỗi tiền tố đang gõ.

        Returns:
            list[tuple[str, dict]]: Kết quả autocomplete.
        """
        return self.mixing_engine.autocomplete(prefix)

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
        self.state = "GAMEOVER"
        self.leaderboard.append({"name": "Player", "score": self.score})
        self.leaderboard = quick_sort_leaderboard(self.leaderboard)

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

    def get_shaker_contents(self):
        """
        Trả về danh sách nguyên liệu trong bình lắc để ShakerUI vẽ.

        Returns:
            list[str]: Danh sách tên nguyên liệu theo thứ tự thêm vào.
        """
        return self.mixing_engine.get_shaker_contents()

    def get_discovery_message(self):
        """
        Lấy tên công thức ẩn vừa được khám phá (nếu có) và tự clear sau khi đọc.

        Được gọi bởi ``main.py`` mỗi frame. Nếu có giá trị, Renderer sẽ
        hiển thị ``DiscoveryBanner``.

        Returns:
            str | None: Tên công thức vừa khám phá, hoặc ``None``.
        """
        msg = self._discovery_msg
        self._discovery_msg = None
        return msg

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
    def _on_discovery(self, drink_name):
        """
        Callback được ``MixingEngine`` gọi khi khám phá công thức ẩn mới.

        Lưu tên công thức vào ``_discovery_msg`` để ``main.py`` đọc
        và truyền cho ``DiscoveryBanner`` hiển thị trong frame tiếp theo.

        Args:
            drink_name (str): Tên công thức vừa được khám phá.
        """
        self._discovery_msg = drink_name