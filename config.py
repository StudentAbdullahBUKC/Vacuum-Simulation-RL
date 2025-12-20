# --- Grid Settings ---
GRID_SIZE = 20
CELL_SIZE = 40
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + 60

# --- Tile Codes ---
EMPTY = 0
DIRT = 1
WALL = 2
CHARGER = 3
BIN = 4

# --- Agent Constraints ---
MAX_BATTERY = 200
MAX_BIN = 5
BATTERY_COST_MOVE = 1
BATTERY_COST_CLEAN = 2

# --- Rewards (TUNED FOR EFFICIENCY) ---
REWARD_CLEAN = 50         # Increased (Was 20) - Makes dirt irresistible
REWARD_CHARGE = 50
REWARD_DUMP = 50
REWARD_STEP = -1          # Increased Penalty (Was -1) - Forces speed
REWARD_WALL = -20         # Increased Penalty (Was -10) - Fears walls more
REWARD_DEATH = -200       # Massive penalty for dying

# --- Q-Learning Hyperparameters ---
LEARNING_RATE = 0.15      # Slightly faster learning (Was 0.1)
DISCOUNT_FACTOR = 0.99    # Cares more about future rewards (Was 0.9)
EPSILON = 1.0
EPSILON_DECAY = 0.995      # Faster decay (Was 0.995)
MIN_EPSILON = 0.05
# --- Q-Learning Hyperparameters ---




# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)