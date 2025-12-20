import pygame
import time
from environment import GridWorld
from agent import VacuumAgent
from config import *


def draw_hud(screen, agent):
    """Draws text stats at the bottom of the screen."""
    # Text Area Position
    text_x = 10
    text_y = SCREEN_HEIGHT - 35

    font = pygame.font.SysFont('Arial', 18, bold=True)

    # Battery Status Text
    batt_color = GREEN if agent.battery > 50 else (YELLOW if agent.battery > 20 else RED)
    batt_text = font.render(f"Battery: {agent.battery}/{MAX_BATTERY}", True, batt_color)
    screen.blit(batt_text, (text_x, text_y))

    # Bin Status Text
    bin_text = font.render(f"Bin: {agent.bin}/{MAX_BIN}", True, BROWN)
    screen.blit(bin_text, (text_x + 150, text_y))

    # Dead Status
    if not agent.is_alive:
        dead_text = font.render("AGENT DEAD - PRESS 'R' TO RESTART", True, RED)
        screen.blit(dead_text, (text_x + 300, text_y))


def draw_agent(screen, agent):
    """Draws the agent with floating progress bars."""
    # Logic: agent.x is Row (Y), agent.y is Col (X)
    pixel_x = agent.y * CELL_SIZE
    pixel_y = agent.x * CELL_SIZE

    # padding to make agent slightly smaller than grid cell
    padding = 5
    agent_rect = (
        pixel_x + padding,
        pixel_y + padding,
        CELL_SIZE - (padding * 2),
        CELL_SIZE - (padding * 2)
    )

    # 1. Draw Agent Body (Blue Square)
    pygame.draw.rect(screen, BLUE, agent_rect)
    pygame.draw.rect(screen, BLACK, agent_rect, 2)  # Border

    # 2. Draw 'V' Logo
    font = pygame.font.SysFont('Arial', 20, bold=True)
    text = font.render("V", True, WHITE)
    text_rect = text.get_rect(center=(pixel_x + CELL_SIZE // 2, pixel_y + CELL_SIZE // 2))
    screen.blit(text, text_rect)

    # --- FLOATING BARS ---
    bar_width = CELL_SIZE - 10
    bar_height = 4

    # Battery Bar (Top of Agent)
    batt_pct = agent.battery / MAX_BATTERY
    batt_fill = int(bar_width * batt_pct)

    # Battery Color Logic
    if batt_pct > 0.5:
        batt_color = GREEN
    elif batt_pct > 0.2:
        batt_color = YELLOW
    else:
        batt_color = RED

    # Bat Bar Background
    pygame.draw.rect(screen, GRAY, (pixel_x + 5, pixel_y + 2, bar_width, bar_height))
    # Bat Bar Fill
    pygame.draw.rect(screen, batt_color, (pixel_x + 5, pixel_y + 2, batt_fill, bar_height))
    # Bat Bar Border
    pygame.draw.rect(screen, BLACK, (pixel_x + 5, pixel_y + 2, bar_width, bar_height), 1)

    # Bin Bar (Bottom of Agent)
    bin_pct = agent.bin / MAX_BIN
    bin_fill = int(bar_width * bin_pct)

    # Bin Bar Background
    pygame.draw.rect(screen, GRAY, (pixel_x + 5, pixel_y + CELL_SIZE - 6, bar_width, bar_height))
    # Bin Bar Fill
    pygame.draw.rect(screen, BROWN, (pixel_x + 5, pixel_y + CELL_SIZE - 6, bin_fill, bar_height))
    # Bin Bar Border
    pygame.draw.rect(screen, BLACK, (pixel_x + 5, pixel_y + CELL_SIZE - 6, bar_width, bar_height), 1)


def main():
    # Initialize Environment and Agent
    env = GridWorld(render_mode=True)
    agent = VacuumAgent()

    # Reset and place agent at charger
    start_pos = env.reset()
    agent.x, agent.y = start_pos

    print("--- MANUAL CONTROL MODE ---")
    print("ARROWS: Move | SPACE: Clean | 'C': Charge | 'D': Dump Bin")

    running = True
    while running:
        action = None

        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Keyboard Input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action = 0
                elif event.key == pygame.K_DOWN:
                    action = 1
                elif event.key == pygame.K_RIGHT:
                    action = 2
                elif event.key == pygame.K_LEFT:
                    action = 3
                elif event.key == pygame.K_SPACE:
                    action = 4  # Clean
                elif event.key == pygame.K_c:
                    action = 5  # Charge
                elif event.key == pygame.K_d:
                    action = 6  # Dump

                # Reset Map if 'R' is pressed
                elif event.key == pygame.K_r:
                    start_pos = env.reset()
                    agent.x, agent.y = start_pos
                    agent.battery = MAX_BATTERY
                    agent.bin = 0
                    agent.is_alive = True
                    print("Map Reset!")

        # Execute Action if one was chosen
        if action is not None and agent.is_alive:
            reward, done = agent.step(action, env)
            print(f"Action: {action} | Rew: {reward} | Batt: {agent.battery} | Bin: {agent.bin}")

        # 1. Draw the Grid
        env.draw()

        # 2. Draw the Agent (with bars)
        draw_agent(env.screen, agent)

        # 3. Draw the HUD Text
        draw_hud(env.screen, agent)

        pygame.display.flip()

        pygame.time.wait(50)  # Small delay

    pygame.quit()


if __name__ == "__main__":
    main()