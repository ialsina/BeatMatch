from argparse import ArgumentParser
from pathlib import Path
import sys

from command_runner.elevate import elevate

from beatmatch.recorder import record
from beatmatch.player import play

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
    play_parser = subparsers.add_parser("play")
    play_parser.add_argument(
        "sound_file",
        type=str,
        help="Path for the sound file to be processed."
    )
    play_parser.add_argument(
        "strokes_file",
        type=str,
        help="Path for the already processed strokes."
    )
    play_parser.add_argument(
        "-r", "--refresh-rate",
        type=float,
        help="Seconds after each loop in the strokes player",
        default=0.001,
    )
    return parser

def _get_default_output_path(song_file: str):
    song_name = Path(song_file).name
    for suffix in (".mp3", ".wav"):
        song_file = song_file.removesuffix(suffix)
    parent = Path(__file__).absolute().resolve().parent
    return str(parent / (song_name + ".json"))


def _record_service(args):
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
    elevate(record, sound_file, output_path)

def _play_service(args):
    sound_file = args.sound_file
    strokes_file = args.strokes_file
    refresh_rate = args.refresh_rate
    for name, file in zip(["Sound", "Strokes"], [sound_file, strokes_file]):
        if not Path(file).exists():
            raise FileNotFoundError(
                f"{name} path {file} not found."
            )
    play(sound_file, strokes_file, refresh=refresh_rate)

SERVICES = {
    "record": _record_service,
    "play": _play_service,
}

def main():
    argv = sys.argv[1:]
    args = _get_parser().parse_args(argv)
    try:
        service = SERVICES[args.service]
    except KeyError:
        _get_parser().print_help()
        sys.exit(1)
    service(args)


if __name__ == "__main__":
    elevate(main)

