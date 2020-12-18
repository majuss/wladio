import threading
from ina219 import INA219
from time import sleep

import utils
import infrared
import rfid
import control
from enums import PowerState

power_thread = None
STATE = utils.state()
# logger = utils.create_logger(__name__)
SHUNT_OHMS = 0.1

ina = INA219(SHUNT_OHMS)
ina.configure()


if 6 < ina.voltage():
    STATE['power_state'] = PowerState.Powered
else:
    STATE['power_state'] = PowerState.Standby


def _power_loop():
    t = threading.current_thread()
    while t.name == 'run':
        voltage = ina.voltage()

        if voltage > 6 and STATE['power_state'] is not PowerState.Powered:  # leaf standby
            STATE['power_state'] = PowerState.Powered

            rfid.start_thread()
            infrared.start_thread()
            control.control_leave_standby()

        if voltage < 6 and STATE['power_state'] is not PowerState.Standby:  # enter standby
            STATE['power_state'] = PowerState.Standby

            control.control_enter_standby()
            infrared.stop_thread()
            rfid.stop_thread()
        sleep(0.5)


def start_thread():
    global power_thread

    if power_thread is not None:
        return

    power_thread = threading.Thread(target=_power_loop)
    power_thread.name = 'run'
    power_thread.start()


def stop_thread():
    global power_thread

    if power_thread is None:
        return

    power_thread.name = 'stop'
    power_thread = None


# def callback_power(channel):
#     logger.debug('power button pressed')

#     if time() - STATE['last_power_button_push'] < CONST.PWR_DEBOUNCE:
#         logger.debug('power button pressed < 2 secs')
#         return

#     logger.debug('continue to decision')

#     STATE['last_power_button_push'] = time()

#     sleep(0.001)

#     power_state = GPIO.input(channel)

#     logger.debug('Power state set to: {}'.format(power_state))

#     if power_state:  # standby is off GPIO is HIGH
#         # leave standby


#     else:  # standby is ON GPIO is LOW
#         # enter standby
#         # GPIO.output(17, GPIO.LOW)
