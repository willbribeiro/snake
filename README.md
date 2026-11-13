# 🐍 Snake Game - Improved Version

A classic Snake game rewritten with modern features and improved architecture using Python and Pygame.

![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)

## ✨ Features (Phase 1 - Completed)

### Core Improvements
- ✅ **Input Buffering System** - Prevents "quick death" from rapid key presses
- ✅ **State Management** - Clean separation between Menu, Playing, Paused, and Game Over states
- ✅ **High Score Persistence** - Saves and loads your best score to `highscore.json`
- ✅ **Score & Level Display** - HUD showing current score, level, and high score
- ✅ **Pause Functionality** - Press `P` key anytime during gameplay to pause/resume
- ✅ **Anti-Reversal Protection** - Can't reverse direction instantly (prevents accidental self-collision)
- ✅ **Food Spawn Protection** - Food never spawns on the snake body

### Enhanced User Interface
- 🎨 **Main Menu Screen** - Attractive title with high score display
- 🎮 **Game Over Screen** - Shows final score, level reached, and restart options
- ⏸️ **Pause Overlay** - Clean pause screen with resume instructions
- 📊 **Score HUD** - Persistent on-screen display during gameplay

## 🚀 Quick Start

### Installation
1. Make sure you have Python 3.7+ installed
2. Install Pygame:
   ```bash
   pip install pygame
   ```

### Running the Game
```bash
python snake.py
```

Or if using pip package format:
```bash
pip install -e .
python -m snake
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `↑` / `W` | Move Up |
| `↓` / `S` | Move Down |
| `→` / `D` | Move Right |
| `←` / `A` | Move Left |
| `P` | Pause/Resume Game |
| `Enter` / `Space` | Start Game (from Menu) |
| `C` | Continue (from Game Over) |
| `Q` | Quit Game |

## 📁 Project Structure

```
snake/
├── snake.py              # Main game file (refactored with all Phase 1 features)
├── config.py             # Game constants and settings
├── snake_main.py         # Alternative refactored version (for reference)
├── snake_melhorado.py    # Original improved version (legacy)
├── highscore.json        # Persisted high scores
└── README.md             # This file
```

## 🎯 How to Play

1. The snake starts in the middle of the screen
2. Use arrow keys to change direction
3. Eat the green food blocks to grow and increase your score
4. Every 50 points, you level up and speed increases!
5. Avoid hitting your own tail or the walls
6. Beat your high score! 🏆

## ⚙️ Configuration (config.py)

All game settings are in `config.py`:

- **Screen Size**: 800x600 pixels
- **Block Size**: 10 pixels per snake segment
- **Initial Speed**: 15 FPS
- **Speed Increment**: +5 FPS per level
- **Max Speed Cap**: 40 FPS
- **Power-up Spawn Chance**: 5%

You can modify these values to customize the game difficulty!

## 🔮 Roadmap - Upcoming Features (Future Phases)

### Phase 2: Visual Polish
- [ ] Snake head with directional eyes
- [ ] Animated food effects
- [ ] Particle effects when eating
- [ ] Better color schemes and gradients

### Phase 3: Power-Up System
- [ ] Speed Boost power-up
- [ ] Shield/Invincibility power-up
- [ ] Length Bonus items
- [ ] Magnet food attractor

### Phase 4: Game Modes
- [ ] Classic mode (current)
- [ ] Endless mode
- [ ] Time Attack mode
- [ ] Survival mode

### Phase 5: Sound & Audio
- [ ] Sound effects for eating, level up, game over
- [ ] Optional background music
- [ ] Volume controls

## 🐛 Known Issues & Limitations

- Input buffering queue size is limited to 1 (can only change direction once per frame)
- Snake starts with length of 3
- No wrap-around (hitting walls ends the game)

## 🤝 Contributing

Suggestions for improvements are welcome! This project demonstrates:
- Modern Python coding practices
- Proper state management
- Input buffering techniques
- High score persistence

## 📜 License

This project uses the standard Snake game mechanics. The code is provided as-is for educational purposes.

---

**Built with ❤️ using Python and Pygame**
