import pygame
import random
import time
import json
import config

pygame.init()

# Setup display
dis = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game - Refactored')
clock = pygame.time.Clock()

# Import game state and functions from main module
from snake_main import (
    init_game, run_game_states, 
    handle_game_state, get_font_size,
    SNAKE_STATE, GAME_OVER_STATE
)

# Main entry point
if __name__ == '__main__':
    pygame.display.set_caption(f'Snake Game - {config.DIFFICULTY_NORMAL}')
    
    # Initialize game state
    game_state, score, high_score = init_game()
    
    # Run the game with state-based architecture
    run_game_states(game_state, score, high_score)
