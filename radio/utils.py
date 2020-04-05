import json


def openFiles():
    with open('stations.json') as stations_file:
        stations = json.load(stations_file)
    with open('music_lib.json') as music_lib_file:
        music_lib = json.load(music_lib_file)

    return [stations, music_lib]
