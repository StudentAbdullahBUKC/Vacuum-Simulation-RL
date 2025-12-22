import numpy as np
import pickle
from environment import GridWorld
from agent import VacuumAgent
from config import *


def train():
    env = GridWorld(render_mode=False)
    agent = VacuumAgent()

    MAX_EPISODES = 20000
    rewards = []

    # -------- EARLY STOPPING PARAMETERS --------
    WINDOW = 500
    PATIENCE = 3000
    IMPROVEMENT_THRESHOLD = 1.02

    best_avg = -float("inf")
    stagnation_counter = 0
    # ------------------------------------------

    print("Starting training with Robust Planning Logic...")

    for ep in range(MAX_EPISODES):
        start_pos = env.reset()

        agent.x, agent.y = start_pos
        agent.battery = MAX_BATTERY
        agent.bin = 0
        agent.is_alive = True
        agent.current_goal = None
        agent.current_path.clear()

        state = agent.get_state(env)
        done = False
        total_reward = 0
        steps = 0

        while not done and steps < 1000:
            # 1. Choose Goal
            goal = agent.choose_goal(state)

            # 2. Plan Path (if needed)
            planning_failed = False
            if agent.current_goal != goal or not agent.current_path:
                agent.current_goal = goal
                success = agent.plan(env, goal)

                # --- FIX: Handle Planning Failure ---
                if not success:
                    planning_failed = True
                    # Penalty for picking an invalid/unreachable goal
                    # This prevents the "Frozen Robot" bug
                    reward = -10

                    # 3. Execute Step
            if planning_failed:
                # If plan failed, don't move. Just learn and retry.
                r1 = 0
                r2 = 0
            else:
                # Normal execution
                r1, done = agent.move_step(env)
                r2 = agent.interact(env)
                reward = r1 + r2

            # 4. Learn
            next_state = agent.get_state(env)
            agent.learn(state, goal, reward, next_state)

            state = next_state
            total_reward += reward
            steps += 1

        rewards.append(total_reward)

        # -------- EPSILON DECAY --------
        if agent.epsilon > MIN_EPSILON:
            agent.epsilon *= EPSILON_DECAY

        # -------- LOGGING --------
        if ep % 1000 == 0:
            avg_100 = np.mean(rewards[-100:]) if len(rewards) >= 100 else np.mean(rewards)
            print(f"Episode {ep} | Avg Reward (100): {avg_100:.2f} | Epsilon: {agent.epsilon:.3f}")

        # -------- EARLY STOPPING CHECK --------
        if len(rewards) >= WINDOW:
            current_avg = np.mean(rewards[-WINDOW:])
            if current_avg > best_avg * IMPROVEMENT_THRESHOLD:
                best_avg = current_avg
                stagnation_counter = 0
            else:
                stagnation_counter += 1

            if stagnation_counter >= PATIENCE:
                print(f"\nEarly stopping triggered at episode {ep}")
                print(f"Best {WINDOW}-episode avg reward: {best_avg:.2f}")
                break

    # -------- SAVE TRAINED POLICY --------
    with open("brain.pkl", "wb") as f:
        pickle.dump(agent.q_table, f)

    print("Training complete. Policy saved to brain.pkl")


if __name__ == "__main__":
    train()