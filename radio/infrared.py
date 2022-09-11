import threading

import control as control
import constants as CONST


# thread
infrared_thread = None

VOLUME_CHANGE_DIFF = 30

def _infrared_loop():
    t = threading.current_thread()

    import pulseio
    import adafruit_irremote

    pulsein = pulseio.PulseIn(18, maxlen=120, idle_state=True)
    decoder = adafruit_irremote.GenericDecode()

    while True:
        pulses = decoder.read_pulses(pulsein)
        try:
            code = decoder.decode_bits(pulses)
            print(code)

            if code == (136, 30, 223, 101):
                control.control_pause_toggle()
            if code == (136, 30, 79, 101):
                control.control_down(-CONST.REMOTE_VOLUME_CHANGE_DIFF)
            if code == (136, 30, 47, 101):
                control.control_up(CONST.REMOTE_VOLUME_CHANGE_DIFF)
            if code == (136, 30, 31, 101):
                control.control_next()
            if code == (136, 30, 239, 101):
                control.control_prev()
            if code == (136, 30, 191, 101):
                control.control_mute_toggle()

        except adafruit_irremote.IRNECRepeatException:  # unusual short code!
            print("NEC repeat!")
        except adafruit_irremote.IRDecodeException as e:     # failed to decode
            print("Failed to decode: ", e.args)
        except Exception as err:
            print(err)


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
