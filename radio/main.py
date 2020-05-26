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
import subprocess


import utils as utils
import display as display
# import sensors as sensors

# create logger
logger = logging.getLogger('radio')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

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
    return 'NO STATION FOUND'


def print_tags():
    last_tag = ''
    global playback_mode

    while True:
        # print("tag loop")
        sleep(1)

        if playback_mode == PlaybackMode.Radio:
            try:
                # print('Radio tags:')
                # if radioPlayer.metadata is not None:
                #     print(radioPlayer.metadata)

                if radioPlayer.metadata is not None and 'icy-title' in radioPlayer.metadata:  # soemtimes buggy
                    tag = radioPlayer.metadata['icy-title']
                    display.main_text(tag)

            except Exception as e:
                logger.debug(
                    "Couldn't run the icy_title while loop in print tags:")
                logger.debug(e)

        if playback_mode is PlaybackMode.CD:
            try:
                player = get_current_player()
                display.main_text(
                    player.metadata['title'] + ' - ' + player.metadata['artist'])
                logger.debug("CD tag is : {}".format(
                    player.metadata['title'], player.metadata['artist']))

            except:
                pass
                logger.error("Couldn't get CD tag")


def infrared_handler():
    lastCode = ''
    last_prev = 0
    global playback_mode

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
                player_playlist_next(player)

            if "prev" in codeIR:
                diff_time = time.time() - last_prev
                last_prev = time.time()

                if 2 < diff_time and diff_time < 10:  # only when two button presses occure in a time frame from greater 2 and smaler 10 seconds
                    player.seek(-15)
                elif diff_time < 2:
                    player_playlist_prev(player)

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
                track = changed['Track']
                logger.debug("BT track has cahnged to : {}, {}, {} detected".format(
                    track['Title'], track['Artist'], track['Album']))
                display.main_text(
                    track['Title'] + ' - ' + track['Artist'] + ' - ' + track['Album'])

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
                logger.debug("Tag with UID: {} detected".format(uid))
                if not error:
                    rfid = str(utils.uid_to_num(uid))
                    last_time_tag_detected = True

                    if playback_mode != PlaybackMode.CD:

                        radioPlayer.mute = True

                        if time.time() - last_stop > 60:
                            cdPlayer.pause = False
                            cdPlayer.play(music_lib_path + music_lib[rfid])
                            logger.debug(
                                "CD Player started fresh with playlist: {}".format(cdPlayer.playlist))
                        else:
                            cdPlayer.pause = False
                            logger.debug(
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

        if state and not last_state:  # turned radio on
            if playback_mode == PlaybackMode.Radio:
                player.playlist_pos = 0
                player.pause = False
            if playback_mode == PlaybackMode.CD:
                player.pause = False
            last_state = state
            subprocess.call(["rfkill", "unblock", "bluetooth"])
            print("player resumed")

        if not state and last_state:  # turned radio off
            if playback_mode == PlaybackMode.Radio:
                player.stop = True
            if playback_mode == PlaybackMode.CD:
                player.pause = True
            display.main_text('standby')
            last_state = state
            subprocess.call(["rfkill", "block", "bluetooth"])
            print("player stopped")


# prev / next control
def player_playlist_prev(player):
    try:
        player.playlist_prev()
    except:
        # Skip to last position
        player.playlist_pos = len(player.playlist) - 1
    finally:
        if playback_mode == PlaybackMode.Radio:
            display.main_text(get_current_station_name(radioPlayer, stations))


def player_playlist_next(player):
    try:
        player.playlist_next()
    except:
        print('reached end of playlist')
        player.playlist_pos = 0  # Skip to first position when end is reached
    finally:
        if playback_mode == PlaybackMode.Radio:
            display.main_text(get_current_station_name(radioPlayer, stations))


def volume_knob_switch_callback():
    volume_mute()


def volume_dec_callback(ka):
    volume_change(1)


def volume_inc_callback(ka):
    volume_change(-1)


def volume_change(amount):
    print("change volumen", amount)
    player = get_current_player()

    try:
        player.volume = player.volume + amount
        if player.volume > 100:
            player.volume = 100  # restrict to 100 .volume can go up to 999 until it throws exception
        display.overlay_rect(int(256 / 100 * player.volume), 1)
    except:
        pass
        logger.debug("Volume limit reached")


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

# volume handler
my_encoder = pyky040.Encoder(CLK=5, DT=6, SW=13)
my_encoder.setup(scale_min=0, scale_max=100, step=1, dec_callback=volume_dec_callback,
                 inc_callback=volume_inc_callback, sw_callback=volume_knob_switch_callback)


def volume_knob_handler():
    my_encoder.watch()


volume_thread = threading.Thread(target=volume_knob_handler)
volume_thread.start()
# volume handler


playback_mode = PlaybackMode.Radio

setup_radio(radioPlayer, stations)

tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()


bt_thread = threading.Thread(target=bt_handler)
bt_thread.start()


def test_func_vol():
    sleep(10)

    player_playlist_next(radioPlayer)

    sleep(3)
    player_playlist_next(radioPlayer)


test_thread = threading.Thread(target=test_func_vol)
test_thread.start()  # for debugging

# power_state_thread = threading.Thread(target=power_state_handler)
# power_state_thread.start()

logger.debug("Init done")
sleep(2)

sys.exit(0)
