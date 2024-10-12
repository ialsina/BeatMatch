from argparse import ArgumentParser
from pathlib import Path
import sys

from command_runner.elevate import elevate

from beatmatch.recorder import record

def _get_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="service")
    record_parser = subparsers.add_parser("record")
    record_parser.add_argument(
        "sound_file",
        type=str,
        help="Path for the sound file to be processed."
    )
    record_parser.add_argument(
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


def record(args):
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
    record(sound_file, output_path)

SERVICES = {
    "record": record,
}

def main():
    argv = sys.argv[1:]
    args = _get_parser().parse_args(argv)
    service = args.service
    SERVICES[service](args)

if __name__ == "__main__":
    elevate(main)

