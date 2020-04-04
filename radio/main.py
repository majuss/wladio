import mpv
import json
import threading
from time import sleep
import sys
import lirc
from pirc522 import RFID

# Load stations file
with open('stations.json') as stations_file:
    stations = json.load(stations_file)
with open('music_lib.json') as music_lib_file:
    music_lib = json.load(music_lib_file)

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
    global playback_mode

    while True:
        if  playback_mode == 0:
            print(get_current_station_name())
            while player.metadata is not None and "icy-title" in player.metadata:
                current_station = get_current_station()
                tag = player.metadata['icy-title']
                if last_tag != player.metadata['icy-title'] and player.metadata['icy-title'] not in stations[current_station]['skip_strings']:
                    for replace_string in stations[current_station]['replace_strings']:
                        tag = tag.replace(replace_string, '').lstrip()
                    print(tag)
                    last_tag = player.metadata['icy-title']
                sleep(1)
            sleep(1)

        if playback_mode == 1:
            print(player.metadata['title'] + ' - ' + player.metadata['artist']) 
            sleep(1)

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
            player.mute = not player.mute
            print("MENU")
        if "play" in codeIR:
            print("PLAY")
            player.pause = not player.pause
        sleep(0.1)

def rfid_handler():
    global playback_mode
    try:
        while True:
            rdr.wait_for_tag()
            (error, tag_type) = rdr.request()
            if not error:
                print("Tag detected")
                (error, uid) = rdr.anticoll()
                if not error:
                    rfid = str(uid_to_num(uid))
                    if playback_mode == 0:
                        player.play('/home/pi/' + music_lib[rfid])
                    playback_mode = 1
                    sleep(1)
    except KeyboardInterrupt:
        rdr.cleanup()
        raise

def uid_to_num(uid):
    n = 0
    for i in range(0, 5):
        n = n * 256 + uid[i]
    return n

def restart_streaming():
    global playback_mode

    player.stop = True
    if len(player.playlist) != 3:
        for station in stations:
            player.playlist_append(stations[station]['url'])
        player.playlist_pos = 0

def set_radio_mode():
    global playback_mode

    while True:
        playback_mode = 0
        sleep(2)
        if playback_mode == 0:
            restart_streaming()


rdr = RFID()
sockid = lirc.init("radio")
player = mpv.MPV()
player.wait_for_property('idle-active')
playback_mode = 0 # 0 = radio, 1 = cd, 2 = bt

restart_streaming()

player_thread = threading.Thread(target=play_stream)
player_thread.start()

tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()

set_mode_thread = threading.Thread(target=set_radio_mode)
set_mode_thread.start()

player.volume = 100

sys.exit(0)
