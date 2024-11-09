from gpiozero import Button, InputDevice, DigitalInputDevice
from signal import pause

import control
import utils
import constants as CONST

logger = utils.create_logger(__name__)
STATE = utils.state()

BUTTON_MAPPING = CONST.BUTTON_MAPPING

# Define buttons and inputs using gpiozero
next_btn = Button(BUTTON_MAPPING['next_btn'], pull_up=True, bounce_time=0.05)
prev_btn = Button(BUTTON_MAPPING['prev_btn'], pull_up=True, bounce_time=0.05)
pause_btn = Button(BUTTON_MAPPING['pause_btn'], pull_up=True, bounce_time=0.05)
garage_door = Button(BUTTON_MAPPING['garage_door'], pull_up=True, bounce_time=0.05)
driveway = Button(BUTTON_MAPPING['driveway'], pull_up=True, bounce_time=0.05)
unknown_btn = Button(BUTTON_MAPPING['unknown'], pull_up=True, bounce_time=0.05)

vol_clk = DigitalInputDevice(BUTTON_MAPPING['vol_clk'], pull_up=False, bounce_time=0.001)
vol_dt = DigitalInputDevice(BUTTON_MAPPING['vol_dt'], pull_up=False)
vol_sw = Button(BUTTON_MAPPING['vol_sw'], pull_up=True, bounce_time=0.05)

# Define callback functions
def callback_next_btn():
    control.control_next()

def callback_prev_btn():
    control.control_prev()

def callback_pause_btn():
    control.control_pause_toggle()

def callback_garage_door():
    logger.debug('garage door pressed')
    control.control_garagedoor()

def callback_driveway():
    print("DRIVEWAY_----------------------------")
    logger.debug('drive way button pressed')
    control.control_drivewaygate()

def callback_unknown():
    logger.debug('shuffle cd button pressed')
    control.control_toggle_shuffle_cd()

# Globals for wheel
direction = True
clk_last = vol_clk.value

def callback_vol():
    global clk_last, direction
    clk_current = vol_clk.value
    if clk_current != clk_last:
        if vol_dt.value != clk_current:
            direction = True
        else:
            direction = False
        if direction:
            control.control_up(CONST.VOL_KNOB_SPEED)  # volume change up
        else:
            control.control_down(-CONST.VOL_KNOB_SPEED)  # volume change down
        clk_last = clk_current

def callback_vol_sw():
    control.control_mute_toggle()  # volume mute toggle

# Assign event handlers
next_btn.when_pressed = callback_next_btn
prev_btn.when_pressed = callback_prev_btn
pause_btn.when_pressed = callback_pause_btn
garage_door.when_pressed = callback_garage_door
driveway.when_pressed = callback_driveway
unknown_btn.when_pressed = callback_unknown

vol_clk.when_activated = callback_vol
vol_clk.when_deactivated = callback_vol
vol_sw.when_pressed = callback_vol_sw
