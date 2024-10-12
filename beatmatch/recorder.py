import json
from pathlib import Path
from threading import Thread

from playsound import playsound

from .controller import record_keystrokes

output_file = "strokes.json"
output_path = Path(output_file).absolute()

def dump_keystrokes(path):
    keystrokes = record_keystrokes()
    with open(path, "w") as wf:
        json.dump(keystrokes, wf)
    print(f"File written: {path}.")

def record(music_path, output_path):
    T_music = Thread(target=playsound, args=(music_path,))
    T_keystrokes = Thread(target=dump_keystrokes, args=(output_path,))

    T_music.start()
    T_keystrokes.start()

    T_music.join()
    T_keystrokes.join()

