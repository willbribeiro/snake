# Changelog

## 2.2 - 2026-11-14

### Added
- Power-up system (previously scaffolding-only, now fully integrated):
  - Spawns on a free cell when food is eaten (20% chance, max one on board);
    collected by the head for +20 points.
  - Shield: immune to self-collision for 50 steps (walls still kill).
  - Speed boost: +10 FPS for 50 steps; base level speed untouched, so
    level-ups remain correct.
  - Length bonus: +5 segments instantly (duplicated tail spreads as the
    snake moves).
  - HUD banners for active timed effects; food turns red while shielded.
  - Timers measured in game steps (FPS-independent, deterministic).
- Particle effects: burst on eating (green) and on power-up pickup
  (power-up color); deterministic per-particle physics.
- Food visuals: pulsing size animation with a shine at the bright phase.
- Level-ups now use a running threshold instead of `score % 50`, so
  power-up points can also trigger them correctly.
- Tests: 31 new (60 total) covering power-up spawning/pickup/expiry rules,
  particle lifecycle, visual state, and edge cases (board full, food None,
  1000-segment snake, key spam, rapid pause toggling).

### Changed
- Food spawning also excludes the power-up's cell; power-up spawning
  excludes food (items can never overlap).

## 2.1 - 2026-11-14

### Changed
- Code-quality pass:
  - Removed dead modules (`snake_v2`, `snake_main`, `snake_refactored`,
    `snake_enhanced`, `snake_melhorado`, `powerups`, `particles`,
    `visual_snake`) - none were imported by the game and several contained
    latent bugs (references to nonexistent attributes).
  - Removed stale documentation that described deleted features.
  - Extracted magic numbers into `config.py`: `POINTS_PER_FOOD`,
    `POINTS_PER_LEVEL`, `STARTING_LENGTH`, `INPUT_BUFFER_SIZE`, `UI_FPS`,
    `BODY_GRAY_MIN/MAX`, `HIGHSCORE_FILE`; renamed `MIN_SPEED` -> `MAX_SPEED`
    (same value, honest name).
  - Deduplicated run-state initialization (`_init_run_stats` shared by menu
    reset and `start_run`).
  - `SnakeGame` accepts an optional `highscore_file` path (aids testing;
    default unchanged).

### Added
- `test_snake.py`: 29 unit tests (headless) covering startup, menu wait,
  movement, eating, buffering/reversal, wall/self/tail collisions, level-up
  and speed cap, pause, game-over navigation, quit, high-score persistence,
  and draw-in-every-state.

## 2.0 - 2026-11-13

### Fixed
- Rewrote the game loop after crash reports:
  - Head is `snake[0]` (single source of truth) - fixes instant self-collision
    on the first movement step caused by position desync.
  - Events are drained and the screen drawn in every state - fixes the frozen,
    unresponsive game-over screen.
  - Menu only exits on user input - fixes the menu being skipped on frame one.
- Bug fixes retained from 1.x: empty-snake guards removed along with the
  rewrite; collision-before-move order; free-cell food spawning.

### Added
- Input buffering with reversal rejection.
- State machine (menu / playing / paused / game over), pause on `P`.
- High score persistence to `highscore.json`.
- Head eyes facing the movement direction, body gradient.

## 1.0 - 2026-11-13 (initial commits)

- Classic snake gameplay (arrow keys, food, growth, speed-up per level).
- Menu, game-over screen, high-score display.
