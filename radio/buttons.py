import RPi.GPIO as GPIO
from time import sleep, time

import control
import utils

import constants as CONST

logger = utils.create_logger(__name__)
STATE = utils.state()

GPIO.setmode(GPIO.BCM)


BUTTON_MAPPING = CONST.BUTTON_MAPPING

# GPIO.setup(7, GPIO.OUT) # relay door

# GPIO.output(7, GPIO.HIGH)


GPIO.setup(BUTTON_MAPPING['next_btn'], GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_MAPPING['prev_btn'], GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_MAPPING['pause_btn'], GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_MAPPING['garage_door'], GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_MAPPING['driveway'], GPIO.IN, GPIO.PUD_UP)
GPIO.setup(BUTTON_MAPPING['unknown'], GPIO.IN, GPIO.PUD_UP)

# GPIO.setup(BUTTON_MAPPING['power'], GPIO.IN, GPIO.PUD_DOWN)

GPIO.setup(BUTTON_MAPPING['vol_clk'], GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(BUTTON_MAPPING['vol_dt'], GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(BUTTON_MAPPING['vol_sw'], GPIO.IN, GPIO.PUD_UP)


def callback_next_btn(channel):
    control.control_next()


def callback_prev_btn(channel):
    control.control_prev()


def callback_pause_btn(channel):
    control.control_pause_toggle()


def callback_garage_door(channel):
    logger.debug('garage door pressed')
    control.control_garagedoor()


def callback_driveway(channel):
    logger.debug('drive way button pressed')
    control.control_drivewaygate()


def callback_unknown(channel):
    logger.debug('shuffle cd button pressed')
    control.control_toggle_shuffle_cd()


# globals for wheel
direction = True
clk_last = 0
clk_current = 0
clk_last = GPIO.input(BUTTON_MAPPING['vol_clk'])


def callback_vol(null):
    global clk_current
    global direction

    clk_current = GPIO.input(BUTTON_MAPPING['vol_clk'])
    print(clk_current, GPIO.input(BUTTON_MAPPING['vol_dt']))
    if clk_current != clk_last:
        if GPIO.input(BUTTON_MAPPING['vol_dt']) != clk_current:
            direction = True
        else:
            direction = False
        if direction:
            control.control_up(CONST.VOL_KNOB_SPEED)  # volume change up
        else:
            control.control_down(-CONST.VOL_KNOB_SPEED)  # volume change down


def callback_vol_sw(null):
    control.control_mute_toggle()  # volume mute toggle


GPIO.add_event_detect(BUTTON_MAPPING['next_btn'], GPIO.FALLING,
                      callback=callback_next_btn, bouncetime=350)
GPIO.add_event_detect(BUTTON_MAPPING['prev_btn'], GPIO.FALLING,
                      callback=callback_prev_btn, bouncetime=350)
GPIO.add_event_detect(BUTTON_MAPPING['pause_btn'], GPIO.FALLING,
                      callback=callback_pause_btn, bouncetime=350)
GPIO.add_event_detect(BUTTON_MAPPING['garage_door'], GPIO.FALLING,
                      callback=callback_garage_door, bouncetime=CONST.DOORS_TIMEOUT * 1000 + 3000)

GPIO.add_event_detect(BUTTON_MAPPING['driveway'], GPIO.FALLING,
                      callback=callback_driveway, bouncetime=CONST.DOORS_TIMEOUT * 1000 + 3000)

GPIO.add_event_detect(BUTTON_MAPPING['unknown'], GPIO.FALLING,
                      callback=callback_unknown, bouncetime=350)

# GPIO.add_event_detect(
#     BUTTON_MAPPING['power'], GPIO.BOTH, callback=callback_power, bouncetime=250)

GPIO.add_event_detect(BUTTON_MAPPING['vol_clk'], GPIO.BOTH,
                      callback=callback_vol, bouncetime=1)
GPIO.add_event_detect(BUTTON_MAPPING['vol_sw'], GPIO.FALLING,
                      callback=callback_vol_sw, bouncetime=350)

# powerState = GPIO.input(BUTTON_MAPPING['power'])
# logger.debug('radio power state is ' + str(powerState))
# if powerState:  # power state on
#     STATE['power_state'] = PowerState.Powered
# else:
#     STATE['power_state'] = PowerState.Standby
