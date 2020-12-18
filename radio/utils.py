import json
import time

import logging
import sys
import os


import constants as CONST

from enums import PowerState, PlaybackMode

stations = None
music_lib = None
with open(CONST.STATIONS_FILE) as stations_file:
    stations = json.load(stations_file)
with open(CONST.MUSIC_LIB_FILE) as music_lib_file:
    music_lib = json.load(music_lib_file)


def openFiles():
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
    'shuffle_cd': False,

    'last_power_button_push': 0,  # when was power button last pressed?


    'radio_playlist_position': 0,
    'radio_volume': 25,
    'radio_last_pause': 0,


    'draw_bluetooth_icon': False,
    'draw_rain_cloud_icon': False
}

try:
    with open('radio_conf.json') as data:
        conf = json.load(data)

        state_object['radio_playlist_position'] = conf['station']
        state_object['radio_volume'] = conf['volume']
except Exception as e:
    # logger.debug('{}'.format(e))
    pass


def save_radio_conf():
    try:
        with open('radio_conf.json', 'w') as outfile:
            json.dump({"station": state_object['radio_playlist_position'],
                       "volume": state_object['radio_volume']}, outfile, indent=4)
    except Exception as e:
        pass


def state():
    return state_object


def create_logger(name):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s | %(message)s"))

    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

    return logger


cd_paths_without_id = []
music_lib_paths = {}

for path in music_lib.values():
    music_lib_paths[path] = 1

for root, subFolders, files in os.walk(CONST.MUSIC_LIB_PATH):
    if len(subFolders):
        continue

    relative_path = root[len(CONST.MUSIC_LIB_PATH):]

    if relative_path not in music_lib_paths:
        cd_paths_without_id.append(relative_path)

print(cd_paths_without_id)


def get_cd_paths_without_id():
    return cd_paths_without_id


def save_music_lib():
    try:
        with open(CONST.MUSIC_LIB_FILE, 'w') as outfile:
            json.dump(music_lib, outfile, indent=4)
    except Exception as e:
        pass
