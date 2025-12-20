import numpy as np
import pickle
import time
from environment import GridWorld
from agent import VacuumAgent
from config import *


def train():
    # 1. Setup Environment (Headless - No Render)
    env = GridWorld(render_mode=False)
    agent = VacuumAgent()

    EPISODES = 20000  # Number of training runs
    print(f"Starting Training for {EPISODES} episodes on 20x20 Map...")

    start_time = time.time()

    for episode in range(EPISODES):
        # A. Reset for new run
        start_pos = env.reset()  # New Random Map!
        agent.x, agent.y = start_pos
        agent.battery = MAX_BATTERY
        agent.bin = 0
        agent.is_alive = True

        # B. Get Initial State
        state = agent.get_state(env)

        done = False
        total_reward = 0
        steps = 0

        # C. Run Episode until Dead or Timeout
        while not done and steps < 500:  # Max 500 steps per game
            # 1. Choose Action
            action = agent.choose_action(state)

            # 2. Execute Action
            reward, done = agent.step(action, env)

            # 3. Observe New State
            next_state = agent.get_state(env)

            # 4. Update Brain
            agent.learn(state, action, reward, next_state)

            # 5. Advance
            state = next_state
            total_reward += reward
            steps += 1

        # D. Decay Epsilon (Explore less as we learn more)
        if agent.epsilon > MIN_EPSILON:
            agent.epsilon *= EPSILON_DECAY

        # Progress Print (Every 1000 episodes)
        if (episode + 1) % 1000 == 0:
            print(f"Eps {episode + 1}/{EPISODES} | Epsilon: {agent.epsilon:.2f} | Last Reward: {total_reward}")

    end_time = time.time()
    print(f"Training Complete in {end_time - start_time:.2f} seconds.")

    # E. Save the Brain
    with open("brain.pkl", "wb") as f:
        pickle.dump(agent.q_table, f)
    print("Brain saved to 'brain.pkl'")


if __name__ == "__main__":
    train()