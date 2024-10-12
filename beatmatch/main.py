from argparse import ArgumentParser
import json
from pathlib import Path
from threading import Thread
import sys

from evdev.events import keys
from playsound import playsound

from controller import record_keystrokes

output_file = "strokes.json"
output_path = Path(output_file).absolute()

def _get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "sound_file",
        type=str,
        help="Path for the sound file to be processed."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path for the output json document with the keystrokes.",
        default=None,
    )
    return parser

def _get_default_output_path(song_file: str):
    song_name = Path(song_file).name
    for suffix in (".mp3", ".wav"):
        song_file = song_file.removesuffix(suffix)
    parent = Path(__file__).absolute().resolve().parent
    return str(parent / (song_name + ".json"))

def dump_keystrokes(path):
    keystrokes = record_keystrokes()
    with open(path, "w") as wf:
        json.dump(keystrokes, wf)
    print(f"File written: {path}.")

def start(music_path, output_path):
    T_music = Thread(target=playsound, args=(music_path,))
    T_keystrokes = Thread(target=dump_keystrokes, args=(output_path,))

    T_music.start()
    T_keystrokes.start()

    T_music.join()
    T_keystrokes.join()

def main():
    argv = sys.argv[1:]
    args = _get_parser().parse_args(argv)
    sound_file = args.sound_file
    if not Path(sound_file).exists():
        raise FileNotFoundError(
            f"Sound path {sound_file} not found."
        )
    output_path = (
        _get_default_output_path(sound_file)
        if args.output is None
        else str.removesuffix(args.output, ".json") + ".json"
    )
    start(sound_file, output_path)

if __name__ == "__main__":
    main()

