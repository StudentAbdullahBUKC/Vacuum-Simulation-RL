import pygame
import numpy as np
import random
import os
from config import *


class GridWorld:
    def __init__(self, size=GRID_SIZE, render_mode=False):
        self.rows = size
        self.cols = size
        self.render_mode = render_mode
        self.grid = np.zeros((self.rows, self.cols), dtype=int)

        # Positions Lists (for dual utilities)
        self.charger_positions = []
        self.bin_positions = []

        # Defaults for single-target fallback
        self.charger_pos = (0, 0)
        self.bin_pos = (0, 0)

        if self.render_mode:
            pygame.init()
            self.width = self.cols * CELL_SIZE
            self.height = self.rows * CELL_SIZE + 60
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Vacuum AI - Sensible House Layout")
            self.font = pygame.font.SysFont('Arial', 18, bold=True)
            self.assets = {}
            self.load_assets()

    def load_assets(self):
        def load_img(filename):
            path = os.path.join("assets", filename)
            if not os.path.exists(path): return None
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

        self.assets['floor'] = load_img("floor.png")
        self.assets['robot'] = load_img("robot.png")
        self.assets[DIRT] = load_img("dirts.png")
        self.assets[CHARGER] = load_img("charger.png")
        self.assets[BIN] = load_img("bin.png")
        self.assets[WALL] = load_img("wall.png")
        self.assets[WALL_UP] = load_img("wall_up.png")
        self.assets[WALL_DOWN] = load_img("wall_down.png")
        self.assets[SOFA_1] = load_img("sofa1.png")
        self.assets[SOFA_2] = load_img("sofa2.png")
        self.assets[CHAIR_UP] = load_img("chair_up.png")
        self.assets[CHAIR_DOWN] = load_img("chair_down.png")
        self.assets[TABLE] = load_img("table.png")
        self.assets[BED] = load_img("bed.png")

    def reset(self):
        """Generates Sensible House with Dual Utilities."""
        self.grid.fill(EMPTY)
        self.charger_positions = []
        self.bin_positions = []

        # --- 1. OUTER SHELL ---
        self.grid[0, :] = WALL_UP
        self.grid[self.rows - 1, :] = WALL_DOWN
        self.grid[:, 0] = WALL
        self.grid[:, self.cols - 1] = WALL
        self.grid[0, 0] = WALL
        self.grid[0, self.cols - 1] = WALL
        self.grid[self.rows - 1, 0] = WALL
        self.grid[self.rows - 1, self.cols - 1] = WALL

        # --- 2. WALLS ---
        for r in range(1, 15): self.grid[r][7] = WALL
        for c in range(1, 7): self.grid[7][c] = WALL
        for c in range(1, 7): self.grid[14][c] = WALL
        for r in range(14, self.rows - 1): self.grid[r][14] = WALL
        for c in range(14, self.cols - 1): self.grid[14][c] = WALL

        # --- 3. DOORS ---
        self.grid[3][7] = EMPTY
        self.grid[10][7] = EMPTY
        self.grid[17][7] = EMPTY
        self.grid[17][14] = EMPTY

        # --- 4. FURNITURE ---
        self.grid[2][2] = BED;
        self.grid[2][5] = TABLE
        self.grid[9][2] = BED;
        self.grid[9][5] = CHAIR_UP
        self.grid[16][2] = BED;
        self.grid[18][5] = TABLE
        self.grid[3][12] = SOFA_1;
        self.grid[3][13] = SOFA_1
        self.grid[5][12] = TABLE;
        self.grid[5][13] = TABLE
        self.grid[8][17] = SOFA_2
        self.grid[10][12] = TABLE;
        self.grid[10][13] = TABLE
        self.grid[9][12] = CHAIR_DOWN;
        self.grid[9][13] = CHAIR_DOWN
        self.grid[11][12] = CHAIR_UP;
        self.grid[11][13] = CHAIR_UP
        self.grid[17][17] = TABLE

        # --- 5. DUAL UTILITIES ---
        # Charger 1 (Top Right)
        self.grid[1][18] = CHARGER
        self.charger_positions.append((1, 18))
        # Charger 2 (Bottom Left)
        self.grid[18][2] = CHARGER
        self.charger_positions.append((18, 2))

        # Bin 1 (Shed)
        self.grid[16][18] = BIN
        self.bin_positions.append((16, 18))
        # Bin 2 (Bedroom 1)
        self.grid[5][2] = BIN
        self.bin_positions.append((5, 2))

        # Fallback for old agent compatibility
        self.charger_pos = self.charger_positions[0]
        self.bin_pos = self.bin_positions[0]

        # --- 6. DIRT ---
        num_dirt = 40
        placed = 0
        attempts = 0
        while placed < num_dirt and attempts < 1000:
            r = random.randint(1, self.rows - 2)
            c = random.randint(1, self.cols - 2)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = DIRT
                placed += 1
            attempts += 1

        return self.charger_positions[0]

    def random_dirt_spawn(self):
        # 1% Chance
        if random.random() < 0.01:
            for _ in range(10):
                r = random.randint(1, self.rows - 2)
                c = random.randint(1, self.cols - 2)
                if self.grid[r][c] == EMPTY:
                    self.grid[r][c] = DIRT
                    return

    def get_sensors(self, x, y):
        def get_val(r, c):
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols: return WALL
            val = self.grid[r][c]
            if val in [SOFA_1, SOFA_2, BED, TABLE, CHAIR_UP, CHAIR_DOWN, WALL_UP, WALL_DOWN]:
                return WALL
            return val

        return (
            get_val(x, y - 1), get_val(x, y + 1), get_val(x + 1, y), get_val(x - 1, y),
            self.grid[x][y]
        )

    def draw(self, agent=None):
        if not self.render_mode: return

        if self.assets.get('floor'):
            for r in range(self.rows):
                for c in range(self.cols):
                    self.screen.blit(self.assets['floor'], (c * CELL_SIZE, r * CELL_SIZE))
        else:
            self.screen.fill(WHITE)

        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.grid[r][c]
                rect = (c * CELL_SIZE, r * CELL_SIZE)
                if tile != EMPTY:
                    if tile in self.assets and self.assets[tile]:
                        self.screen.blit(self.assets[tile], rect)
                    else:
                        color = BLACK
                        if tile == DIRT:
                            color = BROWN
                        elif tile == CHARGER:
                            color = GREEN
                        elif tile == BIN:
                            color = RED
                        elif tile in [SOFA_1, SOFA_2]:
                            color = BLUE
                        pygame.draw.rect(self.screen, color, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        if agent:
            if self.assets.get('robot'):
                self.screen.blit(self.assets['robot'], (agent.y * CELL_SIZE, agent.x * CELL_SIZE))
            else:
                rect = (agent.y * CELL_SIZE + 5, agent.x * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
                pygame.draw.rect(self.screen, BLUE, rect)

        pygame.display.flip()