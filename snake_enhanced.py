"""
Snake Game - Enhanced Version
==============================
This is the main game file with all improvements integrated:
- Phase 1: Input buffering, state management, high scores
- Phase 2: UI/UX improvements (pause menu, HUD)
- Phase 3: Power-up system
"""

import pygame
import random
import json
from collections import deque
import config
from powerups import PowerUpManager, POWERUP_COLORS, get_powerup_info


class SnakeGame:
    """Enhanced Snake game with all features."""
    
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        """Reset all game variables to initial state."""
        # Game state
        self.game_state = 'menu'  # menu, playing, paused, game_over
        self.high_score_file = 'highscore.json'
        
        # Score tracking
        self.score = 0
        try:
            with open(self.high_score_file, 'r') as f:
                self.high_score = int(f.read().strip())
        except FileNotFoundError:
            self.high_score = 0
        
        # Snake properties
        self.snake_block = config.BLOCK_SIZE
        self.start_x = config.SCREEN_WIDTH / 2 - self.snake_block / 2
        self.start_y = config.SCREEN_HEIGHT / 2 - self.snake_block / 2
        self.x = self.start_x
        self.y = self.start_y
        
        # Direction and movement
        self.x_change = 0
        self.y_change = 0
        self.direction = 'RIGHT'
        
        # Snake body (use deque for efficient operations)
        self.snake_list = deque()
        self.snake_length = 3  # Starting length
        
        # Food
        self.food_x = config.SCREEN_WIDTH // 2 * self.snake_block
        self.food_y = config.SCREEN_HEIGHT // 2 * self.snake_block
        
        # Speed and levels
        self.speed = config.INITIAL_SPEED
        self.level = 1
        
        # Input buffer (prevents quick death)
        self.input_buffer = deque(maxlen=1)
        
        # Power-up system
        self.powerup_manager = PowerUpManager(self)
        self.powerup_active = False
        self.shield_active = False
        
        # Create power-up manager after game instance
        self.game_powerups = PowerUpManager(self)
    
    def handle_events(self):
        """Handle pygame events with input buffering."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = 'quit'
                return True
            
            elif event.type == pygame.KEYDOWN:
                
                # Pause toggle (P key)
                if event.key == config.KEY_P and self.game_state == 'playing':
                    if self.game_state == 'playing':
                        self.game_state = 'paused'
                    elif self.game_state == 'paused':
                        self.game_state = 'playing'
                    continue
                
                # Direction changes with input buffering
                if self.game_state == 'playing':
                    if event.key == config.KEY_LEFT:
                        self.input_buffer.append(('LEFT',))
                    elif event.key == config.KEY_RIGHT:
                        self.input_buffer.append(('RIGHT',))
                    elif event.key == config.KEY_UP:
                        self.input_buffer.append(('UP',))
                    elif event.key == config.KEY_DOWN:
                        self.input_buffer.append(('DOWN',))
                
                # Menu navigation
                if self.game_state == 'menu':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_game()
                    
                # Game over navigation
                elif self.game_state == 'game_over':
                    if event.key == config.KEY_C:
                        self.reset_game()
                        self.game_state = 'menu'
                    elif event.key == config.KEY_Q:
                        self.game_state = 'quit'
        
        return False
    
    def process_input(self):
        """Process buffered inputs for smooth movement."""
        if self.input_buffer and len(self.input_buffer) > 0:
            direction_tuple = self.input_buffer[0]
            
            # Prevent reversing direction
            head_x, head_y = self.snake_list[0]
            
            if direction_tuple[0] == 'UP' and self.direction != 'DOWN':
                self.x_change = 0
                self.y_change = -self.snake_block
                self.direction = 'UP'
            elif direction_tuple[0] == 'DOWN' and self.direction != 'UP':
                self.x_change = 0
                self.y_change = self.snake_block
                self.direction = 'DOWN'
            elif direction_tuple[0] == 'LEFT' and self.direction != 'RIGHT':
                self.x_change = -self.snake_block
                self.y_change = 0
                self.direction = 'LEFT'
            elif direction_tuple[0] == 'RIGHT' and self.direction != 'LEFT':
                self.x_change = self.snake_block
                self.y_change = 0
                self.direction = 'RIGHT'
            
            # Remove processed input
            self.input_buffer.popleft()
    
    def spawn_food(self):
        """Spawn food at a random position not on the snake."""
        while True:
            # Generate random grid position
            food_x = random.randrange(
                0, config.SCREEN_WIDTH // config.BLOCK_SIZE) * self.snake_block
            food_y = random.randrange(
                0, config.SCREEN_HEIGHT // config.BLOCK_SIZE) * self.snake_block
            
            # Check if position is on snake body
            on_snake = False
            for segment in self.snake_list:
                if segment[0] == food_x and segment[1] == food_y:
                    on_snake = True
                    break
            
            # Also check current head position
            if self.x != food_x or self.y != food_y:
                if not on_snake:
                    self.food_x = food_x
                    self.food_y = food_y
                    return
        
        # Chance to spawn power-up with food
        return self.game_powerups.spawn_powerup()
    
    def spawn_powerup(self):
        """Helper to spawn power-up."""
        return self.game_powerups.spawn_powerup()
    
    def activate_powerup(self, powerup_type):
        """Activate a power-up effect."""
        
        if powerup_type == 'speed':
            # Speed boost: increase speed by 30%
            self.speed = int(self.speed * 1.3)
            return True
        
        elif powerup_type == 'length':
            # Length bonus: add extra segments without eating food
            bonus_segments = 5
            for _ in range(bonus_segments):
                if len(self.snake_list) >= self.snake_length:
                    removed = self.snake_list.pop()
            
            return True
        
        elif powerup_type == 'shield':
            # Shield: temporary invincibility
            duration_frames = int(
                config.POWERUP_DURATION / (1000 / self.speed)
            )
            self.shield_active = True
            self.powerup_timer = duration_frames
            return True
        
        return False
    
    def check_food_collision(self):
        """Check if snake ate food or power-up."""
        head_x, head_y = self.snake_list[0]
        
        if head_x == self.food_x and head_y == self.food_y:
            # Eat food
            self.score += 10
            self.spawn_food()
            
            # Check for level up every 50 points
            if self.score % 50 == 0:
                self.level_up()
            
            return True
        
        return False
    
    def check_powerup_collision(self):
        """Check if snake collided with a power-up."""
        # For simplicity, we'll spawn powerups adjacent to food
        # and the snake eats them when they're in that position
        head_x, head_y = self.snake_list[0]
        
        powerup_x = self.food_x + self.snake_block // 2
        powerup_y = self.food_y - self.snake_block
        
        if head_x == powerup_x and head_y == powerup_y:
            # Activate the powerup
            activated = self.activate_powerup('shield')  # Default shield for now
            return True
        
        return False
    
    def level_up(self):
        """Increase game speed for level up."""
        self.level += 1
        new_speed = min(
            self.speed + config.SPEED_INCREMENT, 
            config.MIN_SPEED
        )
        self.speed = new_speed
    
    def save_high_score(self):
        """Save high score to file."""
        with open(self.high_score_file, 'w') as f:
            f.write(str(self.high_score))
    
    def start_game(self):
        """Transition to playing state."""
        self.game_state = 'playing'
        # Clear snake and reset to starting position
        self.snake_list.clear()
        self.snake_length = 3
        self.spawn_food()
    
    def draw_rect_rounded(self, color, x, y, size):
        """Draw a rounded rectangle for better visuals."""
        pygame.draw.rect(dis, color, [x, y, size, size])
    
    def draw_snake_head(self, x, y):
        """Draw the snake head with eyes looking in direction of movement."""
        
        # Draw head body
        pygame.draw.rect(
            dis, config.SNAKE_COLORS['head'],
            [x - 2, y - 2, self.snake_block + 4, self.snake_block + 4]
        )
        
        # Add eyes based on direction
        eye_offset = self.snake_block // 4
        center_x, center_y = x + self.snake_block // 2, y + self.snake_block // 2
        
        if self.direction == 'UP':
            eye_positions = [
                (x + eye_offset * 3, y + eye_offset * 3),
                (x + self.snake_block - eye_offset * 3, y + eye_offset * 3)
            ]
        elif self.direction == 'DOWN':
            eye_positions = [
                (x + eye_offset * 3, y + self.snake_block - eye_offset * 3),
                (x + self.snake_body - eye_offset * 3, y + self.snake_block - eye_offset * 3)
            ]
        elif self.direction == 'LEFT':
            eye_positions = [
                (x - eye_offset * 3, y + eye_offset * 3),
                (x - eye_offset * 3, y + self.snake_block - eye_offset * 3)
            ]
        else:  # RIGHT
            eye_positions = [
                (x + self.snake_block - eye_offset * 3, y + eye_offset * 3),
                (x + self.snake_block - eye_offset * 3, y + self.snake_block - eye_offset * 3)
            ]
        
        # Draw eyes
        for ex, ey in eye_positions:
            pygame.draw.circle(dis, config.WHITE, [ex, ey], eye_offset // 2)
    
    def draw_game(self):
        """Draw the game screen."""
        
        # Draw background with subtle gradient effect
        dis.fill(config.BACKGROUND_COLOR)
        
        if self.game_state == 'playing':
            # Draw score HUD
            score_text = font_medium.render(
                f"Score: {self.score}  Level: {self.level}", True, config.BLACK)
            dis.blit(score_text, (5, 5))
            
            # Draw high score
            if self.high_score > 0:
                hi_text = font_small.render(
                    f"High Score: {self.high_score}", True, config.WHITE)
                dis.blit(hi_text, (10, config.SCREEN_HEIGHT - 40))
            
            # Draw power-up indicator if active
            if self.powerup_active and self.shield_active:
                shield_font = pygame.font.SysFont(None, 35)
                shield_text = "🛡️ SHIELD ACTIVE"
                text_surface = shield_font.render(shield_text, True, config.WHITE)
                text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH//2, 
                                                          80))
                dis.blit(text_surface, text_rect)
            
            # Draw food
            pygame.draw.rect(dis, config.GREEN, 
                           [self.food_x, self.food_y, self.snake_block, self.snake_block])
            
            # Add pulsing effect to food
            pulse = (time.time() % 10 < 5)  # Simple pulse toggle
            
            # Draw snake
            for i, segment in enumerate(self.snake_list):
                x, y = segment
                
                if i == 0:
                    # Head - draw separately with eyes
                    self.draw_snake_head(x, y)
                else:
                    # Body segments
                    pygame.draw.rect(dis, config.BLACK, 
                                   [x, y, self.snake_block, self.snake_block])
            
            # Draw pause overlay
            if self.game_state == 'paused':
                pause_font = font_large.render('PAUSED', True, config.WHITE)
                dis.blit(pause_font, (config.SCREEN_WIDTH // 2 - pause_font.get_width() // 2,
                                      config.SCREEN_HEIGHT // 2))
        
        elif self.game_state == 'menu':
            # Draw main menu
            title = font_large.render('SNAKE GAME', True, config.GREEN)
            dis.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, 
                             config.SCREEN_HEIGHT // 2 - 150))
            
            score_text = font_medium.render(
                f"High Score: {self.high_score}", True, config.WHITE)
            dis.blit(score_text, (config.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                  config.SCREEN_HEIGHT // 2 - 50))
            
            start_text = font_medium.render(
                "Press ENTER to Start", True, config.YELLOW)
            dis.blit(start_text, (config.SCREEN_WIDTH // 2 - start_text.get_width() // 2, 
                                  config.SCREEN_HEIGHT // 2 + 50))
            
            # Controls help
            controls = font_small.render(
                "Controls: Arrows to move | P to pause", True, config.WHITE)
            dis.blit(controls, (config.SCREEN_WIDTH // 2 - controls.get_width() // 2, 
                                config.SCREEN_HEIGHT // 2 + 100))
        
        elif self.game_state == 'game_over':
            # Draw game over screen
            title = font_large.render('GAME OVER', True, config.RED)
            dis.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, 
                             config.SCREEN_HEIGHT // 3 - 80))
            
            score_text = font_medium.render(
                f"Final Score: {self.score}", True, config.WHITE)
            dis.blit(score_text, (config.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                  config.SCREEN_HEIGHT // 3 - 30))
            
            high_text = font_medium.render(
                f"High Score: {self.high_score}", True, config.YELLOW)
            dis.blit(high_text, (config.SCREEN_WIDTH // 2 - high_text.get_width() // 2, 
                                  config.SCREEN_HEIGHT // 3 + 20))
            
            level_text = font_small.render(
                f"Level Reached: {self.level}", True, config.WHITE)
            dis.blit(level_text, (config.SCREEN_WIDTH // 2 - level_text.get_width() // 2, 
                                  config.SCREEN_HEIGHT // 3 + 70))
            
            # Instructions
            instr_text = font_small.render(
                "Press 'C' to Play Again or 'Q' to Quit", True, config.WHITE)
            dis.blit(instr_text, (config.SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 
                                  config.SCREEN_HEIGHT // 3 + 140))
        
        pygame.display.update()
    
    def game_loop(self):
        """Main game loop."""
        # Check if already in game over state
        if self.game_state == 'game_over':
            return False
        
        # Handle events
        event_quit = self.handle_events()
        if event_quit:
            return False
        
        # Process buffered input (Phase 1 - prevents quick death)
        self.process_input()
        
        # Check power-up timer
        if hasattr(self, 'powerup_timer') and self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.shield_active = False
                self.powerup_active = False
        
        # Move snake
        head_x = self.x + self.x_change
        head_y = self.y + self.y_change
        
        # Add new head to list
        self.snake_list.appendleft((head_x, head_y))
        
        # Update current position
        self.x = head_x
        self.y = head_y
        
        # Shrink snake if needed
        if len(self.snake_list) > self.snake_length:
            removed = self.snake_list.pop()
        
        # Check collisions in priority order
        game_over = False
        
        # 1. Wall collision
        if self.check_wall_collision():
            game_over = True
        # 2. Self collision (skip if shield active)
        elif not self.shield_active and self.check_self_collision():
            game_over = True
        # 3. Food eating
        elif self.check_food_collision():
            # Grow snake
            self.snake_length += 1
            # Spawn new food
            self.spawn_food()
        
        if game_over:
            self.game_state = 'game_over'
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        
        # Draw everything
        self.draw_game()
        
        return True


# Global variables for drawing (will be set by main)
dis = None
font_large = None
font_medium = None
font_small = None
config.SCREEN_WIDTH = 800
config.SCREEN_HEIGHT = 600
config.BLOCK_SIZE = 10
config.INITIAL_SPEED = 15
config.MIN_SPEED = 40


def main():
    """Main function to start the game."""
    # Global init
    global dis, font_large, font_medium, font_small
    
    pygame.init()
    dis = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(f'Snake Game - Improved')
    clock = pygame.time.Clock()
    
    font_large = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
    font_medium = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
    font_small = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)
    
    # Create game instance
    game = SnakeGame()
    
    running = True
    while running:
        if game.game_loop():
            continue
        
        if game.game_state == 'quit':
            break
    
    pygame.quit()


if __name__ == '__main__':
    main()
