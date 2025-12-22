import numpy as np
import random
from collections import deque, defaultdict
from config import *
from bfs import bfs

# -------- HIGH-LEVEL GOALS (RL decides ONLY these) --------
GO_CLEAN = 0
GO_DUMP = 1
GO_CHARGE = 2
IDLE = 3


class VacuumAgent:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.battery = MAX_BATTERY
        self.bin = 0
        self.is_alive = True

        self.q_table = {}
        self.epsilon = EPSILON

        self.current_goal = None
        self.current_path = deque()

    # ---------------- HIGH-LEVEL STATE ----------------
    def get_state(self, env):
        dirt_left = np.count_nonzero(env.grid == DIRT)

        if self.battery < 40:
            batt = 0
        elif self.battery < 120:
            batt = 1
        else:
            batt = 2

        bin_stat = 1 if self.bin >= MAX_BIN else 0
        dirt_stat = 1 if dirt_left == 0 else 0

        return (batt, bin_stat, dirt_stat)

    # ---------------- GOAL SELECTION ----------------
    def choose_goal(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(4)

        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(4)

        self.q_table[state][action] += LEARNING_RATE * (
                reward
                + DISCOUNT_FACTOR * np.max(self.q_table[next_state])
                - self.q_table[state][action]
        )

    # ---------------- PATH EXECUTION ----------------
    def move_step(self, env):
        if not self.current_path:
            return REWARD_STEP, False

        nx, ny = self.current_path.popleft()

        if env.grid[nx][ny] in OBSTACLES:
            return REWARD_WALL, False

        self.x, self.y = nx, ny
        self.battery -= BATTERY_COST_MOVE

        if self.battery <= 0:
            return REWARD_DEATH, True

        return REWARD_STEP, False

    # ---------------- PLAN NEW GOAL ----------------
    def plan(self, env, goal):
        if goal == GO_CLEAN:
            targets = np.argwhere(env.grid == DIRT)
        elif goal == GO_DUMP:
            targets = env.bin_positions
        elif goal == GO_CHARGE:
            targets = env.charger_positions
        else:
            return False

        if len(targets) == 0:
            return False

        path = bfs(env, (self.x, self.y), targets)
        if not path:
            return False

        self.current_path = deque(path)
        return True

    # ---------------- INTERACTION ----------------
    def interact(self, env):
        reward = 0

        if env.grid[self.x][self.y] == DIRT and self.bin < MAX_BIN:
            env.grid[self.x][self.y] = EMPTY
            self.bin += 1
            self.battery -= BATTERY_COST_CLEAN
            reward += REWARD_CLEAN

        elif env.grid[self.x][self.y] == BIN and self.bin > 0:
            self.bin = 0
            reward += REWARD_DUMP

        elif env.grid[self.x][self.y] == CHARGER and self.battery < MAX_BATTERY:
            self.battery = min(MAX_BATTERY, self.battery + 10)
            reward += 5

        return reward
