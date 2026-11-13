"""Particle system for visual effects."""

import pygame
import random


class Particle:
    """Represents a single particle for visual effects."""
    
    def __init__(self, x, y, color, speed=3, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.lifetime = lifetime
        self.age = 0
        self.direction = random.uniform(0, 1) * 3.14 * 2
        
    def update(self):
        """Update particle position and age."""
        # Move outward in a circular pattern
        angle_offset = (self.direction - random.uniform(0, 1)) * 0.5
        self.x += pygame.math.Vector2(
            pygame.math.Vector2(1, 0).rotate(angle_offset)
        ).x * self.speed
        self.y += pygame.math.Vector2(1, 0).rotate(angle_offset + 1.57).y * self.speed
        
        self.age += 1
    
    def is_alive(self):
        """Check if particle is still alive."""
        return self.age < self.lifetime
    
    def draw(self, surface):
        """Draw the particle."""
        size = max(1, 6 - (self.age / self.lifetime) * 6)
        pygame.draw.circle(surface, self.color, 
                          (int(self.x), int(self.y)), int(size))


class ParticleManager:
    """Manages all particles for visual effects."""
    
    def __init__(self):
        self.particles = []
        self.food_particles = []
        self.speed_boost_trail = []
    
    def spawn_food_particles(self, x, y, color=(0, 255, 0)):
        """Spawn particles when food is eaten."""
        # Create burst of particles
        for _ in range(12):
            angle = random.uniform(0, 3.14 * 2)
            speed = random.uniform(2, 5)
            
            particle = Particle(
                x + self.snake_block // 2,
                y + self.snake_block // 2,
                color,
                speed=speed,
                lifetime=random.randint(15, 30)
            )
            self.food_particles.append(particle)
        
        # Add some white/gold sparks
        for _ in range(6):
            particle = Particle(
                x + random.randint(-5, 15),
                y + random.randint(-5, 15),
                (255, 215, 0) if random.random() < 0.7 else (255, 255, 255),
                speed=random.uniform(3, 6),
                lifetime=random.randint(10, 25)
            )
            self.food_particles.append(particle)
    
    def spawn_speed_trail(self):
        """Spawn trail particles for speed boost effect."""
        # Add some blue/cyan trail particles
        for i in range(5):
            x_offset = random.randint(-3, 10)
            y_offset = random.randint(-3, 10)
            
            particle = Particle(
                self.head_x + x_offset,
                self.head_y + y_offset,
                (80, 200, 255),  # Light blue
                speed=2,
                lifetime=random.randint(15, 25)
            )
            self.speed_boost_trail.append(particle)
    
    def update(self):
        """Update all particles."""
        # Update food particles
        self.food_particles = [p for p in self.food_particles if p.is_alive()]
        for particle in self.food_particles:
            particle.update()
        
        # Update speed boost trail
        self.speed_boost_trail = [p for p in self.speed_boost_trail if p.is_alive()]
        for particle in self.speed_boost_trail:
            particle.update()
    
    def draw(self, surface):
        """Draw all particles."""
        # Draw food particles first (behind snake)
        for particle in self.food_particles:
            particle.draw(surface)
        
        # Draw speed boost trail
        for particle in self.speed_boost_trail:
            particle.draw(surface)


# Color palettes for different effects
FOOD_PARTICLE_COLORS = {
    'green': (0, 255, 0),
    'gold': (255, 215, 0),
    'white': (255, 255, 255),
    'red': (255, 80, 80),
}

SPEED_BOOST_COLORS = [
    (80, 200, 255),   # Light blue
    (100, 220, 255),  # Medium blue
    (50, 180, 230),   # Cyan
]

SHIELD_COLORS = [
    (138, 255, 21),   # Lime green
    (154, 200, 50),   # Gold-ish green
]
