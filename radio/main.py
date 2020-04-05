import mpv
import threading
from time import sleep
import sys
# import lirc
from pirc522 import RFID
from enum import Enum

import lib as lib

# Load stations file
stations, music_lib = lib.openFiles()



class PlaybackMode(Enum):
    Radio = 1
    CD = 2
    BT = 3


def play_stream():
    while True:
        radioPlayer.wait_for_property('core-idle', lambda x: not x)
        radioPlayer.wait_for_property('core-idle')

def get_current_station(player, stations):
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return station

def get_current_station_name(player, stations):
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return stations[station]['name']

def print_tags():
    last_tag = ''
    global playback_mode

    while True:
        if  playback_mode == PlaybackMode.Radio:
            print(get_current_station_name(radioPlayer, stations))
            while radioPlayer.metadata is not None and "icy-title" in radioPlayer.metadata:
                current_station = get_current_station(radioPlayer, stations)
                tag = radioPlayer.metadata['icy-title']
                if last_tag != radioPlayer.metadata['icy-title'] and radioPlayer.metadata['icy-title'] not in stations[current_station]['skip_strings']:
                    for replace_string in stations[current_station]['replace_strings']:
                        tag = tag.replace(replace_string, '').lstrip()
                    print(tag)
                    last_tag = radioPlayer.metadata['icy-title']
                sleep(1)
            sleep(1)

        if playback_mode == PlaybackMode.CD:
            try:
                print(radioPlayer.metadata['title'] + ' - ' + radioPlayer.metadata['artist']) 
            except:
                print('ex')
            sleep(1)

def infrared_handler():
    while True:
        codeIR = '' # lirc.nextcode()
        if "up" in codeIR:
            print("UP")
            radioPlayer.volume = radioPlayer.volume + 2
        if "down" in codeIR:
            print("DOWN")
            radioPlayer.volume = radioPlayer.volume - 2
        if "next" in codeIR:
            print("NEXT")
            try:
                radioPlayer.playlist_next()
            except:
                print("No next title")
        if "prev" in codeIR:
            print("PREV")
            try:
                radioPlayer.playlist_prev()
            except:
                print("No prev title")
        if "menu" in codeIR:
            radioPlayer.mute = not radioPlayer.mute
            print("MENU")
        if "play" in codeIR:
            print("PLAY")
            radioPlayer.pause = not radioPlayer.pause
        sleep(0.1)

def rfid_handler():
    global playback_mode

    cdPlayer = mpv.MPV(loop_playlist='inf')
    cdPlayer.volume = 100






    # @cdPlayer.property_observer('eof-reached')
    # def time_observer(name, value):
    #     print('eof-reached')
    #     print(name)
    #     print(value)

    # @cdPlayer.event_callback('end-file')
    # def my_handler(event):
    #     print('EVENT <<---------------')
    #     print('end-file')

    #     global playback_mode

    #     cdPlayer.command('stop')

    #     # switch back to radio
    #     radioPlayer.pause = False
    #     playback_mode = PlaybackMode.Radio

    try:
        while True:
            sleep(1)
            print("rfid loop")

            last_time_tag_detected = False

            rdr.wait_for_tag()
            (error, tag_type) = rdr.request()
            if not error:
                print("Tag detected")
                (error, uid) = rdr.anticoll()
                print("tag uuid")
                print(uid)
                if not error:
                    rfid = str(uid_to_num(uid))

                    last_time_tag_detected = True

                    if playback_mode != PlaybackMode.CD:

                        print('play rfid title')

                        radioPlayer.pause = True

                        cdPlayer.play('/home/pi/wladio/voy_core_1.mp3')

                    playback_mode = PlaybackMode.CD
                    sleep(1)

            else:
                print("error in rdr request")
                print(error)
                # resume radio?

            if playback_mode == PlaybackMode.CD:
                # tag was removed or track finished playing
                if last_time_tag_detected == False:
                    cdPlayer.command('stop')

                    # switch back to radio
                    radioPlayer.pause = False
                    playback_mode = PlaybackMode.Radio


    except KeyboardInterrupt:
        rdr.cleanup()
        raise

def uid_to_num(uid):
    n = 0
    for i in range(0, 5):
        n = n * 256 + uid[i]
    return n



def setup_radio(player, stations):
    player.stop = True
    
    for station in stations:
        player.playlist_append(stations[station]['url'])
    player.playlist_pos = 0




def set_radio_mode():
    global playback_mode
    
    playback_mode = PlaybackMode.Radio

    while True:
        sleep(2)
        if playback_mode == PlaybackMode.Radio:
            restart_streaming()


rdr = RFID()
# sockid = lirc.init("radio")
radioPlayer = mpv.MPV()
radioPlayer.volume = 100
playback_mode = PlaybackMode.Radio

setup_radio(radioPlayer, stations)



# whats this???
# set_mode_thread = threading.Thread(target=set_radio_mode)
# set_mode_thread.start()

# radioPlayer.wait_for_property('idle-active')


# whats this???
# player_thread = threading.Thread(target=play_stream)
# player_thread.start()



sleep(5)




tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()



sys.exit(0)
