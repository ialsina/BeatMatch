import json

from evdev.events import keys

from controller import record_keystrokes
from pathlib import Path

output_file = "strokes.json"
output_path = Path(output_file).absolute()

if __name__ == "__main__":
    keystrokes = record_keystrokes()
    with open(output_path, "w", newline="") as f:
        json.dump(keystrokes, f)

    print(f"Keystrokes saved to {output_path}.")

