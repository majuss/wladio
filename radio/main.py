from pirc522 import RFID
from enum import Enum
from time import sleep

import mpv
import threading
import sys
import lirc
import logging
import time
import subprocess
import RPi.GPIO as GPIO

import constants as CONST
import utils as utils
import display as display
import weather as weather

# create logger
logger = logging.getLogger('radio')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

GPIO.setmode(GPIO.BCM)


# Load stations and music library file
stations, music_lib = utils.openFiles()


class PlaybackMode(Enum):
    Radio = 1
    CD = 2
    BT = 3


power_last = 0  # when was power button last pressed?


def setup_buttons(BUTTON_MAPPING):

    GPIO.setup(BUTTON_MAPPING['next_btn'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_MAPPING['prev_btn'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_MAPPING['pause_btn'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_MAPPING['garage_door'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_MAPPING['driveway'], GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(BUTTON_MAPPING['unknown'], GPIO.IN, GPIO.PUD_UP)

    GPIO.setup(BUTTON_MAPPING['power'], GPIO.IN, GPIO.PUD_DOWN)

    GPIO.setup(BUTTON_MAPPING['vol_clk'], GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_MAPPING['vol_dt'], GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_MAPPING['vol_sw'], GPIO.IN, GPIO.PUD_UP)

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
        global power_last

        if time.time() - power_last < 2:
            print('power button pressed < 2 secs')
            return

        power_last = time.time()

        sleep(0.01)
        player = get_current_player()

        logger.debug('Power state set to: {}'.format(GPIO.input(channel)))

        if GPIO.input(channel):  # standby is off GPIO is HIGH
            if playback_mode == PlaybackMode.Radio:
                player.pause = False
            if playback_mode == PlaybackMode.CD:
                player.pause = False
            display.set_standby_onoff(False)
            subprocess.call(["rfkill", "unblock", "bluetooth"])
            logger.debug("player resumed")
        else:  # standby is ON GPIO is LOW
            try:
                if playback_mode == PlaybackMode.Radio:
                    player.stop = True
                if playback_mode == PlaybackMode.CD:
                    player.pause = True
                display.set_standby_onoff(True)
                subprocess.call(["rfkill", "block", "bluetooth"])
                logger.debug("player stopped")
            except Exception as e:
                logger.warning('Set power state failed {}'.format(e))
        # 2020-06-13 19:20:16,369 WARNING Set power state failed list.remove(x): x not in list
    direction = True
    clk_last = 0
    clk_current = 0
    clk_last = GPIO.input(BUTTON_MAPPING['vol_clk'])

    def callback_vol(null):
        global clk_current
        global direction

        clk_current = GPIO.input(BUTTON_MAPPING['vol_clk'])
        if clk_current != clk_last:
            if GPIO.input(BUTTON_MAPPING['vol_dt']) != clk_current:
                direction = True
            else:
                direction = False
            if direction:
                volume_change(CONST.VOL_KNOB_SPEED)  # volume change up
            else:
                volume_change(-CONST.VOL_KNOB_SPEED)  # volume change down

    def callback_vol_sw(null):
        volume_mute_toggle()  # volume mute toggle

    GPIO.add_event_detect(BUTTON_MAPPING['next_btn'], GPIO.FALLING,
                          callback=callback_next_btn, bouncetime=350)
    GPIO.add_event_detect(BUTTON_MAPPING['prev_btn'], GPIO.FALLING,
                          callback=callback_prev_btn, bouncetime=350)
    GPIO.add_event_detect(BUTTON_MAPPING['pause_btn'], GPIO.FALLING,
                          callback=callback_pause_btn, bouncetime=350)
    GPIO.add_event_detect(BUTTON_MAPPING['garage_door'], GPIO.FALLING,
                          callback=callback_garage_door, bouncetime=350)
    GPIO.add_event_detect(BUTTON_MAPPING['driveway'], GPIO.FALLING,
                          callback=callback_driveway, bouncetime=350)
    GPIO.add_event_detect(BUTTON_MAPPING['unknown'], GPIO.FALLING,
                          callback=callback_unknown, bouncetime=350)

    GPIO.add_event_detect(
        BUTTON_MAPPING['power'], GPIO.BOTH, callback=callback_power, bouncetime=250)

    GPIO.add_event_detect(BUTTON_MAPPING['vol_clk'], GPIO.BOTH,
                          callback=callback_vol, bouncetime=1)
    GPIO.add_event_detect(BUTTON_MAPPING['vol_sw'], GPIO.FALLING,
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
    global playback_mode

    while True:
        sleep(1)

        if playback_mode is PlaybackMode.Radio:
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


def infrared_handler():
    global playback_mode
    lastCode = ''
    last_prev = 0

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
                    logger.debug('Radio mode set to Bluetooth')
                    display.set_bt_status(True)
                else:
                    logger.debug('Radio mode set to Radio')
                    playback_mode = PlaybackMode.Radio
                    volume_unmute()
                    display.set_bt_status(False)
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


def rfid_handler():
    global playback_mode
    global cdPlayer

    cdPlayer = mpv.MPV(loop_playlist='inf')
    cdPlayer.volume = CONST.CD_PLAYER_START_VOL

    last_stop = 0

    try:
        while True:
            sleep(1)

            last_time_tag_detected = False

            rdr.wait_for_tag()
            (error, tag_type) = rdr.request()
            if not error:
                (error, uid) = rdr.anticoll()
                # logger.debug("Tag with UID: {} detected".format(uid))
                if not error:
                    rfid = str(utils.uid_to_num(uid))
                    last_time_tag_detected = True

                    if playback_mode != PlaybackMode.CD:
                        # TODO: disconnect all bt devices

                        radioPlayer.mute = True

                        diff = time.time() - last_stop  # time since tag was removed

                        if 60 < diff:  # restart cd playback
                            cdPlayer.pause = False
                            cdPlayer.play(
                                CONST.MUSIC_LIB_PATH + music_lib[rfid])
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

def weather_handler():
    rain = weather.get_weather()
    rain = True
    display.set_weather_status(rain)
    logger.debug("Weather set to {}".format(rain))
    sleep(60)

# C O N T R O L S START
def player_playlist_prev(player):
    try:
        player.playlist_prev()
    except Exception as e:
        player.playlist_pos = len(player.playlist) - 1  # Skip to last position
    finally:
        if playback_mode == PlaybackMode.Radio:
            display.main_text(get_current_station_name(radioPlayer, stations))


def player_playlist_next(player):
    try:
        player.playlist_next()
    except Exception as e:
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
    except Exception as e:
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


def setup_radio(player, stations):
    player.stop = True

    for station in stations:
        player.playlist_append(stations[station]['url'])
    player.playlist_pos = CONST.RADIO_INIT_STATION


rdr = RFID()
sockid = lirc.init("radio", blocking=True)
radioPlayer = mpv.MPV()
radioPlayer.volume = CONST.RADIO_PLAYER_START_VOL
cdPlayer = ''
subprocess.call(["bluetoothctl", "discoverable", "on"])
subprocess.call(["bluetoothctl", "pairable", "on"])

playback_mode = PlaybackMode.Radio

setup_buttons(CONST.BUTTON_MAPPING)

setup_radio(radioPlayer, stations)

tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()

bt_thread = threading.Thread(target=bt_handler)
bt_thread.start()

weather_thread = threading.Thread(target=weather_handler)
weather_thread.start()

def test_func_vol():
    sleep(10)

    print('set volume')
    volume_change(2)

    sleep(0.5)
    player_playlist_next(get_current_player())


test_thread = threading.Thread(target=test_func_vol)
test_thread.start()  # for debugging

logger.debug("Init done")

sys.exit(0)
