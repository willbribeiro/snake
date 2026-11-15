"""
Snake Game - Robust Version
===========================
Single source of truth: the head IS snake[0] (no separate x/y to drift apart).
One event loop that ALWAYS processes events and draws -> window can never freeze.

States: menu -> playing <-> paused -> game_over -> (menu | playing)
Controls: ENTER/SPACE start | Arrows move | P pause | C replay | Q menu | ESC quit

Run tests with:  python -m unittest test_snake -v
"""

import math
import random
from collections import deque

import pygame

import config
import particles
import powerups

pygame.init()

dis = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

font_large = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
font_medium = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
font_small = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)

DIRECTIONS = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}


class SnakeGame:
    def __init__(self, highscore_file=None):
        self.high_score_file = highscore_file or config.HIGHSCORE_FILE
        self.high_score = self._load_high_score()
        self._reset_to_menu()

    # ---------- persistence ----------
    def _load_high_score(self):
        try:
            with open(self.high_score_file) as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _save_high_score(self):
        try:
            with open(self.high_score_file, 'w') as f:
                f.write(str(self.high_score))
        except OSError:
            pass

    # ---------- state ----------
    def _init_run_stats(self):
        """Defaults shared by 'back to menu' and 'start a run'."""
        self.score = 0
        self.level = 1
        self.next_level = config.POINTS_PER_LEVEL
        self.speed = config.INITIAL_SPEED
        self.length = config.STARTING_LENGTH
        self.direction = (1, 0)
        self.pending = deque()   # buffered direction changes
        self.shield_steps = 0    # timed effects, measured in game steps
        self.boost_steps = 0
        self.powerup = None      # at most one on the board
        self.frame = 0           # drives food pulse animation
        self.particles = particles.ParticleManager()

    def _reset_to_menu(self):
        """Fresh object state. The game ALWAYS starts on the menu and waits."""
        self.state = 'menu'      # menu | playing | paused | game_over
        self.snake_block = config.BLOCK_SIZE
        self.snake = deque()     # head is snake[0]; single source of truth
        self.food = None
        self._init_run_stats()

    def start_run(self):
        """Begin a run: snake of aligned segments at the center, moving right."""
        self._init_run_stats()
        self.state = 'playing'
        blocks_x = config.SCREEN_WIDTH // self.snake_block
        blocks_y = config.SCREEN_HEIGHT // self.snake_block
        cx = blocks_x // 2 * self.snake_block
        cy = blocks_y // 2 * self.snake_block
        # Head first, then body cells BEHIND it (matching direction).
        self.snake = deque([
            (cx, cy),
            (cx - self.snake_block, cy),
            (cx - 2 * self.snake_block, cy),
        ])
        self.food = self._spawn_food()

    def _free_cells(self, exclude=()):
        """All grid cells not occupied by the snake (minus explicit excludes)."""
        occupied = set(self.snake)
        occupied.update(c for c in exclude if c is not None)
        return [
            (x, y)
            for x in range(0, config.SCREEN_WIDTH, self.snake_block)
            for y in range(0, config.SCREEN_HEIGHT, self.snake_block)
            if (x, y) not in occupied
        ]

    def _spawn_food(self):
        """Pick a random free cell - never on the snake or a power-up."""
        cells = self._free_cells(
            exclude=(self.powerup.cell,) if self.powerup else ())
        return random.choice(cells) if cells else None

    def _maybe_spawn_powerup(self):
        """After eating food, maybe place one power-up (never more than one)."""
        if self.powerup is not None:
            return
        if random.random() >= config.POWERUP_CHANCE:
            return
        cells = self._free_cells(exclude=(self.food,))
        if cells:
            self.powerup = powerups.PowerUp(powerups.pick_kind(),
                                            random.choice(cells))

    # ---------- update ----------
    def _apply_input(self):
        """Apply at most one buffered direction per step, rejecting reversals."""
        while self.pending:
            d = self.pending.popleft()
            if d == self.direction:
                continue
            if d[0] == -self.direction[0] and d[1] == -self.direction[1]:
                continue
            self.direction = d
            break

    def _step(self):
        # Timed effects tick down at the start of every step.
        if self.shield_steps:
            self.shield_steps -= 1
        if self.boost_steps:
            self.boost_steps -= 1

        self._apply_input()
        dx, dy = self.direction
        hx, hy = self.snake[0]
        nx, ny = hx + dx * self.snake_block, hy + dy * self.snake_block

        # 1. Wall collision (checked BEFORE moving - snake never leaves bounds)
        if nx < 0 or ny < 0 or nx >= config.SCREEN_WIDTH or ny >= config.SCREEN_HEIGHT:
            self._game_over()
            return

        # 2. Self collision. The tail cell vacates this step, so exclude it.
        #    An active shield grants immunity (walls still kill).
        if self.shield_steps <= 0 and (nx, ny) in set(list(self.snake)[:-1]):
            self._game_over()
            return

        # 3. Move (only after surviving the checks above)
        self.snake.appendleft((nx, ny))

        # 4. Food: grow, respawn, burst, maybe spawn a power-up, level up.
        if self.food is not None and (nx, ny) == self.food:
            self.score += config.POINTS_PER_FOOD
            self.length += 1
            self.food = self._spawn_food()
            self.particles.spawn_burst(nx + self.snake_block // 2,
                                       ny + self.snake_block // 2,
                                       config.GREEN)
            self._maybe_spawn_powerup()
            self._check_level_up()
        else:
            self.snake.pop()
            while len(self.snake) > self.length:
                self.snake.pop()

        # 5. Pick up a power-up if the head landed on it (after the tail
        #    bookkeeping above, so a length bonus lands on the final body).
        if self.powerup is not None and (nx, ny) == self.powerup.cell:
            pu, self.powerup = self.powerup, None
            self._apply_powerup(pu)

    def _apply_powerup(self, pu):
        """Apply a collected power-up's effect and reward."""
        self.score += config.POWERUP_POINTS
        b = self.snake_block
        if pu.kind == 'shield':
            self.shield_steps = config.SHIELD_STEPS
        elif pu.kind == 'speed':
            self.boost_steps = config.BOOST_STEPS
        elif pu.kind == 'length':
            self.length += config.LENGTH_BONUS
            tail = self.snake[-1]
            for _ in range(config.LENGTH_BONUS):
                self.snake.append(tail)   # duplicated tail spreads as snake moves
        self.particles.spawn_burst(pu.cell[0] + b // 2, pu.cell[1] + b // 2,
                                   powerups.color(pu.kind))
        self._check_level_up()

    def _check_level_up(self):
        """Level up whenever the score crosses the next threshold."""
        if self.score >= self.next_level:
            self.level += 1
            self.speed = min(self.speed + config.SPEED_INCREMENT,
                             config.MAX_SPEED)
            self.next_level += config.POINTS_PER_LEVEL

    def effective_speed(self):
        """FPS for the clock: base speed plus any active boost."""
        return self.speed + (config.SPEED_BOOST_AMOUNT
                             if self.boost_steps > 0 else 0)

    def _game_over(self):
        self.state = 'game_over'
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    # ---------- events ----------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.state = 'quit'
            return
        if event.type != pygame.KEYDOWN:
            return

        if self.state == 'menu':
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_run()
            elif event.key == pygame.K_ESCAPE:
                self.state = 'quit'
        elif self.state == 'playing':
            if event.key == pygame.K_p:
                self.state = 'paused'
            elif event.key in DIRECTIONS and len(self.pending) < config.INPUT_BUFFER_SIZE:
                self.pending.append(DIRECTIONS[event.key])
        elif self.state == 'paused':
            if event.key in (pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
                self.state = 'playing'
            elif event.key == pygame.K_ESCAPE:
                self.state = 'menu'
        elif self.state == 'game_over':
            if event.key in (pygame.K_c, pygame.K_RETURN, pygame.K_SPACE):
                self.start_run()
            elif event.key == pygame.K_q:
                self.state = 'menu'
            elif event.key == pygame.K_ESCAPE:
                self.state = 'quit'

    # ---------- draw ----------
    def draw(self):
        self.frame += 1              # drives the food pulse animation
        dis.fill(config.BACKGROUND_COLOR)
        if self.state == 'menu':
            self._draw_menu()
        elif self.state == 'playing':
            self._draw_playfield()
        elif self.state == 'paused':
            self._draw_playfield()
            self._center_text('PAUSED', font_large, config.WHITE, -40)
            self._center_text('Press P to resume', font_small, config.WHITE, 30)
        elif self.state == 'game_over':
            self._draw_playfield()
            self._center_text('GAME OVER', font_large, config.RED, -120)
            self._center_text(f'Final score: {self.score}   Level: {self.level}',
                              font_medium, config.WHITE, -40)
            self._center_text(f'High score: {self.high_score}',
                              font_medium, config.YELLOW, 10)
            self._center_text('C / ENTER - play again   Q - menu   ESC - quit',
                              font_small, config.WHITE, 70)
        pygame.display.update()

    def _draw_playfield(self):
        hud = font_medium.render(
            f'Score: {self.score}   Level: {self.level}', True, config.BLACK)
        dis.blit(hud, (5, 5))
        hs = font_small.render(
            f'High score: {self.high_score}', True, config.WHITE)
        dis.blit(hs, (config.SCREEN_WIDTH - hs.get_width() - 10,
                      config.SCREEN_HEIGHT - 30))

        # Food: pulsing size, shine at the bright phase; red while shielded.
        if self.food:
            fx, fy = self.food
            pulse = 2 * math.sin(2 * math.pi * self.frame
                                 / config.FOOD_PULSE_PERIOD)
            size = max(2, self.snake_block + int(round(pulse)))
            offset = (self.snake_block - size) // 2
            food_color = config.RED if self.shield_steps > 0 else config.GREEN
            pygame.draw.rect(dis, food_color,
                             [fx + offset, fy + offset, size, size])
            if size >= self.snake_block:         # bright phase -> shine
                pygame.draw.rect(dis, config.WHITE, [fx + 2, fy + 2, 2, 2])

        # Power-up waiting on the board.
        if self.powerup:
            px, py = self.powerup.cell
            pygame.draw.rect(dis, powerups.color(self.powerup.kind),
                             [px + 1, py + 1,
                              self.snake_block - 2, self.snake_block - 2])

        segs = list(self.snake)
        # Body with a subtle gradient (tail is lighter than the neck).
        for i in range(len(segs) - 1, 0, -1):
            x, y = segs[i]
            t = i / max(1, len(segs) - 1)
            gray = config.BODY_GRAY_MIN + int(
                (config.BODY_GRAY_MAX - config.BODY_GRAY_MIN) * t)
            pygame.draw.rect(dis, (gray, gray, gray),
                             [x, y, self.snake_block, self.snake_block])
        # Head with eyes that look where the snake is going.
        hx, hy = segs[0]
        pygame.draw.rect(dis, config.SNAKE_HEAD_COLOR,
                         [hx, hy, self.snake_block, self.snake_block])
        self._draw_eyes(hx, hy)

        # Banners for active timed effects.
        banner_y = 40
        for steps, kind in ((self.shield_steps, 'shield'),
                            (self.boost_steps, 'speed')):
            if steps > 0:
                surf = font_small.render(powerups.label(kind), True,
                                         powerups.color(kind))
                dis.blit(surf, (config.SCREEN_WIDTH // 2
                                - surf.get_width() // 2, banner_y))
                banner_y += 25

        self.particles.draw(dis)

    def _draw_eyes(self, hx, hy):
        b = self.snake_block
        cx, cy = hx + b // 2, hy + b // 2
        dx, dy = self.direction
        if dx != 0:
            offs = [(0, -b // 4), (0, b // 4)]
        else:
            offs = [(-b // 4, 0), (b // 4, 0)]
        for ox, oy in offs:
            ex, ey = cx + ox + dx * (b // 6), cy + oy + dy * (b // 6)
            pygame.draw.circle(dis, config.WHITE, (ex, ey), max(2, b // 8))
            pygame.draw.circle(dis, config.BLACK,
                               (ex + dx, ey + dy), max(1, b // 16))

    def _draw_menu(self):
        self._center_text('SNAKE GAME', font_large, config.GREEN, -120)
        self._center_text(f'High score: {self.high_score}',
                          font_medium, config.WHITE, -40)
        self._center_text('Press ENTER to start', font_medium, config.YELLOW, 40)
        self._center_text('Arrows: move   P: pause   ESC: quit',
                          font_small, config.WHITE, 110)

    def _center_text(self, text, font, color, y_offset):
        surf = font.render(text, True, color)
        dis.blit(surf, (config.SCREEN_WIDTH // 2 - surf.get_width() // 2,
                        config.SCREEN_HEIGHT // 2 - surf.get_height() // 2 + y_offset))

    # ---------- main loop ----------
    def run(self):
        running = True
        while running:
            # Events are ALWAYS drained, in EVERY state. The window can
            # never freeze, even on the game-over screen.
            for event in pygame.event.get():
                self.handle_event(event)

            if self.state == 'playing':
                self._step()

            self.particles.update()
            self.draw()  # drawn every frame, in every state

            if self.state == 'quit':
                running = False
            else:
                clock.tick(self.effective_speed() if self.state == 'playing'
                           else config.UI_FPS)

        pygame.quit()


def main():
    SnakeGame().run()


if __name__ == '__main__':
    main()
