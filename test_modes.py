"""Tests for the modes module (game mode definitions)."""
import unittest

import config
import modes


class ModesTest(unittest.TestCase):
    def test_labels_exist_for_every_configured_mode(self):
        for mode in config.GAME_MODES:
            self.assertIsInstance(modes.label(mode), str)
            self.assertTrue(modes.label(mode))

    def test_only_wrap_mode_wraps(self):
        self.assertFalse(modes.wraps('classic'))
        self.assertTrue(modes.wraps('wrap'))
        self.assertFalse(modes.wraps('maze'))

    def test_cycle_moves_forward(self):
        self.assertEqual(modes.cycle('classic', 1), 'wrap')
        self.assertEqual(modes.cycle('wrap', 1), 'maze')
        self.assertEqual(modes.cycle('maze', 1), 'classic')

    def test_cycle_moves_backward(self):
        self.assertEqual(modes.cycle('classic', -1), 'maze')
        self.assertEqual(modes.cycle('maze', -1), 'wrap')
        self.assertEqual(modes.cycle('wrap', -1), 'classic')

    def test_classic_has_no_obstacles(self):
        self.assertEqual(modes.obstacle_cells('classic'), frozenset())
        self.assertEqual(modes.obstacle_cells('wrap'), frozenset())

    def test_maze_obstacles_are_grid_aligned_and_leave_start_clear(self):
        cells = modes.obstacle_cells('maze')
        self.assertTrue(cells)
        for x, y in cells:
            self.assertEqual(x % config.BLOCK_SIZE, 0)
            self.assertEqual(y % config.BLOCK_SIZE, 0)
        # The snake spawns on the center row; it must be obstacle-free.
        center_row = config.SCREEN_HEIGHT // 2 // config.BLOCK_SIZE \
            * config.BLOCK_SIZE
        self.assertFalse(any(y == center_row for _, y in cells))

    def test_maze_obstacles_have_center_gap(self):
        cells = modes.obstacle_cells('maze')
        cx = config.SCREEN_WIDTH // 2 // config.BLOCK_SIZE * config.BLOCK_SIZE
        for dx in range(-5 * config.BLOCK_SIZE, 6 * config.BLOCK_SIZE,
                        config.BLOCK_SIZE):
            self.assertNotIn((cx + dx, 200), cells)
            self.assertNotIn((cx + dx, 400), cells)

    def test_obstacles_are_cached_immutable(self):
        self.assertIs(modes.obstacle_cells('maze'), modes.obstacle_cells('maze'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
