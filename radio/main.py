from pirc522 import RFID
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
from enums import *

# create logger
logger = logging.getLogger('radio')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

GPIO.setmode(GPIO.BCM)


# Load stations and music library file
stations, music_lib = utils.openFiles()


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
        logger.debug('next button pressed')
        player_playlist_next(get_current_player())

    def callback_prev_btn(channel):
        logger.debug('prev button pressed')
        player_playlist_prev(get_current_player())

    def callback_pause_btn(channel):
        logger.debug('pause button pressed')
        player_toggle_play_pause(get_current_player())

    def callback_garage_door(channel):
        logger.debug('garage door pressed')

    def callback_driveway(channel):
        logger.debug('drive way button pressed')

    def callback_unknown(channel):
        logger.debug('unknown button pressed')

    def callback_power(channel):
        logger.debug('power button pressed')
        global playback_mode

        if time.time() - utils.state()['last_power_button_push'] < 2:
            logger.debug('power button pressed < 2 secs')
            return

        logger.debug('continue to decision')

        utils.state()['last_power_button_push'] = time.time()

        sleep(0.001)
        player = get_current_player()

        logger.debug('Power state set to: {}'.format(GPIO.input(channel)))

        if GPIO.input(channel):  # standby is off GPIO is HIGH
            if playback_mode == PlaybackMode.Radio:
                player.playlist_pos = utils.state()['radio_playlist_position']
            if playback_mode == PlaybackMode.CD:
                player.pause = False

            utils.state()['paused'] = False

            display.set_standby_onoff(False)
            subprocess.call(["rfkill", "unblock", "bluetooth"])
            logger.debug('player resumed')
        else:  # standby is ON GPIO is LOW
            try:
                if playback_mode == PlaybackMode.Radio:
                    logger.debug('stop radio')
                    player.command('stop', 'keep-playlist')
                if playback_mode == PlaybackMode.CD:
                    logger.debug('pause cd')
                    player.pause = True

                utils.state()['paused'] = True

                display.set_standby_onoff(True)
                subprocess.call(["rfkill", "block", "bluetooth"])
                logger.debug('player stopped')
            except Exception as e:

                logger.warning('Set power state failed {}'.format(e))
        # 2020-06-13 19:20:16,369 WARNING Set power state failed list.remove(x): x not in list

    # globals for wheel
    direction = True
    clk_last = 0
    clk_current = 0
    clk_last = GPIO.input(BUTTON_MAPPING['vol_clk'])

    def callback_vol(null):
        global clk_current
        global direction

        clk_current = GPIO.input(BUTTON_MAPPING['vol_clk'])
        if clk_current != clk_last:
            logger.debug('wheel rotated')
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

    return None
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
                    # print('tag:  "' + tag + '"')

                    if tag in station['skip_strings']:
                        tag = station['name']

                    # print(tag)

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
    last_code = ''
    last_prev = 0

    while True:
        player = get_current_player()

        if player is None:
            continue

        codeIR = lirc.nextcode()  # call blocks until IR commands was received

        if 0 == len(codeIR):  # empty array means repeat same code as befores code
            if last_code not in ['up', 'down']:  # for up down we want to proceed
                continue
            codeIR = [last_code]

        last_code = code = codeIR[0]

        # handle IR commands
        if 'up' == code:
            logger.debug('IR: volume up')
            # TODO: use CONST stuff
            volume_change(2)

        elif'down' == code:
            logger.debug('IR: volume down')
            # TODO: use CONST stuff
            volume_change(-2)

        elif 'next' == code:
            logger.debug('IR: next in playlist')
            player_playlist_next(player)

        elif 'prev' == code:
            logger.debug('IR: prev in playlist')
            diff_time = time.time() - last_prev
            last_prev = time.time()

            if 2 < diff_time and diff_time < 10:  # only when two button presses occure in a time frame from greater 2 and smaller 10 seconds
                player.seek(-15)
            elif diff_time < 2:
                player_playlist_prev(player)

        elif 'menu' == code:
            logger.debug('IR: toggle mute')
            volume_mute_toggle()

        elif 'play' == code:
            logger.debug('IR: play / pause player')
            player_toggle_play_pause(player)


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

                        if utils.state()['muted'] is False and utils.state()['paused'] is False:
                            cdPlayer.pause = False

                        if 60 < diff:  # restart cd playback
                            cdPlayer.play(
                                CONST.MUSIC_LIB_PATH + music_lib[rfid])
                            logger.debug(
                                "CD Player started fresh with playlist: {}".format(cdPlayer.playlist))
                        else:
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
                    if utils.state()['muted'] is False and utils.state()['paused'] is False:
                        radioPlayer.mute = False
                    playback_mode = PlaybackMode.Radio

    except KeyboardInterrupt:
        rdr.cleanup()
        raise


def weather_handler():
    rain = weather.get_weather()
    rain = True
    utils.state()['draw_rain_cloud_icon'] = rain
    logger.debug("Weather set to {}".format(rain))
    sleep(60)

# C O N T R O L S START


def player_playlist_prev(player):
    if utils.state()['radio_playlist_position'] - 1 == -1:
        player.playlist_pos = len(player.playlist) - 1
    else:
        player.playlist_prev()

    if playback_mode == PlaybackMode.Radio:
        display.main_text(get_current_station_name(radioPlayer, stations))

    utils.state()['radio_playlist_position'] = player.playlist_pos


def player_playlist_next(player):
    num_playlists = len(player.playlist)

    if utils.state()['radio_playlist_position'] + 1 == num_playlists:
        player.playlist_pos = 0
    else:
        player.playlist_next()

    if playback_mode == PlaybackMode.Radio:
        display.main_text(get_current_station_name(radioPlayer, stations))

    utils.state()['radio_playlist_position'] = player.playlist_pos


def volume_change(amount):
    logger.debug('change volume ' + str(amount))
    player = get_current_player()

    try:
        player.volume = player.volume + amount
        if player.volume > 100:
            player.volume = 100  # restrict to 100 .volume can go up to 999 until it throws exception
        display.overlay_rect(int(256 / 100 * player.volume), 1)
    except Exception as e:
        pass
        logger.debug('volume limit reached')


def volume_mute_toggle():
    player = get_current_player()
    if player is None:
        return

    player.mute = not player.mute

    utils.state()['muted'] = player.mute

    if player.mute:
        display.set_pause_or_mute_text('Lautlos')

    else:
        display.remove_pause_or_mute_text()


def volume_unmute():
    player = get_current_player()
    player.mute = False
    utils.state()['muted'] = False


def volume_mute():
    player = get_current_player()
    player.mute = True
    utils.state()['muted'] = True


def player_toggle_play_pause(player):
    player.pause = not player.pause

    utils.state()['paused'] = player.pause

    if player.pause:
        display.set_pause_or_mute_text('Pause')

    else:
        display.remove_pause_or_mute_text()


# C O N T R O L S END


def setup_radio(player, stations):
    player.command('stop')

    for station in stations:
        player.playlist_append(stations[station]['url'])

    if utils.state()['power_state'] is PowerState.Powered:  # radio is powerd
        player.playlist_pos = CONST.RADIO_INIT_STATION
        utils.state()['paused'] = False
        # TODO: which station (playlist postion should come from config)
        player.playlist_pos = utils.state()['radio_playlist_position']

    logger.debug('Init done')


rdr = RFID()
sockid = lirc.init("radio", blocking=True)
radioPlayer = mpv.MPV()
radioPlayer.volume = CONST.RADIO_PLAYER_START_VOL
cdPlayer = ''
subprocess.call(["bluetoothctl", "discoverable", "on"])
subprocess.call(["bluetoothctl", "pairable", "on"])

playback_mode = PlaybackMode.Radio

setup_buttons(CONST.BUTTON_MAPPING)


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
# test_thread.start()  # for debugging


def _set_initial_state_and_setup():
    powerState = GPIO.input(CONST.BUTTON_MAPPING['power'])

    print('radio power state', powerState)

    if powerState:  # power state on
        utils.state()['power_state'] = PowerState.Powered
    else:
        utils.state()['power_state'] = PowerState.Standby

    display.initalize()
    setup_radio(radioPlayer, stations)


_set_initial_state_and_setup()

sys.exit(0)
