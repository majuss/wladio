import json

def openFiles():
    with open('stations.json') as stations_file:
        stations = json.load(stations_file)
    with open('music_lib.json') as music_lib_file:
        music_lib = json.load(music_lib_file)

    return [stations, music_lib]

def uid_to_num(uid):
    n = 0
    for i in range(0, 5):
        n = n * 256 + uid[i]
    return n