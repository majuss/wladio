
from time import sleep

import mpv
import threading
import time
import subprocess
import sys


import constants as CONST
import utils as utils
import display as display
from enums import *

from control import *
import weather as weather
import infrared as infrared
import rfid as rfid

import buttons

import radio as radio

# create logger
logger = utils.create_logger('main')

STATE = utils.state()


# Load stations and music library file
stations, music_lib = utils.openFiles()


def get_current_station(player, stations):  # todo function name should add _key
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return station


def get_station_obj(station_name):
    return stations[station_name]


def print_tags():
    while True:
        sleep(1)

        if utils.state()['playback_mode'] is PlaybackMode.Radio:
            try:
                player = radio.get_player()

                if player.metadata is not None and 'icy-title' in player.metadata:  # soemtimes buggy
                    station = get_station_obj(
                        get_current_station(player, stations))
                    tag = player.metadata['icy-title']

                    # print(tag)

                    if tag in station['skip_strings']:
                        tag = station['name']

                    display.tag_text(tag)

            except Exception as e:
                logger.debug(
                    "Couldn't run the icy_title while loop in print tags:")
                logger.debug(e)

        if utils.state()['playback_mode'] is PlaybackMode.CD:
            try:
                player = radio.get_player()

                txt = '(' + str(player.playlist_pos + 1) + \
                    '/' + str(player.playlist_count) + ')'

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


def bt_handler():
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    from gi.repository import GLib

    DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    def device_property_changed(interface, changed, invalidated, path):
        global playback_mode

        iface = interface[interface.rfind(".") + 1:]
        if iface == "Device1":
            if "Connected" in changed:
                if changed["Connected"]:
                    volume_mute()
                    playback_mode = PlaybackMode.BT
                    logger.debug('Radio mode set to Bluetooth')

                    utils.state()['draw_bluetooth_icon'] = True
                    display.hard_refresh_top_viewport()
                else:
                    logger.debug('Radio mode set to Radio')
                    playback_mode = PlaybackMode.Radio
                    volume_unmute()

                    utils.state()['draw_bluetooth_icon'] = False
                    display.hard_refresh_top_viewport()
        elif iface == "MediaPlayer1":
            if "Track" in changed:
                track = changed['Track']
                txt = []

                if 'Title' in track:
                    txt.append(track['Title'])
                if 'Artist' in track:
                    txt.append(track['Artist'])
                if 'Album' in track:
                    txt.append(track['Album'])

                txt = ' - '.join(txt)

                logger.debug(
                    "BT track has changed to : {} detected".format(txt))
                display.main_text(txt)

    bus.add_signal_receiver(
        device_property_changed,
        bus_name='org.bluez',
        signal_name='PropertiesChanged',
        dbus_interface='org.freedesktop.DBus.Properties',
        path_keyword='path'
    )

    loop = GLib.MainLoop()
    loop.run()



# C O N T R O L S START

def volume_unmute():
    player = radio.get_player()
    player.mute = False
    STATE['muted'] = False


def volume_mute():
    player = radio.get_player()
    player.mute = True
    STATE['muted'] = True


# C O N T R O L S END


subprocess.call(["bluetoothctl", "discoverable", "on"])
subprocess.call(["bluetoothctl", "pairable", "on"])

playback_mode = PlaybackMode.Radio


tag_thread = threading.Thread(target=print_tags)
tag_thread.start()


bt_thread = threading.Thread(target=bt_handler)
bt_thread.start()

weather.start_thread()


def _set_initial_state_and_setup():
    if STATE['power_state'] is PowerState.Powered:  # power state on
        infrared.start_thread()
        rfid.start_thread()

    display.initalize()

    radio.check_start()


_set_initial_state_and_setup()

sys.exit(0)
