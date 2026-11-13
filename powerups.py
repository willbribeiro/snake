"""Power-up system for Snake Game."""

import config


class PowerUpManager:
    """Manages all power-up effects and spawning."""
    
    def __init__(self, game):
        self.game = game
        self.powerup_chance = config.POWERUP_CHANCE
        self.powerup_duration = config.POWERUP_DURATION
    
    def spawn_powerup(self):
        """Spawn a random power-up near food with specified chance."""
        import random
        
        if random.random() < self.powerup_chance:
            # Choose random powerup type (excluding shield for now)
            types = ['speed', 'length']
            powerup_type = random.choice(types)
            
            # Position powerup slightly offset from food
            powerup_x = self.game.food_x + self.game.snake_block // 2
            powerup_y = self.game.food_y - self.game.snake_block
            
            return (powerup_x, powerup_y, powerup_type)
        
        return None
    
    def activate_powerup(self, powerup_type):
        """Activate a power-up effect."""
        
        if powerup_type == 'speed':
            # Speed boost: increase speed by 30%
            self.game.speed = int(self.game.speed * 1.3)
            return True
        
        elif powerup_type == 'length':
            # Length bonus: add extra segments without eating food
            bonus_segments = 5
            for _ in range(bonus_segments):
                if len(self.game.snake_list) >= self.game.snake_length:
                    removed = self.game.snake_list.pop()
            
            return True
        
        elif powerup_type == 'shield':
            # Shield: temporary invincibility
            duration_frames = int(
                config.POWERUP_DURATION / (1000 / self.game.speed)
            )
            self.game.shield_active = True
            self.game.powerup_timer = duration_frames
            return True
        
        return False
    
    def check_powerup_collision(self):
        """Check if snake collided with a power-up."""
        head_x, head_y = self.game.snake_list[0]
        
        # Store last known powerup position (could be extended to support multiple)
        # For now, we'll use a simple approach - check for stored powerup
        
        return False
    
    def reset_powerups(self):
        """Reset all power-up states."""
        self.game.powerup_active = False
        self.game.shield_active = False
        if hasattr(self.game, 'powerup_timer'):
            self.game.powerup_timer = 0


def get_powerup_info(powerup_type):
    """Get information about a power-up type for display purposes."""
    
    info = {
        'speed': {
            'name': '⚡ Speed Boost',
            'description': f"Move faster! ({int(config.INITIAL_SPEED * 1.3)} FPS)",
            'duration': "2 seconds",
            'color': (255, 215, 0),  # Gold
        },
        'length': {
            'name': '+ Length',
            'description': "Grow extra segments instantly!",
            'duration': "Instant",
            'color': (138, 43, 226),  # Purple
        },
        'shield': {
            'name': '🛡️ Shield',
            'description': "Invincible for a few seconds!",
            'duration': config.POWERUP_DURATION // 1000,
            'color': (138, 255, 21),  # Lime green
        },
    }
    
    return info.get(powerup_type, {'name': 'Unknown', 'description': '', 'color': (255, 255, 255)})


def draw_powerup_indicator(dis, powerup_type, powerup_x, powerup_y):
    """Draw a visual indicator for an active power-up."""
    
    import pygame
    
    if powerup_type == 'shield' and powerup_active:
        # Draw shield icon/text
        shield_text = "🛡️"
        font = pygame.font.SysFont(None, 40)
        text_surface = font.render(shield_text, True, (255, 255, 255))
        
        # Draw glow effect
        glow_radius = 30
        pygame.draw.circle(
            dis, (138, 255, 21),
            (powerup_x + powerup_indicator_size // 2, 
             powerup_y + powerup_indicator_size // 2),
            glow_radius, 3
        )
        
        dis.blit(text_surface, (powerup_x, powerup_y))


# Power-up color scheme for food/powerups
POWERUP_COLORS = {
    'speed': (255, 215, 0),      # Gold/Yellow
    'length': (138, 43, 226),    # Purple
    'shield': (138, 255, 21),    # Lime Green
}
