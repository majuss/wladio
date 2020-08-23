import RPi.GPIO as GPIO

import utils as utils

from constants import SPEAKER_RELAY
from enums import *

GPIO.setup(SPEAKER_RELAY, GPIO.OUT)

logger = utils.create_logger(__name__)
STATE = utils.state()

def off():
    # speaker disconnect
    GPIO.output(SPEAKER_RELAY, GPIO.LOW)

def on():
    # speaker connect
    GPIO.output(SPEAKER_RELAY, GPIO.HIGH)

off()


