"""Game configuration and constants module."""
import pygame

# Screen Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 10

# Game Speed (FPS)
INITIAL_SPEED = 15
SPEED_INCREMENT = 5
MIN_SPEED = 40  # Maximum speed cap

# Food
FOOD_COLORS = {
    'green': (0, 255, 0),
    'red': (213, 50, 80),
    'yellow': (255, 255, 102),
}

# Snake
SNAKE_COLORS = {
    'body': (0, 0, 0),
    'head': (0, 0, 0),
    'eyes': (255, 255, 255),
}

# Background
BACKGROUND_COLOR = (50, 153, 213)

# Text Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 102)
BLUE = (50, 153, 213)

# Font Sizes
FONT_SIZE_LARGE = 50
FONT_SIZE_MEDIUM = 35
FONT_SIZE_SMALL = 20

# Game States
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_GAME_OVER = 'game_over'

# Key Bindings
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_P = pygame.K_p  # Pause toggle
KEY_Q = pygame.K_q  # Quit from game over
KEY_C = pygame.K_c  # Continue from game over

# Difficulty Settings
DIFFICULTY_EASY = 'easy'
DIFFICULTY_NORMAL = 'normal'
DIFFICULTY_HARD = 'hard'
DIFFICULTY_INSANE = 'insane'

DIFFICULTY_CONFIG = {
    DIFFICULTY_EASY: {'base_speed': 10, 'speed_increment': 3, 'level_cap': None},
    DIFFICULTY_NORMAL: {'base_speed': 15, 'speed_increment': 5, 'level_cap': 10},
    DIFFICULTY_HARD: {'base_speed': 20, 'speed_increment': 7, 'level_cap': 8},
    DIFFICULTY_INSANE: {'base_speed': 30, 'speed_increment': 10, 'level_cap': 5},
}

# Power-ups
POWERUP_CHANCE = 0.05  # 5% chance to spawn power-up with food
POWERUP_DURATION = 5000  # Milliseconds for timed power-ups
POWERUP_TYPES = ['speed', 'shield']
