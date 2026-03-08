import sys
import threading
from datetime import datetime
from pathlib import Path

import mss
import mss.tools
from PIL import Image
from pynput import keyboard

# crop region for the enemy portrait strip, adjust with calibrate.py if needed
CAPTURE_REGION = {'top': 660, 'left': 308, 'width': 65, 'height': 311}

OUTPUT_DIR = Path(__file__).parent / "captures"
OUTPUT_DIR.mkdir(exist_ok=True)

_pressed_keys: set = set()
_lock = threading.Lock()


def capture_screen(region: dict) -> tuple:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"capture_{timestamp}.png"
    with mss.mss() as sct:
        raw = sct.grab(region)
        mss.tools.to_png(raw.rgb, raw.size, output=str(filepath))
    img = Image.open(filepath)
    print(f"[Capture] Saved {filepath.name} ({img.width}x{img.height})")
    return str(filepath), img


def run_pipeline():
    # capture -> detect -> analyze -> overlay
    print("[HeroSense] Triggered!")
    filepath, _ = capture_screen(CAPTURE_REGION)

    from Hero_Detector import detect_heroes
    heroes = detect_heroes(filepath)

    from Comp_Analyzer import analyze_comp
    analysis = analyze_comp(heroes)

    from Overlay import show_overlay
    show_overlay(analysis)


def _on_press(key):
    with _lock:
        _pressed_keys.add(key)
        # TAB holds the scoreboard open, K fires the capture
        if key == keyboard.KeyCode(char="k") and keyboard.Key.tab in _pressed_keys:
            threading.Thread(target=run_pipeline, daemon=True).start()


def _on_release(key):
    with _lock:
        _pressed_keys.discard(key)


def start_listener():
    print("[HeroSense] Ready - hold TAB and press K on the scoreboard.")
    print("[HeroSense] Press CTRL+C to quit.\n")
    with keyboard.Listener(on_press=_on_press, on_release=_on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\n[HeroSense] Exiting.")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from Overlay import run_overlay_loop

    # Qt must own the main thread, listener runs in background
    app = QApplication(sys.argv)
    threading.Thread(target=start_listener, daemon=True).start()
    run_overlay_loop()