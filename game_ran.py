import pygame
import os
import sys
import random
import json
import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np

# === PHẦN 1: CẤU HÌNH ===
WIDTH, HEIGHT = 640, 480
CELL_SIZE = 20
FPS = 10
FONT_NAME = "texgyreadventor-regular.otf"
speed_up_enabled = True
speed_up_step = 2
MARGIN_TOP = 40

video_mode = False
video_path = "background.mp4"
video_cap = None

key_bindings = {
    'load_bg': pygame.K_4,
    'load_video': pygame.K_0,
    'speed': pygame.K_2,
    'pause': pygame.K_3,
    'auto_eat': pygame.K_5,
    'auto_loop': pygame.K_6,
    'quit': pygame.K_7,
    'toggle_speedup': pygame.K_8,
    'video_bg': pygame.K_9
}
KEY_CONFIG_FILE = "key_config.json"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Rắn Săn Mồi - Nền video")
clock = pygame.time.Clock()

# === PHẦN 2: PHÔNG, HÌNH, VIDEO ===
def load_font(size):
    return pygame.font.Font(FONT_NAME, size) if os.path.exists(FONT_NAME) else pygame.font.SysFont("Arial", size)

font = load_font(24)
menu_font = load_font(28)
title_font = load_font(36)

def choose_multiple_background_images():
    pygame.display.iconify()
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(filetypes=[("Ảnh PNG", "*.png;*.jpg;*.jpeg")], title="Chọn nhiều hình nền")
    root.destroy()
    images = []
    for path in files:
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            images.append(img)
        except:
            print(f"❌ Không thể tải ảnh: {path}")
    return images

def choose_video_background():
    global video_path
    pygame.display.iconify()
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")], title="Chọn video nền")
    root.destroy()
    if file:
        video_path = file
        print(f"🎞️ Đã chọn video nền: {video_path}")
        return True
    return False

def get_video_frame():
    global video_cap
    if not video_cap or not video_cap.isOpened():
        return None
    ret, frame = video_cap.read()
    if not ret or frame is None or frame.size == 0:
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_cap.read()
        if not ret or frame is None or frame.size == 0:
            return None
    try:
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        return pygame.surfarray.make_surface(frame)
    except:
        return None

bg_frames = []
frame_index = 0
skin_image = None

# === PHẦN 3: PHÍM TẮT ===
def save_key_config():
    with open(KEY_CONFIG_FILE, "w") as f:
        json.dump({k: v for k, v in key_bindings.items()}, f)

def load_key_config():
    global key_bindings
    if os.path.exists(KEY_CONFIG_FILE):
        with open(KEY_CONFIG_FILE, "r") as f:
            data = json.load(f)
            key_bindings.update({k: int(v) for k, v in data.items()})

def key_name(key):
    return pygame.key.name(key).upper()

def wait_for_key(action_key):
    waiting = True
    while waiting:
        screen.fill((0, 0, 0))
        info = font.render("Ấn phím mới cho hành động...", True, (255, 255, 0))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_bindings[action_key] = event.key
                waiting = False

# === PHẦN 4: MENU CHÍNH ===

def customize_keys():
    global speed_up_enabled, speed_up_step
    actions = [
        ('load_bg', "Tải hình nền"),
        ('load_video', "Tải video nền"),
        ('speed', "Tốc độ nền"),
        ('pause', "Tạm dừng / tiếp tục"),
        ('auto_eat', "Đổi nền khi ăn"),
        ('auto_loop', "Đổi nền liên tục"),
        ('quit', "Thoát về menu"),
        ('toggle_speedup', "Bật/tắt tăng tốc"),
        ('video_bg', "Bật/tắt nền video")
    ]
    selecting = True

    # Tự điều chỉnh cỡ font phù hợp
    base_size = 28
    while base_size > 10:
        menu_font_test = load_font(base_size)
        height_required = 100 + len(actions) * (base_size + 8) + 100
        if height_required <= HEIGHT:
            break
        base_size -= 1
    menu_font = load_font(base_size)
    note_font = load_font(max(12, base_size - 2))

    while selecting:
        screen.fill((10, 10, 30))
        title = title_font.render("🔧 Tùy chỉnh phím", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        for i, (act, label) in enumerate(actions):
            txt = menu_font.render(f"{i+1}. {label} [{key_name(key_bindings[act])}]", True, (200, 200, 200))
            screen.blit(txt, (60, 100 + i * (base_size + 8)))

        # Info
        info1 = note_font.render(
            f"Tăng tốc: {'Bật' if speed_up_enabled else 'Tắt'} (Phím: {key_name(key_bindings['toggle_speedup'])})",
            True, (255, 255, 0)
        )
        info2 = note_font.render(
            f"Tăng mỗi 5 điểm: +{speed_up_step} FPS",
            True, (255, 200, 0)
        )
        note = note_font.render("Ấn số để chọn, ESC để quay lại", True, (180, 180, 180))

        y_start = 100 + len(actions) * (base_size + 8) + 20
        screen.blit(info1, (60, y_start))
        screen.blit(info2, (60, y_start + 28))
        # Vẽ nút [+] và [-]
        plus_rect = pygame.Rect(400, y_start + 28, 28, 28)
        minus_rect = pygame.Rect(440, y_start + 28, 28, 28)
        pygame.draw.rect(screen, (80, 200, 80), plus_rect)
        pygame.draw.rect(screen, (200, 80, 80), minus_rect)
        screen.blit(note_font.render("+", True, (0,0,0)), (plus_rect.x + 8, plus_rect.y + 2))
        screen.blit(note_font.render("-", True, (0,0,0)), (minus_rect.x + 10, minus_rect.y + 2))

        screen.blit(note, (60, y_start + 56))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_9 or event.key == pygame.K_0:
                    index = event.key - pygame.K_1 if event.key != pygame.K_0 else 1
                    if index < len(actions):
                        wait_for_key(actions[index][0])
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    speed_up_step += 1
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    speed_up_step = max(1, speed_up_step - 1)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if plus_rect.collidepoint(mx, my):
                        speed_up_step += 1
                    elif minus_rect.collidepoint(mx, my):
                        speed_up_step = max(1, speed_up_step - 1)

                elif event.key == pygame.K_ESCAPE:
                    save_key_config()
                    selecting = False


def show_main_menu():
    global skin_image
    load_key_config()
    while True:
        screen.fill((30, 30, 60))
        title = title_font.render("🐍 RẮN SĂN MỒI", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        menu_items = [
            "1. Bắt đầu chơi",
            "2. Tải hình nền",
            "3. Tải video nền",
            "4. Tùy chỉnh phím",
            "5. Thoát"
        ]
        for i, item in enumerate(menu_items):
            txt = menu_font.render(item, True, (255, 255, 255))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 120 + i * 40))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    run_game()
                elif e.key == pygame.K_2:
                    images = choose_multiple_background_images()
                    if images:
                        bg_frames.clear()
                        bg_frames.extend(images)
                        print(f"✅ Đã chọn {len(images)} ảnh nền")
                elif e.key == pygame.K_3:
                    choose_video_background()
                elif e.key == pygame.K_4:
                    customize_keys()
                elif e.key == pygame.K_5:
                    pygame.quit(); sys.exit()

# === PHẦN 5: GAME LOOP ===
def show_game_over():
    while True:
        screen.fill((0, 0, 0))
        msg1 = title_font.render("💀 THUA RỒI!", True, (255, 255, 255))
        msg2 = font.render("1. Chơi lại | 2. Menu chính", True, (200, 200, 200))
        screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'restart'
                elif event.key == pygame.K_2:
                    return 'menu'

def run_game():
    global video_cap, video_mode, speed_up_enabled, speed_up_step
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = (CELL_SIZE, 0)
    food = (300, 300)
    paused = False
    score = 0
    fps = FPS
    auto_bg = False
    auto_switch = False
    delay_ms = 500
    frame_index = 0
    load_key_config()
    if video_mode:
        try:
            video_cap = cv2.VideoCapture(video_path)
        except:
            video_cap = None
    while True:
        if video_mode and video_cap:
            frame_surface = get_video_frame()
            if frame_surface:
                screen.blit(frame_surface, (0, 0))
        elif bg_frames:
            screen.blit(bg_frames[frame_index], (0, 0))
            if auto_bg and pygame.time.get_ticks() % delay_ms < clock.get_time():
                frame_index = (frame_index + 1) % len(bg_frames)
        else:
            screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, CELL_SIZE): direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE): direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0): direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0): direction = (CELL_SIZE, 0)
                elif event.key == key_bindings['pause']: paused = not paused
                elif event.key == key_bindings['auto_eat']: auto_switch = not auto_switch
                elif event.key == key_bindings['auto_loop']: auto_bg = not auto_bg
                elif event.key == key_bindings['load_bg']:
                    images = choose_multiple_background_images()
                    if images:
                        bg_frames.clear()
                        bg_frames.extend(images)
                elif event.key == key_bindings['load_video']:
                    choose_video_background()
                elif event.key == key_bindings['speed']:
                    if auto_bg:
                        delay_ms = 100 if delay_ms >= 1000 else delay_ms + 100
                elif event.key == key_bindings['quit']:
                    if video_cap: video_cap.release()
                    return
                elif event.key == key_bindings['toggle_speedup']:
                    speed_up_enabled = not speed_up_enabled
                elif event.key == key_bindings['video_bg']:
                    video_mode = not video_mode
                    if video_mode:
                        if not os.path.exists(video_path):
                            print("⚠️ Chưa có video nền.")
                            video_mode = False
                        else:
                            if video_cap:
                                video_cap.release()
                            video_cap = cv2.VideoCapture(video_path)
                    else:
                        if video_cap:
                            video_cap.release()
                            video_cap = None

        if not paused:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            snake.insert(0, new_head)
            if new_head == food:
                score += 1
                if speed_up_enabled and score % 5 == 0:
                    fps += speed_up_step
                while True:
                    new_food = (
                        random.randint(0, WIDTH // CELL_SIZE - 1) * CELL_SIZE,
                        random.randint(0, HEIGHT // CELL_SIZE - 1) * CELL_SIZE
                    )
                    if new_food not in snake:
                        food = new_food
                        break
                if auto_switch and bg_frames:
                    frame_index = (frame_index + 1) % len(bg_frames)
            else:
                snake.pop()
            if (new_head in snake[1:] or new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT):
                result = show_game_over()
                if result == 'restart':
                    run_game()
                else:
                    if video_cap: video_cap.release()
                    return

        for block in snake:
            pygame.draw.rect(screen, (0, 255, 0), (*block, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, (255, 0, 0), (*food, CELL_SIZE, CELL_SIZE))

        pygame.display.update()
        clock.tick(fps)

# === PHẦN 6: CHẠY CHÍNH ===
if __name__ == "__main__":
    while True:
        show_main_menu()
