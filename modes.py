"""Game mode definitions: labels, wrap behavior, and maze obstacles.

Pure data + small helpers so it stays trivially testable; collision and
rendering logic live in snake.py.
"""

import functools

import config

_LABELS = {
    'classic': 'CLASSIC',
    'wrap': 'WRAP',
    'maze': 'MAZE',
}


def label(mode):
    """Menu text for a game mode."""
    return _LABELS[mode]


def wraps(mode):
    """True when the snake teleports across screen edges."""
    return mode == 'wrap'


def cycle(mode, step):
    """The mode `step` positions (±1) away from `mode`, wrapping around."""
    modes = config.GAME_MODES
    return modes[(modes.index(mode) + step) % len(modes)]


@functools.lru_cache(maxsize=None)
def obstacle_cells(mode):
    """Grid cells blocked by static obstacles (empty except in maze mode).

    Two horizontal bars with a gap in the middle, leaving the spawn row
    clear. Cached: the maze is static for the lifetime of the process.
    """
    if mode != 'maze':
        return frozenset()
    b = config.BLOCK_SIZE
    left = config.SCREEN_WIDTH // 5 // b * b
    right = config.SCREEN_WIDTH * 4 // 5 // b * b
    y_top = config.SCREEN_HEIGHT // 3 // b * b
    y_bottom = config.SCREEN_HEIGHT * 2 // 3 // b * b
    gap_half = config.MAZE_GAP_BLOCKS * b
    cx = config.SCREEN_WIDTH // 2 // b * b
    cells = set()
    for x in range(left, right + b, b):
        if abs(x - cx) <= gap_half:
            continue                      # the navigable gap
        cells.add((x, y_top))
        cells.add((x, y_bottom))
    return frozenset(cells)
