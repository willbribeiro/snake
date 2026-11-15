"""Tests for the powerups module."""
import random
import unittest

import config
import powerups


class PowerUpModuleTest(unittest.TestCase):
    def test_pick_kind_returns_known_type(self):
        for seed in range(20):
            random.seed(seed)
            self.assertIn(powerups.pick_kind(), config.POWERUP_TYPES)

    def test_info_tables_cover_every_configured_type(self):
        for kind in config.POWERUP_TYPES:
            color = powerups.color(kind)
            label = powerups.label(kind)
            self.assertIsInstance(color, tuple)
            self.assertEqual(len(color), 3)
            for c in color:
                self.assertTrue(0 <= c <= 255)
            self.assertIsInstance(label, str)
            self.assertTrue(label)

    def test_powerup_stores_kind_and_cell(self):
        pu = powerups.PowerUp('shield', (100, 200))
        self.assertEqual(pu.kind, 'shield')
        self.assertEqual(pu.cell, (100, 200))


if __name__ == '__main__':
    unittest.main(verbosity=2)
