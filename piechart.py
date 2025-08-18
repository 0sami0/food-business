import pygame
import pygame.gfxdraw
import sys
import random
import math
import cv2
import numpy as np

# --- Animation Control ---
FPS = 60
SETUP_DURATION = 1.0
PAUSE_DURATION = 1.5
TRANSITION_DURATION = 3.0
FINAL_STATE_DURATION = 4.0

SETUP_FRAMES = int(SETUP_DURATION * FPS)
PAUSE_1_FRAMES = int(PAUSE_DURATION * FPS)
TRANSITION_FRAMES = int(TRANSITION_DURATION * FPS)
FINAL_STATE_FRAMES = int(FINAL_STATE_DURATION * FPS)

TOTAL_FRAMES = SETUP_FRAMES + PAUSE_1_FRAMES + TRANSITION_FRAMES + FINAL_STATE_FRAMES

# --- Video Output Settings ---
WIDTH, HEIGHT = 1920, 1080
OUTPUT_FILENAME = "market_share_emoji_disk_PERFECTED.mp4"

# --- Data: Customer Distribution (as percentages of 100) ---
pw_food_truck_avg = (40 + 120) / 2
pw_ghost_kitchen_avg = (15 + 60) / 2
pw_no_kitchen_avg = (10 + 40) / 2
pw_total = pw_food_truck_avg + pw_ghost_kitchen_avg + pw_no_kitchen_avg
initial_dist = {
    "Food Truck": int(100 * pw_food_truck_avg / pw_total),
    "Ghost Kitchen": int(100 * pw_ghost_kitchen_avg / pw_total),
    "No-Kitchen": int(100 * pw_no_kitchen_avg / pw_total)
}

poc_food_truck_avg = (30 + 90) / 2
poc_ghost_kitchen_avg = (15 + 60) / 2
poc_no_kitchen_avg = (17 + 69) / 2
poc_total = poc_food_truck_avg + poc_ghost_kitchen_avg + poc_no_kitchen_avg
final_dist = {
    "Food Truck": int(100 * poc_food_truck_avg / poc_total),
    "Ghost Kitchen": int(100 * poc_ghost_kitchen_avg / poc_total),
    "No-Kitchen": int(100 * poc_no_kitchen_avg / poc_total)
}
while sum(initial_dist.values()) < 100: initial_dist["Food Truck"] += 1
while sum(final_dist.values()) < 100: final_dist["No-Kitchen"] += 1

# --- Pygame Setup & Fonts ---
pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))
try:
    title_font = pygame.font.SysFont('Arial', 54, bold=True)
    main_font = pygame.font.SysFont('Arial', 120, bold=True)
    small_font = pygame.font.SysFont('Arial', 48, bold=True)
    emoji_font = pygame.font.SysFont('Segoe UI Emoji', 38)
except:
    title_font, main_font, small_font, emoji_font = [pygame.font.Font(None, s) for s in [68, 90, 60, 50]]

# --- OpenCV Video Writer ---
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, FPS, (WIDTH, HEIGHT))

# --- Colors & Theme ---
BG_COLOR, BG_GRADIENT_CENTER = (21, 43, 87), (31, 53, 97)
TEXT_COLOR, SHADOW_COLOR = (255, 255, 255), (10, 20, 40)
FOOD_TRUCK_COLOR = (87, 171, 240)
GHOST_KITCHEN_COLOR = (34, 197, 94)
NO_KITCHEN_COLOR = (249, 115, 22)
business_colors = {"Food Truck": FOOD_TRUCK_COLOR, "Ghost Kitchen": GHOST_KITCHEN_COLOR, "No-Kitchen": NO_KITCHEN_COLOR}

# --- Helper Functions ---
def draw_background(surface):
    surface.fill(BG_COLOR)
    center = (WIDTH // 2, HEIGHT // 2)
    max_radius = int((WIDTH**2 + HEIGHT**2)**0.5 / 2)
    for i in range(30, 0, -1):
        pygame.gfxdraw.filled_circle(surface, center[0], center[1], int(max_radius * (i / 30)), (*BG_GRADIENT_CENTER, int(15 * (i / 30))))

def draw_text_with_shadow(surface, text, font, color, pos, shadow=True, center_x=False, center_y=False):
    text_render = font.render(text, True, color)
    text_rect = text_render.get_rect()
    if center_x: text_rect.centerx = pos[0]
    else: text_rect.x = pos[0]
    if center_y: text_rect.centery = pos[1]
    else: text_rect.y = pos[1]
    if shadow:
        shadow_render = font.render(text, True, SHADOW_COLOR)
        surface.blit(shadow_render, text_rect.move(3, 3))
    surface.blit(text_render, text_rect)

def ease_in_out_sine(t): return -(math.cos(math.pi * t) - 1) / 2

def generate_poisson_disk_points(radius, min_dist, k=30):
    width, height = radius * 2, radius * 2
    cell_size = min_dist / math.sqrt(2)
    grid_width, grid_height = int(math.ceil(width / cell_size)), int(math.ceil(height / cell_size))
    grid = [None] * (grid_width * grid_height)
    points, spawn_points = [], [pygame.math.Vector2(width/2, height/2)]
    while spawn_points:
        spawn_index = random.randrange(len(spawn_points))
        spawn_centre = spawn_points[spawn_index]
        for i in range(k):
            angle, d = random.uniform(0, 2 * math.pi), random.uniform(min_dist, 2 * min_dist)
            new_point = spawn_centre + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * d
            if 0 <= new_point.x < width and 0 <= new_point.y < height and (new_point - pygame.math.Vector2(width/2, height/2)).length() <= radius:
                col, row = int(new_point.x / cell_size), int(new_point.y / cell_size)
                is_valid = True
                for y in range(max(0, row - 2), min(grid_height, row + 3)):
                    for x in range(max(0, col - 2), min(grid_width, col + 3)):
                        p = grid[x + y * grid_width]
                        if p and (p - new_point).length() < min_dist: is_valid = False; break
                    if not is_valid: break
                if is_valid:
                    points.append(new_point)
                    spawn_points.append(new_point)
                    grid[col + row * grid_width] = new_point
        del spawn_points[spawn_index]
    return points

class Emoji:
    def __init__(self, home_pos):
        self.home_pos = pygame.math.Vector2(home_pos)
        self.pos = pygame.math.Vector2(home_pos)
        self.wiggle_speed = random.uniform(0.5, 1.5)
        self.wiggle_amount = random.uniform(3, 8)
        self.wiggle_angle = random.uniform(0, 2 * math.pi)
        self.time = random.uniform(0, 100)

    def update(self, dt):
        self.time += dt * self.wiggle_speed
        offset_x = math.sin(self.time) * self.wiggle_amount * math.cos(self.wiggle_angle)
        offset_y = math.sin(self.time) * self.wiggle_amount * math.sin(self.wiggle_angle)
        self.pos = self.home_pos + pygame.math.Vector2(offset_x, offset_y)

# --- Pre-generate Emoji Positions ---
disk_radius = 450
emoji_size = 40
center = (WIDTH * 0.4, HEIGHT // 2 + 50)
emojis = []
points = generate_poisson_disk_points(disk_radius, emoji_size)
points.sort(key=lambda p: math.atan2(p.y - disk_radius, p.x - disk_radius))

for p in points:
    emojis.append(Emoji((p.x + center[0] - disk_radius, p.y + center[1] - disk_radius)))

# --- NEW: Pre-render and cache tinted emojis ---
base_emoji_render = emoji_font.render("😊", True, (255, 255, 255))
tinted_emojis = {}
for name, color in business_colors.items():
    tinted_surface = pygame.Surface(base_emoji_render.get_size(), pygame.SRCALPHA)
    # Loop through each pixel to manually create a tinted version
    for x in range(base_emoji_render.get_width()):
        for y in range(base_emoji_render.get_height()):
            r, g, b, a = base_emoji_render.get_at((x, y))
            # Get the brightness (luminance) of the pixel
            grey = 0.299 * r + 0.587 * g + 0.114 * b
            # Mix the target color with the grey value
            new_r = int(color[0] * grey / 255)
            new_g = int(color[1] * grey / 255)
            new_b = int(color[2] * grey / 255)
            tinted_surface.set_at((x, y), (new_r, new_g, new_b, a))
    tinted_emojis[name] = tinted_surface


# --- Main Rendering Loop ---
print(f"Starting render of {OUTPUT_FILENAME}...")
for frame_num in range(TOTAL_FRAMES + 1):
    draw_background(screen)
    
    # --- Animation Stage Logic ---
    current_dist = {}
    if frame_num <= SETUP_FRAMES + PAUSE_1_FRAMES:
        for name in initial_dist: current_dist[name] = initial_dist[name]
    elif frame_num <= SETUP_FRAMES + PAUSE_1_FRAMES + TRANSITION_FRAMES:
        progress = ease_in_out_sine((frame_num - (SETUP_FRAMES + PAUSE_1_FRAMES)) / TRANSITION_FRAMES)
        for name in initial_dist:
            current_dist[name] = initial_dist[name] + (final_dist[name] - initial_dist[name]) * progress
    else:
        for name in final_dist: current_dist[name] = final_dist[name]

    # --- Drawing Logic ---
    draw_text_with_shadow(screen, "Market Share Shift: The Power of Choice", title_font, TEXT_COLOR, (WIDTH/2, 60), center_x=True)

    ft_quota = int(len(emojis) * (current_dist["Food Truck"] / 100))
    gk_quota = int(len(emojis) * (current_dist["Ghost Kitchen"] / 100))
    
    for i, emoji in enumerate(emojis):
        emoji.update(1/FPS)
        
        if i < ft_quota: owner = "Food Truck"
        elif i < ft_quota + gk_quota: owner = "Ghost Kitchen"
        else: owner = "No-Kitchen"
        
        emoji_rect = tinted_emojis[owner].get_rect(center=emoji.pos)
        screen.blit(tinted_emojis[owner], emoji_rect)

    readout_x = WIDTH * 0.8
    readout_y_start = HEIGHT * 0.3
    readout_spacing = (HEIGHT * 0.7 - readout_y_start) / 2 
    
    draw_text_with_shadow(screen, "Food Truck", small_font, FOOD_TRUCK_COLOR, (readout_x, readout_y_start), center_x=True)
    draw_text_with_shadow(screen, f"{current_dist['Food Truck']:.0f}%", main_font, FOOD_TRUCK_COLOR, (readout_x, readout_y_start + 70), center_x=True)

    draw_text_with_shadow(screen, "Ghost Kitchen", small_font, GHOST_KITCHEN_COLOR, (readout_x, readout_y_start + readout_spacing), center_x=True)
    draw_text_with_shadow(screen, f"{current_dist['Ghost Kitchen']:.0f}%", main_font, GHOST_KITCHEN_COLOR, (readout_x, readout_y_start + readout_spacing + 70), center_x=True)
    
    draw_text_with_shadow(screen, "No-Kitchen", small_font, NO_KITCHEN_COLOR, (readout_x, readout_y_start + 2 * readout_spacing), center_x=True)
    draw_text_with_shadow(screen, f"{current_dist['No-Kitchen']:.0f}%", main_font, NO_KITCHEN_COLOR, (readout_x, readout_y_start + 2 * readout_spacing + 70), center_x=True)

    # Convert and Write Frame to Video
    frame = pygame.surfarray.pixels3d(screen).swapaxes(0, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video_writer.write(frame)
    
    print(f"\rRendering frame {frame_num}/{TOTAL_FRAMES}...", end="")

# Finalize
video_writer.release()
pygame.quit()
print(f"\nDone! Video saved as {OUTPUT_FILENAME}")