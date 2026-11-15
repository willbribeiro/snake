"""Tests for the audio module (procedural sound synthesis).

The game must degrade to silence when there is no audio device, so the
SoundBank is tested against a fake sound builder; the pure synthesis
functions are tested directly.
"""
import unittest
from unittest import mock

import config
import audio


class SynthTest(unittest.TestCase):
    def test_every_sound_has_nonempty_samples(self):
        for name in audio.SOUND_NAMES:
            self.assertTrue(audio.synth_samples(name))

    def test_unknown_name_yields_no_samples(self):
        self.assertEqual(audio.synth_samples('does-not-exist'), [])

    def test_samples_within_unit_range(self):
        for name in audio.SOUND_NAMES:
            for s in audio.synth_samples(name):
                self.assertGreaterEqual(s, -1.0)
                self.assertLessEqual(s, 1.0)

    def test_sounds_are_not_silent(self):
        for name in audio.SOUND_NAMES:
            peak = max(abs(s) for s in audio.synth_samples(name))
            self.assertGreater(peak, 0.1)

    def test_sample_count_matches_configured_durations(self):
        for name, segments in audio._SPECS.items():
            expected = sum(int(config.SAMPLE_RATE * seconds)
                           for _, seconds in segments)
            self.assertEqual(len(audio.synth_samples(name)), expected)

    def test_melody_is_concatenated_segments(self):
        samples = audio.synth_samples('gameover')
        seg_lens = [int(config.SAMPLE_RATE * d)
                    for _, d in audio._SPECS['gameover']]
        self.assertEqual(len(samples), sum(seg_lens))
        # A melody: the first segment differs from the last one.
        self.assertNotEqual(samples[:seg_lens[0]],
                            samples[-seg_lens[-1]:])


class BufferTest(unittest.TestCase):
    def test_mono_buffer_is_signed_16bit_little_endian(self):
        buf = audio._buffer([0.5, -0.5])
        self.assertEqual(len(buf), 4)   # 2 samples x 2 bytes
        self.assertEqual(int.from_bytes(buf[0:2], 'little', signed=True),
                         int(0.5 * config.SOUND_VOLUME * 32767))

    def test_stereo_doubles_every_sample(self):
        self.assertEqual(len(audio._buffer([0.5], stereo=True)),
                         2 * len(audio._buffer([0.5])))

    def test_volume_scales_amplitude(self):
        full = int.from_bytes(audio._buffer([1.0])[0:2], 'little', signed=True)
        self.assertEqual(full, int(config.SOUND_VOLUME * 32767))
        with mock.patch.object(config, 'SOUND_VOLUME', 0):
            self.assertEqual(audio._buffer([1.0]),
                             (0).to_bytes(2, 'little'))


class SoundBankTest(unittest.TestCase):
    def test_reads_config_flag_at_call_time(self):
        with mock.patch.object(config, 'SOUND_ENABLED', False):
            bank = audio.SoundBank()
        self.assertFalse(bank.enabled)
        self.assertEqual(bank.sounds, {})

    def test_explicit_flag_overrides_config(self):
        self.assertFalse(audio.SoundBank(enabled=False).enabled)

    def test_enabled_builds_sounds(self):
        sentinel = {'eat': object()}
        with mock.patch.object(audio, '_build_sounds',
                               return_value=sentinel) as builder:
            bank = audio.SoundBank()
        self.assertTrue(bank.enabled)
        self.assertIs(bank.sounds, sentinel)
        builder.assert_called_once_with()

    def test_play_starts_known_sound(self):
        started = []

        class FakeSound:
            def play(self):
                started.append(True)

        with mock.patch.object(audio, '_build_sounds',
                               return_value={'eat': FakeSound()}):
            bank = audio.SoundBank()
        bank.play('eat')
        self.assertEqual(started, [True])

    def test_play_unknown_name_is_noop(self):
        with mock.patch.object(audio, '_build_sounds', return_value={}):
            bank = audio.SoundBank()
        bank.play('nope')                       # must not raise
        bank.play('')                           # must not raise

    def test_play_swallows_device_errors(self):
        class BrokenSound:
            def play(self):
                raise RuntimeError('no audio device')

        with mock.patch.object(audio, '_build_sounds',
                               return_value={'eat': BrokenSound()}):
            bank = audio.SoundBank()
        bank.play('eat')                        # swallowed, game goes on


if __name__ == '__main__':
    unittest.main(verbosity=2)
