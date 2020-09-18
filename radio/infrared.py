import threading
import lirc


import control as control
import constants as CONST


sockid = lirc.init('radio', blocking=True)


# thread
infrared_thread = None


def _infrared_loop():
    t = threading.current_thread()
    last_code = ''

    while True:
        codeIR = lirc.nextcode()  # call blocks until IR commands was received

        if t.name is 'stop':
            break

        if 0 is len(codeIR):  # empty array means repeat same code as befores code
            if last_code not in ['up', 'down']:  # for up down we want to proceed
                continue
            codeIR = [last_code]

        last_code = code = codeIR[0]

        # handle IR commands
        if 'up' == code:
            control.control_up(CONST.VOLUME_CHANGE_DIFF)

        elif 'down' == code:
            control.control_down(-CONST.VOLUME_CHANGE_DIFF)

        elif 'next' == code:
            control.control_next()

        elif 'prev' == code:
            control.control_prev()

        elif 'menu' == code:
            control.control_mute_toggle()

        elif 'play' == code:
            control.control_pause_toggle()


def start_thread():
    global infrared_thread

    if infrared_thread is not None:
        return

    infrared_thread = threading.Thread(target=_infrared_loop)
    infrared_thread.name = 'run'
    infrared_thread.start()


def stop_thread():
    global infrared_thread

    if infrared_thread is None:
        return

    infrared_thread.name = 'stop'
    infrared_thread = None
