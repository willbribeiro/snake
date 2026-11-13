# 🚀 Snake Game - Quick Start Guide

## Installation (2 minutes)

### Step 1: Install Pygame
Open PowerShell or Command Prompt and run:
```powershell
pip install pygame
```

If that fails, try:
```powershell
pip install --upgrade pip
pip install "pygame==2.5.0"
```

### Step 2: Verify Installation
```powershell
python -c "import pygame; print('Success!')"
```

## Running the Game (30 seconds)

### Simple Run:
```powershell
cd C:\Users\ventoy\Documents\snake
python snake.py
```

### Or as a module:
```powershell
python -m snake
```

---

## 🎮 Controls Quick Reference

| Key | Action |
|-----|--------|
| **↑** | Move Up |
| **↓** | Move Down |
| **→** | Move Right |
| **←** | Move Left |
| **P** | Pause/Resume Game |
| **Enter** | Start Game (from Menu) |
| **C** | Continue (after Game Over) |
| **Q** | Quit Game |

---

## ✨ What's New This Version?

### 🎯 Game Features:
- ⚡ **Input Buffering** - Can't die from pressing keys too fast!
- 💾 **High Scores** - Your best scores are saved forever
- ⏸️ **Pause Anytime** - Press P to take a break
- 📊 **Score Display** - See your score and level at all times
- 🎨 **Menus & Overlays** - Professional-looking screens

### ⚡ Power-Ups (Coming Soon):
- 🛡️ **Shield** - Temporary invincibility
- ⚡ **Speed Boost** - Move faster temporarily  
- ➕ **Length Bonus** - Instant growth

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `snake.py` | **← Run this file to play!** |
| `config.py` | Game settings and colors |
| `powerups.py` | Power-up system (for future) |
| `highscore.json` | Your saved high scores |

---

## 🎯 First Time Play Guide

1. **Start**: Press ENTER when you see the menu
2. **Move**: Use arrow keys to navigate
3. **Eat Food**: Green squares = food (+10 points)
4. **Level Up**: Every 50 points, speed increases!
5. **Don't Crash**: Avoid walls and your own tail
6. **Pause**: Press P anytime to pause/resume
7. **High Score**: Beat your best score! 🏆

---

## 💡 Tips for Beginners

1. **Take Your Time** - Don't move too fast at first
2. **Plan Turns** - Use arrow keys one at a time
3. **Watch the Tail** - Keep distance from your own body
4. **Don't Worry About Level** - Survival first, points second
5. **Use Pause** - Press P if you need to think

---

## 🎯 Tips for Advanced Players

1. **Level Up Strategy**: Eat consistently to increase speed
2. **Corner Movement**: Use corners to trap yourself strategically
3. **Long Snake Advantage**: More segments = more food you can cross
4. **Patience**: Let the snake grow before making tight turns

---

## ❓ Common Questions

### "The game window is blank/black"
- Make sure pygame installed: `pip install pygame`
- Try running as Administrator (some Windows setups need this)

### "How do I increase speed?"
- Edit `config.py` and change `INITIAL_SPEED = 15` to a higher value

### "Can I modify the game?"
- Yes! All settings are in `config.py`
- Look at other files in the folder for code reference

### "Where's my high score saved?"
- Check `highscore.json` in the same folder as snake.py

---

## 🆘 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pygame'"
**Solution**: Run `pip install pygame`

### Problem: Game window opens but nothing visible
**Solution**: Try running Python as Administrator

### Problem: Snake moves too fast/slow
**Solution**: Edit `config.py`:
```python
INITIAL_SPEED = 15  # Change this value
MIN_SPEED = 40      # Maximum speed cap
```

---

## 📊 Game Stats to Watch

- **Score**: Points from eating food (+10 each)
- **Level**: Increases every 50 points
- **Speed**: Current FPS (increases with level)
- **High Score**: Your best score this session

---

## 🎯 Challenge Mode Ideas

### Beginner Goal: Reach Level 3
### Intermediate Goal: Score 200 Points
### Advanced Goal: Beat Your High Score by 50%
### Expert Goal: Survive Without Hitting Walls (Pure Survival!)

---

## 🌟 Enjoy Your Snake Game!

```
    ___________
   /           \
  |  SNAKE GAME  |
   \___________/
```

**Press ENTER to Start Playing!** 🎮

---

**Need Help?** Check `README.md` for full documentation or `INSTALL.md` for installation help.
