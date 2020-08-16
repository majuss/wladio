import RPi.GPIO as GPIO

import utils as utils

from enums import *

GPIO.setup(17, GPIO.OUT)

logger = utils.create_logger(__name__)
STATE = utils.state()

def off():
    # speaker disconnect
    GPIO.output(17, GPIO.LOW)

def on():
    # speaker connect
    GPIO.output(17, GPIO.HIGH)

off()


