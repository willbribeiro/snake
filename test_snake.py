"""Test suite for snake.py.

Run with:  python -m unittest discover -v
Covers startup/state flow, movement, eating, buffering, collisions,
progression, pause, game over, persistence, power-ups, visuals, and
edge cases (board full, long snakes, input spam).
"""
import os
import tempfile
import unittest
from collections import deque
from unittest import mock

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')  # headless testing

import pygame  # noqa: E402

import config  # noqa: E402
import powerups  # noqa: E402
import snake   # noqa: E402


def press(game, key):
    """Simulate a KEYDOWN event reaching the game."""
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))


def force_eat(game):
    """Place food exactly one cell ahead of the head, then step (snake eats)."""
    hx, hy = game.snake[0]
    game.food = (hx + game.snake_block, hy)
    game._step()


def place_powerup_ahead(game, kind):
    """Put a power-up on the cell the head will enter next."""
    hx, hy = game.snake[0]
    dx, dy = game.direction
    cell = (hx + dx * game.snake_block, hy + dy * game.snake_block)
    game.powerup = powerups.PowerUp(kind, cell)
    return cell


def run_until_game_over(game, max_steps=400):
    for _ in range(max_steps):
        if game.state != 'playing':
            return
        game._step()


class GameTestBase(unittest.TestCase):
    def setUp(self):
        # Isolate highscore.json inside a temp working directory and
        # disable random power-up spawns by default (tests opt in).
        self._tmp = tempfile.TemporaryDirectory()
        self._old_cwd = os.getcwd()
        os.chdir(self._tmp.name)
        self._no_spawn = mock.patch('random.random', return_value=1.0)
        self._no_spawn.start()
        self.game = snake.SnakeGame()

    def tearDown(self):
        self._no_spawn.stop()
        os.chdir(self._old_cwd)
        self._tmp.cleanup()


class SnakeGameTest(GameTestBase):
    # ---------- startup / menu ----------

    def test_starts_on_menu_with_empty_snake(self):
        self.assertEqual(self.game.state, 'menu')
        self.assertEqual(len(self.game.snake), 0)

    def test_menu_persists_without_input(self):
        """Regression: game used to auto-transition to playing/game_over."""
        for _ in range(10):
            self.game.draw()
        self.assertEqual(self.game.state, 'menu')

    def test_enter_starts_run(self):
        press(self.game, pygame.K_RETURN)
        self.assertEqual(self.game.state, 'playing')

    def test_space_starts_run(self):
        press(self.game, pygame.K_SPACE)
        self.assertEqual(self.game.state, 'playing')

    def test_esc_on_menu_quits(self):
        press(self.game, pygame.K_ESCAPE)
        self.assertEqual(self.game.state, 'quit')

    # ---------- run initialization ----------

    def test_run_initial_layout(self):
        self.game.start_run()
        self.assertEqual(len(self.game.snake), config.STARTING_LENGTH)
        for x, y in self.game.snake:
            self.assertEqual(x % config.BLOCK_SIZE, 0)
            self.assertEqual(y % config.BLOCK_SIZE, 0)
        (hx, hy), (bx, by) = self.game.snake[0], self.game.snake[1]
        self.assertEqual((bx, by), (hx - config.BLOCK_SIZE, hy))
        self.assertEqual(self.game.direction, (1, 0))
        self.assertIsNotNone(self.game.food)
        self.assertNotIn(self.game.food, set(self.game.snake))

    def test_first_steps_survive_and_advance(self):
        """Regression: first movement step used to duplicate a body cell."""
        self.game.start_run()
        start = self.game.snake[0]
        for _ in range(5):
            self.game._step()
            self.assertEqual(self.game.state, 'playing')
        hx, hy = self.game.snake[0]
        self.assertEqual((hx, hy),
                         (start[0] + 5 * config.BLOCK_SIZE, start[1]))

    # ---------- eating ----------

    def test_eating_scores_grows_and_respawns_food(self):
        self.game.start_run()
        force_eat(self.game)
        self.assertEqual(self.game.score, config.POINTS_PER_FOOD)
        self.assertEqual(len(self.game.snake), config.STARTING_LENGTH + 1)
        self.assertIsNotNone(self.game.food)
        self.assertNotIn(self.game.food, set(self.game.snake))

    def test_food_never_spawns_on_snake(self):
        self.game.start_run()
        for _ in range(20):
            self.game.food = self.game._spawn_food()
            self.assertNotIn(self.game.food, set(self.game.snake))

    # ---------- input buffering ----------

    def test_reversal_rejected(self):
        self.game.start_run()
        press(self.game, pygame.K_LEFT)          # reverse of RIGHT
        self.game._step()
        self.assertEqual(self.game.direction, (1, 0))
        self.assertEqual(self.game.state, 'playing')

    def test_buffered_double_turn_applies_over_two_steps(self):
        self.game.start_run()
        press(self.game, pygame.K_UP)            # RIGHT -> UP
        press(self.game, pygame.K_LEFT)          # UP -> LEFT
        self.game._step()
        self.assertEqual(self.game.direction, (0, -1))
        self.game._step()
        self.assertEqual(self.game.direction, (-1, 0))
        self.assertEqual(self.game.state, 'playing')

    def test_buffer_capped(self):
        self.game.start_run()
        for key in (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN):
            press(self.game, key)
        self.assertEqual(len(self.game.pending), config.INPUT_BUFFER_SIZE)

    # ---------- collisions ----------

    def test_wall_collision_ends_run_and_saves_high_score(self):
        self.game.start_run()
        force_eat(self.game)                     # score 10 so it is saved
        self.game.food = (0, 0)                  # never on the snake's path
        run_until_game_over(self.game)
        self.assertEqual(self.game.state, 'game_over')
        self.assertEqual(self.game.high_score, config.POINTS_PER_FOOD)
        with open(self.game.high_score_file) as f:
            self.assertEqual(f.read().strip(),
                             str(config.POINTS_PER_FOOD))

    def test_self_collision_ends_run(self):
        self.game.start_run()
        # Head runs into its own body: head at (130,100) moving LEFT,
        # second segment at (120,100).
        self.game.snake.clear()
        self.game.snake.extend([(130, 100), (120, 100), (110, 100), (100, 100)])
        self.game.direction = (-1, 0)
        self.game.food = (0, 0)
        self.game._step()
        self.assertEqual(self.game.state, 'game_over')

    def test_tail_cell_is_safe_to_enter(self):
        """The tail vacates this step, so moving into it must not kill."""
        self.game.start_run()
        self.game.snake.clear()
        self.game.snake.extend([(130, 100), (110, 100), (120, 100)])
        self.game.direction = (-1, 0)
        self.game.food = (0, 0)
        self.game._step()
        self.assertEqual(self.game.state, 'playing')
        self.assertEqual(self.game.snake[0], (120, 100))

    # ---------- progression ----------

    def test_level_up_and_speed_increase_at_threshold(self):
        self.game.start_run()
        for _ in range(config.POINTS_PER_LEVEL // config.POINTS_PER_FOOD):
            force_eat(self.game)
        self.assertEqual(self.game.score, config.POINTS_PER_LEVEL)
        self.assertEqual(self.game.level, 2)
        self.assertEqual(self.game.speed,
                         config.INITIAL_SPEED + config.SPEED_INCREMENT)

    def test_speed_capped(self):
        self.game.start_run()
        self.game.speed = config.MAX_SPEED - 1
        self.game.score = config.POINTS_PER_LEVEL - config.POINTS_PER_FOOD
        force_eat(self.game)                     # crosses the threshold
        self.assertEqual(self.game.speed, config.MAX_SPEED)

    # ---------- pause ----------

    def test_pause_and_resume(self):
        self.game.start_run()
        press(self.game, pygame.K_p)
        self.assertEqual(self.game.state, 'paused')
        press(self.game, pygame.K_p)
        self.assertEqual(self.game.state, 'playing')

    def test_enter_and_space_resume_from_pause(self):
        for key in (pygame.K_RETURN, pygame.K_SPACE):
            self.game.start_run()
            press(self.game, pygame.K_p)
            press(self.game, key)
            self.assertEqual(self.game.state, 'playing')

    def test_esc_from_pause_returns_to_menu(self):
        self.game.start_run()
        press(self.game, pygame.K_p)
        press(self.game, pygame.K_ESCAPE)
        self.assertEqual(self.game.state, 'menu')
        press(self.game, pygame.K_RETURN)        # fresh run from menu
        self.assertEqual(self.game.state, 'playing')
        self.assertEqual(self.game.score, 0)
        self.assertEqual(len(self.game.snake), config.STARTING_LENGTH)

    # ---------- game over screen ----------

    def _reach_game_over(self):
        self.game.start_run()
        force_eat(self.game)
        self.game.food = (0, 0)
        run_until_game_over(self.game)
        self.assertEqual(self.game.state, 'game_over')

    def test_c_restarts_from_game_over(self):
        self._reach_game_over()
        press(self.game, pygame.K_c)
        self.assertEqual(self.game.state, 'playing')
        self.assertEqual(self.game.score, 0)
        self.assertEqual(len(self.game.snake), config.STARTING_LENGTH)

    def test_enter_restarts_from_game_over(self):
        self._reach_game_over()
        press(self.game, pygame.K_RETURN)
        self.assertEqual(self.game.state, 'playing')

    def test_q_returns_to_menu_from_game_over(self):
        self._reach_game_over()
        press(self.game, pygame.K_q)
        self.assertEqual(self.game.state, 'menu')

    def test_esc_quits_from_game_over(self):
        self._reach_game_over()
        press(self.game, pygame.K_ESCAPE)
        self.assertEqual(self.game.state, 'quit')

    # ---------- quitting ----------

    def test_quit_event(self):
        self.game.handle_event(pygame.event.Event(pygame.QUIT))
        self.assertEqual(self.game.state, 'quit')

    # ---------- high score persistence ----------

    def test_high_score_loaded_from_file(self):
        with open('highscore.json', 'w') as f:
            f.write('42')
        game = snake.SnakeGame()
        self.assertEqual(game.high_score, 42)

    def test_corrupt_high_score_file_defaults_to_zero(self):
        with open('highscore.json', 'w') as f:
            f.write('not-a-number')
        game = snake.SnakeGame()
        self.assertEqual(game.high_score, 0)

    def test_high_score_never_lowered(self):
        self._reach_game_over()                  # saves 10
        game = snake.SnakeGame()
        self.assertEqual(game.high_score, config.POINTS_PER_FOOD)
        game.start_run()
        game.food = (0, 0)                       # die with score 0
        run_until_game_over(game)
        self.assertEqual(game.state, 'game_over')
        self.assertEqual(game.high_score, config.POINTS_PER_FOOD)
        with open('highscore.json') as f:
            self.assertEqual(f.read().strip(), str(config.POINTS_PER_FOOD))

    # ---------- rendering ----------

    def test_draw_does_not_crash_in_every_state(self):
        self.game.draw()                         # menu
        self.game.start_run()
        self.game.draw()                         # playing
        press(self.game, pygame.K_p)
        self.game.draw()                         # paused
        press(self.game, pygame.K_p)
        self._reach_game_over()
        self.game.draw()                         # game over


class PowerUpTest(GameTestBase):
    # ---------- spawning ----------

    def test_no_powerup_on_fresh_run(self):
        self.game.start_run()
        self.assertIsNone(self.game.powerup)
        self.assertEqual(self.game.shield_steps, 0)
        self.assertEqual(self.game.boost_steps, 0)

    def test_powerup_spawns_on_eating_when_roll_hits(self):
        with mock.patch('random.random', return_value=0.0):
            self.game.start_run()
            force_eat(self.game)
        self.assertIsNotNone(self.game.powerup)
        cell = self.game.powerup.cell
        self.assertIn(self.game.powerup.kind, config.POWERUP_TYPES)
        self.assertNotIn(cell, set(self.game.snake))
        self.assertNotEqual(cell, self.game.food)

    def test_no_powerup_spawn_when_roll_misses(self):
        # setUp patches random.random -> 1.0 (always miss)
        self.game.start_run()
        force_eat(self.game)
        self.assertIsNone(self.game.powerup)

    def test_only_one_powerup_on_board(self):
        with mock.patch('random.random', return_value=0.0):
            self.game.start_run()
            force_eat(self.game)
            self.game.powerup.cell = (0, 0)      # pin it off the snake's path
            first = self.game.powerup.cell
            force_eat(self.game)                 # would roll again
        self.assertEqual(self.game.powerup.cell, first)

    def test_powerup_never_spawns_on_food_or_snake(self):
        with mock.patch('random.random', return_value=0.0):
            self.game.start_run()
            for _ in range(10):
                force_eat(self.game)
                if self.game.powerup:
                    self.assertNotIn(self.game.powerup.cell,
                                     set(self.game.snake))
                    self.assertNotEqual(self.game.powerup.cell,
                                        self.game.food)
                    # keep it off the snake's straight-line path
                    self.game.powerup.cell = (0, 0)

    # ---------- shield ----------

    def test_shield_pickup_activates_and_scores(self):
        self.game.start_run()
        self.game.food = (0, 0)                  # keep the path food-free
        place_powerup_ahead(self.game, 'shield')
        self.game._step()
        self.assertEqual(self.game.shield_steps, config.SHIELD_STEPS)
        self.assertEqual(self.game.score, config.POWERUP_POINTS)
        self.assertIsNone(self.game.powerup)

    def test_shield_prevents_self_collision_death(self):
        self.game.start_run()
        self.game.snake.clear()
        self.game.snake.extend([(130, 100), (120, 100), (110, 100), (100, 100)])
        self.game.direction = (-1, 0)
        self.game.food = (0, 0)
        self.game.shield_steps = 2
        self.game._step()                        # head enters (120,100)
        self.assertEqual(self.game.state, 'playing')
        self.assertEqual(self.game.snake[0], (120, 100))
        self.assertEqual(self.game.shield_steps, 1)

    def test_shield_expires(self):
        self.game.start_run()
        self.game.shield_steps = 1
        self.game.food = (0, 0)
        self.game._step()                        # timer reaches 0
        self.assertEqual(self.game.shield_steps, 0)
        # Now the same self-collision setup is fatal again.
        self.game.snake.clear()
        self.game.snake.extend([(130, 100), (120, 100), (110, 100), (100, 100)])
        self.game.direction = (-1, 0)
        self.game._step()
        self.assertEqual(self.game.state, 'game_over')

    def test_shield_does_not_prevent_wall_death(self):
        self.game.start_run()
        force_eat(self.game)
        self.game.food = (0, 0)
        self.game.shield_steps = 999
        run_until_game_over(self.game)
        self.assertEqual(self.game.state, 'game_over')

    # ---------- speed boost ----------

    def test_speed_pickup_boosts_effective_speed_only(self):
        self.game.start_run()
        self.game.food = (0, 0)
        base = self.game.speed
        place_powerup_ahead(self.game, 'speed')
        self.game._step()
        self.assertEqual(self.game.boost_steps, config.BOOST_STEPS)
        self.assertEqual(self.game.effective_speed(),
                         base + config.SPEED_BOOST_AMOUNT)
        self.assertEqual(self.game.speed, base)  # base untouched

    def test_speed_boost_expires(self):
        self.game.start_run()
        base = self.game.speed
        self.game.boost_steps = 1
        self.game.food = (0, 0)
        self.game._step()
        self.assertEqual(self.game.boost_steps, 0)
        self.assertEqual(self.game.effective_speed(), base)

    # ---------- length bonus ----------

    def test_length_bonus_instantly_adds_segments(self):
        self.game.start_run()
        self.game.food = (0, 0)
        before = len(self.game.snake)
        place_powerup_ahead(self.game, 'length')
        self.game._step()
        self.assertEqual(self.game.length, before + config.LENGTH_BONUS)
        self.assertEqual(len(self.game.snake), before + config.LENGTH_BONUS)
        self.assertEqual(self.game.state, 'playing')

    def test_powerup_points_can_trigger_level_up(self):
        self.game.start_run()
        self.game.score = config.POINTS_PER_LEVEL - config.POWERUP_POINTS
        self.game.food = (0, 0)
        place_powerup_ahead(self.game, 'shield')
        self.game._step()                        # score crosses the threshold
        self.assertEqual(self.game.level, 2)
        self.assertEqual(self.game.next_level,
                         2 * config.POINTS_PER_LEVEL)

    # ---------- rendering ----------

    def test_draw_with_active_powerup_and_effects(self):
        self.game.start_run()
        place_powerup_ahead(self.game, 'shield')
        self.game.shield_steps = 5
        self.game.boost_steps = 5
        self.game.draw()                         # must not raise


class VisualTest(GameTestBase):
    def test_particles_spawned_on_eating(self):
        self.game.start_run()
        force_eat(self.game)
        self.assertEqual(len(self.game.particles.particles),
                         config.PARTICLE_COUNT)

    def test_particles_cleared_on_new_run(self):
        self.game.start_run()
        force_eat(self.game)
        press(self.game, pygame.K_p)             # pause -> menu -> restart
        press(self.game, pygame.K_ESCAPE)
        press(self.game, pygame.K_RETURN)
        self.assertEqual(len(self.game.particles.particles), 0)

    def test_frame_counter_advances_on_draw(self):
        self.game.start_run()
        self.assertEqual(self.game.frame, 0)
        self.game.draw()
        self.game.draw()
        self.assertEqual(self.game.frame, 2)


class EdgeCaseTest(GameTestBase):
    def test_board_full_food_is_none_and_no_powerup(self):
        self.game.start_run()
        cells = [(x, y)
                 for x in range(0, config.SCREEN_WIDTH, config.BLOCK_SIZE)
                 for y in range(0, config.SCREEN_HEIGHT, config.BLOCK_SIZE)]
        self.game.snake = deque(cells)
        self.game.food = None
        self.assertIsNone(self.game._spawn_food())
        with mock.patch('random.random', return_value=0.0):
            self.game._maybe_spawn_powerup()
        self.assertIsNone(self.game.powerup)

    def test_playing_survives_food_none(self):
        self.game.start_run()
        self.game.food = None
        for _ in range(3):
            self.game._step()
        self.assertEqual(self.game.state, 'playing')

    def test_long_snake_draw_does_not_crash(self):
        self.game.start_run()
        cells = [(10 * (i % 79), 10 * (i % 59)) for i in range(1000)]
        self.game.snake = deque(cells)
        self.game.draw()

    def test_key_spam_capped_and_survivable(self):
        self.game.start_run()
        for i in range(100):
            press(self.game, pygame.K_UP if i % 2 else pygame.K_DOWN)
        self.assertLessEqual(len(self.game.pending), config.INPUT_BUFFER_SIZE)
        for _ in range(5):
            self.game._step()
        self.assertEqual(self.game.state, 'playing')

    def test_rapid_pause_toggling(self):
        self.game.start_run()
        for _ in range(40):
            press(self.game, pygame.K_p)
        self.assertEqual(self.game.state, 'playing')   # even toggles
        press(self.game, pygame.K_p)
        self.assertEqual(self.game.state, 'paused')
        press(self.game, pygame.K_p)
        self.assertEqual(self.game.state, 'playing')


if __name__ == '__main__':
    unittest.main(verbosity=2)
