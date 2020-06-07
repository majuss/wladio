from pirc522 import RFID
from enum import Enum
from time import sleep

import mpv
import threading
import sys
import lirc
import math
import logging
import time
import subprocess
import RPi.GPIO as GPIO

import constants
import utils as utils
import display as display
import sensors_dummy as sensors

# create logger
logger = logging.getLogger('radio')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

GPIO.setmode(GPIO.BCM)

FRAMES = constants.FPS

# Load stations and music library file
stations, music_lib = utils.openFiles()


class PlaybackMode(Enum):
    Radio = 1
    CD = 2
    BT = 3


temps = []


def setup_buttons(next_btn, prev_btn, pause_btn, garage_door, driveway, unknown, power, vol_clk, vol_dt, vol_sw):

    GPIO.setup(next_btn, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(prev_btn, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(pause_btn, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(garage_door, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(driveway, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(unknown, GPIO.IN, GPIO.PUD_UP)

    GPIO.setup(power, GPIO.IN, GPIO.PUD_DOWN)

    GPIO.setup(vol_clk, GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(vol_dt, GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(vol_sw, GPIO.IN, GPIO.PUD_UP)

    def callback_next_btn(channel):
        print('NEXT BTN')
        player_playlist_next(get_current_player())

    def callback_prev_btn(channel):
        print('PREV BTN')
        player_playlist_prev(get_current_player())

    def callback_pause_btn(channel):
        player_toggle_play_pause(get_current_player())

    def callback_garage_door(channel):
        logger.debug("callie garage_door")

    def callback_driveway(channel):
        logger.debug("callie driveway")

    def callback_unknown(channel):
        logger.debug("callie unknown")

    def callback_power(channel):
        global playback_mode

        sleep(0.01)
        player = get_current_player()
        if GPIO.input(channel):
            if playback_mode == PlaybackMode.Radio:
                player.playlist_pos = 0
                player.pause = False
            if playback_mode == PlaybackMode.CD:
                player.pause = False
            subprocess.call(["rfkill", "unblock", "bluetooth"])
            logger.debug("player resumed")
        else:
            if playback_mode == PlaybackMode.Radio:
                player.stop = True
            if playback_mode == PlaybackMode.CD:
                player.pause = True
            display.main_text('standby')
            subprocess.call(["rfkill", "block", "bluetooth"])
            logger.debug("player stopped")

    direction = True
    clk_last = 0
    clk_current = 0
    clk_last = GPIO.input(vol_clk)

    def callback_vol(null):
        clk_current = GPIO.input(vol_clk)
        if clk_current != clk_last:
            if GPIO.input(vol_dt) != clk_current:
                direction = True
            else:
                direction = False
            if direction:
                volume_change(1)  # volume change up
            else:
                volume_change(-1)  # volume change down

    def callback_vol_sw(null):
        volume_mute_toggle()  # volume mute toggle

    GPIO.add_event_detect(next_btn, GPIO.FALLING,
                          callback=callback_next_btn, bouncetime=350)
    GPIO.add_event_detect(prev_btn, GPIO.FALLING,
                          callback=callback_prev_btn, bouncetime=350)
    GPIO.add_event_detect(pause_btn, GPIO.FALLING,
                          callback=callback_pause_btn, bouncetime=350)
    GPIO.add_event_detect(garage_door, GPIO.FALLING,
                          callback=callback_garage_door, bouncetime=350)
    GPIO.add_event_detect(driveway, GPIO.FALLING,
                          callback=callback_driveway, bouncetime=350)
    GPIO.add_event_detect(unknown, GPIO.FALLING,
                          callback=callback_unknown, bouncetime=350)

    GPIO.add_event_detect(
        power, GPIO.BOTH, callback=callback_power, bouncetime=250)

    GPIO.add_event_detect(vol_clk, GPIO.BOTH,
                          callback=callback_vol, bouncetime=1)
    GPIO.add_event_detect(vol_sw, GPIO.FALLING,
                          callback=callback_vol_sw, bouncetime=350)


def get_current_station(player, stations):  # todo function name should add _key
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return station


def get_station_obj(station_name):
    return stations[station_name]


def get_current_station_name(player, stations):
    url = player.playlist[player.playlist_pos]['filename']
    for station in stations:
        if url == stations[station]['url']:
            return stations[station]['name']
    return 'NO STATION FOUND'


def get_current_player():
    if playback_mode == PlaybackMode.Radio:
        return radioPlayer
    if playback_mode == PlaybackMode.CD:
        return cdPlayer
    # if playback_mode == playback_mode.BT:
    #     return btPlayer


def print_tags():
    last_tag = ''
    global playback_mode

    while True:
        sleep(1)

        if playback_mode == PlaybackMode.Radio:
            try:
                if radioPlayer.metadata is not None and 'icy-title' in radioPlayer.metadata:  # soemtimes buggy
                    station = get_station_obj(
                        get_current_station(radioPlayer, stations))
                    tag = radioPlayer.metadata['icy-title']
                    print('tag:  "' + tag + '"')

                    if tag in station['skip_strings']:
                        tag = station['name']

                    display.tag_text(tag)

            except Exception as e:
                logger.debug(
                    "Couldn't run the icy_title while loop in print tags:")
                logger.debug(e)

        if playback_mode is PlaybackMode.CD:
            try:
                player = get_current_player()
                display.tag_text(
                    player.metadata['title'] + ' - ' + player.metadata['artist'])
                logger.debug("CD tag is : {}".format(
                    player.metadata['title'], player.metadata['artist']))

            except:
                pass
                logger.error("Couldn't get CD tag")


def infrared_handler():
    # import pulseio
    # import adafruit_irremote

    # pulses = pulseio.PulseIn(22, maxlen=200, idle_state=False)
    # decoder = adafruit_irremote.GenericDecode()

    # while True:
    #     # pulse = decoder.read_pulses(pulses)
    #     # print(pulse)
    #     try:
    #         for pulse in pulses:
    #             print(pulse)
    #     except Exception as e:
    #         print(e)

    #     sleep(0.1)

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
                logger.debug("Next IR track")
                player_playlist_next(player)

            if "prev" in codeIR:
                diff_time = time.time() - last_prev
                last_prev = time.time()

                if 2 < diff_time and diff_time < 10:  # only when two button presses occure in a time frame from greater 2 and smaller 10 seconds
                    player.seek(-15)
                elif diff_time < 2:
                    player_playlist_prev(player)

            if "menu" in codeIR:
                volume_mute_toggle()

            if "play" in codeIR:
                player_toggle_play_pause(player)
        sleep(0.1)


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
                    print('SET MODE TO BT')
                    display.set_bt_status(True)
                else:
                    print('SET MODE TO RADIO')
                    playback_mode = PlaybackMode.Radio
                    volume_unmute()
                    display.set_bt_status(False)
        elif iface == "MediaPlayer1":
            print(changed)
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


def rfid_handler():
    global playback_mode
    global cdPlayer

    cdPlayer = mpv.MPV(loop_playlist='inf')
    cdPlayer.volume = constants.CD_PLAYER_START_VOL

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
                            cdPlayer.play(
                                constants.MUSIC_LIB_PATH + music_lib[rfid])
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
                    last_stop = time.time()

                    # switch back to radio
                    radioPlayer.mute = False
                    playback_mode = PlaybackMode.Radio

    except KeyboardInterrupt:
        rdr.cleanup()
        raise


# C O N T R O L S START
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


def volume_change(amount):
    print("change volume", amount)
    player = get_current_player()

    try:
        player.volume = player.volume + amount
        if player.volume > 100:
            player.volume = 100  # restrict to 100 .volume can go up to 999 until it throws exception
        display.overlay_rect(int(256 / 100 * player.volume), 1)
    except:
        pass
        logger.debug("Volume limit reached")


def volume_mute_toggle():
    player = get_current_player()
    player.mute = not player.mute

def volume_unmute():
    player = get_current_player()
    player.mute = False

def volume_mute():
    player = get_current_player()
    player.mute = True

def player_toggle_play_pause(player):
    player.pause = not player.pause

# C O N T R O L S END


def sensor_handler():
    global temps
    while True:
        bme280, bme680 = sensors.get_data()
        temps = [bme280, bme680]
        print(temps)
        sleep(60)


def setup_radio(player, stations):
    player.stop = True

    for station in stations:
        player.playlist_append(stations[station]['url'])
    player.playlist_pos = 0


rdr = RFID()
sockid = lirc.init("radio", blocking=True)
radioPlayer = mpv.MPV()
radioPlayer.volume = constants.RADIO_PLAYER_START_VOL
cdPlayer = ''

playback_mode = PlaybackMode.Radio

setup_buttons(
    4,  # next_btn
    12,  # prev_btn
    19,  # pause_btn
    20,  # garage_door
    21,  # driveway
    27,  # unknown
    23,  # power
    5,  # vol clock
    6,  # vol dt
    13,  # vol sw
)

setup_radio(radioPlayer, stations)

tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()

bt_thread = threading.Thread(target=bt_handler)
bt_thread.start()

sensor_thread = threading.Thread(target=sensor_handler)
sensor_thread.start()


def test_func_vol():
    sleep(10)

    player_playlist_next(radioPlayer)

    sleep(3)
    player_playlist_next(radioPlayer)


test_thread = threading.Thread(target=test_func_vol)
# test_thread.start()  # for debugging


logger.debug("Init done")
sleep(2)

sys.exit(0)
