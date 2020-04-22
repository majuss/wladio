import mpv
import threading
from time import sleep
import sys
import lirc
from pirc522 import RFID
from enum import Enum

import utils as utils

# Load stations and music library file
stations, music_lib = utils.openFiles()
music_lib_path = '/home/pi/'


class PlaybackMode(Enum):
    Radio = 1
    CD = 2
    BT = 3


def init_sensors():
    import board
    import digitalio
    from busio import I2C
    import adafruit_bme280
    import adafruit_bme680

    i2c = I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    bme280.sea_level_pressure = 1013.25
    bme680.sea_level_pressure = 1013.25
    return bme280, bme680

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
        if playback_mode == PlaybackMode.Radio:
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
                print(radioPlayer.metadata['title'] +
                      ' - ' + radioPlayer.metadata['artist'])
            except:
                print('ex')
            sleep(1)


def infrared_handler():
    lastCode = ''
    while True:
        player = get_current_player()
        codeIR = lirc.nextcode()
        if "up" in codeIR or "down" in codeIR or lastCode == "up" or lastCode == "down":
            if len(codeIR) == 0:
                codeIR.append(lastCode)
            if "up" in codeIR:
                player.volume = player.volume + 2
            if "down" in codeIR:
                player.volume = player.volume - 2
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
                    player.playlist_pos = len(player.playlist) - 1  # Skip to last position
            if "menu" in codeIR:
                player.mute = not player.mute
            if "play" in codeIR:
                player.pause = not player.pause
        sleep(0.1)


def rfid_handler():
    global playback_mode
    global cdPlayer

    cdPlayer = mpv.MPV(loop_playlist='inf')
    cdPlayer.volume = 30


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

            last_time_tag_detected = False

            rdr.wait_for_tag()
            (error, tag_type) = rdr.request()
            if not error:
                print("Tag detected")
                (error, uid) = rdr.anticoll()
                print("tag uuid")
                print(uid)
                if not error:
                    rfid = str(utils.uid_to_num(uid))

                    last_time_tag_detected = True

                    if playback_mode != PlaybackMode.CD:

                        radioPlayer.mute = True

                        cdPlayer.play(music_lib_path + music_lib[rfid])
                        print(cdPlayer.playlist)

                    playback_mode = PlaybackMode.CD

            # else:
            #     print("error in rdr request")
            #     # resume radio?

            if playback_mode == PlaybackMode.CD:
                # tag was removed or track finished playing
                if last_time_tag_detected is False:
                    cdPlayer.command('stop')

                    # switch back to radio
                    radioPlayer.mute = False
                    playback_mode = PlaybackMode.Radio

    except KeyboardInterrupt:
        rdr.cleanup()
        raise

def sensor_handler():
    bme280, bme680 = init_sensors()
    while True:
        # print("BME280: %0.1f")
        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)
        print("Altitude = %0.2f meters" % bme280.altitude)

        print("\nTemperature: %0.1f C" % bme680.temperature)
        print("Gas: %d ohm" % bme680.gas)
        print("Humidity: %0.1f %%" % bme680.humidity)
        print("Pressure: %0.3f hPa" % bme680.pressure)
        print("Altitude = %0.2f meters" % bme680.altitude)

        sleep(60)

def volume_knob_handler():
    print("Work in progress")
    sleep(1000000)


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
    if playback_mode == playback_mode.BT:
        return btPlayer

# def set_radio_mode():
#     global playback_mode

#     playback_mode = PlaybackMode.Radio

#     while True:
#         sleep(2)
#         if playback_mode == PlaybackMode.Radio:
#             restart_streaming()


rdr = RFID()
sockid = lirc.init("radio", blocking=True)
radioPlayer = mpv.MPV()
radioPlayer.volume = 25
cdPlayer = ''

playback_mode = PlaybackMode.Radio

setup_radio(radioPlayer, stations)

tag_thread = threading.Thread(target=print_tags)
tag_thread.start()

infrared_thread = threading.Thread(target=infrared_handler)
infrared_thread.start()

rfid_thread = threading.Thread(target=rfid_handler)
rfid_thread.start()

# sensor_thread = threading.Thread(target=sensor_handler)
# sensor_thread.start()

# volume_thread = threading.Thread(target=volume_knob_handler)
# volume_thread.start()
sleep(2)
print(radioPlayer.__dict__)
sys.exit(0)








