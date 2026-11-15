"""Tests for the particles module (deterministic physics)."""
import random
import unittest

import config
from particles import Particle, ParticleManager


class ParticleTest(unittest.TestCase):
    def test_moves_by_velocity_each_update(self):
        p = Particle(10, 20, vx=3, vy=-2, color=(255, 0, 0), lifetime=5)
        p.update()
        self.assertEqual((p.x, p.y), (13, 18))
        self.assertEqual(p.age, 1)

    def test_dies_at_end_of_lifetime(self):
        p = Particle(0, 0, vx=1, vy=1, color=(0, 0, 0), lifetime=3)
        self.assertTrue(p.alive)
        p.update(); p.update()
        self.assertTrue(p.alive)
        p.update()
        self.assertFalse(p.alive)


class ParticleManagerTest(unittest.TestCase):
    def setUp(self):
        random.seed(42)  # deterministic bursts

    def test_burst_creates_requested_count(self):
        m = ParticleManager()
        m.spawn_burst(100, 100, (0, 255, 0), count=config.PARTICLE_COUNT)
        self.assertEqual(len(m.particles), config.PARTICLE_COUNT)
        self.assertTrue(all(p.alive for p in m.particles))

    def test_update_removes_dead_particles(self):
        m = ParticleManager()
        m.spawn_burst(0, 0, (0, 255, 0), count=5)
        for _ in range(config.PARTICLE_LIFETIME):
            m.update()
        self.assertEqual(len(m.particles), 0)

    def test_update_keeps_alive_particles(self):
        m = ParticleManager()
        m.spawn_burst(0, 0, (0, 255, 0), count=5)
        m.update()
        self.assertTrue(len(m.particles) > 0)

    def test_draw_does_not_crash(self):
        import pygame
        import os
        os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        pygame.init()
        surf = pygame.display.set_mode((100, 100))
        m = ParticleManager()
        m.spawn_burst(50, 50, (255, 255, 255), count=4)
        m.update()
        m.draw(surf)  # must not raise


if __name__ == '__main__':
    unittest.main(verbosity=2)
