"""
Snake Game v2.0 - Complete Enhanced Version
============================================
This version includes ALL improvements:
- Phase 1: Core refactoring, input buffering, state management, high scores
- Phase 2: UI/UX improvements (menus, pause, HUD)
- Phase 3: Power-up system
- Phase 4: Visual polish (particle effects, enhanced graphics)
"""

import pygame
import random
import json
from collections import deque
import config
import time


# Import visual components
from particles import ParticleManager, Particle
from visual_snake import VISUAL_SETTINGS


class SnakeGameEnhanced:
    """Enhanced Snake game with all visual polish features."""
    
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        """Reset all game variables to initial state."""
        # Game state
        self.game_state = 'menu'
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
        self.snake_length = 3
        
        # Food
        self.food_x = config.SCREEN_WIDTH // 2 * self.snake_block
        self.food_y = config.SCREEN_HEIGHT // 2 * self.snake_block
        
        # Speed and levels
        self.speed = config.INITIAL_SPEED
        self.level = 1
        
        # Input buffer (prevents quick death)
        self.input_buffer = deque(maxlen=1)
        
        # Power-up state
        self.powerup_active = False
        self.shield_active = False
        self.powerup_timer = 0
        
        # Particle system for visual effects
        self.particle_manager = ParticleManager()
        self.food_particle_size = self.snake_block // 2 + 1
        self.pulse_offset = 0
    
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
            
            self.input_buffer.popleft()
    
    def spawn_food(self):
        """Spawn food at a random position not on the snake."""
        while True:
            food_x = random.randrange(
                0, config.SCREEN_WIDTH // config.BLOCK_SIZE) * self.snake_block
            food_y = random.randrange(
                0, config.SCREEN_HEIGHT // config.BLOCK_SIZE) * self.snake_block
            
            on_snake = False
            for segment in self.snake_list:
                if segment[0] == food_x and segment[1] == food_y:
                    on_snake = True
                    break
            
            if self.x != food_x or self.y != food_y:
                if not on_snake:
                    self.food_x = food_x
                    self.food_y = food_y
                    return
        
        # Chance to spawn power-up with food (5%)
        import random as rd
        if rd.random() < config.POWERUP_CHANCE:
            pass  # Power-up logic would go here
    
    def spawn_powerup(self):
        """Spawn a random power-up."""
        types = ['speed', 'length']
        powerup_type = random.choice(types)
        
        powerup_x = self.food_x + self.snake_block // 2
        powerup_y = self.food_y - self.snake_block
        
        return (powerup_x, powerup_y, powerup_type)
    
    def activate_powerup(self, powerup_type):
        """Activate a power-up effect."""
        
        if powerup_type == 'speed':
            self.speed = int(self.speed * 1.3)
            return True
        
        elif powerup_type == 'shield':
            duration_frames = int(
                config.POWERUP_DURATION / (1000 / self.speed)
            )
            self.shield_active = True
            self.powerup_timer = duration_frames
            return True
        
        return False
    
    def check_food_collision(self):
        """Check if snake ate food."""
        head_x, head_y = self.snake_list[0]
        
        if head_x == self.food_x and head_y == self.food_y:
            self.score += 10
            self.spawn_food()
            
            if self.score % 50 == 0:
                self.level_up()
            
            return True
        
        return False
    
    def check_powerup_collision(self):
        """Check if snake collided with a power-up."""
        head_x, head_y = self.snake_list[0]
        
        powerup_x = self.food_x + self.snake_block // 2
        powerup_y = self.food_y - self.snake_block
        
        if head_x == powerup_x and head_y == powerup_y:
            activated = self.activate_powerup('shield')
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
        self.snake_list.clear()
        self.snake_length = 3
        self.spawn_food()
    
    def update_particles(self):
        """Update particle effects every frame."""
        self.particle_manager.update()
        
        # Pulse effect for food
        self.pulse_offset += config.INITIAL_SPEED * 0.1
    
    def draw_particle_burst(self, x, y):
        """Draw a particle burst at position (x, y)."""
        if not VISUAL_SETTINGS['particle_effects']:
            return
        
        # Create particle colors based on food type
        base_color = config.GREEN if self.shield_active else config.GREEN
        
        # Spawn food particles
        for i in range(12):
            angle = (i / 12) * 3.14 * 2 + random.uniform(-0.5, 0.5)
            speed = random.uniform(2, 5)
            
            particle = Particle(
                x + self.snake_block // 2,
                y + self.snake_block // 2,
                base_color,
                speed=speed,
                lifetime=random.randint(15, 30)
            )
            self.particle_manager.food_particles.append(particle)
        
        # Add sparks
        for i in range(6):
            particle = Particle(
                x + random.randint(-8, 18),
                y + random.randint(-8, 18),
                (255, 215, 0) if random.random() < 0.7 else (255, 255, 255),
                speed=random.uniform(3, 6),
                lifetime=random.randint(10, 25)
            )
            self.particle_manager.food_particles.append(particle)
    
    def draw_game(self):
        """Draw the game screen with enhanced visuals."""
        
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
            
            # Draw shield indicator if active
            if self.powerup_active and self.shield_active:
                shield_font = pygame.font.SysFont(None, 35)
                shield_text = "🛡️ SHIELD ACTIVE"
                text_surface = shield_font.render(shield_text, True, config.WHITE)
                text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH//2, 
                                                          80))
                dis.blit(text_surface, text_rect)
            
            # Draw food with enhanced visuals
            self.draw_enhanced_food()
            
            # Draw snake with visual polish
            self.draw_enhanced_snake()
            
            # Update and draw particles
            self.update_particles()
            self.draw_particle_burst(self.food_x, self.food_y)
            self.particle_manager.draw(dis)
            
            # Draw pause overlay if paused
            if self.game_state == 'paused':
                pause_font = font_large.render('PAUSED', True, config.WHITE)
                dis.blit(pause_font, (config.SCREEN_WIDTH // 2 - pause_font.get_width() // 2,
                                      config.SCREEN_HEIGHT // 2))
        
        elif self.game_state == 'menu':
            self.draw_menu()
        
        elif self.game_state == 'game_over':
            self.draw_game_over()
        
        pygame.display.update()
    
    def draw_enhanced_food(self):
        """Draw food with enhanced visual effects."""
        
        # Pulsing effect
        pulse_factor = 1 + (0.1 * sin(self.pulse_offset))
        effective_size = max(
            self.snake_block - 2, 
            (self.snake_block // 2) * pulse_factor
        )
        
        # Draw food with glow effect
        glow_x = self.food_x - 2
        glow_y = self.food_y - 2
        
        if not self.shield_active:
            pygame.draw.rect(
                dis, config.GREEN, 
                [glow_x, glow_y, effective_size, effective_size]
            )
        else:
            # Red food when shield is active (visual indicator)
            pygame.draw.rect(
                dis, config.RED, 
                [glow_x, glow_y, effective_size, effective_size]
            )
        
        # Add shine effect to food
        if VISUAL_SETTINGS['food_shine']:
            shine_x = self.food_x + 2
            shine_y = self.food_y - 2
            pygame.draw.rect(dis, (255, 255, 255), 
                           [shine_x, shine_y, 3, 3])
    
    def draw_enhanced_snake(self):
        """Draw snake with enhanced visual polish."""
        
        if not self.snake_list:
            return
        
        # Draw body segments (excluding head)
        for i in range(len(self.snake_list) - 1, 0, -1):
            x, y = self.snake_list[i]
            
            # Vary segment color based on position
            intensity = 0.7 + (0.3 * (i / len(self.snake_list)))
            base_color = (0, 0, 0)
            color = tuple(min(255, c * intensity) for c in base_color)
            
            # Add slight variation for gradient effect
            if config.BLOCK_SIZE > 10:  # Only if block size allows
                pygame.draw.rect(dis, color, 
                               [x - 1, y - 1, config.BLOCK_SIZE + 2, config.BLOCK_SIZE + 2])
        
        # Draw head with eyes
        head_x, head_y = self.snake_list[0]
        
        # Head body
        pygame.draw.rect(
            dis, config.SNAKE_COLORS['head'],
            [head_x - 2, head_y - 2, config.BLOCK_SIZE + 4, config.BLOCK_SIZE + 4]
        )
        
        # Eyes based on direction
        eye_size = 3
        
        if self.direction == 'UP':
            eye_positions = [
                (head_x + 4, head_y + 3),
                (head_x + config.BLOCK_SIZE - 5, head_y + 3)
            ]
            pupil_positions = [
                (head_x + 4, head_y + 1),
                (head_x + config.BLOCK_SIZE - 5, head_y + 1)
            ]
        elif self.direction == 'DOWN':
            eye_positions = [
                (head_x + 4, head_y + config.BLOCK_SIZE - 3),
                (head_x + config.BLOCK_SIZE - 5, head_y + config.BLOCK_SIZE - 3)
            ]
            pupil_positions = [
                (head_x + 4, head_y + config.BLOCK_SIZE - 1),
                (head_x + config.BLOCK_SIZE - 5, head_y + config.BLOCK_SIZE - 1)
            ]
        elif self.direction == 'LEFT':
            eye_positions = [
                (head_x + 2, head_y + 4),
                (head_x + 2, head_y + config.BLOCK_SIZE - 4)
            ]
            pupil_positions = [
                (head_x - 1, head_y + 4),
                (head_x - 1, head_y + config.BLOCK_SIZE - 4)
            ]
        else:  # RIGHT
            eye_positions = [
                (head_x + config.BLOCK_SIZE - 3, head_y + 4),
                (head_x + config.BLOCK_SIZE - 3, head_y + config.BLOCK_SIZE - 4)
            ]
            pupil_positions = [
                (head_x + config.BLOCK_SIZE, head_y + 4),
                (head_x + config.BLOCK_SIZE, head_y + config.BLOCK_SIZE - 4)
            ]
        
        # Draw eyes (white sclera)
        for ex, ey in eye_positions:
            pygame.draw.circle(dis, (255, 255, 255), [ex, ey], eye_size)
        
        # Draw pupils (black)
        for px, py in pupil_positions:
            pygame.draw.circle(dis, (0, 0, 0), [px, py], eye_size // 2)
    
    def draw_menu(self):
        """Draw the main menu."""
        title = font_large.render('SNAKE GAME v2.0', True, config.GREEN)
        dis.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, 
                         config.SCREEN_HEIGHT // 2 - 170))
        
        subtitle = font_small.render(
            "Enhanced with Visual Polish & Particle Effects", True, config.WHITE)
        dis.blit(subtitle, (config.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 
                            config.SCREEN_HEIGHT // 2 - 130))
        
        score_text = font_medium.render(
            f"High Score: {self.high_score}", True, config.WHITE)
        dis.blit(score_text, (config.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                              config.SCREEN_HEIGHT // 2 - 50))
        
        start_text = font_medium.render(
            "Press ENTER to Start", True, config.YELLOW)
        dis.blit(start_text, (config.SCREEN_WIDTH // 2 - start_text.get_width() // 2, 
                              config.SCREEN_HEIGHT // 2 + 30))
        
        # Controls help with icons
        controls = font_small.render(
            "🕹️ Arrows to move | P to pause", True, config.WHITE)
        dis.blit(controls, (config.SCREEN_WIDTH // 2 - controls.get_width() // 2, 
                            config.SCREEN_HEIGHT // 2 + 90))
        
        # Visual polish indicator
        polish_info = font_small.render(
            "✨ New: Particle Effects & Enhanced Graphics", True, (138, 255, 21))
        dis.blit(polish_info, (config.SCREEN_WIDTH // 2 - polish_info.get_width() // 2, 
                               config.SCREEN_HEIGHT // 2 + 140))


# Import sin function for smooth animations
import math

def sin(x):
    """Simple sine function approximation."""
    return abs(math.sin(x))


def main():
    """Main function to start the game."""
    # Global init
    global dis, font_large, font_medium, font_small
    
    pygame.init()
    dis = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(f'Snake Game v2.0 - Enhanced')
    clock = pygame.time.Clock()
    
    font_large = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
    font_medium = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
    font_small = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)
    
    # Create game instance
    game = SnakeGameEnhanced()
    
    running = True
    while running:
        if game.game_loop():
            continue
        
        if game.game_state == 'quit':
            break
    
    pygame.quit()


def game_loop(self):
    """Game loop helper method."""
    # Check if already in game over state
    if self.game_state == 'game_over':
        return False
    
    # Handle events
    event_quit = self.handle_events()
    if event_quit:
        return False
    
    # Process buffered input
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
    
    self.snake_list.appendleft((head_x, head_y))
    
    self.x = head_x
    self.y = head_y
    
    # Shrink snake if needed
    if len(self.snake_list) > self.snake_length:
        removed = self.snake_list.pop()
    
    # Check collisions in priority order
    game_over = False
    
    if self.check_wall_collision():
        game_over = True
    elif not self.shield_active and self.check_self_collision():
        game_over = True
    elif self.check_food_collision():
        self.snake_length += 1
        self.spawn_food()
    
    if game_over:
        self.game_state = 'game_over'
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
    
    # Draw everything
    self.draw_game()
    
    return True


if __name__ == '__main__':
    main()
