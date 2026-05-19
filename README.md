# Bar Rush: The Mixologist

**Bar Rush: The Mixologist** là một game mô phỏng pha chế cocktail được xây dựng bằng **Python** và **Pygame**. Người chơi vào vai bartender trong một quầy bar, tiếp nhận yêu cầu của khách, kéo thả nguyên liệu vào shaker, lắc bình, phục vụ đồ uống và cố gắng đạt điểm cao nhất trước khi khách hết kiên nhẫn.

Game không chỉ tập trung vào gameplay mà còn tích hợp nhiều **cấu trúc dữ liệu và thuật toán** như Min Heap, Queue, Trie, Inverted Index, Quick Sort và Merge Sort để xử lý logic khách hàng, tìm kiếm công thức, gợi ý món và bảng xếp hạng.

---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng chính](#tính-năng-chính)
- [Gameplay](#gameplay)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Cài đặt](#cài-đặt)
- [Cách chạy game](#cách-chạy-game)
- [Điều khiển](#điều-khiển)
- [Các thuật toán và cấu trúc dữ liệu sử dụng](#các-thuật-toán-và-cấu-trúc-dữ-liệu-sử-dụng)
- [Luồng hoạt động chính](#luồng-hoạt-động-chính)
- [Tài nguyên game](#tài-nguyên-game)
- [Ghi chú phát triển](#ghi-chú-phát-triển)

---

## Giới thiệu

Trong **Bar Rush: The Mixologist**, mỗi lượt chơi sẽ có nhiều khách hàng xuất hiện tại quầy bar. Khách có thể gọi món theo hai kiểu:

1. **Gọi trực tiếp tên cocktail**  
   Ví dụ: `Margarita`, `Martini`, `Mojito`.

2. **Mô tả tâm trạng hoặc nhu cầu**  
   Ví dụ: khách muốn một ly `strong`, `bitter`, `refreshing`, `sweet`, `tropical`,...  
   Khi đó người chơi phải dựa vào tag gợi ý để chọn công thức phù hợp.

Người chơi cần pha đúng tỉ lệ nguyên liệu, lắc shaker, phục vụ khách trước khi họ hết kiên nhẫn và cố gắng đạt điểm cao nhất.

---

## Tính năng chính

- Gameplay pha chế cocktail bằng thao tác kéo thả nguyên liệu.
- Bình shaker có giới hạn dung tích và cơ chế trộn màu theo thể tích.
- Khách hàng có thanh kiên nhẫn giảm dần theo thời gian.
- Khách VIP có thời gian chờ ngắn hơn nhưng cho nhiều điểm hơn.
- Hệ thống order theo tên món hoặc theo mood/tag.
- Thanh tìm kiếm công thức có autocomplete bằng Trie.
- Gợi ý món theo tag bằng Inverted Index.
- Kho nguyên liệu có phân loại theo nhóm: base, mixer, modifier, garnish.
- Bảng xếp hạng điểm cao được lưu bằng file JSON.
- Âm thanh nền, hiệu ứng rót, lắc, phục vụ và thoại khách hàng.
- Hỗ trợ các chế độ hiển thị: windowed, borderless và fullscreen.

---

## Gameplay

Mục tiêu của người chơi là phục vụ đúng đồ uống cho khách trong thời gian giới hạn.

Quy trình cơ bản:

1. Khách xuất hiện tại quầy bar.
2. Người chơi đọc order hoặc mood của khách.
3. Mở khu vực tools bằng phím `TAB`.
4. Kéo chai nguyên liệu vào shaker để rót.
5. Đậy nắp shaker và lắc đủ số nhịp.
6. Nhấn `SPACE` để phục vụ khách gấp nhất.
7. Game cộng hoặc trừ điểm dựa trên độ chính xác của món pha.

Nếu khách hết kiên nhẫn, họ rời đi và người chơi bị trừ điểm.

---

## Cấu trúc thư mục

```text
Bar-Rush-The-Mixologist/
│
├── main.py              # Điểm khởi chạy game, vòng lặp Pygame chính
├── game_logic.py        # Logic game: khách hàng, pha chế, điểm, state
├── algorithms.py        # Các cấu trúc dữ liệu và thuật toán
├── ui.py                # Giao diện Pygame, renderer, UI components
├── settings.py          # Cấu hình, dữ liệu nguyên liệu, công thức, dialogue
├── sound_manager.py     # Quản lý nhạc nền và hiệu ứng âm thanh
│
├── assets/              # Hình ảnh, sprite, font, âm thanh
│   ├── sounds/
│   ├── start/
│   └── ...
│
├── leaderboard.json     # File lưu bảng xếp hạng, tự tạo sau khi chơi
└── README.md
```

---


## Cách chạy game

Chạy file `main.py`:

```bash
python main.py
```

Sau khi mở game:

1. Nhấn `ENTER` ở màn hình menu.
2. Đọc màn hình hướng dẫn.
3. Nhấn `ENTER` lần nữa để bắt đầu chơi.

---

## Điều khiển

| Phím / Thao tác | Chức năng |
|---|---|
| `ENTER` | Đi tiếp từ menu / hướng dẫn |
| `TAB` | Ẩn hoặc hiện khu vực tools và shaker |
| Kéo chuột | Kéo chai nguyên liệu |
| Giữ chai trên shaker | Rót nguyên liệu vào bình |
| Click nút `LID` | Đậy hoặc mở nắp shaker |
| Click và lắc chuột trên shaker | Lắc bình |
| `SPACE` | Phục vụ khách gấp nhất |
| `C` | Đổ bỏ toàn bộ nguyên liệu trong shaker |
| `ESC` | Tạm dừng hoặc tiếp tục game |
| `R` | Chơi lại ở màn hình Game Over |
| `F11` | Đổi chế độ hiển thị: windowed / borderless / fullscreen |

---

## Các thuật toán và cấu trúc dữ liệu sử dụng

### 1. Min Heap

**Vị trí:** `algorithms.py`, `game_logic.py`

Min Heap được dùng để quản lý các khách đang ngồi tại quầy. Mỗi khách được lưu theo dạng:

```python
[time_left, customer_id, customer_obj]
```

Khách có `time_left` nhỏ nhất sẽ nằm ở đỉnh heap. Nhờ đó, game luôn biết ai là người sắp hết kiên nhẫn nhất để ưu tiên phục vụ hoặc kiểm tra timeout.

Độ phức tạp:

- Thêm khách: `O(log n)`
- Lấy khách gấp nhất: `O(1)` với `peek`
- Xóa khách: `O(log n)` sau khi tìm được vị trí
- Rebuild heap khi cập nhật thời gian: `O(n)`

---

### 2. Queue FIFO

**Vị trí:** `algorithms.py`, `game_logic.py`

Queue được dùng cho khách đứng chờ bên ngoài khi quầy đã đầy. Khách đến trước sẽ được vào trước.

Nguyên tắc:

```text
First In, First Out
```

Khi có khách rời quầy hoặc được phục vụ xong, game lấy khách đầu hàng chờ đưa vào quầy.

---

### 3. Liquid Shaker

**Vị trí:** `algorithms.py`

`LiquidShaker` quản lý toàn bộ trạng thái bình lắc:

- Dung tích tối đa.
- Tổng ml hiện tại.
- Danh sách nguyên liệu đã rót.
- Màu hỗn hợp hiện tại.

Màu chất lỏng được tính bằng trung bình có trọng số theo thể tích:

```text
new_color = (old_color * old_volume + ingredient_color * added_volume) / total_volume
```

Cơ chế này giúp màu trong shaker thay đổi trực quan theo nguyên liệu người chơi rót vào.

---

### 4. Trie

**Vị trí:** `algorithms.py`, `game_logic.py`, `ui.py`

Trie được dùng cho thanh tìm kiếm công thức. Khi người chơi nhập tiền tố như:

```text
ma
```

Game có thể gợi ý các món như:

```text
Margarita
Manhattan
Mai Tai
```

Trie phù hợp vì tìm kiếm theo prefix rất nhanh, với độ phức tạp `O(L)`, trong đó `L` là độ dài chuỗi nhập.

---

### 5. DFS trong Trie

Sau khi tìm được node cuối của prefix, game dùng DFS để duyệt toàn bộ cây con và thu thập các công thức hợp lệ.

Ví dụ:

```text
Prefix: "mo"
→ DFS từ node "o"
→ tìm ra Mojito, Moscow Mule, ...
```

DFS giúp lấy tất cả kết quả autocomplete nằm dưới một nhánh của Trie.

---

### 6. Inverted Index

**Vị trí:** `algorithms.py`, `game_logic.py`, `settings.py`

Inverted Index được dùng cho hệ thống đọc mood của khách.

Cấu trúc dạng:

```python
{
    "strong": {"Martini", "Margarita", "Mai Tai"},
    "bitter": {"Martini", "Manhattan"},
    "tropical": {"Pina Colada", "Mai Tai", "Reggae Punch"}
}
```

Khi khách nói muốn một ly `strong` và `bitter`, game sẽ tìm các công thức có tag tương ứng, tính số tag khớp và sắp xếp theo độ phù hợp.

---

### 7. Quick Sort

**Vị trí:** `algorithms.py`, `game_logic.py`

Quick Sort được dùng để sắp xếp leaderboard theo điểm giảm dần.

Mỗi entry có dạng:

```python
{"name": "Player", "score": 1200}
```

Sau khi game kết thúc, điểm mới được thêm vào leaderboard và danh sách được sắp xếp lại từ cao xuống thấp.

Độ phức tạp trung bình: `O(n log n)`.

---

### 8. Merge Sort

**Vị trí:** `algorithms.py`, `game_logic.py`

Merge Sort được dùng để sắp xếp kho nguyên liệu. Thuật toán này có tính **stable**, nghĩa là các phần tử có cùng key vẫn giữ thứ tự tương đối ban đầu.

Game tận dụng tính stable để sort đa tiêu chí:

```python
items = merge_sort_inventory(items, "name")
items = merge_sort_inventory(items, "type")
```

Kết quả: nguyên liệu được nhóm theo `type`, và trong mỗi nhóm lại được sắp theo `name`.

Độ phức tạp: `O(n log n)`.

---

## Luồng hoạt động chính

```text
main.py
│
├── Khởi tạo Pygame
├── Khởi tạo SoundManager
├── Tạo GameState
├── Tạo Renderer
│
└── Game Loop
    │
    ├── Nhận input từ người chơi
    ├── Cập nhật game_state
    ├── Spawn khách mới
    ├── Cập nhật patience / timeout
    ├── Xử lý rót, lắc, phục vụ
    ├── Tính điểm
    └── Renderer vẽ lại màn hình
```

---

## Tài nguyên game

Game sử dụng thư mục `assets/` để lưu:

- Ảnh nền quầy bar.
- Sprite bartender.
- Ảnh chai nguyên liệu.
- Ảnh shaker.
- Ảnh ly cocktail thành phẩm.
- Font pixel.
- Nhạc nền và hiệu ứng âm thanh.
- Voice line cho mood dialogue.
- Video intro ở màn hình start nếu có.

Một số asset path quan trọng được khai báo trong `settings.py`:

```python
FONT_PATH = "assets/pixel_font.ttf"
BG_PATH = "assets/Bar.png"
SPRITE_RAW_PATH = "assets/Bartender_Spritesheet.png"
SPRITE_PROC_PATH = "assets/Bartender.png"
```

---

## Công thức cocktail

Dữ liệu công thức nằm trong `RECIPES_DATA` của `settings.py`.

Mỗi công thức gồm:

```python
"Margarita": {
    "ingredients": {
        "Tequila": 0.5,
        "Triple Sec": 0.3,
        "Lime Juice": 0.2
    },
    "tags": ["sour", "strong", "classic"],
    "hidden": False
}
```

Trong đó:

- `ingredients`: tỉ lệ nguyên liệu chuẩn.
- `tags`: đặc điểm dùng cho mood order.
- `hidden`: đánh dấu công thức ẩn hoặc công thức đã mở.

---

## Cách tính điểm

Game tính điểm dựa trên:

- Khách thường hay khách VIP.
- Đúng hoặc sai order.
- Độ chính xác của tỉ lệ pha chế.
- Khách có bị timeout hay không.

Các mức điểm chính:

```python
SCORE_CORRECT_NORMAL = 100
SCORE_CORRECT_VIP = 200
SCORE_WRONG_PENALTY = -30
SCORE_TIMEOUT_PENALTY = -50
```

Nếu pha càng gần công thức chuẩn, điểm nhận được càng cao.

---

## Ghi chú phát triển

- `game_logic.py` không import Pygame, giúp logic game tách biệt với giao diện.
- `ui.py` chỉ chịu trách nhiệm hiển thị và xử lý UI.
- `algorithms.py` có thể test độc lập vì không phụ thuộc vào Pygame.
- `sound_manager.py` dùng cơ chế singleton qua biến toàn cục `sound_mgr`.
- `leaderboard.json` sẽ được tạo tự động khi game kết thúc.

---

## Công nghệ sử dụng

- Python
- Pygame
- OpenCV Python
- JSON
- Custom Data Structures & Algorithms

---

## Tác giả

Dự án được phát triển cho mục đích học tập, thực hành lập trình game bằng Pygame và minh họa ứng dụng của cấu trúc dữ liệu & giải thuật trong gameplay thực tế.
