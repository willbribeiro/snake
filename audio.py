"""Procedural sound effects - generated in code, no asset files.

Sounds degrade to silence when there is no audio device (or when
SOUND_ENABLED is off), so the game never crashes or stalls on audio.
"""

import functools
import math

import pygame

import config

# Sound names offered by the bank.
SOUND_NAMES = ('eat', 'pickup', 'levelup', 'gameover')

# Each sound is a sequence of (frequency, seconds) tones; melodies are
# simply several tones played one after the other.
_SPECS = {
    'eat': [(660, 0.06)],                                    # short blip
    'pickup': [(523, 0.05), (784, 0.07)],                    # chime
    'levelup': [(523, 0.08), (659, 0.08),                    # rising arpeggio
                (784, 0.08), (1047, 0.12)],
    'gameover': [(440, 0.15), (349, 0.15), (262, 0.30)],     # falling melody
}


def synth_samples(name):
    """Samples (floats in [-1, 1]) for a sound name; unknown names -> []"""
    out = []
    for freq, seconds in _SPECS.get(name, ()):
        out.extend(_tone(freq, seconds))
    return out


def _tone(freq, seconds):
    """One decaying sine tone as a list of floats in [-1, 1]."""
    n = int(config.SAMPLE_RATE * seconds)
    return [
        math.sin(2 * math.pi * freq * i / config.SAMPLE_RATE) * (1 - i / n)
        for i in range(n)
    ]


def _buffer(samples, stereo=False):
    """Encode floats as signed 16-bit little-endian PCM bytes."""
    out = bytearray()
    for s in samples:
        pcm = int(max(-1.0, min(1.0, s * config.SOUND_VOLUME)) * 32767)
        frame = pcm.to_bytes(2, 'little', signed=True)
        out += frame
        if stereo:
            out += frame                     # same sample in both channels
    return bytes(out)


@functools.lru_cache(maxsize=1)
def _build_sounds():
    """Build mixer Sound objects; {} when no audio device is available."""
    try:
        pygame.mixer.init()
    except pygame.error:
        return {}
    stereo = pygame.mixer.get_init()[2] == 2
    sounds = {}
    for name in SOUND_NAMES:
        try:
            sounds[name] = pygame.mixer.Sound(
                buffer=_buffer(synth_samples(name), stereo=stereo))
        except pygame.error:
            pass                             # missing one sound must not kill the game
    return sounds


class SoundBank:
    """Owns the game's sound effects; safe to use even when silent."""

    def __init__(self, enabled=None):
        if enabled is None:
            enabled = config.SOUND_ENABLED   # read at call time, not import
        self.enabled = enabled
        self.sounds = _build_sounds() if enabled else {}

    def play(self, name):
        """Play a sound if it exists; never raises."""
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass                             # audio must never break the game
