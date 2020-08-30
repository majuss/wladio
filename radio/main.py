
from time import sleep

import threading
import sys


import buttons

import constants as CONST
import utils as utils
import display as display
from enums import *

from control import *
import weather as weather
import infrared as infrared
import rfid as rfid
import bluetooth as bluetooth
import radio as radio
import power as power
import speakers as speakers


logger = utils.create_logger('main')
STATE = utils.state()


# Load stations and music library file
stations, music_lib = utils.openFiles()

def get_station_object_by_player(player, stations):
    return stations[player.playlist_pos]


def print_tags():
    while True:
        sleep(1)

        if STATE['playback_mode'] is PlaybackMode.Radio:
            try:
                player = radio.get_player()

                if player.metadata is not None and 'icy-title' in player.metadata:  # soemtimes buggy
                    station = get_station_object_by_player(player, stations)
                    tag = player.metadata['icy-title']
                    # print(tag)

                    if tag in station['skip_strings']:
                        tag = station['name']

                    display.tag_text(tag)

            except Exception as e:
                logger.debug(
                    "Couldn't run the icy_title while loop in print tags:")
                print(e)

        if STATE['playback_mode'] is PlaybackMode.CD:
            try:
                player = radio.get_player()

                txt = str(player.playlist_pos + 1) + \
                    '/' + str(player.playlist_count)

                txts = []
                if 'title' in player.metadata:
                    txts.append(player.metadata['title'])
                if 'artist' in player.metadata:
                    txts.append(player.metadata['artist'])
                txts = txt + ' ' + ' - '.join(txts)

                display.tag_text(txts)
                # logger.debug("CD tag is : {}".format(txts))

            except:
                pass
                logger.error("Couldn't get CD tag")


tag_thread = threading.Thread(target=print_tags)
tag_thread.start()


weather.start_thread()
bluetooth.start_thread()
power.start_thread()


def _set_initial_state_and_setup():
    display.initalize()

    if STATE['power_state'] is PowerState.Powered:  # power state on
        infrared.start_thread()
        rfid.start_thread()
        radio.leave_standby()
        speakers.on()


_set_initial_state_and_setup()

sys.exit(0)
