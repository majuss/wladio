import mpv
import json
import threading
import time
import sys
import lirc




# Load stations file
with open('stations.json') as stations_file:
    stations = json.load(stations_file)

sockid = lirc.init("radio")
player = mpv.MPV()
player.wait_for_property('idle-active')

for station in stations:
    player.playlist_append(stations[station]['url'])

def play_stream():
    while True:
        player.wait_for_property('core-idle', lambda x: not x)
        player.wait_for_property('core-idle')

def get_current_station():
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return station

def get_current_station_name():
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return stations[station]['name']

def print_tags():
    last_tag = ''

    while True:
        print(get_current_station_name())
        while player.metadata is not None and "icy-title" in player.metadata:
            current_station = get_current_station()
            tag = player.metadata['icy-title']
            if last_tag != player.metadata['icy-title'] and player.metadata['icy-title'] not in stations[current_station]['skip_strings']:
                for replace_string in stations[current_station]['replace_strings']:
                    tag = tag.replace(replace_string, '').lstrip()
                print(tag)
                last_tag = player.metadata['icy-title']
            time.sleep(1)
        time.sleep(1)

def infrared_handler():
    while True:
        codeIR = lirc.nextcode()
        if "up" in codeIR:
            print("UP")
            player.volume = player.volume + 2
        if "down" in codeIR:
            print("DOWN")
            player.volume = player.volume - 2
        if "next" in codeIR:
            print("NEXT")
            try:
                player.playlist_next()
            except:
                print("No next title")
        if "prev" in codeIR:
            print("PREV")
            try:
                player.playlist_prev()
            except:
                print("No prev title")
        if "menu" in codeIR:
            print("MENU")
        if "play" in codeIR:
            print("PLAY")
            player.pause = not player.pause

player.playlist_pos = 0
player_thread = threading.Thread(target=play_stream)
player_thread.start()
tag_thread = threading.Thread(target=print_tags)
tag_thread.start()
infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()
player.volume = 100


# time.sleep(5)

# player.playlist_next()
# time.sleep(10)
# player.playlist_next()

sys.exit(0)
