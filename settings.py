# settings.py

# ─────────────────────────────────────────
#  Màn hình & Hiển thị
# ─────────────────────────────────────────
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
FPS           = 60
TITLE         = "Bar Rush: The Mixologist"
"""
Module settings.py
Định nghĩa các thông số cấu hình và tài nguyên dữ liệu tĩnh cho toàn bộ ứng dụng.

Các nhóm dữ liệu chính:
    - WINDOW_SETTINGS: Kích thước màn hình (1280x720) và tốc độ khung hình.
    - GAMEPLAY_CONSTANTS: Điểm thưởng, hình phạt, thời gian kiên nhẫn.
    - INGREDIENTS_DATA: Danh mục toàn bộ nguyên liệu kèm theo màu sắc nhận diện.
    - RECIPES_DATA: Cấu trúc dữ liệu chứa các công thức pha chế, bao gồm thành phần và thẻ (Tags).
    - MOOD_DIALOGUES: Thư viện câu thoại của khách hàng dùng cho giải thuật Inverted Index.
"""
# ─────────────────────────────────────────
#  Gameplay
# ─────────────────────────────────────────
BASE_PATIENCE           = 30.0
VIP_PATIENCE            = 20.0   # VIP ít kiên nhẫn hơn (đòi hỏi cao)
MAX_CUSTOMERS_ON_SCREEN = 4      # số ghế tại quầy
MAX_CUSTOMERS_PER_GAME  = 12     # tổng khách 1 ván

SCORE_CORRECT_NORMAL    = 100
SCORE_CORRECT_VIP       = 200
SCORE_DISCOVERY_BONUS   = 150    # thưởng khám phá công thức mới
SCORE_WRONG_PENALTY     = -30
SCORE_TIMEOUT_PENALTY   = -50

SHAKER_CAPACITY         = 5      # tối đa 5 nguyên liệu trong bình
SHAKE_THRESHOLD         = 40     # số nhịp lắc để hoàn thành
VIP_SPAWN_CHANCE        = 0.3

# ─────────────────────────────────────────
#  Màu sắc
# ─────────────────────────────────────────
C_BG            = (40,  44,  52)
C_TEXT          = (255, 255, 255)
C_TEXT_DIM      = (160, 160, 160)
C_ALERT         = (255, 85,  85)
C_SUCCESS       = (100, 220, 130)
C_GOLD          = (255, 215, 0)
C_PANEL         = (28,  32,  42)
C_PANEL_BORDER  = (60,  70,  90)
C_SHAKER        = (180, 190, 200)
C_SHAKER_ACTIVE = (100, 255, 150)

C_VODKA    = (200, 220, 255)
C_GIN      = (180, 245, 240)
C_TEQUILA  = (255, 223, 80)
C_RUM      = (180, 100, 40)
C_VERMOUTH = (160, 50,  50)
C_LIME     = (80,  200, 80)
C_SYRUP    = (255, 80,  140)
C_MINT     = (100, 220, 130)
C_OJ       = (255, 165, 0)

# ─────────────────────────────────────────
#  Dữ liệu nguyên liệu
# ─────────────────────────────────────────
INGREDIENTS_DATA = {
    "Vodka":        {"color": C_VODKA,    "asset": "assets/vodka.png", "price": 40, "type": "base"},
    "Gin":          {"color": C_GIN,      "asset": "assets/gin.png",   "price": 45, "type": "base"},
    "Tequila":      {"color": C_TEQUILA,  "asset": "assets/teq.png",   "price": 50, "type": "base"},
    "Rum":          {"color": C_RUM,      "asset": "assets/rum.png",   "price": 35, "type": "base"},
    "Vermouth":     {"color": C_VERMOUTH, "asset": "assets/ver.png",   "price": 30, "type": "modifier"},
    "Lime Juice":   {"color": C_LIME,     "asset": "assets/lime.png",  "price": 20, "type": "mixer"},
    "Syrup":        {"color": C_SYRUP,    "asset": "assets/syrup.png", "price": 15, "type": "mixer"},
    "Mint":         {"color": C_MINT,     "asset": "assets/mint.png",  "price": 10, "type": "garnish"},
    "Orange Juice": {"color": C_OJ,       "asset": "assets/oj.png",    "price": 18, "type": "mixer"},
}

# ─────────────────────────────────────────
#  Dữ liệu công thức
#  hidden=True → cần khám phá, chưa hiện trong recipe book
# ─────────────────────────────────────────
RECIPES_DATA = {
    "Margarita": {
        "ingredients": ["Tequila", "Lime Juice"],
        "tags":        ["chua", "mạnh", "tươi mát"],
        "hidden":      False,
    },
    "Martini": {
        "ingredients": ["Gin", "Vermouth"],
        "tags":        ["đắng", "mạnh", "cổ điển"],
        "hidden":      False,
    },
    "Mojito": {
        "ingredients": ["Rum", "Mint", "Lime Juice"],
        "tags":        ["tươi mát", "thảo mộc", "ngọt nhẹ"],
        "hidden":      False,
    },
    "Cosmopolitan": {
        "ingredients": ["Vodka", "Syrup", "Lime Juice"],
        "tags":        ["ngọt", "chua nhẹ", "sang trọng"],
        "hidden":      True,
    },
    "Tequila Sunrise": {
        "ingredients": ["Tequila", "Orange Juice", "Syrup"],
        "tags":        ["ngọt", "hoa quả", "tươi mát"],
        "hidden":      True,
    },
    "Dark & Stormy": {
        "ingredients": ["Rum", "Syrup"],
        "tags":        ["đắng", "mạnh", "ngọt"],
        "hidden":      True,
    },
}

# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng
# ─────────────────────────────────────────
MOOD_DIALOGUES = [
    {"text": "Hôm nay mệt quá, cần thứ gì đó mạnh và đắng.",           "tags": ["mạnh", "đắng"]},
    {"text": "Trời nóng thế này, cho tôi thứ gì tươi mát và chua.",     "tags": ["tươi mát", "chua"]},
    {"text": "Tôi muốn thứ ngọt ngọt, sang trọng một chút.",            "tags": ["ngọt", "sang trọng"]},
    {"text": "Gì đó cổ điển thôi, kiểu mạnh mạnh ấy.",                  "tags": ["cổ điển", "mạnh"]},
    {"text": "Cho tôi thứ thảo mộc, tươi mát, nhẹ nhàng.",              "tags": ["thảo mộc", "tươi mát"]},
    {"text": "Tôi thích hoa quả, ngọt ngọt là được.",                   "tags": ["hoa quả", "ngọt"]},
]

# ─────────────────────────────────────────
#  Tên khách ngẫu nhiên
# ─────────────────────────────────────────
CUSTOMER_NAMES = [
    "Alex", "Sam", "Jordan", "Casey", "Riley",
    "Morgan", "Taylor", "Jamie", "Avery", "Quinn",
]

# ─────────────────────────────────────────
#  Asset paths
# ─────────────────────────────────────────
FONT_PATH        = "assets/pixel_font.ttf"
BG_PATH          = "assets/Bar.png"
SPRITE_RAW_PATH  = "assets/Bartender_Spritesheet.png"
SPRITE_PROC_PATH = "assets/bartender_transparent.png"