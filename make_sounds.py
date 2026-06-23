"""
make_sounds.py

Quick and dirty script I wrote because I couldn't find any royalty-free
sound effects I liked in time and didn't want to deal with licensing
random downloaded sounds. This just generates simple beep-style wav
files using basic sine waves instead.

Run this once: `python make_sounds.py`
It writes into assets/sounds and assets/music. If those files already
exist you don't need to run this again - the game just loads them.
"""

import math
import struct
import wave
import os

from settings import SOUND_DIR, MUSIC_DIR

SAMPLE_RATE = 44100


def make_tone(freq, duration_sec, volume=0.4, fade=True):
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        value = math.sin(2 * math.pi * freq * t)
        # quick fade out at the end so it doesn't click/pop
        if fade:
            fade_len = n_samples // 5
            if i > n_samples - fade_len:
                value *= (n_samples - i) / fade_len
        samples.append(int(value * volume * 32767))
    return samples


def make_sweep(start_freq, end_freq, duration_sec, volume=0.4):
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        progress = i / n_samples
        freq = start_freq + (end_freq - start_freq) * progress
        value = math.sin(2 * math.pi * freq * t)
        fade_len = n_samples // 5
        if i > n_samples - fade_len:
            value *= (n_samples - i) / fade_len
        samples.append(int(value * volume * 32767))
    return samples


def write_wav(filepath, samples):
    with wave.open(filepath, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        packed = b"".join(struct.pack("<h", s) for s in samples)
        f.writeframes(packed)


def make_eat_sound():
    # short, high pitched "blip"
    samples = make_tone(900, 0.08, volume=0.5) + make_tone(1300, 0.07, volume=0.45)
    write_wav(os.path.join(SOUND_DIR, "eat.wav"), samples)


def make_bonus_sound():
    # two ascending notes, sounds a bit more special than the regular eat blip
    samples = make_tone(700, 0.08, volume=0.5) + make_tone(1100, 0.08, volume=0.5) + make_tone(1500, 0.1, volume=0.5)
    write_wav(os.path.join(SOUND_DIR, "bonus.wav"), samples)


def make_gameover_sound():
    # downward sweep, sounds appropriately sad
    samples = make_sweep(500, 120, 0.6, volume=0.5)
    write_wav(os.path.join(SOUND_DIR, "gameover.wav"), samples)


def make_background_music():
    # super basic looping arpeggio, definitely not going to win any awards
    # but it's better than total silence
    notes = [262, 330, 392, 330, 262, 330, 392, 523]
    samples = []
    for note in notes:
        samples += make_tone(note, 0.3, volume=0.18, fade=True)
    write_wav(os.path.join(MUSIC_DIR, "background.wav"), samples)


if __name__ == "__main__":
    os.makedirs(SOUND_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    make_eat_sound()
    make_bonus_sound()
    make_gameover_sound()
    make_background_music()
    print("done generating placeholder sounds in assets/sounds and assets/music")
