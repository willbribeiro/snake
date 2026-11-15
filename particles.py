"""Deterministic particle effects for eating and power-up pickups.

Each particle has fixed velocity and lifetime; the manager advances them
once per frame and removes expired ones. Randomness is confined to burst
spawning (tests seed the RNG or construct particles directly).
"""

import math
import random

import pygame

import config


class Particle:
    """A single fading dot moving in a straight line."""

    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'age', 'lifetime')

    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1

    @property
    def alive(self):
        return self.age < self.lifetime

    def draw(self, surface):
        t = self.age / self.lifetime
        radius = max(1, int(3 * (1 - t)))          # shrink as it fades
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), radius)


class ParticleManager:
    """Owns all live particles and spawns bursts."""

    def __init__(self):
        self.particles = []

    def spawn_burst(self, x, y, color, count=None):
        """Spawn `count` particles flying outward from (x, y)."""
        if count is None:
            count = config.PARTICLE_COUNT
        for i in range(count):
            angle = 2 * math.pi * i / count + random.uniform(-0.3, 0.3)
            speed = random.uniform(1.0, 3.0)
            self.particles.append(Particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                lifetime=random.randint(config.PARTICLE_LIFETIME // 2,
                                        config.PARTICLE_LIFETIME),
            ))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
