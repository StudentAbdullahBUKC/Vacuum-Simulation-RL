import matplotlib.pyplot as plt
import numpy as np
import pickle
from environment import GridWorld
from agent import VacuumAgent
from config import *


def train():
    # 1. Setup Environment (Headless)
    env = GridWorld(render_mode=False)
    agent = VacuumAgent()

    EPISODES = 20000  # Increased to 20,000 as requested

    # Data storage
    episode_list = []
    reward_list = []

    # 2. Setup Live Plot
    print("Initializing Live Dashboard...")
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))

    # Line 1: Raw Data (Blue, faint)
    line, = ax.plot([], [], 'b-', alpha=0.3, label='Episode Reward')
    # Line 2: Moving Average (Red, thick) - Window 100 for smoother look
    avg_line, = ax.plot([], [], 'r-', linewidth=2, label='Avg Reward (100 eps)')

    ax.set_title(f"AI Training Performance (Map: {GRID_SIZE}x{GRID_SIZE})")
    ax.set_xlabel("Episodes")
    ax.set_ylabel("Total Reward")
    ax.legend()
    ax.grid(True)

    print(f"🚀 Starting Training for {EPISODES} episodes...")

    for ep in range(EPISODES):
        # Reset
        start_pos = env.reset()
        agent.x, agent.y = start_pos
        agent.battery = MAX_BATTERY
        agent.bin = 0
        agent.is_alive = True

        state = agent.get_state(env)
        done = False
        total_reward = 0
        steps = 0

        # Run Episode
        while not done and steps < 500:
            action = agent.choose_action(state)
            reward, done = agent.step(action, env)
            next_state = agent.get_state(env)
            agent.learn(state, action, reward, next_state)

            state = next_state
            total_reward += reward
            steps += 1

        # Decay Epsilon
        if agent.epsilon > MIN_EPSILON:
            agent.epsilon *= EPSILON_DECAY

        # Store Data
        episode_list.append(ep)
        reward_list.append(total_reward)

        # Update Plot Every 1000 Episodes (As requested)
        if ep % 1000 == 0 and len(episode_list) > 0:
            # Update Raw Data
            line.set_xdata(episode_list)
            line.set_ydata(reward_list)

            # Calculate and Plot Running Average (Window 100)
            window_size = 100
            if len(reward_list) >= window_size:
                avg_rewards = np.convolve(reward_list, np.ones(window_size) / window_size, mode='valid')

                # Align X-axis
                avg_x = episode_list[len(episode_list) - len(avg_rewards):]

                avg_line.set_xdata(avg_x)
                avg_line.set_ydata(avg_rewards)

            # Adjust Scale
            try:
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()
            except ValueError:
                pass

                # Console Log (Average of last 1000 for clarity)
            block_avg = np.mean(reward_list[-1000:]) if len(reward_list) >= 1000 else np.mean(reward_list)
            print(f"Eps {ep} | Avg Reward (Last 1k): {block_avg:.1f} | Epsilon: {agent.epsilon:.2f}")

    # Save Brain
    with open("brain.pkl", "wb") as f:
        pickle.dump(agent.q_table, f)

    print("Training Complete. Brain Saved.")
    print("Close the graph window to exit.")
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    train()