<<<<<<< HEAD
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
BASE_PATIENCE           = 120.0
=======
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
BASE_PATIENCE           = 120.0
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
VIP_PATIENCE            = 80.0  # VIP ít kiên nhẫn hơn (đòi hỏi cao)
MAX_CUSTOMERS_ON_SCREEN = 4      # số ghế tại quầy
MAX_CUSTOMERS_PER_GAME  = 12     # tổng khách 1 ván
CUSTOMER_SPAWN_INTERVAL = 15.0   # giãn thời gian giữa các lượt khách vào quán (giây)
<<<<<<< HEAD

SCORE_CORRECT_NORMAL    = 100
SCORE_CORRECT_VIP       = 200
SCORE_DISCOVERY_BONUS   = 150    # thưởng khám phá công thức mới
SCORE_WRONG_PENALTY     = -30
SCORE_TIMEOUT_PENALTY   = -50

SHAKER_MAX_VOLUME = 300.0  # Dung tích tối đa của bình lắc (ml)
POUR_RATE         = 1.0    # Tốc độ rót chậm hơn: 1ml mỗi frame (chạy 60FPS thì 1s rót được khoảng 60ml)
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
C_SYRUP    = (255, 210, 70)
C_MINT     = (100, 220, 130)
C_OJ       = (255, 165, 0)

# --- Màu cho nguyên liệu mở rộng ---
C_TRIPLE_SEC   = (255, 240, 220)
C_APEROL       = (255, 100, 50)
C_BLUE_CURACAO = (0, 150, 255)
C_AMARETTO     = (180, 100, 50)
C_GINGER_BEER  = (220, 200, 140)
C_CRANBERRY    = (180, 20, 40)
C_CREAM        = (255, 250, 240)
C_CHERRY       = (200, 0, 30)

# --- Các màu bổ sung cho nguyên liệu mới ---
C_WHISKEY      = (200, 130, 50)
C_CAMPARI      = (220, 20,  40)
C_COLA         = (50,  30,  20)
C_SODA         = (230, 245, 255)
C_BITTERS      = (100, 40,  20)
C_OLIVE        = (110, 130, 50)
C_COFFEE_LIQ   = (70,  40,  20)
C_ESPRESSO     = (40,  20,  10)
C_PINEAPPLE    = (255, 220, 100)
C_COCONUT      = (240, 240, 240)

# ─────────────────────────────────────────
#  Dữ liệu nguyên liệu
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Dữ liệu nguyên liệu (Đã mở rộng)
# ─────────────────────────────────────────
INGREDIENTS_DATA = {
    # Base Spirits
    "Vodka":        {"color": C_VODKA,      "asset": "assets/Vodka.png",   "price": 40, "type": "base"},
    "Gin":          {"color": C_GIN,        "asset": "assets/Gin.png",     "price": 45, "type": "base"},
    "Tequila":      {"color": C_TEQUILA,    "asset": "assets/Tequila.png", "price": 50, "type": "base"},
    "Rum":          {"color": C_RUM,        "asset": "assets/Rum.png",     "price": 35, "type": "base"},
    "Whiskey":      {"color": C_WHISKEY,    "asset": "assets/Whiskey.png", "price": 55, "type": "base"},
    "Cachaca":      {"color": C_RUM,        "asset": "assets/Cachaca.png", "price": 45, "type": "base"},
    
    # Modifiers
    "Vermouth":     {"color": C_VERMOUTH,   "asset": "assets/Vermouth.png","price": 30, "type": "modifier"},
    "Campari":      {"color": C_CAMPARI,    "asset": "assets/Campari.png", "price": 35, "type": "modifier"},
    "Coffee Liq":   {"color": C_COFFEE_LIQ, "asset": "assets/Kahlúa.png",  "price": 35, "type": "modifier"},
    "Bitters":      {"color": C_BITTERS,    "asset": "assets/Bitters.png", "price": 10, "type": "modifier"},
    "Triple Sec":   {"color": C_TRIPLE_SEC, "asset": "assets/Triplesec.png","price": 30, "type": "modifier"},
    "Aperol":       {"color": C_APEROL,     "asset": "assets/Aperol.png",  "price": 35, "type": "modifier"},
    "Blue Curacao": {"color": C_BLUE_CURACAO,"asset": "assets/BlueCuracao.png","price": 25, "type": "modifier"},
    "Amaretto":     {"color": C_AMARETTO,   "asset": "assets/Amaretto.png","price": 30, "type": "modifier"},
    
    # Mixers
    "Lime Juice":   {"color": C_LIME,       "asset": "assets/Lime.png",    "price": 20, "type": "mixer"},
    "Syrup":        {"color": C_SYRUP,      "asset": "assets/Syrup.png",   "price": 15, "type": "mixer"},
    "Orange Juice": {"color": C_OJ,         "asset": "assets/orange.png",  "price": 18, "type": "mixer"},
    "Pineapple":    {"color": C_PINEAPPLE,  "asset": "assets/Pineapple.png","price": 22, "type": "mixer"},
    "Coconut Cream":{"color": C_COCONUT,    "asset": "assets/Coconut.png", "price": 25, "type": "mixer"},
    "Cola":         {"color": C_COLA,       "asset": "assets/Coke.png",    "price": 15, "type": "mixer"},
    "Soda Water":   {"color": C_SODA,       "asset": "assets/Soda.png",    "price": 10, "type": "mixer"},
    "Espresso":     {"color": C_ESPRESSO,   "asset": "assets/Espresso.png","price": 20, "type": "mixer"},
    "Ginger Beer":  {"color": C_GINGER_BEER,"asset": "assets/GingerBeer.png","price": 20,"type": "mixer"},
    "Cranberry":    {"color": C_CRANBERRY,  "asset": "assets/Cranberry.png","price": 18, "type": "mixer"},
    "Cream":        {"color": C_CREAM,      "asset": "assets/Cream.png",   "price": 15, "type": "mixer"},
    
    # Garnishes
    "Mint":         {"color": C_MINT,       "asset": "assets/mint.png",    "price": 10, "type": "garnish"},
    "Olive":        {"color": C_OLIVE,      "asset": "assets/olive.png",   "price": 12, "type": "garnish"},
    "Cherry":       {"color": C_CHERRY,     "asset": "assets/cherry.png",  "price": 10, "type": "garnish"},
}

# ─────────────────────────────────────────
#  Dữ liệu công thức
#  hidden=True → cần khám phá, chưa hiện trong recipe book
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Dữ liệu công thức (Tỉ lệ IBA Standard)
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Dữ liệu công thức (Cập nhật theo Sprite & IBA Standard)
# ─────────────────────────────────────────
RECIPES_DATA = {
    # --- Nhóm 1: Các món đã có trong list cũ (Cân lại tỷ lệ chuẩn) ---
    "Margarita": {
        "ingredients": {"Tequila": 0.5, "Triple Sec": 0.3, "Lime Juice": 0.2}, 
        "tags": ["sour", "strong", "classic"], "hidden": False,
    },
    "Martini": {
        "ingredients": {"Gin": 0.8, "Vermouth": 0.2},
        "tags": ["strong", "bitter", "classic"], "hidden": False,
    },
    "Mojito": {
        "ingredients": {"Rum": 0.4, "Lime Juice": 0.2, "Soda Water": 0.3, "Syrup": 0.05, "Mint": 0.05},
        "tags": ["refreshing", "herbal", "light"], "hidden": False,
    },
    "Daiquiri": {
        "ingredients": {"Rum": 0.6, "Lime Juice": 0.25, "Syrup": 0.15},
        "tags": ["sour", "strong", "classic"], "hidden": False,
    },
    "Manhattan": {
        "ingredients": {"Whiskey": 0.7, "Vermouth": 0.25, "Bitters": 0.05},
        "tags": ["strong", "bitter", "luxury"], "hidden": False,
    },
    "Tequila Sunrise": {
        "ingredients": {"Tequila": 0.3, "Orange Juice": 0.6, "Syrup": 0.1},
        "tags": ["sweet", "fruity", "refreshing"], "hidden": False,
    },
    "Pina Colada": {
        "ingredients": {"Rum": 0.33, "Pineapple": 0.33, "Coconut Cream": 0.34},
        "tags": ["sweet", "tropical", "creamy"], "hidden": False,
    },
    "Moscow Mule": {
        "ingredients": {"Vodka": 0.3, "Ginger Beer": 0.6, "Lime Juice": 0.1},
        "tags": ["spicy", "refreshing", "sour"], "hidden": False,
    },
    "Cosmopolitan": {
        "ingredients": {"Vodka": 0.4, "Triple Sec": 0.2, "Cranberry": 0.3, "Lime Juice": 0.1},
        "tags": ["sweet", "sour", "luxury"], "hidden": False,
    },
    "Mai Tai": {
        "ingredients": {"Rum": 0.5, "Triple Sec": 0.2, "Lime Juice": 0.2, "Syrup": 0.1},
        "tags": ["tropical", "strong", "fruity"], "hidden": False,
    },

    # --- Nhóm 2: Các món mới từ hình ảnh (Sử dụng nguyên liệu hiện có) ---
    "Screwdriver": {
        "ingredients": {"Vodka": 0.35, "Orange Juice": 0.65},
        "tags": ["simple", "fruity", "classic"], "hidden": False,
    },
    "Blue Monday": {
        "ingredients": {"Vodka": 0.6, "Triple Sec": 0.2, "Blue Curacao": 0.2},
        "tags": ["strong", "blue", "sweet"], "hidden": True, # Món ẩn để khách tự khám phá
    },
    "Algonquin": {
        "ingredients": {"Whiskey": 0.5, "Vermouth": 0.25, "Pineapple": 0.25},
        "tags": ["strong", "bitter", "fruity"], "hidden": False,
    },
    "King's Valley": {
        "ingredients": {"Gin": 0.5, "Blue Curacao": 0.2, "Lime Juice": 0.2, "Syrup": 0.1},
        "tags": ["green", "sour", "strong"], "hidden": False,
    },
    "Princess Mary": {
        "ingredients": {"Gin": 0.4, "Blue Curacao": 0.3, "Cream": 0.3},
        "tags": ["creamy", "sweet", "blue"], "hidden": True,
    },
    "Reggae Punch": {
        "ingredients": {"Rum": 0.4, "Orange Juice": 0.3, "Pineapple": 0.2, "Syrup": 0.1},
        "tags": ["tropical", "sweet", "fruity"], "hidden": False,
    },
    "Exorcist": {
        "ingredients": {"Tequila": 0.5, "Blue Curacao": 0.3, "Lime Juice": 0.2},
        "tags": ["strong", "blue", "sour"], "hidden": True,
    },
    "China Blue": {
        "ingredients": {"Vodka": 0.4, "Blue Curacao": 0.2, "Cranberry": 0.4}, # Map tạm vì thiếu nước bưởi (grapefruit)
        "tags": ["blue", "fruity", "refreshing"], "hidden": False,
    },
}

# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng (Bản tấu hài)
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng 
#  (Hiển thị Tiếng Anh - Đọc Tiếng Việt)
# ─────────────────────────────────────────
MOOD_DIALOGUES = [
    # Gợi ý cho Martini, Manhattan, Algonquin
    {"text": "Code Pygame của tôi vừa văng lỗi lần thứ 100. Pha cho tôi thứ gì đó thật mạnh và đắng, giống hệt nước mắt lúc này.", "tags": ["strong", "bitter"], "audio": "mood_1"},
    
    # Gợi ý cho Moscow Mule
    {"text": "Notebook Kaggle của tôi vừa dính lỗi hết bộ nhớ sau 12 tiếng train. Tôi cần một ly cay cho hợp cơn tức, nhưng cũng phải mát để hạ nhiệt cái GPU.", "tags": ["spicy", "refreshing"], "audio": "mood_2"},
    
    # Gợi ý cho Cosmopolitan
    {"text": "Tôi mới nhận tiền trợ cấp sinh viên. Cho tôi giả làm người giàu đúng 5 phút với một ly ngọt ngào và sang chảnh đi.", "tags": ["sweet", "luxury"], "audio": "mood_3"},
    
    # Gợi ý cho Margarita, Daiquiri
    {"text": "Khỏi cần ô dù màu mè. Cứ cho tôi một ly cổ điển và thật mạnh, vì tôi còn deadline lúc 11 giờ 59 tối.", "tags": ["classic", "strong"], "audio": "mood_4"},
    
    # Gợi ý cho Mojito
    {"text": "Ba ngày rồi tôi chưa bước ra ngoài. Cho tôi thứ gì đó thơm mùi thảo mộc và mát lạnh để còn nhớ thiên nhiên có vị ra sao.", "tags": ["herbal", "refreshing"], "audio": "mood_5"},
    
    # Gợi ý cho Tequila Sunrise, Reggae Punch
    {"text": "Pha cho tôi một ly trái cây và ngọt ngào. Tôi đang cố che đi vị đắng của trưởng thành và những con bug không sửa nổi.", "tags": ["fruity", "sweet"], "audio": "mood_6"},
    
    # Gợi ý cho Mai Tai, Reggae Punch
    {"text": "Tôi không đủ tiền đi Hawaii, nên cứ rót cho tôi thứ gì đó nhiệt đới và đầy vị trái cây, rồi tôi sẽ tự nhắm mắt tưởng tượng.", "tags": ["tropical", "fruity"], "audio": "mood_7"},
    
    # Gợi ý cho Pina Colada
    {"text": "Cho tôi một ly béo mịn và đậm chất nhiệt đới. Biết đâu uống đủ nhiều, tôi sẽ thấy bãi biển thay vì cái màn hình trước mặt.", "tags": ["creamy", "tropical"], "audio": "mood_8"},
    
    # Gợi ý cho Princess Mary (Món ẩn)
    {"text": "Tôi muốn thứ gì đó béo mịn và... màu xanh. Đúng vậy, xanh như màn hình xanh chết chóc của Windows, nhưng phải ngon.", "tags": ["creamy", "blue"], "audio": "mood_9"},
    
    # Gợi ý cho China Blue
    {"text": "Tôi cần một ly xanh như quầng thâm dưới mắt tôi, nhưng phải đủ sảng khoái để giữ tôi tỉnh táo.", "tags": ["blue", "refreshing"], "audio": "mood_10"},
    
    # Gợi ý cho Blue Monday (Ẩn), Exorcist (Ẩn)
    {"text": "Làm nó màu xanh, làm nó thật mạnh, và làm nhanh lên trước khi giáo sư hỏi tiến độ nghiên cứu của tôi.", "tags": ["blue", "strong"], "audio": "mood_11"},
    
    # Gợi ý cho King's Valley
    {"text": "Tôi cần thứ gì đó màu xanh lá để nhắc mình đi chạm cỏ, và chua chua một chút cho hợp tâm trạng lúc debug.", "tags": ["green", "sour"], "audio": "mood_12"},
    
    # Gợi ý cho Screwdriver
    {"text": "Não tôi cháy khét vì nhân ma trận rồi. Cứ cho tôi một ly đơn giản, vị trái cây, và tuyệt đối không dính dáng gì tới toán nữa.", "tags": ["simple", "fruity"], "audio": "mood_13"},
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
=======

SCORE_CORRECT_NORMAL    = 100
SCORE_CORRECT_VIP       = 200
SCORE_DISCOVERY_BONUS   = 150    # thưởng khám phá công thức mới
SCORE_WRONG_PENALTY     = -30
SCORE_TIMEOUT_PENALTY   = -50

SHAKER_MAX_VOLUME = 300.0  # Dung tích tối đa của bình lắc (ml)
POUR_RATE         = 1.0    # Tốc độ rót chậm hơn: 1ml mỗi frame (chạy 60FPS thì 1s rót được khoảng 60ml)
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
C_SYRUP    = (255, 210, 70)
C_MINT     = (100, 220, 130)
C_OJ       = (255, 165, 0)

# --- Màu cho nguyên liệu mở rộng ---
C_TRIPLE_SEC   = (255, 240, 220)
C_APEROL       = (255, 100, 50)
C_BLUE_CURACAO = (0, 150, 255)
C_AMARETTO     = (180, 100, 50)
C_GINGER_BEER  = (220, 200, 140)
C_CRANBERRY    = (180, 20, 40)
C_CREAM        = (255, 250, 240)
C_CHERRY       = (200, 0, 30)

# --- Các màu bổ sung cho nguyên liệu mới ---
C_WHISKEY      = (200, 130, 50)
C_CAMPARI      = (220, 20,  40)
C_COLA         = (50,  30,  20)
C_SODA         = (230, 245, 255)
C_BITTERS      = (100, 40,  20)
C_OLIVE        = (110, 130, 50)
C_COFFEE_LIQ   = (70,  40,  20)
C_ESPRESSO     = (40,  20,  10)
C_PINEAPPLE    = (255, 220, 100)
C_COCONUT      = (240, 240, 240)

# ─────────────────────────────────────────
#  Dữ liệu nguyên liệu
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Dữ liệu nguyên liệu (Đã mở rộng)
# ─────────────────────────────────────────
INGREDIENTS_DATA = {
    # Base Spirits
    "Vodka":        {"color": C_VODKA,      "asset": "assets/Vodka.png",   "price": 40, "type": "base"},
    "Gin":          {"color": C_GIN,        "asset": "assets/Gin.png",     "price": 45, "type": "base"},
    "Tequila":      {"color": C_TEQUILA,    "asset": "assets/Tequila.png", "price": 50, "type": "base"},
    "Rum":          {"color": C_RUM,        "asset": "assets/Rum.png",     "price": 35, "type": "base"},
    "Whiskey":      {"color": C_WHISKEY,    "asset": "assets/Whiskey.png", "price": 55, "type": "base"},
    "Cachaca":      {"color": C_RUM,        "asset": "assets/Cachaca.png", "price": 45, "type": "base"},
    
    # Modifiers
    "Vermouth":     {"color": C_VERMOUTH,   "asset": "assets/Vermouth.png","price": 30, "type": "modifier"},
    "Campari":      {"color": C_CAMPARI,    "asset": "assets/Campari.png", "price": 35, "type": "modifier"},
    "Coffee Liq":   {"color": C_COFFEE_LIQ, "asset": "assets/Kahlúa.png",  "price": 35, "type": "modifier"},
    "Bitters":      {"color": C_BITTERS,    "asset": "assets/Bitters.png", "price": 10, "type": "modifier"},
    "Triple Sec":   {"color": C_TRIPLE_SEC, "asset": "assets/Triplesec.png","price": 30, "type": "modifier"},
    "Aperol":       {"color": C_APEROL,     "asset": "assets/Aperol.png",  "price": 35, "type": "modifier"},
    "Blue Curacao": {"color": C_BLUE_CURACAO,"asset": "assets/BlueCuracao.png","price": 25, "type": "modifier"},
    "Amaretto":     {"color": C_AMARETTO,   "asset": "assets/Amaretto.png","price": 30, "type": "modifier"},
    
    # Mixers
    "Lime Juice":   {"color": C_LIME,       "asset": "assets/Lime.png",    "price": 20, "type": "mixer"},
    "Syrup":        {"color": C_SYRUP,      "asset": "assets/Syrup.png",   "price": 15, "type": "mixer"},
    "Orange Juice": {"color": C_OJ,         "asset": "assets/orange.png",  "price": 18, "type": "mixer"},
    "Pineapple":    {"color": C_PINEAPPLE,  "asset": "assets/Pineapple.png","price": 22, "type": "mixer"},
    "Coconut Cream":{"color": C_COCONUT,    "asset": "assets/Coconut.png", "price": 25, "type": "mixer"},
    "Cola":         {"color": C_COLA,       "asset": "assets/Coke.png",    "price": 15, "type": "mixer"},
    "Soda Water":   {"color": C_SODA,       "asset": "assets/Soda.png",    "price": 10, "type": "mixer"},
    "Espresso":     {"color": C_ESPRESSO,   "asset": "assets/Espresso.png","price": 20, "type": "mixer"},
    "Ginger Beer":  {"color": C_GINGER_BEER,"asset": "assets/GingerBeer.png","price": 20,"type": "mixer"},
    "Cranberry":    {"color": C_CRANBERRY,  "asset": "assets/Cranberry.png","price": 18, "type": "mixer"},
    "Cream":        {"color": C_CREAM,      "asset": "assets/Cream.png",   "price": 15, "type": "mixer"},
    
    # Garnishes
    "Mint":         {"color": C_MINT,       "asset": "assets/mint.png",    "price": 10, "type": "garnish"},
    "Olive":        {"color": C_OLIVE,      "asset": "assets/olive.png",   "price": 12, "type": "garnish"},
    "Cherry":       {"color": C_CHERRY,     "asset": "assets/cherry.png",  "price": 10, "type": "garnish"},
}

# ─────────────────────────────────────────
#  Dữ liệu công thức
#  hidden=True → cần khám phá, chưa hiện trong recipe book
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Dữ liệu công thức (Tỉ lệ IBA Standard)
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Dữ liệu công thức (Cập nhật theo Sprite & IBA Standard)
# ─────────────────────────────────────────
RECIPES_DATA = {
    # --- Nhóm 1: Các món đã có trong list cũ (Cân lại tỷ lệ chuẩn) ---
    "Margarita": {
        "ingredients": {"Tequila": 0.5, "Triple Sec": 0.3, "Lime Juice": 0.2}, 
        "tags": ["sour", "strong", "classic"], "hidden": False,
    },
    "Martini": {
        "ingredients": {"Gin": 0.8, "Vermouth": 0.2},
        "tags": ["strong", "bitter", "classic"], "hidden": False,
    },
    "Mojito": {
        "ingredients": {"Rum": 0.4, "Lime Juice": 0.2, "Soda Water": 0.3, "Syrup": 0.05, "Mint": 0.05},
        "tags": ["refreshing", "herbal", "light"], "hidden": False,
    },
    "Daiquiri": {
        "ingredients": {"Rum": 0.6, "Lime Juice": 0.25, "Syrup": 0.15},
        "tags": ["sour", "strong", "classic"], "hidden": False,
    },
    "Manhattan": {
        "ingredients": {"Whiskey": 0.7, "Vermouth": 0.25, "Bitters": 0.05},
        "tags": ["strong", "bitter", "luxury"], "hidden": False,
    },
    "Tequila Sunrise": {
        "ingredients": {"Tequila": 0.3, "Orange Juice": 0.6, "Syrup": 0.1},
        "tags": ["sweet", "fruity", "refreshing"], "hidden": False,
    },
    "Pina Colada": {
        "ingredients": {"Rum": 0.33, "Pineapple": 0.33, "Coconut Cream": 0.34},
        "tags": ["sweet", "tropical", "creamy"], "hidden": False,
    },
    "Moscow Mule": {
        "ingredients": {"Vodka": 0.3, "Ginger Beer": 0.6, "Lime Juice": 0.1},
        "tags": ["spicy", "refreshing", "sour"], "hidden": False,
    },
    "Cosmopolitan": {
        "ingredients": {"Vodka": 0.4, "Triple Sec": 0.2, "Cranberry": 0.3, "Lime Juice": 0.1},
        "tags": ["sweet", "sour", "luxury"], "hidden": False,
    },
    "Mai Tai": {
        "ingredients": {"Rum": 0.5, "Triple Sec": 0.2, "Lime Juice": 0.2, "Syrup": 0.1},
        "tags": ["tropical", "strong", "fruity"], "hidden": False,
    },

    # --- Nhóm 2: Các món mới từ hình ảnh (Sử dụng nguyên liệu hiện có) ---
    "Screwdriver": {
        "ingredients": {"Vodka": 0.35, "Orange Juice": 0.65},
        "tags": ["simple", "fruity", "classic"], "hidden": False,
    },
    "Blue Monday": {
        "ingredients": {"Vodka": 0.6, "Triple Sec": 0.2, "Blue Curacao": 0.2},
        "tags": ["strong", "blue", "sweet"], "hidden": True, # Món ẩn để khách tự khám phá
    },
    "Algonquin": {
        "ingredients": {"Whiskey": 0.5, "Vermouth": 0.25, "Pineapple": 0.25},
        "tags": ["strong", "bitter", "fruity"], "hidden": False,
    },
    "King's Valley": {
        "ingredients": {"Gin": 0.5, "Blue Curacao": 0.2, "Lime Juice": 0.2, "Syrup": 0.1},
        "tags": ["green", "sour", "strong"], "hidden": False,
    },
    "Princess Mary": {
        "ingredients": {"Gin": 0.4, "Blue Curacao": 0.3, "Cream": 0.3},
        "tags": ["creamy", "sweet", "blue"], "hidden": True,
    },
    "Reggae Punch": {
        "ingredients": {"Rum": 0.4, "Orange Juice": 0.3, "Pineapple": 0.2, "Syrup": 0.1},
        "tags": ["tropical", "sweet", "fruity"], "hidden": False,
    },
    "Exorcist": {
        "ingredients": {"Tequila": 0.5, "Blue Curacao": 0.3, "Lime Juice": 0.2},
        "tags": ["strong", "blue", "sour"], "hidden": True,
    },
    "China Blue": {
        "ingredients": {"Vodka": 0.4, "Blue Curacao": 0.2, "Cranberry": 0.4}, # Map tạm vì thiếu nước bưởi (grapefruit)
        "tags": ["blue", "fruity", "refreshing"], "hidden": False,
    },
}

# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng (Bản tấu hài)
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  Câu thoại "đọc vị" khách + tags tương ứng 
#  (Hiển thị Tiếng Anh - Đọc Tiếng Việt)
# ─────────────────────────────────────────
MOOD_DIALOGUES = [
    # Gợi ý cho Martini, Manhattan, Algonquin
    {"text": "Code Pygame của tôi vừa văng lỗi lần thứ 100. Pha cho tôi thứ gì đó thật mạnh và đắng, giống hệt nước mắt lúc này.", "tags": ["strong", "bitter"], "audio": "mood_1"},
    
    # Gợi ý cho Moscow Mule
    {"text": "Notebook Kaggle của tôi vừa dính lỗi hết bộ nhớ sau 12 tiếng train. Tôi cần một ly cay cho hợp cơn tức, nhưng cũng phải mát để hạ nhiệt cái GPU.", "tags": ["spicy", "refreshing"], "audio": "mood_2"},
    
    # Gợi ý cho Cosmopolitan
    {"text": "Tôi mới nhận tiền trợ cấp sinh viên. Cho tôi giả làm người giàu đúng 5 phút với một ly ngọt ngào và sang chảnh đi.", "tags": ["sweet", "luxury"], "audio": "mood_3"},
    
    # Gợi ý cho Margarita, Daiquiri
    {"text": "Khỏi cần ô dù màu mè. Cứ cho tôi một ly cổ điển và thật mạnh, vì tôi còn deadline lúc 11 giờ 59 tối.", "tags": ["classic", "strong"], "audio": "mood_4"},
    
    # Gợi ý cho Mojito
    {"text": "Ba ngày rồi tôi chưa bước ra ngoài. Cho tôi thứ gì đó thơm mùi thảo mộc và mát lạnh để còn nhớ thiên nhiên có vị ra sao.", "tags": ["herbal", "refreshing"], "audio": "mood_5"},
    
    # Gợi ý cho Tequila Sunrise, Reggae Punch
    {"text": "Pha cho tôi một ly trái cây và ngọt ngào. Tôi đang cố che đi vị đắng của trưởng thành và những con bug không sửa nổi.", "tags": ["fruity", "sweet"], "audio": "mood_6"},
    
    # Gợi ý cho Mai Tai, Reggae Punch
    {"text": "Tôi không đủ tiền đi Hawaii, nên cứ rót cho tôi thứ gì đó nhiệt đới và đầy vị trái cây, rồi tôi sẽ tự nhắm mắt tưởng tượng.", "tags": ["tropical", "fruity"], "audio": "mood_7"},
    
    # Gợi ý cho Pina Colada
    {"text": "Cho tôi một ly béo mịn và đậm chất nhiệt đới. Biết đâu uống đủ nhiều, tôi sẽ thấy bãi biển thay vì cái màn hình trước mặt.", "tags": ["creamy", "tropical"], "audio": "mood_8"},
    
    # Gợi ý cho Princess Mary (Món ẩn)
    {"text": "Tôi muốn thứ gì đó béo mịn và... màu xanh. Đúng vậy, xanh như màn hình xanh chết chóc của Windows, nhưng phải ngon.", "tags": ["creamy", "blue"], "audio": "mood_9"},
    
    # Gợi ý cho China Blue
    {"text": "Tôi cần một ly xanh như quầng thâm dưới mắt tôi, nhưng phải đủ sảng khoái để giữ tôi tỉnh táo.", "tags": ["blue", "refreshing"], "audio": "mood_10"},
    
    # Gợi ý cho Blue Monday (Ẩn), Exorcist (Ẩn)
    {"text": "Làm nó màu xanh, làm nó thật mạnh, và làm nhanh lên trước khi giáo sư hỏi tiến độ nghiên cứu của tôi.", "tags": ["blue", "strong"], "audio": "mood_11"},
    
    # Gợi ý cho King's Valley
    {"text": "Tôi cần thứ gì đó màu xanh lá để nhắc mình đi chạm cỏ, và chua chua một chút cho hợp tâm trạng lúc debug.", "tags": ["green", "sour"], "audio": "mood_12"},
    
    # Gợi ý cho Screwdriver
    {"text": "Não tôi cháy khét vì nhân ma trận rồi. Cứ cho tôi một ly đơn giản, vị trái cây, và tuyệt đối không dính dáng gì tới toán nữa.", "tags": ["simple", "fruity"], "audio": "mood_13"},
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
>>>>>>> 17b9509fddbc3fb2f1cd46574ed71afdaa5a183c
SPRITE_PROC_PATH = "assets/Bartender.png"
