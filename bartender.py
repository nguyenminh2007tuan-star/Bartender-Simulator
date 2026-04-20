import pygame
import time
import random
import os
import math
from PIL import Image

# ==========================================
# CẤU HÌNH HỆ THỐNG & MÀU SẮC
# ==========================================
WIDTH, HEIGHT = 1200, 700
FPS = 60
MAX_CUSTOMERS_PER_GAME = 5 

COLORS = {
    'BG': (20, 24, 35), 'WHITE': (248, 250, 252), 'LIME': (222, 255, 154),
    'RED': (255, 100, 100), 'TEQUILA': (255, 223, 0), 'GIN': (200, 245, 255),
    'LIME_JUICE': (50, 205, 50), 'VERMOUTH': (180, 50, 50),
    'GOLD': (255, 215, 0), 'GRAY': (100, 100, 100), 'GLASS': (255, 255, 255, 50)
}

# ==========================================
# HÀM PHỤ TRỢ (HELPER FUNCTIONS)
# ==========================================
def convert_white_to_transparent(input_path, output_path):
    if os.path.exists(input_path) and not os.path.exists(output_path):
        dir_name = os.path.dirname(output_path)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] > 245 and item[1] > 245 and item[2] > 245:
                newData.append((255, 255, 255, 0))
            elif item[0] < 50 and item[1] < 50 and item[2] < 50:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        img.save(output_path, "PNG")

def load_image_or_fallback(path, size, fallback_color, alpha=255):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    else:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((*fallback_color, alpha))
        # Viền cho fallback để nhìn rõ hơn
        pygame.draw.rect(surf, COLORS['WHITE'], surf.get_rect(), 2)
        return surf

def load_font_or_fallback(path, size, fallback="Arial"):
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    else:
        return pygame.font.SysFont(fallback, size, bold=True)

# ==========================================
# DSA: STACK, PRIORITY QUEUE, TRIE, QUICKSORT
# ==========================================
class Stack:
    def __init__(self, capacity=6):
        self.items = []
        self.capacity = capacity
    def push(self, val):
        if len(self.items) < self.capacity: self.items.append(val)
    def clear(self): self.items = []
    def to_list(self): return [i.name for i in self.items]

class PriorityQueue:
    def __init__(self):
        self.items = [] 
    def enqueue(self, customer, priority):
        self.items.append((priority, time.time(), customer))
        self.items.sort(key=lambda x: (x[0], x[1]))
    def dequeue(self):
        return self.items.pop(0)[2] if self.items else None
    def is_empty(self): return len(self.items) == 0
    def peek(self): return self.items[0][2] if self.items else None

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.ingredients = []

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word, ingredients):
        node = self.root
        for char in word.lower():
            if char not in node.children: node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.ingredients = ingredients
    def search_exact(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children: return None
            node = node.children[char]
        return node.ingredients if node.is_end else None
    def search_prefix(self, prefix):
        if not prefix: return []
        node = self.root
        for char in prefix.lower():
            if char not in node.children: return []
            node = node.children[char]
        suggestions = []
        self._dfs(node, prefix.capitalize(), suggestions)
        return suggestions
    def _dfs(self, node, current_word, suggestions):
        if node.is_end: suggestions.append({'name': current_word, 'ingredients': node.ingredients})
        for char, child_node in node.children.items():
            self._dfs(child_node, current_word + char, suggestions)

def partition_hoare(arr, low, high):
    pivot = arr[low]
    i = low - 1
    j = high + 1
    while True:
        i += 1
        while arr[i] > pivot: i += 1
        j -= 1
        while arr[j] < pivot: j -= 1
        if i >= j: return j
        arr[i], arr[j] = arr[j], arr[i]

def quick_sort_desc(arr, low, high):
    if low < high:
        pi = partition_hoare(arr, low, high)
        quick_sort_desc(arr, low, pi)
        quick_sort_desc(arr, pi + 1, high)

# ==========================================
# HIỆU ỨNG PARTICLE (RÓT RƯỢU)
# ==========================================
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(2, 6) # Rơi xuống
        self.color = color
        self.lifetime = 255
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.2 # Trọng lực (Gravity)
        self.lifetime -= 5

    def draw(self, screen):
        if self.lifetime > 0:
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.lifetime), (self.size//2, self.size//2), self.size//2)
            screen.blit(surf, (int(self.x), int(self.y)))

# ==========================================
# OOP: GAME OBJECTS
# ==========================================
class BartenderSprite:
    def __init__(self, x, y, path):
        self.x, self.y = x, y
        self.frames = {}
        self.speed = 6
        self.facing_right = True
        target_h = 240
        actions = ["WALKING", "SHAKING", "POURING", "WIPING"]
        
        if os.path.exists(path):
            sheet = pygame.image.load(path).convert_alpha()
            f_w, f_h = sheet.get_width() // 4, sheet.get_height() // 4
            scale_factor = target_h / f_h
            new_w = int(f_w * scale_factor)
            for row, action in enumerate(actions):
                self.frames[action] = []
                for col in range(4):
                    rect = pygame.Rect(col * f_w, row * f_h, f_w, f_h)
                    frame = sheet.subsurface(rect)
                    self.frames[action].append(pygame.transform.scale(frame, (new_w, target_h)))
        else:
            for action in actions:
                self.frames[action] = [pygame.Surface((target_h//2, target_h), pygame.SRCALPHA)] * 4

        self.current_action = "WIPING"
        self.current_frame = 0
        self.last_update = time.time()

    def handle_input(self, keys, is_typing):
        if is_typing: return 
        moving = False
        if keys[pygame.K_LEFT]: self.x -= self.speed; self.facing_right = False; moving = True
        if keys[pygame.K_RIGHT]: self.x += self.speed; self.facing_right = True; moving = True
        if keys[pygame.K_UP]: self.y -= self.speed; moving = True
        if keys[pygame.K_DOWN]: self.y += self.speed; moving = True
        if self.current_action not in ["SHAKING", "POURING"]:
            self.current_action = "WALKING" if moving else "WIPING"

    def update(self):
        if time.time() - self.last_update > 0.12:
            self.last_update = time.time()
            self.current_frame = (self.current_frame + 1) % 4

    def draw(self, screen):
        img = self.frames[self.current_action][self.current_frame]
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
        screen.blit(img, (self.x, self.y))

class Ingredient:
    def __init__(self, name, path, color):
        self.name = name
        self.color = color # Dùng cho hiệu ứng particle
        self.image = load_image_or_fallback(path, (140, 40), color) # Thu nhỏ lại xíu cho vừa grid

class Customer:
    def __init__(self, name, order, is_vip):
        self.name, self.order, self.is_vip = name, order, is_vip
        self.start_time = time.time()
        self.patience = 40 if is_vip else 25
        self.frames = [load_image_or_fallback(f"assets/cust_{i}.png", (160, 210), (100, 150, 200), 0 if not os.path.exists(f"assets/cust_{i}.png") else 255) for i in range(4)]
        self.curr_f = 0
        self.last_up = time.time()

    def draw(self, screen, font):
        if time.time() - self.last_up > 0.15:
            self.last_up = time.time()
            self.curr_f = (self.curr_f + 1) % 4
        # Đặt khách hàng lệch sang trái một chút để nhường chỗ cho Shaker ở giữa
        screen.blit(self.frames[self.curr_f], (350, 360)) 
        
        tag_color = COLORS['GOLD'] if self.is_vip else COLORS['WHITE']
        tag_text = "VIP" if self.is_vip else "GUEST"
        txt = font.render(f"[{tag_text}] Order: {self.order}", True, tag_color)
        screen.blit(txt, (320, 320))

# ==========================================
# MAIN GAME CONTROLLER
# ==========================================
class BartenderGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        font_path = "assets/pixel_font.ttf"
        self.font = load_font_or_fallback(font_path, 20)
        self.small_font = load_font_or_fallback(font_path, 14)
        
        # Load nền
        self.bg = load_image_or_fallback("Bar.png", (WIDTH, HEIGHT), COLORS['BG'])
        
        # Load Bartender
        raw_sprite_path = "assets/Bartender_Spritesheet.png"
        processed_sprite_path = "assets/bartender_transparent.png"
        convert_white_to_transparent(raw_sprite_path, processed_sprite_path)
        
        # Init Trie Công thức
        self.recipes = Trie()
        self.recipes.insert("Margarita", ["Tequila", "Lime Juice"])
        self.recipes.insert("Martini", ["Gin", "Vermouth"])
        
        # Cơ sở dữ liệu Rượu
        self.ingredients_db = {
            "Tequila": Ingredient("Tequila", "assets/teq.png", COLORS['TEQUILA']),
            "Lime Juice": Ingredient("Lime Juice", "assets/lime.png", COLORS['LIME_JUICE']),
            "Gin": Ingredient("Gin", "assets/gin.png", COLORS['GIN']),
            "Vermouth": Ingredient("Vermouth", "assets/ver.png", COLORS['VERMOUTH'])
        }
        
        self.leaderboard = [1200, 500, 2500]
        self.state = "MENU"
        self.reset_game(processed_sprite_path)

    def reset_game(self, sprite_path):
        self.shaker = Stack(5)
        self.customers = PriorityQueue()
        self.bartender = BartenderSprite(650, 350, sprite_path) # Đứng cạnh shaker
        self.score = 0
        self.served = 0
        self.dragging = None
        
        # Biến cho UI & Hiệu ứng
        self.search_text = ""
        self.is_typing = False
        self.particles = []
        
        # Setup Grid cho Kệ Rượu (Bên phải)
        self.shelf_bottles = []
        start_x, start_y = 980, 200
        for i, (name, ing) in enumerate(self.ingredients_db.items()):
            pos = (start_x, start_y + i * 60)
            rect = ing.image.get_rect(topleft=pos)
            self.shelf_bottles.append({'ing': ing, 'rect': rect, 'origin': pos})
            
        self._spawn_customer()

    def _spawn_customer(self):
        if self.served >= MAX_CUSTOMERS_PER_GAME:
            self.state = "GAMEOVER"
            self.leaderboard.append(self.score)
            quick_sort_desc(self.leaderboard, 0, len(self.leaderboard) - 1)
            return
        
        is_vip = random.random() < 0.3
        priority = 1 if is_vip else 2
        new_order = random.choice(["Margarita", "Martini"])
        c = Customer(f"Guest_{self.served}", new_order, is_vip)
        self.customers.enqueue(c, priority)

    def create_pour_effect(self, x, y, color):
        for _ in range(15): # Tạo 15 hạt mỗi frame khi rót
            self.particles.append(Particle(x + random.randint(20, 120), y + 40, color))

    def draw_gameplay(self):
        self.screen.blit(self.bg, (0, 0))
        
        # 1. VẼ KHÁCH HÀNG & BARTENDER
        if not self.customers.is_empty():
            c = self.customers.peek()
            c.draw(self.screen, self.font)
            
            # Xử lý thời gian chờ
            time_waited = time.time() - c.start_time
            if time_waited > c.patience:
                self.customers.dequeue(); self.served += 1; self._spawn_customer()
            else:
                # Vẽ thanh patience
                bar_width = 100
                fill = (1 - (time_waited / c.patience)) * bar_width
                pygame.draw.rect(self.screen, COLORS['RED'], (350, 300, bar_width, 10))
                pygame.draw.rect(self.screen, COLORS['LIME'], (350, 300, fill, 10))

        self.bartender.update()
        self.bartender.draw(self.screen)

        # 2. VẼ LY SHAKE TRONG SUỐT (Ở Giữa)
        shaker_surface = pygame.Surface((120, 180), pygame.SRCALPHA)
        shaker_surface.fill(COLORS['GLASS'])
        pygame.draw.rect(shaker_surface, COLORS['WHITE'], shaker_surface.get_rect(), 3, border_radius=10)
        self.screen.blit(shaker_surface, (580, 420))
        
        # Vẽ các lớp rượu đã rót vào ly
        for i, ing in enumerate(self.shaker.items):
            pygame.draw.rect(self.screen, ing.color, (585, 570 - i * 30, 110, 25), border_radius=5)

        # 3. VẼ KỆ RƯỢU INVENTORY (Bên Phải)
        pygame.draw.rect(self.screen, (30, 30, 30, 200), (950, 150, 220, 400), border_radius=15)
        pygame.draw.rect(self.screen, COLORS['GRAY'], (950, 150, 220, 400), 2, border_radius=15)
        self.screen.blit(self.small_font.render("INVENTORY", True, COLORS['WHITE']), (1010, 165))
        for b in self.shelf_bottles:
            self.screen.blit(b['ing'].image, b['rect'].topleft)

        # 4. VẼ HIỆU ỨNG PARTICLES
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.lifetime <= 0:
                self.particles.remove(particle)

        # 5. VẼ SÁCH CÔNG THỨC - TRIE UI (Bên Trái)
        pygame.draw.rect(self.screen, (20, 25, 35, 230), (30, 50, 350, 250), border_radius=10)
        pygame.draw.rect(self.screen, COLORS['LIME'] if self.is_typing else COLORS['GRAY'], (30, 50, 350, 250), 3, border_radius=10)
        
        title = self.small_font.render("RECIPE BOOK (Nhấn ENTER)", True, COLORS['WHITE'])
        self.screen.blit(title, (45, 65))
        
        # Thanh search bar
        pygame.draw.rect(self.screen, (10, 15, 25), (45, 95, 320, 35), border_radius=5)
        search_surface = self.font.render(self.search_text + ("|" if self.is_typing and time.time() % 1 > 0.5 else ""), True, COLORS['LIME'])
        self.screen.blit(search_surface, (55, 100))
        
        if self.search_text:
            suggestions = self.recipes.search_prefix(self.search_text)
            if suggestions:
                for i, sugg in enumerate(suggestions):
                    ing_text = ", ".join(sugg['ingredients'])
                    res_txt = self.small_font.render(f"> {sugg['name']}: {ing_text}", True, COLORS['WHITE'])
                    self.screen.blit(res_txt, (45, 150 + i * 30)) 
            else:
                self.screen.blit(self.small_font.render("Không tìm thấy...", True, COLORS['RED']), (45, 150))

    def run(self):
        while True:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                
                if self.state == "PLAYING":
                    # Xử lý Gõ Phím
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.is_typing = not self.is_typing
                        elif self.is_typing:
                            if event.key == pygame.K_BACKSPACE:
                                self.search_text = self.search_text[:-1]
                            elif event.unicode.isprintable():
                                self.search_text += event.unicode
                        
                        # Phím tắt phục vụ / xóa ly
                        elif not self.is_typing:
                            if event.key == pygame.K_SPACE and not self.customers.is_empty():
                                c = self.customers.dequeue()
                                correct_recipe = self.recipes.search_exact(c.order)
                                if correct_recipe and sorted(self.shaker.to_list()) == sorted(correct_recipe):
                                    self.score += 200 if c.is_vip else 100
                                self.shaker.clear(); self.served += 1; self._spawn_customer()
                            elif event.key == pygame.K_c:
                                self.shaker.clear()

                    # Xử lý Kéo Thả Rót Rượu
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.is_typing:
                        for b in self.shelf_bottles:
                            if b['rect'].collidepoint(event.pos):
                                self.dragging = b
                                self.bartender.current_action = "POURING"
                                
                    elif event.type == pygame.MOUSEMOTION and self.dragging:
                        self.dragging['rect'].center = event.pos
                        # Nếu chai rượu đang di chuyển trên khu vực Ly Shake -> Tỏa hạt (Particles)
                        sh_rect = pygame.Rect(580, 420, 120, 180)
                        if self.dragging['rect'].colliderect(sh_rect):
                            self.create_pour_effect(self.dragging['rect'].x, self.dragging['rect'].y, self.dragging['ing'].color)
                            
                    elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
                        sh_rect = pygame.Rect(580, 420, 120, 180)
                        if self.dragging['rect'].colliderect(sh_rect):
                            self.shaker.push(self.dragging['ing'])
                        self.dragging['rect'].topleft = self.dragging['origin']
                        self.dragging = None
                        self.bartender.current_action = "WIPING"
                        
                elif event.type == pygame.KEYDOWN:
                    if self.state == "MENU" and event.key == pygame.K_RETURN: 
                        self.state = "PLAYING"; self.reset_game("assets/bartender_transparent.png")
                    if self.state == "GAMEOVER" and event.key == pygame.K_r: 
                        self.state = "PLAYING"; self.reset_game("assets/bartender_transparent.png")

            if self.state == "PLAYING":
                self.bartender.handle_input(keys, self.is_typing)
                self.draw_gameplay()
            elif self.state == "MENU":
                self.screen.fill(COLORS['BG'])
                t = self.font.render("BARTENDER SIMULATOR - NHẤN ENTER", True, COLORS['LIME'])
                self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2))
            else: # GAMEOVER
                self.screen.fill(COLORS['BG'])
                res = self.font.render(f"KẾT THÚC! ĐIỂM: {self.score}", True, COLORS['RED'])
                self.screen.blit(res, (WIDTH//2 - res.get_width()//2, 100))
                for i, s in enumerate(self.leaderboard[:5]):
                    txt = self.font.render(f"TOP {i+1}: {s}", True, COLORS['WHITE'])
                    self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200 + i*40))

            pygame.display.flip()

if __name__ == "__main__":
    BartenderGame().run()