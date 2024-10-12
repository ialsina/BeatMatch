from collections import defaultdict
from evdev import categorize, InputDevice, ecodes, list_devices
import os
import sys
import termios
import time
from typing import Sequence, Tuple, Optional
import warnings


def set_terminal_echo(enabled=True):
    """Enable or disable terminal echo."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = old_settings[:]
    new_settings[3] = new_settings[3] & ~termios.ECHO if not enabled else new_settings[3] | termios.ECHO
    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

def list_input_devices():
    devices = list_devices()
    if devices:
        print("Input Devices:")
        for device in devices:
            print(f"Device: {device}")
            dev = InputDevice(device)
            print(f"  Name: {dev.name}")
            print(f"  Physical Location: {dev.phys}")
            print(f"  Unique ID: {dev.info.vendor}:{dev.info.product}")
            print()
    else:
        print("No input devices found.")

def get_keyboard_device():
    devices = list_devices()
    if not devices:
        raise RuntimeError("No devices found.")
    keyboard_devices = []
    for device in devices:
        if "keyboard" in InputDevice(device).name.lower():
            keyboard_devices.append(device)
    if not keyboard_devices:
        raise RuntimeError("No keyboard devices found.")
    if len(keyboard_devices) > 1:
        warnings.warn("Multiple keyboad devices found.")
    return keyboard_devices[0]

def postprocess_strokes(keystrokes: Sequence[Tuple[str, float]], start_time: float):
    keystrokes_dct = defaultdict(list)
    for key, t in keystrokes:
        keystrokes_dct[key].append(t - start_time)
    return dict(keystrokes_dct)

def evdev_controller(device):
    # Create an InputDevice instance for the specified device
    dev = InputDevice(device)

    def record_keystrokes(ref_time: Optional[float] = None):
        keystrokes = []

        set_terminal_echo(False)
        print("Recording keystrokes... Press 'Enter' to stop.")

        start_time = time.time()  # Time 0 (start time)
        try:
            for event in dev.read_loop():
                if event.type == ecodes.EV_KEY:  # Check if the event is a key event
                    key_event = categorize(event)

                    if key_event.keystate == key_event.key_down:  # Key pressed
                        key_name = key_event.keycode
                        keystrokes.append((key_name, time.time()))

                    # Stop recording if 'Esc' key is pressed
                    if key_event.keycode == 'KEY_ENTER' and key_event.keystate == key_event.key_up:
                        print("Esc pressed. Stopping...")
                        break

        except KeyboardInterrupt:
            # Allow stopping with Ctrl+C
            print("Recording interrupted.")

        finally:
            set_terminal_echo(True)
            return postprocess_strokes(keystrokes, ref_time or start_time)

    return record_keystrokes

def pynput_controller():
    raise NotImplementedError(
        "Only session type 'wayland' session is implemented."
    )

def get_keyboard_controller():
    session_type = os.environ.get("XDG_SESSION_TYPE", "wayland")
    if os.geteuid() != 0:
        raise PermissionError(
            "Script was not run with elevated permission."
        )
    if session_type == "wayland":
        keyboard_devivce = get_keyboard_device()
        return evdev_controller(keyboard_devivce)
    return pynput_controller()
