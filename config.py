# --- Grid Settings ---
GRID_SIZE = 20      # Increased from 10 to 20
CELL_SIZE = 40      # Reduced from 50 to 40 to fit screen
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + 60  # UI space at bottom

# --- Tile Codes ---
EMPTY = 0
DIRT = 1
WALL = 2
CHARGER = 3
BIN = 4

# --- Agent Constraints ---
MAX_BATTERY = 200         # Increased to support larger map travel
MAX_BIN = 5
BATTERY_COST_MOVE = 1
BATTERY_COST_CLEAN = 2

# --- Rewards ---
REWARD_CLEAN = 20
REWARD_CHARGE = 50
REWARD_DUMP = 50
REWARD_STEP = -1
REWARD_WALL = -10
REWARD_DEATH = -100

# --- Q-Learning Hyperparameters ---
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EPSILON = 1.0
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.05

# --- Colors (R, G, B) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)