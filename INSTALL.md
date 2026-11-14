# Installation

## Python 3.13 – 3.15 (including 3.15.2)

The `pygame` package does not publish wheels for Python 3.15 and building it
from source fails. Use **pygame-ce** instead — it is a maintained fork with a
compatible API and prebuilt wheels:

```bash
pip install pygame-ce
```

Verify:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

## Run

```bash
python snake.py
```

## Tests

```bash
python -m unittest test_snake -v
```

The suite runs headless (`SDL_VIDEODRIVER=dummy`), so it works without a
display.

## Troubleshooting

**`ModuleNotFoundError: No module named 'pygame'`**
Install into the same interpreter you run the game with:
`py -m pip install pygame-ce` (Windows) or `python3 -m pip install pygame-ce`.

**`ModuleNotFoundError: No module named 'pygame_ce'`**
Nothing is wrong — `import pygame` still works after installing pygame-ce;
the distribution name (`pip install pygame-ce`) differs from the import name.

**Source-build errors mentioning `distutils` / `msvccompiler`**
You tried to install classic `pygame` on a Python version without wheels.
Install `pygame-ce` instead.

**Black or frozen window**
Update pygame-ce: `pip install -U pygame-ce`. If it persists, open an issue
with the traceback.
