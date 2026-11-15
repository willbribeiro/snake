"""Power-up definitions: types, colors, labels, and the collectible object.

Spawn/collision logic lives in snake.py; this module only defines data so
it stays trivially testable.
"""

import random

import config


class PowerUp:
    """A collectible placed on a grid cell until the snake's head reaches it."""

    __slots__ = ('kind', 'cell')

    def __init__(self, kind, cell):
        self.kind = kind
        self.cell = cell


def pick_kind():
    """Choose a power-up type uniformly from the configured types."""
    return random.choice(config.POWERUP_TYPES)


_COLORS = {
    'shield': (138, 255, 21),   # lime green
    'speed': (255, 215, 0),     # gold
    'length': (138, 43, 226),   # purple
}

_LABELS = {
    'shield': 'SHIELD',
    'speed': 'SPEED BOOST',
    'length': 'LENGTH BONUS',
}


def color(kind):
    """Board color for a power-up type."""
    return _COLORS[kind]


def label(kind):
    """HUD banner text for an active (timed) power-up effect."""
    return _LABELS[kind]
