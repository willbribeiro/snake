"""Enhanced snake class with visual polish features."""

import pygame


class VisualSnake:
    """Snake class with enhanced graphics and visual effects."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 10
        
        # Head details
        self.head_size = 8
        self.eyes_open = True
        self.eye_color = (255, 255, 255)
        
        # Body gradient
        self.body_gradient = True
        
    def draw_head(self, surface, direction):
        """Draw the snake head with directional eyes."""
        
        # Draw head body with rounded corners effect
        pygame.draw.rect(
            surface, (0, 0, 0),
            [self.x - 2, self.y - 2, self.width + 4, self.height + 4]
        )
        
        # Draw a lighter inner area for head detail
        pygame.draw.rect(
            surface, (20, 20, 20),
            [self.x - 1, self.y - 1, self.width + 2, self.height + 2]
        )
        
        # Position eyes based on direction
        eye_size = 3
        
        if direction == 'UP':
            eye_positions = [
                (self.x + 4, self.y + 3),
                (self.x + self.width - 5, self.y + 3)
            ]
            # Pupils looking up
            pupil_positions = [
                (self.x + 4, self.y + 1),
                (self.x + self.width - 5, self.y + 1)
            ]
            
        elif direction == 'DOWN':
            eye_positions = [
                (self.x + 4, self.y + self.height - 3),
                (self.x + self.width - 5, self.y + self.height - 3)
            ]
            pupil_positions = [
                (self.x + 4, self.y + self.height - 1),
                (self.x + self.width - 5, self.y + self.height - 1)
            ]
            
        elif direction == 'LEFT':
            eye_positions = [
                (self.x + 2, self.y + 4),
                (self.x + 2, self.y + self.height - 4)
            ]
            pupil_positions = [
                (self.x - 1, self.y + 4),
                (self.x - 1, self.y + self.height - 4)
            ]
            
        else:  # RIGHT
            eye_positions = [
                (self.x + self.width - 3, self.y + 4),
                (self.x + self.width - 3, self.y + self.height - 4)
            ]
            pupil_positions = [
                (self.x + self.width, self.y + 4),
                (self.x + self.width, self.y + self.height - 4)
            ]
        
        # Draw eyes (white sclera)
        for ex, ey in eye_positions:
            pygame.draw.circle(surface, (255, 255, 255), [ex, ey], eye_size)
        
        # Draw pupils (black)
        for px, py in pupil_positions:
            pygame.draw.circle(surface, (0, 0, 0), [px, py], eye_size // 2)
        
        # Add slight shine to eyes
        shine_pos = eye_positions[0]
        shine_x, shine_y = shine_pos[0] + 1, shine_pos[1] - 1
        pygame.draw.circle(surface, (255, 255, 255), [shine_x, shine_y], 1)
    
    def draw_body_segment(self, surface):
        """Draw a body segment with gradient effect."""
        
        # Base color (dark gray/black)
        base_color = (0, 0, 0)
        
        # Add slight variation based on position for subtle gradient
        if self.body_gradient:
            # Lighten segments slightly towards the tail
            intensity = 1 + (0.05 * len(self.segments))
            color = tuple(min(255, c * intensity) for c in base_color)
        else:
            color = base_color
        
        pygame.draw.rect(surface, color, 
                        [self.x - 1, self.y - 1, self.width + 2, self.height + 2])
    
    def draw_full(self, surface, segments):
        """Draw the entire snake with all visual effects."""
        
        # Draw body segments (excluding head)
        for i in range(len(segments) - 1, -1, -1):
            x, y = segments[i]
            
            if i == 0:
                # This is actually the head
                pass
            else:
                self.draw_body_segment(surface)
    
    def draw_head_with_segments(self, surface, segments, direction):
        """Draw snake with head and body segments."""
        
        # Draw body segments from tail to head-1 (in reverse order)
        for i in range(len(segments) - 1, 0, -1):
            x, y = segments[i]
            
            # Vary segment color based on position
            intensity = 0.7 + (0.3 * (i / len(segments)))
            base_color = (0, 0, 0)
            color = tuple(min(255, c * intensity) for c in base_color)
            
            pygame.draw.rect(surface, color, 
                           [x - 1, y - 1, self.width + 2, self.height + 2])
        
        # Draw head last (on top)
        self.draw_head(surface, direction)


# Visual effects constants
VISUAL_SETTINGS = {
    'head_eyes': True,          # Show eyes on snake head
    'body_gradient': True,       # Subtle gradient on body
    'food_shine': True,         # Shine effect on food
    'particle_effects': True,    # Enable particle effects
    
    # Particle settings
    'food_particles_count': 12,      # Particles when eating food
    'spark_particles_count': 6,      # Spark particles for variety
    
    # Animation settings
    'food_pulse_rate': 0.05,         # How fast food pulses
}
