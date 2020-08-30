import RPi.GPIO as GPIO

import utils as utils

from constants import SPEAKER_RELAY
from enums import *

GPIO.setmode(GPIO.BCM)

GPIO.setup(SPEAKER_RELAY, GPIO.OUT)

logger = utils.create_logger(__name__)
STATE = utils.state()

def off():
    # speaker disconnect
    logger.debug('speakers off')
    GPIO.output(SPEAKER_RELAY, GPIO.HIGH)

def on():
    # speaker connect
    logger.debug('speakers on')
    GPIO.output(SPEAKER_RELAY, GPIO.LOW)

off()
