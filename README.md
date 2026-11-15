# 🐍 Snake Game

A classic Snake game in Python + pygame-ce, focused on a small, robust,
fully tested codebase.

## Quick start

Requires Python 3.13+ (developed on 3.15).

```bash
pip install pygame-ce
python snake.py
```

Run the test suite:

```bash
python -m unittest test_snake -v
```

## Controls

| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` | Move |
| `Enter` / `Space` | Start game (menu) / Play again (game over) |
| `P` | Pause / Resume |
| `C` | Play again (game over) |
| `Q` | Back to menu (game over) |
| `Esc` | Quit |

## Features

- State machine: menu → playing ⇄ paused → game over
- Input buffering with reversal rejection (no unfair deaths from fast keys)
- Collision checks before movement — walls, self (tail cell is safe to enter)
- Food only spawns on free cells (never overlaps the snake or a power-up)
- Score, level, speed-up every 50 points, capped FPS
- High score persisted to `highscore.json` (tolerates corrupt files)
- Event loop always drains input and redraws — the window cannot freeze

### Power-ups

Eating food has a chance (20%, tunable) to also place one power-up on a free
cell; collect it with the snake's head for +20 points. At most one exists at
a time; food never spawns on its cell.

| Type | Effect | Color |
|------|--------|-------|
| Shield | Immune to self-collision for 50 steps (walls still kill) | Lime |
| Speed boost | +10 FPS for 50 steps (base speed untouched) | Gold |
| Length bonus | +5 segments instantly | Purple |

Timed effects tick down in game steps (FPS-independent) and show a HUD banner
while active.

### Visual effects

- Particle burst (green) when eating; particle burst in the power-up's color
  when collecting one
- Pulsing food with a shine at the bright phase; food turns red while the
  shield is active
- Head eyes that face the movement direction; subtle body gradient

## Project structure

```
snake/
├── snake.py          # game (entry point)
├── config.py         # all tunable constants
├── powerups.py       # power-up data (types, colors, labels)
├── particles.py      # deterministic particle effects
├── test_snake.py     # game tests
├── test_powerups.py  # power-up module tests
├── test_particles.py # particle module tests
├── highscore.json    # created at runtime
├── requirements.txt
├── INSTALL.md        # installation troubleshooting
├── CHANGELOG.md
└── LICENSE
```

## Configuration

All tuning lives in `config.py`: window size, grid block size, speeds
(`INITIAL_SPEED`, `SPEED_INCREMENT`, `MAX_SPEED`), scoring
(`POINTS_PER_FOOD`, `POINTS_PER_LEVEL`), input buffer size, power-ups
(`POWERUP_CHANCE`, `POWERUP_TYPES`, `SHIELD_STEPS`, `BOOST_STEPS`,
`SPEED_BOOST_AMOUNT`, `LENGTH_BONUS`, `POWERUP_POINTS`), and visual effect
tuning (`FOOD_PULSE_PERIOD`, `PARTICLE_COUNT`, `PARTICLE_LIFETIME`),
plus colors and fonts.

## Design notes

- The head **is** `snake[0]` — there is no separate position variable, so the
  head/body can never drift apart (the cause of an earlier "instant death" bug).
- Events are drained and the screen redrawn in every state, which is what makes
  the game-over screen responsive.
- Buffered direction changes are validated against the *live* direction at
  apply-time, so quick double-turns work but 180° reversals never kill.
