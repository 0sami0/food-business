import pygame
import pygame.gfxdraw
import sys
import random
import math
import cv2
import numpy as np

# --- Simulation Parameters ---
BUSINESS_NAME = "No-Kitchen Restaurant (External Factors)"
UPFRONT_COST = 140000
PROFIT_PER_CUSTOMER = 10.00
MIN_CUSTOMERS_PER_DAY = 17
MAX_CUSTOMERS_PER_DAY = 69
SIMULATION_DAYS = 730 

# --- Animation Control ---
FPS = 60
LAYOUT_ANIM_DURATION = 1.5
PAUSE_DURATION = 1.0
CONE_ANIM_DURATION = 1.5
SIM_ANIM_DURATION = 5.0

LAYOUT_FRAMES, PAUSE_FRAMES, CONE_FRAMES, SIM_FRAMES = \
    int(LAYOUT_ANIM_DURATION*FPS), int(PAUSE_DURATION*FPS), int(CONE_ANIM_DURATION*FPS), int(SIM_ANIM_DURATION*FPS)

STAGE1_END, STAGE2_END, STAGE3_END, STAGE4_END, STAGE5_END = \
    LAYOUT_FRAMES, LAYOUT_FRAMES + PAUSE_FRAMES, \
    LAYOUT_FRAMES + PAUSE_FRAMES + CONE_FRAMES, \
    LAYOUT_FRAMES + PAUSE_FRAMES + CONE_FRAMES + PAUSE_FRAMES, \
    LAYOUT_FRAMES + PAUSE_FRAMES + CONE_FRAMES + PAUSE_FRAMES + SIM_FRAMES
TOTAL_FRAMES = STAGE5_END

# --- Video Output Settings ---
WIDTH, HEIGHT = 1920, 1080
OUTPUT_FILENAME = "no_kitchen_factors_final.mp4"

# --- Aesthetics ---
X_AXIS_PADDING_DAYS = 80
DISPLAY_DAYS = SIMULATION_DAYS + X_AXIS_PADDING_DAYS

pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))

try:
    title_font = pygame.font.SysFont('Arial', 54, bold=True)
    main_font = pygame.font.SysFont('Arial', 72, bold=True)
    small_font = pygame.font.SysFont('Arial', 33)
    label_font = pygame.font.SysFont('Arial', 27, bold=True)
    tick_font = pygame.font.SysFont('Arial', 24)
    meter_font = pygame.font.SysFont('Arial', 60, bold=True)
    summary_font = pygame.font.SysFont('Arial', 64, bold=True)
    icon_font = pygame.font.SysFont('Segoe UI Emoji', 28)
except:
    title_font, main_font, small_font, label_font, tick_font, meter_font, summary_font, icon_font = [pygame.font.Font(None, s) for s in [68, 90, 41, 36, 30, 75, 80, 32]]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, FPS, (WIDTH, HEIGHT))

# --- Colors ---
BG_COLOR, BG_GRADIENT_CENTER = (21, 43, 87), (31, 53, 97)
TEXT_COLOR, AXES_COLOR = (255, 255, 255), (255, 255, 255, 120)
SHADOW_COLOR = (10, 20, 40)
BREAK_EVEN_COLOR, DATA_LINE_FUTURE_COLOR = (255, 80, 80), (255, 255, 255, 200)
DATA_LINE_PAST_COLOR, FOG_VEIL_COLOR = (255, 255, 255, 50), (*BG_COLOR, 180)
POSITIVE_GREEN, PROFIT_GOLD_COLOR = (34, 197, 94), (253, 224, 71)

# --- THEME COLOR for No-Kitchen Restaurant ---
ORANGE_THEME = (249, 115, 22) # #F97316
LINE_COLOR = ORANGE_THEME
DOT_COLOR, DOT_GLOW_COLOR = ORANGE_THEME, (*ORANGE_THEME, 100)
CONE_FILL_COLOR = (*ORANGE_THEME, 150)
GLOW_COLOR_1 = (*ORANGE_THEME, 100)
GLOW_COLOR_2 = (*ORANGE_THEME, 50)
RAINY_COLOR = (100, 116, 139, 100)
SUNNY_COLOR = (234, 179, 8, 100)
FESTIVAL_COLOR = (168, 85, 247, 100)

# --- Hand-Crafted Event Calendar ---
event_periods = [
    {'type': 'rainy', 'start': 60, 'end': 120, 'label': 'Rainy Period', 'color': RAINY_COLOR, 'icon': '🌧️'},
    {'type': 'sunny', 'start': 180, 'end': 300, 'label': 'Sunny Spell', 'color': SUNNY_COLOR, 'icon': '☀️'},
    {'type': 'festival', 'start': 360, 'end': 362, 'label': 'Festival', 'color': FESTIVAL_COLOR, 'icon': '🎉'},
    {'type': 'rainy', 'start': 480, 'end': 600, 'label': 'Rainy Period', 'color': RAINY_COLOR, 'icon': '🌧️'},
    {'type': 'festival', 'start': 600, 'end': 602, 'label': 'Festival', 'color': FESTIVAL_COLOR, 'icon': '🎉'},
    {'type': 'sunny', 'start': 660, 'end': 720, 'label': 'Sunny Spell', 'color': SUNNY_COLOR, 'icon': '☀️'},
]

# --- Graphing Area & Data Pre-calculation ---
GRAPH_X_START, GRAPH_X_END = 240, WIDTH - 120
GRAPH_Y_START, GRAPH_Y_END = 180, HEIGHT - 250
GRAPH_WIDTH, GRAPH_HEIGHT = GRAPH_X_END - GRAPH_X_START, GRAPH_Y_END - GRAPH_Y_START

full_worst_case, full_best_case = [-UPFRONT_COST], [-UPFRONT_COST]
full_actual_path, daily_customer_history = [-UPFRONT_COST], []
avg_customers = (MIN_CUSTOMERS_PER_DAY + MAX_CUSTOMERS_PER_DAY) / 2
customers_today = avg_customers

random.seed(1234)

for day in range(1, DISPLAY_DAYS + 1):
    min_c, max_c = MIN_CUSTOMERS_PER_DAY, MAX_CUSTOMERS_PER_DAY
    # --- NEW: No-Kitchen Event Logic ---
    for event in event_periods:
        if event['start'] <= day <= event['end']:
            if event['type'] == 'sunny': min_c, max_c = min_c * 1.5, max_c * 1.5 # Boost
            elif event['type'] == 'rainy': min_c, max_c = min_c * 1.2, max_c * 1.2 # Slight Boost
            elif event['type'] == 'festival': min_c, max_c = min_c * 2.0, max_c * 2.0 # Boost
            break
    
    if day <= SIMULATION_DAYS:
        customers_today += random.randint(-5, 5) + (avg_customers - customers_today) * 0.05
        customers_today = max(min_c, min(customers_today, max_c))
        daily_customer_history.append(customers_today)
        full_actual_path.append(full_actual_path[-1] + (customers_today * PROFIT_PER_CUSTOMER))

    full_worst_case.append(full_worst_case[-1] + (min_c * PROFIT_PER_CUSTOMER))
    full_best_case.append(full_best_case[-1] + (max_c * PROFIT_PER_CUSTOMER))

full_average_case = [(w + b) / 2 for w, b in zip(full_worst_case, full_best_case)]
Y_RANGE = full_best_case[-1] - full_worst_case[0]
Y_PADDING = Y_RANGE * 0.10
PADDED_MAX_BALANCE, PADDED_MIN_BALANCE = full_best_case[-1] + Y_PADDING, full_worst_case[0] - Y_PADDING
PADDED_RANGE = PADDED_MAX_BALANCE - PADDED_MIN_BALANCE

# --- Helper Functions ---
def to_screen_coords(day_index, balance):
    x = GRAPH_X_START + (day_index / DISPLAY_DAYS) * GRAPH_WIDTH
    y = GRAPH_Y_END - ((balance - PADDED_MIN_BALANCE) / PADDED_RANGE) * GRAPH_HEIGHT
    return int(x), int(y)
def draw_text_with_shadow(surface, text, font, color, pos, shadow=True, center_x=False, center_y=False):
    text_render = font.render(text, True, color)
    text_rect = text_render.get_rect()
    if center_x: text_rect.centerx = pos[0]; 
    else: text_rect.x = pos[0]
    if center_y: text_rect.centery = pos[1]; 
    else: text_rect.y = pos[1]
    if shadow:
        shadow_render = font.render(text, True, SHADOW_COLOR)
        surface.blit(shadow_render, text_rect.move(3, 3))
    surface.blit(text_render, text_rect)
def draw_background(surface):
    surface.fill(BG_COLOR)
    center = (WIDTH // 2, HEIGHT // 2)
    max_radius = int((WIDTH**2 + HEIGHT**2)**0.5 / 2)
    for i in range(30, 0, -1): pygame.gfxdraw.filled_circle(surface, center[0], center[1], int(max_radius * (i / 30)), (*BG_GRADIENT_CENTER, int(15 * (i / 30))))
def draw_definitive_styled_line(surface, points, color, style, width=3):
    if len(points) < 2: return
    if style == "solid": pygame.draw.lines(surface, color, False, points, width); return
    if style == "dashed": dash_len, gap_len = 22, 15
    elif style == "dotted": dash_len, gap_len = 3, 22
    else: return
    total_dist = 0
    for i in range(1, len(points)):
        start, end = pygame.math.Vector2(points[i-1]), pygame.math.Vector2(points[i])
        segment_vec, segment_len = (end - start), (end - start).length()
        if segment_len < 0.1: continue
        direction = segment_vec.normalize()
        dist_on_segment = 0
        while dist_on_segment < segment_len:
            dist_in_cycle, pen_down = total_dist % (dash_len + gap_len), (total_dist % (dash_len + gap_len)) < dash_len
            remaining_in_state = (dash_len - dist_in_cycle) if pen_down else ((dash_len + gap_len) - dist_in_cycle)
            draw_len = min(remaining_in_state, segment_len - dist_on_segment)
            if pen_down: pygame.draw.line(surface, color, start + dist_on_segment * direction, start + (dist_on_segment + draw_len) * direction, width)
            dist_on_segment += draw_len; total_dist += draw_len
def ease_in_out_sine(t): return -(math.cos(math.pi * t) - 1) / 2

# --- Main Rendering Loop ---
print(f"Starting render of {OUTPUT_FILENAME}...")
breakeven_day = None
for frame_num in range(TOTAL_FRAMES + 1):
    stage_progress, current_day = 0, 0
    if frame_num <= STAGE1_END: stage_progress = ease_in_out_sine(frame_num / STAGE1_END)
    elif frame_num <= STAGE2_END: stage_progress = 1.0
    elif frame_num <= STAGE3_END: stage_progress = ease_in_out_sine((frame_num - STAGE2_END) / CONE_FRAMES)
    elif frame_num <= STAGE4_END: stage_progress = 1.0
    else:
        sim_progress = (frame_num - STAGE4_END) / SIM_FRAMES
        current_day = min(int(ease_in_out_sine(sim_progress) * SIMULATION_DAYS), SIMULATION_DAYS)
        if full_actual_path[current_day] >= 0 and breakeven_day is None: breakeven_day = current_day
    draw_background(screen)
    title_y = -100 + (130 * stage_progress) if frame_num <= STAGE1_END else 30
    draw_text_with_shadow(screen, BUSINESS_NAME, title_font, TEXT_COLOR, (45, title_y))
    draw_text_with_shadow(screen, "2-Year Financial Projection", small_font, TEXT_COLOR, (48, title_y + 60))
    y_axis_end = (GRAPH_X_START, GRAPH_Y_START + (GRAPH_HEIGHT * (1-stage_progress))) if frame_num <= STAGE1_END else (GRAPH_X_START, GRAPH_Y_START)
    x_axis_end = (GRAPH_X_START + (GRAPH_WIDTH * stage_progress), GRAPH_Y_END) if frame_num <= STAGE1_END else (GRAPH_X_END, GRAPH_Y_END)
    pygame.draw.aaline(screen, AXES_COLOR, (GRAPH_X_START, GRAPH_Y_END), y_axis_end)
    pygame.draw.aaline(screen, AXES_COLOR, (GRAPH_X_START, GRAPH_Y_END), x_axis_end)
    if frame_num > STAGE2_END:
        cone_progress = 1.0 if frame_num > STAGE3_END else stage_progress
        reveal_x = GRAPH_X_START + int(GRAPH_WIDTH * cone_progress)
        best_points = [p for p in [to_screen_coords(i,b) for i,b in enumerate(full_best_case)] if p[0] <= reveal_x]
        worst_points = [p for p in [to_screen_coords(i,b) for i,b in enumerate(full_worst_case)] if p[0] <= reveal_x]
        avg_points = [p for p in [to_screen_coords(i,b) for i,b in enumerate(full_average_case)] if p[0] <= reveal_x]
        if len(best_points) > 1 and len(worst_points) > 1:
            revealed_cone_poly = best_points + worst_points[::-1]
            pygame.gfxdraw.filled_polygon(screen, revealed_cone_poly, CONE_FILL_COLOR)
        draw_definitive_styled_line(screen, best_points, DATA_LINE_FUTURE_COLOR, "dashed")
        draw_definitive_styled_line(screen, worst_points, DATA_LINE_FUTURE_COLOR, "dashed")
        draw_definitive_styled_line(screen, avg_points, DATA_LINE_FUTURE_COLOR, "dotted")
    if frame_num > STAGE4_END:
        current_x = to_screen_coords(current_day, 0)[0]
        fog_rect = pygame.Rect(GRAPH_X_START, GRAPH_Y_START, current_x - GRAPH_X_START, GRAPH_HEIGHT)
        fog_surface = pygame.Surface((GRAPH_WIDTH, GRAPH_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(fog_surface, FOG_VEIL_COLOR, (0, 0, current_x - GRAPH_X_START, GRAPH_HEIGHT))
        screen.blit(fog_surface, (GRAPH_X_START, GRAPH_Y_START))
        draw_definitive_styled_line(screen, [(current_x, GRAPH_Y_START), (current_x, GRAPH_Y_END)], (255,255,255,150), "dashed")
        if current_day > 1:
            past_points = { "best": [p for p in [to_screen_coords(i,b) for i,b in enumerate(full_best_case)] if p[0] <= current_x + 1],
                            "worst": [p for p in [to_screen_coords(i,b) for i,b in enumerate(full_worst_case)] if p[0] <= current_x + 1],
                            "avg": [p for p in [to_screen_coords(i,b) for i,b in enumerate(full_average_case)] if p[0] <= current_x + 1]}
            draw_definitive_styled_line(screen, past_points["best"], DATA_LINE_PAST_COLOR, "dashed")
            draw_definitive_styled_line(screen, past_points["worst"], DATA_LINE_PAST_COLOR, "dashed")
            draw_definitive_styled_line(screen, past_points["avg"], DATA_LINE_PAST_COLOR, "dotted")
    if PADDED_MIN_BALANCE < 0 < PADDED_MAX_BALANCE:
        zero_line_y = to_screen_coords(0, 0)[1]
        pygame.draw.aaline(screen, BREAK_EVEN_COLOR, (GRAPH_X_START, zero_line_y), (GRAPH_X_END, zero_line_y))
        draw_text_with_shadow(screen, "BREAK-EVEN POINT", label_font, BREAK_EVEN_COLOR, (GRAPH_X_START + 15, zero_line_y - 36), shadow=False)
    if current_day > 0:
        points = [to_screen_coords(i, b) for i, b in enumerate(full_actual_path[:current_day + 1])]
        draw_definitive_styled_line(screen, points, LINE_COLOR, "solid", width=4)
        last_point = points[-1]
        pygame.gfxdraw.filled_circle(screen, last_point[0], last_point[1], 12, DOT_GLOW_COLOR)
        pygame.gfxdraw.filled_circle(screen, last_point[0], last_point[1], 9, DOT_COLOR)
    day_text_str = f"Day: {current_day} / {SIMULATION_DAYS}"
    draw_text_with_shadow(screen, day_text_str, small_font, TEXT_COLOR, (WIDTH - small_font.render(day_text_str, True, TEXT_COLOR).get_width() - 45, 45))
    meter_y_pos = HEIGHT - 180
    avg_weekly_cust = sum(daily_customer_history[max(0, current_day - 7):current_day]) / len(daily_customer_history[max(0, current_day - 7):current_day]) if current_day > 0 else 0
    draw_text_with_shadow(screen, "Avg. Weekly Customers", small_font, TEXT_COLOR, (WIDTH * 0.25, meter_y_pos), center_x=True)
    draw_text_with_shadow(screen, f"{avg_weekly_cust:.0f}", meter_font, TEXT_COLOR, (WIDTH * 0.25, meter_y_pos + 50), center_x=True)
    current_balance = full_actual_path[current_day]
    balance_color = POSITIVE_GREEN if current_balance >= 0 else (255, 100, 100)
    draw_text_with_shadow(screen, "Balance", small_font, TEXT_COLOR, (WIDTH * 0.5, meter_y_pos), center_x=True)
    draw_text_with_shadow(screen, f"${current_balance:,.2f}", main_font, balance_color, (WIDTH * 0.5, meter_y_pos + 40), center_x=True)
    total_profit = current_balance + UPFRONT_COST
    rr_ratio = total_profit / UPFRONT_COST if UPFRONT_COST > 0 else 0
    rr_color = PROFIT_GOLD_COLOR if rr_ratio >= 1.0 else TEXT_COLOR
    draw_text_with_shadow(screen, "Risk/Reward Ratio", small_font, TEXT_COLOR, (WIDTH * 0.75, meter_y_pos), center_x=True)
    draw_text_with_shadow(screen, f"{rr_ratio:.2f} : 1", meter_font, rr_color, (WIDTH * 0.75, meter_y_pos + 50), center_x=True)
    max_label_str, min_label_str = f"${full_best_case[SIMULATION_DAYS]:,.0f}", f"${full_worst_case[0]:,.0f}"
    draw_text_with_shadow(screen, max_label_str, small_font, TEXT_COLOR, (GRAPH_X_START - small_font.render(max_label_str, True, TEXT_COLOR).get_width() - 22, to_screen_coords(0, full_best_case[SIMULATION_DAYS])[1] - 15))
    draw_text_with_shadow(screen, min_label_str, small_font, TEXT_COLOR, (GRAPH_X_START - small_font.render(min_label_str, True, TEXT_COLOR).get_width() - 22, to_screen_coords(0, full_worst_case[0])[1] - 15))
    if PADDED_MIN_BALANCE < 0 < PADDED_MAX_BALANCE: draw_text_with_shadow(screen, "$0", small_font, BREAK_EVEN_COLOR, (GRAPH_X_START - 60, zero_line_y - 18))
    for d in range(120, DISPLAY_DAYS, 120):
        x = to_screen_coords(d, 0)[0]
        if x < GRAPH_X_END:
            draw_text_with_shadow(screen, f"Day {d}", tick_font, TEXT_COLOR, (x - tick_font.render(f"Day {d}", True, TEXT_COLOR).get_width()/2, GRAPH_Y_END + 15))
            pygame.draw.aaline(screen, AXES_COLOR, (x, GRAPH_Y_END), (x, GRAPH_Y_END + 8))
    for event in event_periods:
        start_x = to_screen_coords(event['start'], 0)[0]
        end_x = to_screen_coords(event['end'], 0)[0]
        if end_x < GRAPH_X_END:
            bar_rect = pygame.Rect(start_x, GRAPH_Y_END + 35, end_x - start_x, 30)
            pygame.draw.rect(screen, event['color'], bar_rect, border_radius=5)
            draw_text_with_shadow(screen, event['icon'], icon_font, TEXT_COLOR, (bar_rect.centerx, bar_rect.centery), center_x=True, center_y=True)

    if frame_num >= STAGE5_END:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))
        draw_text_with_shadow(screen, "FINAL RESULTS", title_font, TEXT_COLOR, (WIDTH/2, HEIGHT*0.3), center_x=True, center_y=True)
        draw_text_with_shadow(screen, f"Final Balance: ${full_actual_path[-1]:,.2f}", summary_font, POSITIVE_GREEN, (WIDTH/2, HEIGHT*0.5), center_x=True, center_y=True)
        draw_text_with_shadow(screen, f"Breakeven Point: Day {breakeven_day if breakeven_day else 'N/A'}", small_font, TEXT_COLOR, (WIDTH/2, HEIGHT*0.6), center_x=True, center_y=True)
        draw_text_with_shadow(screen, f"Final Risk/Reward: {rr_ratio:.2f} : 1", small_font, PROFIT_GOLD_COLOR, (WIDTH/2, HEIGHT*0.65), center_x=True, center_y=True)
    frame = pygame.surfarray.pixels3d(screen).swapaxes(0, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video_writer.write(frame)
    print(f"\rRendering frame {frame_num}/{TOTAL_FRAMES}...", end="")
video_writer.release()
pygame.quit()
print(f"\nDone! Video saved as {OUTPUT_FILENAME}")