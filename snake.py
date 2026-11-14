"""
Snake Game - Robust Version
===========================
Single source of truth: the head IS snake[0] (no separate x/y to drift apart).
One event loop that ALWAYS processes events and draws -> window can never freeze.

States: menu -> playing <-> paused -> game_over -> (menu | playing)
Controls: ENTER/SPACE start | Arrows move | P pause | C replay | Q menu | ESC quit
"""

import json
import random
from collections import deque

import pygame

import config

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
    def __init__(self):
        self.high_score_file = 'highscore.json'
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
    def _reset_to_menu(self):
        """Fresh object state. The game ALWAYS starts on the menu and waits."""
        self.state = 'menu'      # menu | playing | paused | game_over
        self.score = 0
        self.level = 1
        self.speed = config.INITIAL_SPEED
        self.snake_block = config.BLOCK_SIZE
        self.snake = deque()     # head is snake[0]; single source of truth
        self.length = 3
        self.direction = (1, 0)
        self.pending = deque()   # buffered direction changes
        self.food = None

    def start_run(self):
        """Begin a run: snake of 3 aligned segments at the center, moving right."""
        self.state = 'playing'
        self.score = 0
        self.level = 1
        self.speed = config.INITIAL_SPEED
        self.length = 3
        blocks_x = config.SCREEN_WIDTH // self.snake_block
        blocks_y = config.SCREEN_HEIGHT // self.snake_block
        cx = blocks_x // 2 * self.snake_block
        cy = blocks_y // 2 * self.snake_block
        # Head first, then two body cells BEHIND it (matching direction).
        self.snake = deque([
            (cx, cy),
            (cx - self.snake_block, cy),
            (cx - 2 * self.snake_block, cy),
        ])
        self.direction = (1, 0)
        self.pending.clear()
        self.food = self._spawn_food()

    def _spawn_food(self):
        """Pick a random free cell - can never land on the snake."""
        occupied = set(self.snake)
        cells = [
            (x, y)
            for x in range(0, config.SCREEN_WIDTH, self.snake_block)
            for y in range(0, config.SCREEN_HEIGHT, self.snake_block)
            if (x, y) not in occupied
        ]
        return random.choice(cells) if cells else None

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
        self._apply_input()
        dx, dy = self.direction
        hx, hy = self.snake[0]
        nx, ny = hx + dx * self.snake_block, hy + dy * self.snake_block

        # 1. Wall collision (checked BEFORE moving - snake never leaves bounds)
        if nx < 0 or ny < 0 or nx >= config.SCREEN_WIDTH or ny >= config.SCREEN_HEIGHT:
            self._game_over()
            return

        # 2. Self collision. The tail cell vacates this step, so exclude it.
        if (nx, ny) in set(list(self.snake)[:-1]):
            self._game_over()
            return

        # 3. Move (only after surviving the checks above)
        self.snake.appendleft((nx, ny))
        if self.food is not None and (nx, ny) == self.food:
            self.score += 10
            self.length += 1
            self.food = self._spawn_food()
            if self.score % 50 == 0:
                self.level += 1
                self.speed = min(self.speed + config.SPEED_INCREMENT,
                                 config.MIN_SPEED)
        else:
            self.snake.pop()
            while len(self.snake) > self.length:
                self.snake.pop()

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
            elif event.key in DIRECTIONS and len(self.pending) < 2:
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

        if self.food:
            pygame.draw.rect(dis, config.GREEN,
                             [self.food[0], self.food[1],
                              self.snake_block, self.snake_block])

        segs = list(self.snake)
        # Body with a subtle gradient (tail is lighter than the neck).
        for i in range(len(segs) - 1, 0, -1):
            x, y = segs[i]
            t = i / max(1, len(segs) - 1)
            c = 15 + int(55 * t)
            pygame.draw.rect(dis, (c, c, c),
                             [x, y, self.snake_block, self.snake_block])
        # Head with eyes that look where the snake is going.
        hx, hy = segs[0]
        pygame.draw.rect(dis, config.SNAKE_COLORS['head'],
                         [hx, hy, self.snake_block, self.snake_block])
        self._draw_eyes(hx, hy)

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

            self.draw()  # drawn every frame, in every state

            if self.state == 'quit':
                running = False
            else:
                clock.tick(self.speed if self.state == 'playing' else 30)

        pygame.quit()


def main():
    SnakeGame().run()


if __name__ == '__main__':
    main()
