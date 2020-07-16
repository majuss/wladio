import json
import time

import logging
import sys


import constants

from enums import *


def openFiles():
    with open(constants.STATIONS_FILE) as stations_file:
        stations = json.load(stations_file)
    with open(constants.MUSIC_LIB_FILE) as music_lib_file:
        music_lib = json.load(music_lib_file)

    return [stations, music_lib]


def uid_to_num(uid):
    n = 0
    for i in range(0, 5):
        n = n * 256 + uid[i]
    return n


def fuzzy_pulse_compare(pulse1, pulse2, fuzzyness=0.2):
    if len(pulse1) != len(pulse2):
        return False
    for i in range(len(pulse1)):
        threshold = int(pulse1[i] * fuzzyness)
        if abs(pulse1[i] - pulse2[i]) > threshold:
            return False
    return True


def get_local_hours_minutes():
    localTime = time.localtime()
    return localTime.tm_hour, localTime.tm_min


state_object = {
    'muted': False,
    'paused': True,

    'power_state': PowerState.Unknown,
    'playback_mode': PlaybackMode.Radio,

    'last_power_button_push': 0,  # when was power button last pressed?


    'radio_playlist_position': 0,  # TODO: has to come from config


    'draw_bluetooth_icon': False,
    'draw_rain_cloud_icon': False
}


def state():
    return state_object


def create_logger(name):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    return logger
