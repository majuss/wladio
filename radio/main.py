from pirc522 import RFID
from time import sleep

import mpv
import threading
import lirc
import time
import subprocess
import sys
import RPi.GPIO as GPIO

import constants as CONST
import utils as utils
import display as display
import weather as weather
from enums import *

import radio as radio

# create logger
logger = utils.create_logger('main')

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
        control_next()

    def callback_prev_btn(channel):
        control_prev()

    def callback_pause_btn(channel):
        control_pause_toggle()

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

        logger.debug('Power state set to: {}'.format(GPIO.input(channel)))

        if GPIO.input(channel):  # standby is off GPIO is HIGH
            # leaf standby
            control_leaf_standby()
        else:  # standby is ON GPIO is LOW
            # enter standby
            control_enter_standby()

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
        print(clk_current, GPIO.input(BUTTON_MAPPING['vol_dt']))
        if clk_current != clk_last:
            if GPIO.input(BUTTON_MAPPING['vol_dt']) != clk_current:
                direction = True
            else:
                direction = False
            if direction:
                control_up(CONST.VOL_KNOB_SPEED)  # volume change up
            else:
                control_down(-CONST.VOL_KNOB_SPEED)  # volume change down

    def callback_vol_sw(null):
        control_mute_toggle()  # volume mute toggle

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


def print_tags():
    global playback_mode

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


def infrared_handler():
    global playback_mode
    last_code = ''

    while True:
        codeIR = lirc.nextcode()  # call blocks until IR commands was received

        if 0 == len(codeIR):  # empty array means repeat same code as befores code
            if last_code not in ['up', 'down']:  # for up down we want to proceed
                continue
            codeIR = [last_code]

        last_code = code = codeIR[0]

        # handle IR commands
        if 'up' == code:
            control_up(CONST.VOLUME_CHANGE_DIFF)

        elif 'down' == code:
            control_down(-CONST.VOLUME_CHANGE_DIFF)

        elif 'next' == code:
            control_next()

        elif 'prev' == code:
            control_prev()

        elif 'menu' == code:
            control_mute_toggle()

        elif 'play' == code:
            control_pause_toggle()


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
                # tag was removed
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


def control_up(diff):
    logger.debug('control_up')
    player = radio.get_player()
    if player == None:
        return
    radio.up(diff)
    display.overlay_rect(int(256 / 100 * player.volume), 1)


def control_down(diff):
    logger.debug('control_down')
    player = radio.get_player()
    if player == None:
        return
    radio.down(diff)
    display.overlay_rect(int(256 / 100 * player.volume), 1)


def control_prev():
    logger.debug('control_prev')
    radio.prev()

    display.main_text(radio.get_stream_name())


def control_next():
    logger.debug('control_next')
    radio.next()

    display.main_text(radio.get_stream_name())


def control_pause_toggle():
    logger.debug('control_pause_toggle')

    player = radio.get_player()
    if player is None:
        return

    radio.pause_toggle()

    if utils.state()['paused']:
        display.set_pause_or_mute_text('Pause')

    else:
        display.remove_pause_or_mute_text()


def control_mute_toggle():
    logger.debug('control_mute_toggle')

    player = radio.get_player()
    if player is None:
        return

    radio.mute_toggle()

    if utils.state()['muted']:
        display.set_pause_or_mute_text('Lautlos')

    else:
        display.remove_pause_or_mute_text()


def control_enter_standby():
    logger.debug('control_enter_standby')
    radio.enter_standby()

    try:
        display.set_standby_onoff(True)
        subprocess.call(["rfkill", "block", "bluetooth"])
    except Exception as e:
        logger.warning('Set power state failed {}'.format(e))


def control_leaf_standby():
    logger.debug('control_leaf_standby')
    radio.leaf_standby()

    display.set_standby_onoff(False)
    subprocess.call(["rfkill", "unblock", "bluetooth"])


def volume_unmute():
    player = radio.get_player()
    player.mute = False
    utils.state()['muted'] = False


def volume_mute():
    player = radio.get_player()
    player.mute = True
    utils.state()['muted'] = True


# C O N T R O L S END
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


def _set_initial_state_and_setup():
    powerState = GPIO.input(CONST.BUTTON_MAPPING['power'])

    logger.debug('radio power state is ' + str(powerState))

    if powerState:  # power state on
        utils.state()['power_state'] = PowerState.Powered
    else:
        utils.state()['power_state'] = PowerState.Standby

    display.initalize()

    radio.check_start()


_set_initial_state_and_setup()

sys.exit(0)
