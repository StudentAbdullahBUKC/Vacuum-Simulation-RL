import pygame
import pickle
import time
import sys
import numpy as np
from environment import GridWorld
from agent import VacuumAgent
from config import *

# --- CONFIGURATION ---
SIDEBAR_WIDTH = 260
WINDOW_WIDTH = SCREEN_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT

# --- COLORS ---
DARK_BG = (20, 25, 30)
PANEL_BG = (15, 18, 23)
NEON_BLUE = (0, 200, 255)
NEON_RED = (255, 60, 90)
NEON_GREEN = (50, 255, 120)
NEON_YELLOW = (255, 220, 50)
WHITE = (240, 240, 250)
GRAY_TEXT = (150, 160, 170)
BORDER_COLOR = (40, 50, 60)


# --- HELPER FUNCTIONS ---
def draw_text_centered(surface, text, font, color, center_x, center_y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(center_x, center_y))
    surface.blit(text_obj, text_rect)


def draw_bar(surface, x, y, width, height, current, max_val, color, label):
    """Draws a vertical progress bar."""
    pygame.draw.rect(surface, (10, 10, 15), (x, y, width, height), border_radius=4)
    if max_val == 0: max_val = 1
    pct = max(0, min(1, current / max_val))
    fill_h = int(height * pct)
    fill_rect = pygame.Rect(x, y + height - fill_h, width, fill_h)
    pygame.draw.rect(surface, color, fill_rect, border_radius=4)
    pygame.draw.rect(surface, (60, 70, 80), (x, y, width, height), 1, border_radius=4)
    font = pygame.font.SysFont('Consolas', 12, bold=True)
    lbl = font.render(label, True, GRAY_TEXT)
    surface.blit(lbl, (x + (width - lbl.get_width()) // 2, y + height + 8))
    val_font = pygame.font.SysFont('Arial', 12, bold=True)
    val = val_font.render(f"{int(pct * 100)}%", True, WHITE)
    surface.blit(val, (x + (width - val.get_width()) // 2, y - 18))


def draw_sidebar(surface, agent, episode_num):
    """Draws the left control panel."""
    # Background
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(surface, PANEL_BG, sidebar_rect)
    pygame.draw.line(surface, NEON_BLUE, (SIDEBAR_WIDTH - 2, 0), (SIDEBAR_WIDTH - 2, SCREEN_HEIGHT), 2)

    # Header
    font_head = pygame.font.SysFont('Arial', 20, bold=True)
    font_sub = pygame.font.SysFont('Consolas', 14)
    surface.blit(font_head.render("SYS MONITOR", True, NEON_BLUE), (20, 30))
    surface.blit(font_sub.render(f"RUN CYCLE: #{episode_num}", True, WHITE), (20, 60))
    pygame.draw.line(surface, BORDER_COLOR, (20, 85), (SIDEBAR_WIDTH - 20, 85), 1)

    # Status Box
    goals = {0: "CLEANING", 1: "DUMPING", 2: "CHARGING", 3: "IDLE"}
    status = goals.get(agent.current_goal, "WAIT")
    if not agent.is_alive: status = "OFFLINE"
    status_color = NEON_GREEN if status == "CLEANING" else NEON_YELLOW
    if status == "DUMPING": status_color = NEON_RED
    if status == "OFFLINE": status_color = GRAY_TEXT
    pygame.draw.rect(surface, (30, 35, 40), (20, 110, SIDEBAR_WIDTH - 40, 50), border_radius=5)
    pygame.draw.rect(surface, status_color, (20, 110, SIDEBAR_WIDTH - 40, 50), 2, border_radius=5)
    lbl = font_sub.render("CURRENT OP:", True, GRAY_TEXT)
    val = font_head.render(status, True, status_color)
    surface.blit(lbl, (30, 118))
    surface.blit(val, (30, 135))

    # Bars
    bar_y = 220;
    bar_h = 200;
    bar_w = 40;
    gap = 40
    batt_color = NEON_GREEN
    if agent.battery < 150: batt_color = NEON_YELLOW
    if agent.battery < 50: batt_color = NEON_RED
    draw_bar(surface, 50, bar_y, bar_w, bar_h, agent.battery, MAX_BATTERY, batt_color, "PWR")
    bin_color = NEON_BLUE
    if agent.bin >= MAX_BIN * 0.8: bin_color = NEON_RED
    draw_bar(surface, 50 + bar_w + gap, bar_y, bar_w, bar_h, agent.bin, MAX_BIN, bin_color, "BIN")

    # Sensor Feed
    pygame.draw.line(surface, BORDER_COLOR, (20, 480), (SIDEBAR_WIDTH - 20, 480), 1)
    surface.blit(font_sub.render("SENSOR FEED:", True, GRAY_TEXT), (20, 500))
    surface.blit(font_sub.render(">> LIDAR OK", True, NEON_GREEN), (20, 525))
    surface.blit(font_sub.render(">> NAV MESH OK", True, NEON_GREEN), (20, 545))


def show_menu(screen):
    running = True
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont('Arial', 50, bold=True)
    sub_font = pygame.font.SysFont('Consolas', 16)
    btn_font = pygame.font.SysFont('Arial', 22, bold=True)

    while running:
        screen.fill(DARK_BG)
        for i in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(screen, (30, 35, 40), (i, 0), (i, WINDOW_HEIGHT), 1)

        mouse_pos = pygame.mouse.get_pos()
        draw_text_centered(screen, "VACUUM AI SIMULATOR", title_font, NEON_BLUE, WINDOW_WIDTH // 2, 120)
        draw_text_centered(screen, "Autonomous Cleaning Agent v2.5", sub_font, GRAY_TEXT, WINDOW_WIDTH // 2, 170)

        btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2, 240, 60)
        is_hover = btn_rect.collidepoint(mouse_pos)

        if is_hover:
            pygame.draw.rect(screen, NEON_BLUE, btn_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=8)
            btn_text_color = DARK_BG
        else:
            pygame.draw.rect(screen, PANEL_BG, btn_rect, border_radius=8)
            pygame.draw.rect(screen, NEON_BLUE, btn_rect, 2, border_radius=8)
            btn_text_color = NEON_BLUE

        draw_text_centered(screen, "INITIALIZE SYSTEM", btn_font, btn_text_color, btn_rect.centerx, btn_rect.centery)
        draw_text_centered(screen, "Press SPACE to Start", sub_font, GRAY_TEXT, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hover: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: running = False
        clock.tick(60)


def main():
    env = GridWorld(size=20, render_mode=True)
    main_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Vacuum AI Simulator - Dashboard View")

    map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    env.screen = map_surface

    show_menu(main_window)
    agent = VacuumAgent()

    try:
        with open("brain.pkl", "rb") as f:
            agent.q_table = pickle.load(f)
        print("✅ Super Brain Loaded!")
    except FileNotFoundError:
        print("❌ Error: 'brain.pkl' not found.")
        return

    agent.epsilon = 0.0
    running = True
    run_count = 1

    print("--- GENERATING MAP (PERSISTENT) ---")
    start_pos = env.reset()

    while running:
        agent.x, agent.y = start_pos
        agent.battery = MAX_BATTERY  # Uses 500 from config
        agent.bin = 0
        agent.is_alive = True
        agent.current_path.clear()
        agent.current_goal = None
        done = False

        print(f"--- Starting Run #{run_count} ---")

        while not done and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: done = True

            # --- 1. RANDOM DIRT SPAWN ---
            # This calls the function in your environment.py (approx 1% chance per frame)
            env.random_dirt_spawn()

            state = agent.get_state(env)

            # --- CHARGING TRAP LOGIC ---
            is_charging = False
            if env.grid[agent.x][agent.y] == CHARGER and agent.battery < MAX_BATTERY:
                agent.current_goal = 2  # Force status to CHARGING
                agent.current_path.clear()  # Clear path so it doesn't move
                is_charging = True

            # Standard Decision Logic
            if not is_charging:
                if agent.current_goal is None or not agent.current_path:
                    if state in agent.q_table:
                        goal = np.argmax(agent.q_table[state])
                    else:
                        goal = 0

                    if agent.current_goal != goal or not agent.current_path:
                        agent.current_goal = goal
                        success = agent.plan(env, goal)
                        if not success:
                            if agent.plan(env, 0):
                                agent.current_goal = 0
                            elif agent.plan(env, 1):
                                agent.current_goal = 1
                            elif agent.plan(env, 2):
                                agent.current_goal = 2

            # Execute
            r1, done_move = agent.move_step(env)
            r2 = agent.interact(env)

            if r1 == REWARD_DEATH:
                done = True
                print("Agent died (Battery Depleted)")

            # Draw
            env.draw(agent)
            main_window.fill(DARK_BG)
            draw_sidebar(main_window, agent, run_count)
            main_window.blit(map_surface, (SIDEBAR_WIDTH, 0))
            pygame.display.flip()
            pygame.time.wait(20)

        run_count += 1
        time.sleep(1)
    pygame.quit()


if __name__ == "__main__":
    main()