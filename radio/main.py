import mpv, threading, sys, math, time
import lirc

from pyky040 import pyky040
from time import sleep
from pirc522 import RFID
from enum import Enum

from PIL import ImageFont
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.oled.device import ssd1322

import utils as utils



# from PIL import ImageFont
# main_font = ImageFont.truetype("fonts/hel_new.otf",78)
# secondary_font = ImageFont.truetype("fonts/hel_new.otf",30)


display_device = ssd1322(spi(device=0, port=0))

# display_dict = {
#     "display_text": "Radio is warming up",

# }
virtual = viewport(display_device, width=display_device.width, height=display_device.height)
toDisplay = []


frames = 60

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
    # global display_dict

    while True:
        # print("tag loop")
        if playback_mode == PlaybackMode.Radio:
            # display_dict['display_text'] = get_current_station_name(radioPlayer, stations)
            utils.fixed_text(get_current_station_name(radioPlayer, stations))


            while radioPlayer.metadata is not None and "icy-title" in radioPlayer.metadata:
                current_station = get_current_station(radioPlayer, stations)
                tag = radioPlayer.metadata['icy-title']
                if last_tag != radioPlayer.metadata['icy-title'] and radioPlayer.metadata['icy-title'] not in stations[current_station]['skip_strings']:
                    for replace_string in stations[current_station]['replace_strings']:
                        tag = tag.replace(replace_string, '').lstrip()
                    print(tag)
                    utils.fixed_text(tag)
                    # display_dict['display_text'] = tag
                    last_tag = radioPlayer.metadata['icy-title']
                sleep(4/frames)
            sleep(4/frames)

        if playback_mode is PlaybackMode.CD:
            try:
                print("foo")
                player = get_current_player()
                # display_dict['display_text'] = player.metadata['title'] + ' - ' + player.metadata['artist']
                utils.fixed_text(player.metadata['title'] + ' - ' + player.metadata['artist'])
                print(player.metadata['title'] +
                      ' - ' + player.metadata['artist'])
            except:
                print('ex')
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
    my_encoder.watch()

def volume_knob_switch_callback():
    volume_mute()

def volume_dec_callback(ka):
    volume_change(1)

def volume_inc_callback(ka):
    volume_change(-1)

def volume_change(amount):
    player = get_current_player()
    utils.add_text('rect', 0.5)
    # display_dict['display_text'] = 'rect'
    try:
        player.volume = player.volume + amount
    except:
        print("Volume limit reached")

def volume_mute():
    player = get_current_player()
    player.mute = not player.mute

def display_make_text_dict(text, timeout):
    font_size = 68
    font = ImageFont.truetype("fonts/hel_new.otf", font_size)
    (width, height) = font.getsize(text)

    while font.getsize(text)[0] > 256: # text longer than display?
        font_size -= 1
        font = ImageFont.truetype("fonts/hel_new.otf", font_size)
        (width, height) = font.getsize(text)

        if font_size == 25:
            break

    y = math.ceil((64 - height) / 2 + 1)

    print('font size', font_size, 'y', y, 'for', text)

    return {
        'text': text,
        'timeout': time.time() + timeout,
        'x': 0,
        'y': y,
        'max_position':0,

        # font stuff
        'font': font,
        'width': width,
        'height': height,
        'extra_size': max(width - display_device.width, 0)
    }




def display_add_text(text, timeout):
    for stackElement in toDisplay: stackElement['timeout'] += timeout

    toDisplay.append(
         display_make_text_dict(text, timeout)
    ) 

def display_handler():
    while True:
        now = time.time()

        latestItem = toDisplay[-1]


        if latestItem['timeout'] < now:
            toDisplay.pop()
            continue

        # render text
        # print('would print at', latestItem['x'], latestItem['y'], latestItem['text'])

        with canvas(virtual) as draw:
            draw.text((-latestItem['x'], latestItem['y']), latestItem['text'], fill='white', font=latestItem['font']) 


        # recalc position for next step
        if latestItem['x'] == latestItem['extra_size']:
            # reached end
            sleep(0.7)
            latestItem['x'] = 0

        elif 0 != latestItem['extra_size']:
            if 0 == latestItem['x']:
                sleep(0.7)
            else:
                sleep(1/30)
            latestItem['x'] += 1

        elif 0 == latestItem['x']:
            sleep(0.5)
    # global main_font

    # last_text = ''
    # counter = 0

    # while True:
    #     font_size = 68
    #     if last_text is display_dict['display_text']:
    #         pass
    #         sleep(1/frames)  # 33 ms for each frame equals 30 fps

    #     while main_font.getsize(display_dict['display_text'])[0] > 256:
    #         font_size -= 1
    #         main_font = ImageFont.truetype("../radio/fonts/hel_new.otf", font_size)
    #         if font_size == 25:
    #             break

    #     string_size = main_font.getsize(display_dict['display_text'])
    #     ycursor = math.ceil((64 - string_size[1])/2 +1)
    #     virtual = viewport(display_device, width=max(display_device.width, string_size[0]), height=display_device.height)


    #     with canvas(virtual) as draw:
    #         draw.text((0, ycursor), display_dict['display_text'], fill="white", font=main_font) 
    #     i = 0
    #     sleep(0.5)

    #     while i < string_size[0] -  display_device.width :
    #         virtual.set_position((i, 0))
    #         if i == 0:
    #             sleep(0.5)
    #         i += 2
    #         sleep(1/frames)

        # else:
        #     with canvas(display) as draw:
        #         # if counter == 60:
        #         #     display_dict['display_text'] = last_text
        #         #     counter = 0
        #         if display_dict['display_text'] is not 'rect':
        #             # draw.rectangle(display.bounding_box, outline="white", fill="black")
        #             draw.text((0, 0), display_dict['display_text'], fill="white", font=main_font)
        #             draw.text((200, 5), display_dict['display_text'], fill="white", font=secondary_font)

        #             last_text = display_dict['display_text']
        #         else:
        #             # print("foo")
        #             player = get_current_player()
        #             # print(player.volume * 2.54)
        #             draw.rectangle((0, 0, player.volume * 2.54, 64), outline="white", fill="white")
        #             # counter = counter + 1


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

my_encoder = pyky040.Encoder(CLK=5, DT=6, SW=13)
my_encoder.setup(scale_min=0, scale_max=100, step=1, dec_callback=volume_dec_callback, inc_callback=volume_inc_callback, sw_callback=volume_knob_switch_callback)

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

volume_thread = threading.Thread(target=volume_knob_handler)
volume_thread.start()

display_thread = threading.Thread(target=display_handler)
display_thread.start()

sleep(2)

sys.exit(0)

