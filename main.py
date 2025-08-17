import pygame
import threading
import time
import pynput.keyboard
import sys
from pydub import AudioSegment
import io

IDLE_TIMEOUT = 2
CROSSFADE_MS = 500  # duration of volume crossfade in milliseconds
FADE_STEP_MS = 50   # time per volume step for smooth fade

# Initialize mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)  # works for MP3 or WAV
    # Convert to WAV bytes for pygame
    wav_bytes = io.BytesIO()
    audio.export(wav_bytes, format="wav")
    wav_bytes.seek(0)
    return pygame.mixer.Sound(wav_bytes)

# Load tracks
try:
    #CALM_MUSIC = pygame.mixer.Sound("BlackIceCalm.wav")
    #COMBAT_MUSIC = pygame.mixer.Sound("BlackIceCombat.wav")
    #CALM_MUSIC = load_audio("0-1Calm.mp3")
    #COMBAT_MUSIC = load_audio("0-1Combat.mp3")
    #CALM_MUSIC = load_audio("deepbluecalm.mp3")
    #COMBAT_MUSIC = load_audio("deepbluecombat.mp3")
    CALM_MUSIC = load_audio("tenebreCalm.mp3")
    COMBAT_MUSIC = load_audio("tenebreCombat.mp3")
except FileNotFoundError:
    print("Error: WAV files missing.")
    sys.exit(1)

# Two channels for seamless crossfade
calm_channel = pygame.mixer.Channel(0)
combat_channel = pygame.mixer.Channel(1)

# Global state
current_track = "calm"
is_typing = False
has_typed_before = False
last_keypress_time = time.time()
running = True
start_time = time.time()

# Start both tracks at the same timestamp
calm_channel.play(CALM_MUSIC, loops=-1)
combat_channel.play(COMBAT_MUSIC, loops=-1)
combat_channel.set_volume(0.0)  # start muted

def crossfade(to_track, duration_ms=CROSSFADE_MS):
    steps = max(int(duration_ms / FADE_STEP_MS), 1)
    for i in range(steps + 1):
        t = i / steps
        if to_track == "combat":
            calm_channel.set_volume(1.0 - t)
            combat_channel.set_volume(t)
        else:
            calm_channel.set_volume(t)
            combat_channel.set_volume(1.0 - t)
        pygame.time.delay(FADE_STEP_MS)

def stop_and_start_new_track(new_track):
    global current_track
    if new_track == current_track:
        return
    print(f"Switching to {new_track} music...")
    crossfade(new_track)
    current_track = new_track

def on_press(key):
    global last_keypress_time, is_typing, has_typed_before, running
    if key == pynput.keyboard.Key.esc:
        print("Escape pressed. Exiting.")
        running = False
        pygame.mixer.quit()
        listener.stop()
        return False
    is_typing = True
    has_typed_before = True
    last_keypress_time = time.time()

def on_release(key):
    pass

listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("Music system active. Press ESC to exit. Start typing to switch to combat music.")

try:
    while running:
        if time.time() - last_keypress_time > IDLE_TIMEOUT:
            is_typing = False

        if is_typing and current_track != "combat" and has_typed_before:
            stop_and_start_new_track("combat")
        elif not is_typing and current_track != "calm":
            stop_and_start_new_track("calm")

        pygame.time.delay(50)  # main loop sleep

except KeyboardInterrupt:
    pygame.mixer.quit()
    listener.stop()
