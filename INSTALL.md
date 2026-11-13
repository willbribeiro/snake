# Installation Guide for Snake Game

## Prerequisites

### Option 1: Using pip (Recommended)

**Step 1: Install pygame**

Try the standard installation first:
```bash
pip install --upgrade pip
pip install pygame
```

If that fails, try with a pre-built wheel:
```bash
pip install "pygame==2.5.0" --find-links=https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
```

**Step 2: Verify Installation**
```bash
python -c "import pygame; print('Pygame version:', pygame.version.ver)"
```

### Option 2: Using Anaconda/Miniconda (Easier on Windows)

```bash
conda create -n snake_env python=3.10 pygame
conda activate snake_env
cd C:\Users\ventoy\Documents\snake
python snake.py
```

### Option 3: Using Chocolatey

```bash
choco install python pygame
```

## Running the Game

After installation, simply run:
```bash
python snake.py
```

Or use:
```bash
pip install -e .
python -m snake
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"

Make sure you installed pygame in the same Python environment you're using to run the game:
```bash
# Check which python you're using
where python

# Install for that specific python
py -m pip install pygame  # For Python 3.x on Windows
```

### "distutils.msvccompiler" errors

This happens with newer Python versions. Use a pre-built wheel instead:
```bash
pip install --upgrade pip
pip install "pygame==2.5.0" --extra-index-url https://www.lfd.uci.edu/~gohlke/pythonlibs/
```

### Game window appears black or empty

- Make sure pygame is installed correctly
- Try running as administrator (some systems need this for window creation)

## Project Structure After Installation

```
snake/
├── snake.py              # ← Run this file
├── config.py             # Game settings
├── highscore.json        # Your saved scores (created after first game)
├── requirements.txt      # Python dependencies
└── INSTALL.md           # This file
```
