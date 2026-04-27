# algorithms.py
"""
Toàn bộ cấu trúc dữ liệu & giải thuật của game.

Module này KHÔNG import pygame và có thể được test hoàn toàn độc lập.

Các cấu trúc dữ liệu được triển khai:
    - MinHeap      : Hàng đợi ưu tiên quản lý khách theo thời gian còn lại.
    - WaitingQueue : Hàng đợi FIFO cho khách đứng chờ bên ngoài.
    - ActionStack  : Stack có giới hạn dung lượng cho bình lắc (shaker).
    - Trie         : Cây tiền tố hỗ trợ autocomplete tên công thức.
    - InvertedIndex: Chỉ mục đảo ngược tag → công thức để "đọc vị" khách.

Các giải thuật sắp xếp:
    - quick_sort_leaderboard  : Sắp xếp bảng điểm (giảm dần theo điểm).
    - merge_sort_inventory    : Sắp xếp kho nguyên liệu (ổn định, đa tiêu chí).
"""


# ══════════════════════════════════════════════════════════
#  1. MIN-HEAP — quản lý hàng đợi khách theo độ ưu tiên
#     Key = time_left (thời gian còn lại), nhỏ nhất → đỉnh
# ══════════════════════════════════════════════════════════
class MinHeap:
    """
    Min-Heap tùy chỉnh để quản lý hàng đợi khách đang ngồi tại quầy.

    Mỗi phần tử trong heap có dạng: ``[time_left, customer_id, customer_obj]``

    Khách có ``time_left`` nhỏ nhất (sắp hết kiên nhẫn nhất) luôn ở đỉnh heap,
    giúp game ưu tiên phục vụ đúng người trước.

    Độ phức tạp:
        - push / pop: O(log n)
        - remove_by_id: O(n) tìm + O(log n) heapify
        - update_times / _build_heap: O(n)
        - peek: O(1)
    """

    def __init__(self):
        """Khởi tạo heap rỗng."""
        # Mỗi phần tử: [time_left, customer_id, customer_obj]
        self.heap = []

    def push(self, item):
        """
        Thêm một phần tử mới vào heap.

        Args:
            item (list): ``[time_left, customer_id, customer_obj]``

        Complexity: O(log n)
        """
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        """
        Lấy và xóa phần tử có ``time_left`` nhỏ nhất (đỉnh heap).

        Returns:
            list | None: Phần tử ``[time_left, customer_id, customer_obj]``,
            hoặc ``None`` nếu heap rỗng.

        Complexity: O(log n)
        """
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def remove_by_id(self, customer_id):
        """
        Xóa một phần tử bất kỳ khỏi heap theo ``customer_id``.

        Được gọi khi bartender đã phục vụ xong một khách cụ thể
        (không nhất thiết phải là khách gấp nhất).

        Thuật toán:
            1. Tìm tuyến tính phần tử có ``customer_id`` khớp — O(n).
            2. Swap với phần tử cuối và xóa cuối.
            3. Heapify cả lên lẫn xuống tại vị trí vừa swap — O(log n).

        Chấp nhận được vì heap thực tế rất nhỏ (tối đa 4–5 khách).

        Args:
            customer_id (int): ID duy nhất của khách cần xóa.

        Returns:
            list | None: Phần tử bị xóa, hoặc ``None`` nếu không tìm thấy.
        """
        idx = None
        for i, item in enumerate(self.heap):
            if item[1] == customer_id:
                idx = i
                break
        if idx is None:
            return None

        removed = self.heap[idx]
        last = self.heap.pop()

        if idx < len(self.heap):
            self.heap[idx] = last
            self._heapify_up(idx)
            self._heapify_down(idx)

        return removed

    def update_times(self, dt):
        """
        Giảm ``time_left`` của toàn bộ khách trong heap đi ``dt`` giây,
        sau đó rebuild heap để đảm bảo heap property.

        Args:
            dt (float): Thời gian delta (giây) kể từ frame trước.

        Note:
            Vì tất cả key đều thay đổi cùng lúc, việc rebuild toàn bộ
            (O(n)) hiệu quả hơn heapify từng phần tử riêng lẻ.
        """
        for item in self.heap:
            item[0] -= dt
        self._build_heap()

    def peek(self):
        """
        Xem phần tử đỉnh heap mà không xóa.

        Returns:
            list | None: Phần tử có ``time_left`` nhỏ nhất, hoặc ``None`` nếu rỗng.
        """
        return self.heap[0] if self.heap else None

    def is_empty(self):
        """Trả về ``True`` nếu heap không có phần tử nào."""
        return len(self.heap) == 0

    def __len__(self):
        """Số phần tử hiện có trong heap."""
        return len(self.heap)

    # ── Nội bộ ──
    def _heapify_up(self, index):
        """
        Đẩy phần tử tại ``index`` lên đúng vị trí trong heap.

        So sánh với node cha và swap nếu nhỏ hơn, lặp lại đến khi
        heap property được thỏa mãn.

        Args:
            index (int): Chỉ số phần tử cần heapify lên.
        """
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def _heapify_down(self, index):
        """
        Đẩy phần tử tại ``index`` xuống đúng vị trí trong heap.

        So sánh với cả hai node con và swap với con nhỏ hơn nếu cần,
        lặp lại đến khi heap property được thỏa mãn.

        Args:
            index (int): Chỉ số phần tử cần heapify xuống.
        """
        smallest = index
        left, right = 2 * index + 1, 2 * index + 2
        n = len(self.heap)
        if left  < n and self.heap[left][0]  < self.heap[smallest][0]: smallest = left
        if right < n and self.heap[right][0] < self.heap[smallest][0]: smallest = right
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def _build_heap(self):
        """
        Xây dựng lại heap từ mảng hiện tại bằng cách heapify từ dưới lên.

        Được gọi sau ``update_times()`` hoặc bất kỳ thao tác nào
        làm thay đổi nhiều key cùng lúc.

        Complexity: O(n) — hiệu quả hơn O(n log n) của việc push từng phần tử.
        """
        n = len(self.heap)
        for i in range(n // 2 - 1, -1, -1):
            self._heapify_down(i)


# ══════════════════════════════════════════════════════════
#  2. QUEUE NGOÀI CỬA — khách đứng chờ chỗ trống (FIFO)
# ══════════════════════════════════════════════════════════
class WaitingQueue:
    """
    Hàng đợi FIFO cho khách đứng chờ bên ngoài khi quầy đã đầy chỗ.

    Khách đến trước sẽ được vào quầy trước (first-in, first-out).
    Khi một chỗ ngồi trống (khách rời đi hoặc bị phục vụ xong),
    ``CustomerManager`` sẽ gọi ``dequeue()`` để đưa khách tiếp theo vào.
    """

    def __init__(self):
        """Khởi tạo hàng đợi rỗng."""
        self._items = []

    def enqueue(self, customer):
        """
        Thêm khách vào cuối hàng đợi.

        Args:
            customer (Customer): Đối tượng khách hàng cần xếp hàng.
        """
        self._items.append(customer)

    def dequeue(self):
        """
        Lấy khách đầu hàng ra (người chờ lâu nhất).

        Returns:
            Customer | None: Khách đầu hàng, hoặc ``None`` nếu hàng rỗng.
        """
        return self._items.pop(0) if self._items else None

    def is_empty(self):
        """Trả về ``True`` nếu không có khách nào đang chờ."""
        return len(self._items) == 0

    def __len__(self):
        """Số khách đang đứng chờ bên ngoài."""
        return len(self._items)

    def peek(self):
        """
        Xem khách đầu hàng mà không lấy ra.

        Returns:
            Customer | None: Khách đầu hàng, hoặc ``None`` nếu rỗng.
        """
        return self._items[0] if self._items else None


# ══════════════════════════════════════════════════════════
#  3. STACK — shaker (thêm/undo nguyên liệu)
# ══════════════════════════════════════════════════════════
class ActionStack:
    """
    Stack có giới hạn dung lượng, mô phỏng bình lắc (shaker) của bartender.

    Nguyên liệu được thêm vào đỉnh stack (push) và có thể hoàn tác
    bằng cách lấy nguyên liệu cuối ra (pop — undo).
    Khi stack đầy (đạt ``capacity``), không thể thêm nguyên liệu mới.

    Attributes:
        capacity (int): Số nguyên liệu tối đa bình có thể chứa.
            Mặc định lấy từ ``settings.SHAKER_CAPACITY`` = 5.
    """

    def __init__(self, capacity=5):
        """
        Khởi tạo stack rỗng với dung lượng giới hạn.

        Args:
            capacity (int): Số nguyên liệu tối đa. Mặc định là 5.
        """
        self._stack = []
        self.capacity = capacity

    def push(self, item):
        """
        Thêm một nguyên liệu vào đỉnh stack (vào bình lắc).

        Args:
            item (str): Tên nguyên liệu cần thêm.

        Returns:
            bool: ``True`` nếu thêm thành công, ``False`` nếu bình đã đầy.
        """
        if len(self._stack) >= self.capacity:
            return False    # bình đầy
        self._stack.append(item)
        return True

    def pop(self):
        """
        Lấy nguyên liệu cuối ra khỏi bình (thao tác undo).

        Returns:
            str | None: Tên nguyên liệu vừa lấy ra, hoặc ``None`` nếu bình rỗng.
        """
        return self._stack.pop() if self._stack else None

    def peek(self):
        """
        Xem nguyên liệu trên cùng mà không lấy ra.

        Returns:
            str | None: Tên nguyên liệu trên cùng, hoặc ``None`` nếu rỗng.
        """
        return self._stack[-1] if self._stack else None

    def is_empty(self):
        """Trả về ``True`` nếu bình lắc không có nguyên liệu nào."""
        return len(self._stack) == 0

    def is_full(self):
        """Trả về ``True`` nếu bình lắc đã đạt giới hạn dung lượng."""
        return len(self._stack) >= self.capacity

    def to_list(self):
        """
        Trả về bản sao danh sách nguyên liệu hiện có trong bình (không expose internal list).

        Returns:
            list[str]: Danh sách tên nguyên liệu theo thứ tự thêm vào.
        """
        return list(self._stack)

    def clear(self):
        """Xóa toàn bộ nguyên liệu trong bình lắc."""
        self._stack.clear()

    def __len__(self):
        """Số nguyên liệu hiện có trong bình."""
        return len(self._stack)


# ══════════════════════════════════════════════════════════
#  4. TRIE — autocomplete thanh tìm kiếm công thức O(L)
# ══════════════════════════════════════════════════════════
class TrieNode:
    """
    Một node trong cây Trie.

    Attributes:
        children (dict): Ánh xạ ký tự → TrieNode con.
        is_end (bool): ``True`` nếu node này đánh dấu kết thúc một từ hợp lệ.
        item_data (dict | None): Dữ liệu công thức đính kèm khi ``is_end = True``.
    """

    def __init__(self):
        """Khởi tạo node với không có con và chưa là kết thúc từ."""
        self.children  = {}
        self.is_end    = False
        self.item_data = None   # lưu data công thức khi kết thúc từ


class Trie:
    """
    Cây tiền tố (Prefix Tree) dùng để tìm kiếm và autocomplete tên công thức.

    Hỗ trợ:
        - Chèn tên công thức vào Trie kèm dữ liệu đính kèm.
        - Tìm kiếm theo tiền tố (prefix) với độ phức tạp O(L),
          trong đó L là độ dài chuỗi tìm kiếm.
        - Trả về tất cả công thức bắt đầu bằng một prefix cho trước (DFS).

    Ứng dụng trong game:
        Thanh tìm kiếm (SearchBar) gọi ``autocomplete()`` mỗi khi người chơi
        gõ ký tự mới để hiển thị danh sách công thức khớp.
    """

    def __init__(self):
        """Khởi tạo Trie với root node rỗng."""
        self.root = TrieNode()

    def insert(self, word, data):
        """
        Chèn một tên công thức vào Trie kèm dữ liệu.

        Tất cả ký tự được chuyển thành chữ thường trước khi lưu
        để đảm bảo tìm kiếm không phân biệt hoa/thường.

        Args:
            word (str): Tên công thức cần chèn (vd: ``"Margarita"``).
            data (dict): Dữ liệu công thức từ ``settings.RECIPES_DATA``
                (ingredients, tags, hidden).
        """
        node = self.root
        for ch in word.lower():
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end    = True
        node.item_data = data

    def search_prefix(self, prefix):
        """
        Duyệt Trie theo ``prefix`` và trả về node tại cuối chuỗi.

        Args:
            prefix (str): Chuỗi tiền tố cần tìm (không phân biệt hoa/thường).

        Returns:
            TrieNode | None: Node cuối cùng của prefix,
            hoặc ``None`` nếu prefix không tồn tại trong Trie.
        """
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def autocomplete(self, prefix):
        """
        Trả về tất cả công thức bắt đầu bằng ``prefix``.

        Thực hiện DFS từ node cuối của prefix để thu thập toàn bộ
        từ hợp lệ (``is_end = True``) trong cây con.

        Args:
            prefix (str): Chuỗi tiền tố cần tìm.

        Returns:
            list[tuple[str, dict]]: Danh sách ``(tên_công_thức, dữ_liệu)``
            khớp với prefix. Rỗng nếu không tìm thấy.
        """
        results = []
        node = self.search_prefix(prefix)
        if node:
            self._dfs(node, prefix, results)
        return results

    def _dfs(self, node, current, results):
        """
        Duyệt DFS từ ``node``, tích lũy kết quả vào ``results``.

        Args:
            node (TrieNode): Node hiện tại đang duyệt.
            current (str): Chuỗi đã tích lũy đến node hiện tại.
            results (list): List kết quả được cập nhật in-place.
        """
        if node.is_end:
            results.append((current, node.item_data))
        for ch, child in node.children.items():
            self._dfs(child, current + ch, results)


# ══════════════════════════════════════════════════════════
#  5. INVERTED INDEX — hệ thống "đọc vị" khách
#     tag → set(tên công thức phù hợp)
# ══════════════════════════════════════════════════════════
class InvertedIndex:
    """
    Chỉ mục đảo ngược (Inverted Index) ánh xạ tag → tập hợp công thức phù hợp.

    Dùng để "đọc vị" khách: khi khách mô tả tâm trạng thay vì gọi thẳng tên món,
    hệ thống tìm các tag trong lời nói và gợi ý công thức phù hợp nhất.

    Cấu trúc nội bộ:
        ``{ tag: set(drink_name) }``
        Ví dụ: ``{"chua": {"Margarita", "Mojito"}, "mạnh": {"Martini", "Margarita"}}``

    Ứng dụng trong game:
        - ``build()``: Xây dựng index khi khởi tạo game từ ``settings.RECIPES_DATA``.
        - ``unlock_drink()``: Cập nhật index khi người chơi khám phá công thức ẩn.
        - ``suggest()``: Trả về danh sách món phù hợp nhất với tags của khách.
    """

    def __init__(self):
        """Khởi tạo index rỗng."""
        self._index = {}   # { tag: set(drink_name) }

    def build(self, recipes_data):
        """
        Xây dựng chỉ mục từ toàn bộ dữ liệu công thức.

        Chỉ index các công thức đã mở khóa (``hidden=False``).
        Công thức ẩn sẽ được thêm sau qua ``unlock_drink()``.

        Args:
            recipes_data (dict): Dữ liệu từ ``settings.RECIPES_DATA``.
                Mỗi entry có dạng ``{name: {ingredients, tags, hidden}}``.
        """
        self._index.clear()
        for drink_name, info in recipes_data.items():
            if info.get("hidden", False):
                continue
            for tag in info["tags"]:
                if tag not in self._index:
                    self._index[tag] = set()
                self._index[tag].add(drink_name)

    def unlock_drink(self, drink_name, tags):
        """
        Thêm một công thức mới vừa được khám phá vào chỉ mục.

        Được gọi bởi ``MixingEngine`` khi người chơi pha thành công
        một công thức ẩn lần đầu tiên.

        Args:
            drink_name (str): Tên công thức vừa khám phá.
            tags (list[str]): Danh sách tag của công thức đó.
        """
        for tag in tags:
            if tag not in self._index:
                self._index[tag] = set()
            self._index[tag].add(drink_name)

    def suggest(self, tags):
        """
        Gợi ý các công thức phù hợp với danh sách tag cho trước.

        Tính điểm cho mỗi công thức dựa trên số tag khớp,
        sau đó sắp xếp giảm dần theo điểm (nhiều tag khớp = ưu tiên cao hơn).

        Args:
            tags (list[str]): Danh sách tag trích xuất từ lời nói của khách.

        Returns:
            list[str]: Danh sách tên công thức sắp xếp theo độ phù hợp,
            hoặc ``[]`` nếu không tìm thấy gì.

        Example:
            >>> idx.suggest(["chua", "mạnh"])
            ["Margarita", "Martini", "Mojito"]
            # Margarita có 2 tag khớp → đứng đầu
        """
        if not tags:
            return []

        score = {}
        for tag in tags:
            for drink in self._index.get(tag, set()):
                score[drink] = score.get(drink, 0) + 1

        sorted_drinks = sorted(score.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in sorted_drinks]


# ══════════════════════════════════════════════════════════
#  6. QUICK SORT — leaderboard (giảm dần theo điểm)
# ══════════════════════════════════════════════════════════
def quick_sort_leaderboard(arr):
    """
    Sắp xếp bảng điểm theo thứ tự giảm dần sử dụng Quick Sort.

    Pivot là phần tử giữa mảng. Mảng được phân thành 3 phần:
    lớn hơn pivot, bằng pivot, và nhỏ hơn pivot, sau đó đệ quy.

    Args:
        arr (list[dict]): Danh sách entry bảng điểm.
            Mỗi phần tử có dạng ``{'name': str, 'score': int}``.

    Returns:
        list[dict]: Danh sách mới được sắp xếp giảm dần theo ``score``.
            Danh sách đầu vào không bị thay đổi.

    Example:
        >>> data = [{"name": "A", "score": 50}, {"name": "B", "score": 120}]
        >>> quick_sort_leaderboard(data)
        [{"name": "B", "score": 120}, {"name": "A", "score": 50}]

    Complexity: O(n log n) trung bình, O(n²) worst case.
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]["score"]
    left   = [x for x in arr if x["score"] >  pivot]
    middle = [x for x in arr if x["score"] == pivot]
    right  = [x for x in arr if x["score"] <  pivot]
    return quick_sort_leaderboard(left) + middle + quick_sort_leaderboard(right)


# ══════════════════════════════════════════════════════════
#  7. MERGE SORT — sắp xếp kho nguyên liệu (stable, đa tiêu chí)
# ══════════════════════════════════════════════════════════
def merge_sort_inventory(arr, sort_key="name"):
    """
    Sắp xếp danh sách nguyên liệu theo một key cho trước sử dụng Merge Sort.

    Thuật toán ổn định (stable) — thứ tự tương đối của các phần tử
    bằng nhau được bảo toàn. Tính chất này cho phép sắp xếp đa tiêu chí
    bằng cách gọi hàm 2 lần liên tiếp:

    .. code-block:: python

        items = merge_sort_inventory(items, "name")  # sắp xếp phụ
        items = merge_sort_inventory(items, "type")  # sắp xếp chính

    Kết quả: trong cùng ``type``, các nguyên liệu được sắp xếp theo ``name``.

    Args:
        arr (list[dict]): Danh sách nguyên liệu.
            Mỗi phần tử phải có key ``sort_key`` với giá trị là string.
        sort_key (str): Tên trường dùng để so sánh. Mặc định là ``"name"``.

    Returns:
        list[dict]: Danh sách mới đã sắp xếp tăng dần (A–Z, không phân biệt hoa/thường).
            Danh sách đầu vào không bị thay đổi.

    Complexity: O(n log n) — ổn định trên mọi đầu vào.
    """
    if len(arr) <= 1:
        return arr
    mid   = len(arr) // 2
    left  = merge_sort_inventory(arr[:mid],  sort_key)
    right = merge_sort_inventory(arr[mid:], sort_key)
    return _merge(left, right, sort_key)


def _merge(left, right, key):
    """
    Gộp hai danh sách đã sắp xếp thành một danh sách sắp xếp duy nhất.

    Hàm nội bộ, được gọi bởi ``merge_sort_inventory()``.
    So sánh không phân biệt hoa/thường (lowercase).

    Args:
        left (list[dict]): Nửa trái đã sắp xếp.
        right (list[dict]): Nửa phải đã sắp xếp.
        key (str): Trường dùng để so sánh.

    Returns:
        list[dict]: Danh sách đã gộp và sắp xếp.
    """
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i][key].lower() <= right[j][key].lower():
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result