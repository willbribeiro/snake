"""Test suite for snake.py.

Run with:  python -m unittest test_snake -v
Covers the exact crash scenarios that previously occurred (instant game
over on startup, frozen window) plus gameplay rules and persistence.
"""
import os
import tempfile
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')  # headless testing

import pygame  # noqa: E402

import config  # noqa: E402
import snake   # noqa: E402


def press(game, key):
    """Simulate a KEYDOWN event reaching the game."""
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))


def force_eat(game):
    """Place food exactly one cell ahead of the head, then step (snake eats)."""
    hx, hy = game.snake[0]
    game.food = (hx + game.snake_block, hy)
    game._step()


def run_until_game_over(game, max_steps=400):
    for _ in range(max_steps):
        if game.state != 'playing':
            return
        game._step()


class SnakeGameTest(unittest.TestCase):
    def setUp(self):
        # Isolate highscore.json writes inside a temp working directory.
        self._tmp = tempfile.TemporaryDirectory()
        self._old_cwd = os.getcwd()
        os.chdir(self._tmp.name)
        self.game = snake.SnakeGame()

    def tearDown(self):
        os.chdir(self._old_cwd)
        self._tmp.cleanup()

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
