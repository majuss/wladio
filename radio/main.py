from pyky040 import pyky040
import mpv
import threading
from time import sleep
import sys
import lirc
from pirc522 import RFID
from enum import Enum
import math
import logging
import time


import utils as utils
import display as display
# import sensors as sensors

LOG_LEVEL = logging.DEBUG
LOG_FILE = "/home/pi/log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)

frames = 60

# Load stations and music library file
stations, music_lib = utils.openFiles()
music_lib_path = '/home/pi/'


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
    # global display_dict

    while True:
        # print("tag loop")
        if playback_mode == PlaybackMode.Radio:
            # display_dict['display_text'] = get_current_station_name(radioPlayer, stations)
            display.fixed_text(get_current_station_name(radioPlayer, stations))

            while radioPlayer.metadata is not None and "icy-title" in radioPlayer.metadata:
                current_station = get_current_station(radioPlayer, stations)
                tag = radioPlayer.metadata['icy-title']
                if last_tag != radioPlayer.metadata['icy-title'] and radioPlayer.metadata['icy-title'] not in stations[current_station]['skip_strings']:
                    for replace_string in stations[current_station]['replace_strings']:
                        tag = tag.replace(replace_string, '').lstrip()
                    logging.debug("New tag is : {}".format(tag))
                    display.fixed_text(tag)
                    # display_dict['display_text'] = tag
                    last_tag = radioPlayer.metadata['icy-title']
                sleep(4/frames)
            sleep(4/frames)

        if playback_mode is PlaybackMode.CD:
            try:
                player = get_current_player()
                # display_dict['display_text'] = player.metadata['title'] + ' - ' + player.metadata['artist']
                display.fixed_text(
                    player.metadata['title'] + ' - ' + player.metadata['artist'])
                logging.debug("CD tag is : {}".format(
                    player.metadata['title'], player.metadata['artist']))

            except:
                pass
                logging.error("Couldn't get CD tag")
            sleep(4/frames)


def infrared_handler():
    lastCode = ''
    global playback_mode
    # global display_dict

    while True:
        player = get_current_player()
        codeIR = lirc.nextcode()
        if "up" in codeIR or "down" in codeIR or lastCode == "up" or lastCode == "down":
            if len(codeIR) == 0:
                codeIR.append(lastCode)
            if "up" in codeIR:
                volume_change(2)
            if "down" in codeIR:
                volume_change(-2)
            lastCode = codeIR[0]
        else:
            if "next" in codeIR:
                try:
                    player.playlist_next()
                except:
                    player.playlist_pos = 0  # Skip to first position when end is reached
            if "prev" in codeIR:
                try:
                    player.playlist_prev()
                except:
                    # Skip to last position
                    player.playlist_pos = len(player.playlist) - 1
            if "menu" in codeIR:
                volume_mute()
            if "play" in codeIR:
                player.pause = not player.pause
        sleep(0.1)


def bt_handler():
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    from gi.repository import GLib
    global playback_mode

    DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    def device_property_changed(interface, changed, invalidated, path):
        iface = interface[interface.rfind(".") + 1:]
        if iface == "Device1":
            if "Connected" in changed:
                if changed["Connected"]:
                    playback_mode.BT
                    volume_mute()
                else:
                    playback_mode.Radio
                    volume_mute()
        elif iface == "MediaPlayer1":
            if "Track" in changed:
                track = changed["track"]
                logging.debug("BT track has cahnged to : {}, {}, {} detected".format(
                    track["Title"], track["Artist"], track["Album"]))
                display.fixed_text(
                    track["Title"] + " - " + track["Artist"] + " - " + track["Album"])

    bus.add_signal_receiver(
        device_property_changed,
        bus_name='org.bluez',
        signal_name='PropertiesChanged',
        dbus_interface='org.freedesktop.DBus.Properties',
        path_keyword='path'
    )

    loop = GLib.MainLoop()
    loop.run()


def rfid_handler():
    global playback_mode
    global cdPlayer

    cdPlayer = mpv.MPV(loop_playlist='inf')
    cdPlayer.volume = 30

    last_stop = 0

    try:
        while True:
            sleep(1)

            last_time_tag_detected = False

            rdr.wait_for_tag()
            (error, tag_type) = rdr.request()
            if not error:
                (error, uid) = rdr.anticoll()
                logging.debug("Tag with UID: {} detected".format(uid))
                if not error:
                    rfid = str(utils.uid_to_num(uid))
                    last_time_tag_detected = True

                    if playback_mode != PlaybackMode.CD:

                        radioPlayer.mute = True

                        if time.time() - last_stop > 60:
                            cdPlayer.pause = False
                            cdPlayer.play(music_lib_path + music_lib[rfid])
                            logging.debug(
                                "CD Player started fresh with playlist: {}".format(cdPlayer.playlist))
                        else:
                            cdPlayer.pause = False
                            logging.debug(
                                "CD Player resumed with old playlist: {}".format(cdPlayer.playlist))

                    playback_mode = PlaybackMode.CD

            # else:
            #     print("error in rdr request")
            #     # resume radio?

            if playback_mode == PlaybackMode.CD:
                # tag was removed or track finished playing
                if last_time_tag_detected is False:
                    cdPlayer.pause = True
                    last_stop = int(time.time())

                    # switch back to radio
                    radioPlayer.mute = False
                    playback_mode = PlaybackMode.Radio

    except KeyboardInterrupt:
        rdr.cleanup()
        raise

def power_state_handler():
    import RPi.GPIO as GPIO
    global playback_mode

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)

    last_state = GPIO.input(12)
    while True:
        state = GPIO.input(12)
        sleep(0.1)
        player = get_current_player()

        if state and not last_state: # turned radio on
            if playback_mode == PlaybackMode.Radio:
                player.playlist_pos = 0
            if playback_mode == PlaybackMode.CD:
                player.pause = False
            last_state = state
            print("player resumed")

        if not state and last_state: # turned radio off
            if playback_mode == PlaybackMode.Radio:
                player.stop = True
            if playback_mode == PlaybackMode.CD:
                player.pause = True
            display.fixed_text("standby")
            last_state = state
            print("player stopped")


def volume_knob_handler():
    my_encoder.watch()


def volume_knob_switch_callback():
    volume_mute()


def volume_dec_callback(ka):
    volume_change(1)


def volume_inc_callback(ka):
    volume_change(-1)


def volume_change(amount):
    player = get_current_player()
    # display.add_text('rect', 0.5)
    # display_dict['display_text'] = 'rect'
    try:
        player.volume = player.volume + amount
    except:
        pass
        logging.debug("Volume limit reached")


def volume_mute():
    player = get_current_player()
    player.mute = not player.mute


def setup_radio(player, stations):
    player.stop = True

    for station in stations:
        player.playlist_append(stations[station]['url'])
    player.playlist_pos = 0


def get_current_player():
    if playback_mode == playback_mode.Radio:
        return radioPlayer
    if playback_mode == playback_mode.CD:
        return cdPlayer
    # if playback_mode == playback_mode.BT:
    #     return btPlayer


rdr = RFID()
sockid = lirc.init("radio", blocking=True)
radioPlayer = mpv.MPV()
radioPlayer.volume = 25
cdPlayer = ''

my_encoder = pyky040.Encoder(CLK=5, DT=6, SW=13)
my_encoder.setup(scale_min=0, scale_max=100, step=1, dec_callback=volume_dec_callback,
                 inc_callback=volume_inc_callback, sw_callback=volume_knob_switch_callback)

playback_mode = PlaybackMode.Radio

setup_radio(radioPlayer, stations)

tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()

volume_thread = threading.Thread(target=volume_knob_handler)
volume_thread.start()

bt_thread = threading.Thread(target=bt_handler)
bt_thread.start()

power_state_thread = threading.Thread(target=power_state_handler)
power_state_thread.start()

logging.debug("Init done")
sleep(2)

sys.exit(0)
