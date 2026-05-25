import pygame
import os

class _SoundManager:
    """
    Quản lý toàn bộ âm thanh của game: nhạc nền, hiệu ứng, và tiếng rót rượu.

    Được thiết kế dưới dạng singleton, truy cập qua biến toàn cục ``sound_mgr``.
    Tất cả âm thanh được nạp lười (lazy) sau khi gọi ``init()``.
    """

    def __init__(self):
        """Khởi tạo manager ở trạng thái chưa kích hoạt, chưa nạp file âm thanh."""
        self.initialized = False
        self.sounds = {}
        self.pour_channel = None
        self.shake_channel = None
        self.mood_dialogue_enabled = True
        
        # ---> CHỈNH CON SỐ Ở ĐÂY CHO NHỎ LẠI
        self.bgm_volume = 0.1  
        self.sfx_volume = 0.1  
    def init(self):
        """
        Khởi tạo pygame.mixer và nạp toàn bộ file âm thanh vào bộ nhớ.

        Phải được gọi một lần sau ``pygame.init()`` trước khi dùng bất kỳ
        phương thức nào khác. Dành riêng kênh số 1 cho tiếng rót rượu lặp vô hạn.
        """
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.initialized = True
        
        # Dành riêng kênh cho các âm lặp liên tục để dễ bật/tắt đúng lúc
        self.pour_channel = pygame.mixer.Channel(1)
        self.shake_channel = pygame.mixer.Channel(2)
        
        # ==========================================
        # 1. ÂM THANH MÔI TRƯỜNG & UI
        # ==========================================
        self._load("bgm", "assets/sounds/bgm.mp3")              # Nhạc nền chill chill
        self._load("bell", "assets/sounds/doorbell.wav")       # Kính koong chuông cửa
        self._load("timeout", "assets/sounds/timeout.wav")      # Khách tức giận đập bàn bỏ đi
        
        # ==========================================
        # 2. ÂM THANH TƯƠNG TÁC PHA CHẾ
        # ==========================================
        self._load("pickup", "assets/sounds/pickup.wav")        # Cầm chai rượu lên
        self._load("pour", "assets/sounds/pour.mp3")            # Rót rượu xèo xèo
        self._load("shake", "assets/sounds/shake.wav")          # Lắc shaker sột soạt
        self._load("lid", "assets/sounds/ice_clink.mp3")        # Đậy nắp (tiếng đá rơi)
        self._load("serve", "assets/sounds/serve.mp3")
        # ==========================================
        # 3. ÂM THANH KẾT QUẢ & PHẢN ỨNG CỦA KHÁCH
        # ==========================================
        self._load("score_up", "assets/sounds/score_up.mp3")   
        
        # Tiếng khách nhận xét bằng tiếng Việt
        self._load("khen", "assets/sounds/khen.mp3") # VD file gen ra: "Đỉnh của chóp!", "Tuyệt vời!"
        self._load("che", "assets/sounds/che.mp3")   # VD file gen ra: "Pha như nước cống!", "Tởm quá!"
        
        
        # Tải đủ 13 câu thoại tâm trạng, đồng bộ với assets/sounds/Mood1..Mood13.mp3
        for i in range(1, 14):
            self._load(f"mood_{i}", f"assets/sounds/Mood{i}.mp3")     # Khách chửi: "What is this trash?"
        self.set_bgm_volume(self.bgm_volume)
        self.set_sfx_volume(self.sfx_volume)
    def _load(self, name, path):
        """
        Nạp một file âm thanh vào ``self.sounds[name]``.
        Bỏ qua âm thầm nếu file không tồn tại (tránh crash khi thiếu asset).
        """
        # ---> PHẢI CÓ DÒNG CHECK EXIST NÀY KHÔNG LÀ CRASH
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
            # Ép âm lượng tiếng gõ phím nhỏ xuống để khỏi nhức đầu
            if name == "type":
                self.sounds[name].set_volume(0.3)
        else:
            self.sounds[name] = None # ---> Dòng này phải nằm ở hàm else của cái check exists

    def play(self, name):
        """Phát hiệu ứng âm thanh 1 lần (Click, chấm điểm, khách nói...)"""
        if isinstance(name, str) and name.startswith("mood_") and not self.mood_dialogue_enabled:
            return
        if self.initialized and name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def set_mood_dialogue_enabled(self, enabled):
        """Bật/tắt phát voice cho các order mood dialogue."""
        self.mood_dialogue_enabled = bool(enabled)

    def play_bgm(self):
        """Bật nhạc nền chạy lặp vô tận"""
        if self.initialized and "bgm" in self.sounds and self.sounds["bgm"]:
            pygame.mixer.music.load("assets/sounds/bgm.mp3")
            pygame.mixer.music.set_volume(0.1) 
            pygame.mixer.music.play(-1) 
    def set_bgm_volume(self, vol):
        """Cập nhật âm lượng nhạc nền đang phát."""
        self.bgm_volume = max(0.0, min(1.0, vol))  # ---> M LỠ XÓA DÒNG NÀY RỒI, THÊM LẠI VÀO
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.bgm_volume)
    def set_sfx_volume(self, vol):
        """Cập nhật âm lượng cho toàn bộ hiệu ứng âm thanh (SFX)."""
        self.sfx_volume = max(0.0, min(1.0, vol))  # ---> M LỠ XÓA DÒNG NÀY LUÔN, THÊM LẠI
        
        # Cập nhật âm lượng cho toàn bộ SFX
        for name, sound in self.sounds.items():
            if sound and name != "bgm":
                if name == "type":
                    sound.set_volume(self.sfx_volume * 0.3) 
                else:
                    sound.set_volume(self.sfx_volume)
                    
        # Ép volume cho các kênh âm lặp
        if self.pour_channel:
            self.pour_channel.set_volume(self.sfx_volume)
        if self.shake_channel:
            self.shake_channel.set_volume(self.sfx_volume)
    def start_pouring(self):
        """Phát tiếng rót rượu lặp vô hạn khi đang giữ chuột"""
        if self.initialized and self.sounds["pour"]:
            if not self.pour_channel.get_busy():
                self.pour_channel.play(self.sounds["pour"], loops=-1)

    def stop_pouring(self):
        """Ngắt tiếng rót rượu khi nhả chuột ra"""
        if self.initialized and self.pour_channel.get_busy():
            self.pour_channel.stop()

    def start_shaking(self):
        """Phát tiếng lắc shaker lặp vô hạn trong lúc đang shake."""
        if self.initialized and self.sounds.get("shake") and self.shake_channel:
            if not self.shake_channel.get_busy():
                self.shake_channel.play(self.sounds["shake"], loops=-1)

    def stop_shaking(self):
        """Ngắt tiếng lắc shaker ngay khi dừng thao tác shake."""
        if self.initialized and self.shake_channel and self.shake_channel.get_busy():
            self.shake_channel.stop()

# Biến toàn cục để xài chung
sound_mgr = _SoundManager()
