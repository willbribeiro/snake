"""Game configuration and constants.

Every tunable value lives here. Values are gameplay-affecting; the test
suite (test_snake.py) pins the important ones down.
"""

# Window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Grid / gameplay
BLOCK_SIZE = 10
STARTING_LENGTH = 3
INITIAL_SPEED = 15        # FPS at level 1
SPEED_INCREMENT = 5       # FPS added on every level-up
MAX_SPEED = 40            # FPS cap

# Scoring
POINTS_PER_FOOD = 10
POINTS_PER_LEVEL = 50     # score multiple at which a level-up happens

# Input
INPUT_BUFFER_SIZE = 2     # max queued direction changes

# Rendering
UI_FPS = 30               # tick rate on menu / pause / game-over screens
BODY_GRAY_MIN = 15        # body gradient intensity near the head
BODY_GRAY_MAX = 70        # body gradient intensity at the tail

# Persistence
HIGHSCORE_FILE = 'highscore.json'

# Colors
BACKGROUND_COLOR = (50, 153, 213)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 102)
SNAKE_HEAD_COLOR = (0, 0, 0)

# Fonts
FONT_SIZE_LARGE = 50
FONT_SIZE_MEDIUM = 35
FONT_SIZE_SMALL = 20
