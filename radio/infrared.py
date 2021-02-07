import threading
from evdev import InputDevice, ecodes


import control as control
import constants as CONST


# thread
infrared_thread = None

dev = InputDevice("/dev/input/event1")
dev.grab()

def _infrared_loop():
    t = threading.current_thread()
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            if t.name == "stop":
                break
            if event.code == 78 and event.value:
                control.control_up(CONST.VOLUME_CHANGE_DIFF)
            elif event.code == 74 and event.value:
                control.control_down(-CONST.VOLUME_CHANGE_DIFF)
            elif event.code == 208 and event.value:
                control.control_next()
            elif event.code == 168 and event.value:
                control.control_prev()
            elif event.code == 207 and event.value:
                control.control_pause_toggle()
            elif event.code == 139 and event.value:
                control.control_mute_toggle()


def start_thread():
    global infrared_thread

    if infrared_thread is not None:
        return

    infrared_thread = threading.Thread(target=_infrared_loop)
    infrared_thread.name = "run"
    infrared_thread.start()


def stop_thread():
    global infrared_thread

    if infrared_thread is None:
        return

    infrared_thread.name = "stop"
    infrared_thread = None
