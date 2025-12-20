import numpy as np
import random
from config import *


class VacuumAgent:
    def __init__(self):
        # Position & Resources
        self.x = 0
        self.y = 0
        self.battery = MAX_BATTERY
        self.bin = 0
        self.is_alive = True

        # Stats
        self.dirt_cleaned = 0

        # AI BRAIN (Q-Learning)
        # Key: State Tuple -> Value: Array of Q-Values for 7 actions
        self.q_table = {}
        self.epsilon = EPSILON  # Exploration rate

    def get_state(self, env):
        """
        Converts raw environment data into a Generalized State Tuple.
        State = (North, South, East, West, Current, Battery_Status, Bin_Status)
        """
        # 1. Get Local Sensors (What is around me?)
        # Returns (N, S, E, W, Current)
        sensors = env.get_sensors(self.x, self.y)

        # 2. Discretize Battery (Simplify to High/Low/Critical)
        if self.battery < 20:
            batt_state = 0  # Critical (Find charger NOW)
        elif self.battery < 60:
            batt_state = 1  # Low
        else:
            batt_state = 2  # High

        # 3. Discretize Bin (Simplify to Full/Not Full)
        bin_state = 1 if self.bin >= MAX_BIN else 0

        # Combine into one tuple
        return sensors + (batt_state, bin_state)

    def choose_action(self, state):
        """Epsilon-Greedy Strategy: Explore vs Exploit"""
        # If this state is new, initialize it in the brain with zeros
        if state not in self.q_table:
            self.q_table[state] = np.zeros(7)  # 7 Actions

        # Exploration (Random Guess)
        if random.random() < self.epsilon:
            return random.randint(0, 6)

        # Exploitation (Best Known Move)
        else:
            return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        """The Bellman Equation: Updates the Q-Value based on results"""
        # Ensure next_state exists in table
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(7)

        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])

        # Q(s,a) = Q(s,a) + lr * (reward + gamma * max(Q(s')) - Q(s,a))
        new_value = old_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * next_max - old_value)

        self.q_table[state][action] = new_value

    def step(self, action, env):
        """
        Executes an action and updates the agent's state.
        Actions: 0=Up, 1=Down, 2=Right, 3=Left, 4=Clean, 5=Charge, 6=Dump
        """
        prev_x, prev_y = self.x, self.y


        if not self.is_alive:
            return REWARD_DEATH, True

        if self.battery < 20:
            reward = -5  # High stress mode!
        else:
            reward = REWARD_STEP  # Normal mode (-2)

        done = False



        # Calculate potential new position
        next_x, next_y = self.x, self.y
        if action == 0:
            next_x -= 1  # Up
        elif action == 1:
            next_x += 1  # Down
        elif action == 2:
            next_y += 1  # Right
        elif action == 3:
            next_y -= 1  # Left

        # --- PHYSICS LOGIC ---

        # 1. MOVEMENT (Actions 0-3)
        if action < 4:
            # Check for Wall Collision
            if env.grid[next_x][next_y] == WALL:
                reward = REWARD_WALL
            else:
                self.x, self.y = next_x, next_y
                self.battery -= BATTERY_COST_MOVE

        # 2. CLEANING (Action 4)
        elif action == 4:
            current_tile = env.grid[self.x][self.y]
            if current_tile == DIRT:
                if self.bin < MAX_BIN:
                    env.grid[self.x][self.y] = EMPTY
                    self.bin += 1
                    self.dirt_cleaned += 1
                    reward = REWARD_CLEAN
                    self.battery -= BATTERY_COST_CLEAN
                else:
                    reward = -5  # Bin full!
            else:
                reward = -2  # Wasted clean

        # 3. CHARGING (Action 5)
        elif action == 5:
            if env.grid[self.x][self.y] == CHARGER:
                # Big reward ONLY if we actually needed it
                if self.battery < 60:
                    reward = REWARD_CHARGE
                self.battery = MAX_BATTERY
            else:
                reward = -5  # Not at charger

        # 4. DUMPING (Action 6)
        elif action == 6:
            if env.grid[self.x][self.y] == BIN:
                # Big reward ONLY if we actually needed it
                if self.bin >= MAX_BIN:
                    reward = REWARD_DUMP
                self.bin = 0
            else:
                reward = -5  # Not at bin

        # --- DEATH CHECK ---
        if self.battery <= 0:
            self.battery = 0
            self.is_alive = False
            reward = REWARD_DEATH
            done = True

        if self.x == prev_x and self.y == prev_y and action < 4:
            reward -= 5  # Extra penalty for wasting time hitting walls

        return reward, done
