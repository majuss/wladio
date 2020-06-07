import json
import constants

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