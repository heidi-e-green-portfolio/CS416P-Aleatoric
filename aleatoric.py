import sys
import random
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write

USAGE = """
Usage: aleatoric.py [options]

Options:
  --output FILENAME.wav  Write performance to a WAV file instead of playing directly
  --drums                Add a percussion track using white noise
  --harmony              Add a harmony voice below each melody note
  --help                 Show this message and exit
"""

# Samples per second
SAMPLE_RATE = 48000
# 16-bit
BIT_DEPTH = 16
# Max amplitude for 16-bit signed short
MAX_AMP = 32767

CHORD_LOOP_CHOICES = ["I-IV-ii-V", "I-vi-ii-V", "I-iii-IV-iv", "I-V-ii-V", "I-vi-IV-V", 
                      "IV-I-vi-IV", "I-V-vi-I", "I-IV-iv-I", "IV-V-I-I", "vi-IV-I-V"]

SONG_STRUCTURE_CHOICES = ["AABB/CC", "ABAB/CD", "AB/CDDD"]

# Roman numeral to major scale
CHORD_DEGREES = {"I":  [0, 2, 4], "ii":  [1, 3, 5], "iii": [2, 4, 6], 
                "IV":  [3, 5, 0], "V":   [4, 6, 1], "vi":  [5, 0, 2]}

# Flatted third not in the major scale
BORROWED_CHORD_NOTES = {"iv":  [3, 5, 6]}

# Major scale intervals relative to the root note (in semitones)
MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]

def get_song_structure():
    return random.choice(SONG_STRUCTURE_CHOICES)

def assign_chord_loops(song_structure):
    unique_letters = list(dict.fromkeys(song_structure))
    pool = random.sample(CHORD_LOOP_CHOICES, len(unique_letters))
    return {letter: loop for letter, loop in zip(unique_letters, pool)}

def generate_sawtooth(freq, duration):
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = 2 * (t * freq - np.floor(t * freq + 0.5))
    return wave

def midi_to_freq(midi_note):
    # Conversion of MIDI note number to frequency in Hz
    return 220.0 * (2.0 ** ((midi_note - 69) / 12.0))

def generate_drum_pattern(seconds_per_eighth):
    slots = [True] + [random.random() < 0.4 for _ in range(7)]
    if not any(slots[1:]):
        slots[random.randint(1, 7)] = True

    hit_samples = int(SAMPLE_RATE * seconds_per_eighth)
    decay = np.exp(-np.linspace(0, 6, hit_samples))
    hit_audio = np.random.uniform(-1, 1, hit_samples) * decay * 0.35
    silence = np.zeros(hit_samples)

    measure = np.concatenate([hit_audio if s else silence for s in slots])
    return slots, measure

def build_drum_track(total_measures, drum_measure):
    return np.tile(drum_measure, total_measures)

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE)
        sys.exit(0)

    # For optional additions
    use_drums = "--drums" in sys.argv
    use_harmony = "--harmony" in sys.argv

    raw_structure = get_song_structure()
    print(f"\nSong Structure: {raw_structure}\n")
    song_structure = raw_structure.replace("/", "")

    section_loops = assign_chord_loops(song_structure)
    for letter, loop in section_loops.items():
        print(f"Chord loop for {letter}: {loop}")

    # Key in range A3 (57) to A4 (69) inclusive
    key = random.randint(57, 69)
    print(f"\nKey (MIDI): {key}")

    # Random tempo in range 80 to 160 beats per minute
    tempo = random.randint(80, 160)
    print(f"\nTempo: {tempo}")

    seconds_per_beat = 60.0 / tempo
    seconds_per_eighth = seconds_per_beat / 2.0

    # Define the 7 notes available in the first octave of this key's major scale
    scale_midi_notes = [key + interval for interval in MAJOR_SCALE_INTERVALS]

    full_audio = []
    total_measures = 0
    
    # Generate melody and audio structure
    for letter in song_structure:
        chord_loop = section_loops[letter]
        chords = chord_loop.split('-')

        for chord in chords:
            total_measures += 1

            if chord in BORROWED_CHORD_NOTES:
                chord_midi_notes = [scale_midi_notes[idx] for idx in BORROWED_CHORD_NOTES[chord]]
            else:
                chord_midi_notes = [scale_midi_notes[idx] for idx in CHORD_DEGREES[chord]]

            for _ in range(8):
                note = (random.choice(chord_midi_notes)
                        if random.random() < 0.8
                        else random.choice(scale_midi_notes))

                note_wave = generate_sawtooth(midi_to_freq(note), seconds_per_eighth)

                if use_harmony:
                    below = [n for n in chord_midi_notes if n < note]
                    if below:
                        harmony_note = max(below)
                        note_wave = note_wave + generate_sawtooth(midi_to_freq(harmony_note), seconds_per_eighth) * 0.6
                
                full_audio.append(note_wave)

    audio_signal = np.concatenate(full_audio)

    if use_drums:
        drum_slots, drum_measure = generate_drum_pattern(seconds_per_eighth)
        print(f"\nDrum pattern (8 slots): {['X' if s else '.' for s in drum_slots]}")
        drum_track = build_drum_track(total_measures, drum_measure)
        drum_track = drum_track[:len(audio_signal)]
        if len(drum_track) < len(audio_signal):
            drum_track = np.pad(drum_track, (0, len(audio_signal) - len(drum_track)))
        audio_signal = np.clip(audio_signal * 0.75 + drum_track, -1.0, 1.0)

    audio_signal = (audio_signal * MAX_AMP).astype(np.int16)

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        filename = sys.argv[idx + 1]
        wav_write(filename, SAMPLE_RATE, audio_signal)
        print(f"\nSuccessfully wrote performance to {filename}.\n")
    else:
        print("\nPlaying melody directly...")
        sd.play(audio_signal, SAMPLE_RATE)
        sd.wait()
        print("Playback finished.\n")

if __name__ == "__main__":
    main()