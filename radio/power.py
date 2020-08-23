import threading
from ina219 import INA219

import utils
from time import sleep
from enums import PowerState

power_thread = None
STATE = utils.state()
logger = utils.create_logger(__name__)
SHUNT_OHMS = 0.1

def _power_loop():
    ina = INA219(SHUNT_OHMS)
    ina.configure()
    # last_state = False

    while True:
        voltage = ina.voltage()

        if voltage > 10:  # power state on
            # logger.debug('radio power state is ' + str(voltage) + ' V')
            STATE['power_state'] = PowerState.Powered
            last_state = 1

        if voltage < 10:
            # logger.debug('radio power state is ' + str(voltage) + ' V')
            # STATE['power_state'] = PowerState.Standby
            STATE['power_state'] = PowerState.Powered

            last_state = 0
        sleep(0.05)


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