import pygame
import numpy as np
import random
from config import *


class GridWorld:
    def __init__(self, size=GRID_SIZE, render_mode=False):
        self.rows = size
        self.cols = size
        self.render_mode = render_mode
        self.grid = np.zeros((self.rows, self.cols), dtype=int)

        if self.render_mode:
            pygame.init()
            self.width = self.cols * CELL_SIZE
            self.height = self.rows * CELL_SIZE + 60
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Vacuum AI - Large Map Training")
            self.font = pygame.font.SysFont('Arial', 18)

    def reset(self):
        """Generates a complex random map with borders and obstacles."""
        self.grid.fill(EMPTY)

        # 1. Create Boundary Walls (The "Cage")
        self.grid[0, :] = WALL
        self.grid[self.rows - 1, :] = WALL
        self.grid[:, 0] = WALL
        self.grid[:, self.cols - 1] = WALL

        # 2. Add Random Internal Obstacles (Furniture)
        # Fill about 10% of the inner area with random walls
        inner_area = (self.rows - 2) * (self.cols - 2)
        num_obstacles = int(inner_area * 0.10)  # Reduced slightly for better flow on large map

        placed_obs = 0
        while placed_obs < num_obstacles:
            r = random.randint(1, self.rows - 2)
            c = random.randint(1, self.cols - 2)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = WALL
                placed_obs += 1

        # 3. Place Charger (Green) & Bin (Red)
        self.charger_pos = self._find_empty()
        self.grid[self.charger_pos] = CHARGER

        self.bin_pos = self._find_empty()
        self.grid[self.bin_pos] = BIN

        # 4. Place Dirt (Yellow/Brown)
        # Fill 15% of free space with dirt
        num_dirt = int(inner_area * 0.15)
        placed_dirt = 0
        while placed_dirt < num_dirt:
            r = random.randint(1, self.rows - 2)
            c = random.randint(1, self.cols - 2)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = DIRT
                placed_dirt += 1

        return self.charger_pos

    def _find_empty(self):
        """Finds an empty spot guaranteed to be inside the walls."""
        while True:
            r = random.randint(1, self.rows - 2)
            c = random.randint(1, self.cols - 2)
            if self.grid[r][c] == EMPTY:
                return (r, c)

    def get_sensors(self, x, y):
        """Returns neighbor values for AI."""

        def get_val(r, c):
            return self.grid[r][c]

        return (
            get_val(x, y - 1),  # North
            get_val(x, y + 1),  # South
            get_val(x + 1, y),  # East
            get_val(x - 1, y),  # West
            self.grid[x][y],  # Current
        )

    def draw(self, agent=None):
        if not self.render_mode: return
        self.screen.fill(WHITE)

        for r in range(self.rows):
            for c in range(self.cols):
                rect = (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                tile = self.grid[r][c]
                color = WHITE

                if tile == WALL:
                    color = BLACK
                elif tile == DIRT:
                    color = BROWN
                elif tile == CHARGER:
                    color = GREEN
                elif tile == BIN:
                    color = RED

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)  # Border

        if agent:
            agent_rect = (agent.y * CELL_SIZE + 5, agent.x * CELL_SIZE + 5,
                          CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, BLUE, agent_rect)

        pygame.display.flip()


# --- SELF TEST BLOCK ---
if __name__ == "__main__":
    env = GridWorld(render_mode=True)
    env.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    env.reset()  # Generate new map

        env.draw()
        pygame.time.wait(100)
    pygame.quit()