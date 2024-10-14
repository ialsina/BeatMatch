import bisect
import json
from pathlib import Path
from threading import Thread
from time import sleep, time
from typing import Callable, Mapping, Optional, Sequence

from playsound import playsound

from .controller import get_keyboard_controller

output_file = "strokes.json"
output_path = Path(output_file).absolute()

record_keystrokes = get_keyboard_controller

def read_json(strokes_path: Path):
    with open(strokes_path, "r") as rf:
        return json.load(rf)

def _get_realtime_strokes(
    times: Sequence[float],
    strokes: Sequence[str],
    refresh: float,
    t_max: float,
    fun: Callable,
):
    def start():
        nonlocal times, strokes
        start_time = time()
        current_time = 0
        index = 0
        while current_time <= t_max:
            current_time = time() - start_time
            for index in range(0, len(strokes)):
                if times[index] >= current_time:
                    break
            cur_strokes = strokes[:index]
            strokes = strokes[index:]
            times = times[index:]
            if cur_strokes:
                fun(cur_strokes[-1])
            sleep(refresh)
            # Increment the time (you might want to change how time progresses)
    return start

def realtime_strokes(strokes_path: Path, refresh: float = 0.001, fun: Optional[Callable] = None):
    strokes_times = sorted([
        (time, stroke)
        for stroke, stroke_times
        in read_json(strokes_path).items()
        for time in stroke_times
    ], key=lambda x: x[0])

    # Handle case where strokes_times is empty
    if not strokes_times:
        return lambda: None  # Return a no-op function if there are no strokes

    # Unzip the times and strokes
    times, strokes = zip(*strokes_times)
    # Find the maximum time
    t_max = max(times)
    # Default callback function if none is provided
    if fun is None:
        print()
        fun = lambda x: print(f"\r{x:<70s}", end="")
    return _get_realtime_strokes(times, strokes, refresh, t_max, fun)


def play(music_path: Path, strokes_path: Path, refresh: float = 0.001, fun: Optional[Callable] = None):

    start_strokes_fun = realtime_strokes(strokes_path, refresh, fun)
    T_music = Thread(target=playsound, args=(music_path,))
    T_keystrokes = Thread(target=start_strokes_fun)

    T_music.start()
    T_keystrokes.start()

    T_music.join()
    T_keystrokes.join()

