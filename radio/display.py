import time
import math
import threading

from enum import Enum
from time import sleep as t_sleep
from PIL import ImageFont, Image

from luma.core.interface.serial import spi
from luma.core.virtual import viewport, snapshot, hotspot
from luma.oled.device import ssd1322

import constants as CONST
import sensors_dummy as sensors

display_device = ssd1322(spi(device=0, port=0))

virtual = viewport(display_device, width=display_device.width,
                   height=display_device.height)


sleep_time = 1 / CONST.FPS
main_text_dirty = True  # main text was overdrawn
volume_changes = False  # the volume bar is visible

show_bluetooth_icon = False
show_weather_icon = False


def get_font(font_size, font_path='ressources/hel_new.otf'):
    return ImageFont.truetype(font_path, font_size)


font_28 = get_font(28)
font_16 = get_font(16)
font_16_seg = get_font(
    16, 'ressources/DSEG14ClassicMini-Regular.ttf')
font_32_seg = get_font(
    32, 'ressources/DSEG14ClassicMini-Regular.ttf')


class DrawType(Enum):
    Text = 1
    Rect = 2

class WorkingState(Enum):
    Standby = 1
    Powered = 2

g_working_state = WorkingState.Powered


def make_text_dict(text, timeout=0, font_size=28):
    (width, height) = font_28.getsize(text)

    y = math.ceil((64 - height) / 2 + 1)

    # print('font size', font_size, 'y', y, 'for', text)

    return {
        'timeout': timeout,
        'type': DrawType.Text,
        'text': text,
        'x': 0,
        'y': y,
        'max_position': 0,

        # font stuff
        'font': font_28,
        'width': width,
        'height': height,
        'extra_size': max(width - display_device.width, 0),
        'next': 0
    }


########


current_rendered_main = make_text_dict('M & M Radio')


cloud_image = Image.open('ressources/cloud.png').convert('RGBA')
bt_image = Image.open('ressources/bt.png').convert('RGBA')


def top_snap(draw, width, height):
    print('draw')
    localTime = time.localtime()
    temp_out, temp_in = sensors.get_data()

    draw.text((0, 0), '{}°  {}°'.format(
        temp_out, temp_in), fill='white', font=font_16)
    draw.text((100, 0), '{:02d}:{:02d}'.format(localTime.tm_hour, localTime.tm_min),
              fill='white', font=font_16_seg)

    if (show_weather_icon):
        draw.bitmap((255 - 16, 1), cloud_image)
    if (show_bluetooth_icon):
        draw.bitmap((255-32-5, 0), bt_image)


top_viewport = snapshot(256, 16, top_snap, 60.0)


def standby_snap(draw, width, height):
    print('standby draw')
    localTime = time.localtime()
    temp_out, temp_in = sensors.get_data()

    draw.text((90, 16), '{:02d}:{:02d}'.format(localTime.tm_hour, localTime.tm_min),
              fill='white', font=font_32_seg)

    draw.text((20, 10), '{}°'.format(temp_out), fill='white', font=font_28)
    draw.text((20, 35), '{}°'.format(temp_in), fill='white', font=font_28)

    if (show_weather_icon):
        draw.bitmap((255 - 16, 1), cloud_image)


standby_viewport = None


class Main_Hotspot(hotspot):
    def __init__(self, width, height):
        super(Main_Hotspot, self).__init__(width, height)
        self._data = make_text_dict('')
        self._text = ''

    def should_redraw(self):
        # print(self._data['next'], str(time.time()), str(self._data['next'] < time.time()), str(self._data['next'] - time.time()))
        return \
            (current_rendered_main['type'] != self._data['type']) or \
            (current_rendered_main['text'] != self._data['text']) or \
            self._data['next'] < time.time()

    def update(self, draw):
        global main_text_dirty
        global volume_changes

        data = current_rendered_main

        if DrawType.Rect == data['type'] and data['next'] < time.time():
            volume_changes = False
            tag_text(self._text)
            print('RESET TO TEXT')

        self._data = current_rendered_main

        # draw.text((0, 0), self._data['text'],
        #           fill='white', font=self._data['font'])

        # draw text
        if DrawType.Text == data['type']:
            main_text_dirty = False
            volume_changes = False
            self._text = data['text']

            # draw text that fits completely on display

            draw.text((-data['x'], 0), data['text'],
                      fill='white', font=data['font'])

            # draw text that fits not completely on display, has to check for stop
            if 0 != data['extra_size']:
                if data['extra_size'] <= data['x']:
                    # reached end
                    data['x'] = 0
                    data['next'] = time.time() + CONST.SCROLL_RETAIN

                elif 0 == data['x']:
                    data['next'] = time.time() + CONST.SCROLL_RETAIN
                    data['x'] += CONST.SCROLL_SPEED

                else:
                    data['x'] += CONST.SCROLL_SPEED
            else:
                data['next'] = time.time() + 60

        # draw rectangle
        if DrawType.Rect == data['type']:
            volume_changes = True
            draw.rectangle((0, 0, data['x'], 64), fill='white', outline=None)


main_viewport = Main_Hotspot(256, 28)

virtual.add_hotspot(top_viewport, (0, 0))
virtual.add_hotspot(main_viewport, (0, 64-29))


def get_viewport():
    return virtual


obj_main_text = {}
obj_overlay_text = {}


def main_text(text):
    global current_rendered_main
    global main_text_dirty

    if current_rendered_main['text'] is text and not main_text_dirty:
        print(volume_changes, main_text_dirty, 'same text and dirty false')
        return

    print('set main text to', text)

    current_rendered_main = make_text_dict(text, 0)
    main_text_dirty = True


def tag_text(text):
    global current_rendered_main

    if volume_changes or (current_rendered_main['text'] == text and not main_text_dirty):
        # print(volume_changes, main_text_dirty, 'same text and dirty false')
        return

    current_rendered_main = make_text_dict(text, 0)


def overlay_rect(x, timeout=CONST.RECT_TIMEOUT):
    global current_rendered_main
    global main_text_dirty
    global volume_changes

    print('overlay_rect')

    current_rendered_main = {
        'type': DrawType.Rect,
        'x': x,
        'next': time.time() + CONST.RECT_TIMEOUT,
        'text': 'rect_' + str(time.time())
    }

    main_text_dirty = True
    volume_changes = True


def _hard_refresh_top_viewport():
    global virtual
    global top_viewport
    global top_snap

    new_top_viewport = snapshot(256, 16, top_snap, 60.0)
    virtual.remove_hotspot(top_viewport, (0, 0))

    top_viewport = new_top_viewport
    virtual.add_hotspot(top_viewport, (0, 0))


def set_bt_status(onoff):
    global show_bluetooth_icon
    show_bluetooth_icon = onoff
    _hard_refresh_top_viewport()


def set_weather_status(onoff):
    global show_weather_icon
    show_weather_icon = onoff


def set_standby_onoff(onoff):
    global sleep_time
    global top_viewport
    global main_viewport
    global standby_viewport
    global test_thread
    global viewport_thread
    global g_working_state

    if onoff:  # standby is on
        if g_working_state is WorkingState.Standby:
            return
        g_working_state = WorkingState.Standby
        
        display_device.contrast(CONST.BRIGHTNESS_STANDBY)
        sleep_time = 60

        virtual.remove_hotspot(top_viewport, (0, 0))
        virtual.remove_hotspot(main_viewport, (0, 64 - 29))

        top_viewport = None
        main_viewport = None

        standby_viewport = snapshot(256, 64, standby_snap, 60)
        virtual.add_hotspot(standby_viewport, (0, 0))
        t_sleep(1)
        virtual.refresh()

    else:  # standby is off
        if g_working_state is WorkingState.Powered:
            return
        g_working_state = WorkingState.Powered

        display_device.contrast(CONST.BRIGHTNESS)
        sleep_time = 1 / CONST.FPS

        try:
            # ValueError: list.remove(x): x not in list
            virtual.remove_hotspot(standby_viewport, (0, 0))
        except ValueError as e:
            print(e)

        current_rendered_main['next'] = time.time()
        top_viewport = snapshot(256, 16, top_snap, 60.0)
        main_viewport = Main_Hotspot(256, 28)

        virtual.add_hotspot(top_viewport, (0, 0))
        virtual.add_hotspot(main_viewport, (0, 64 - 29))
        virtual.refresh()
        viewport_thread.name = 'stop'  # trigger stop for old thread

        viewport_thread = threading.Thread(target=viewport_loop)
        viewport_thread.name = 'run'
        viewport_thread.start()

# Traceback (most recent call last):
#   File "main.py", line 98, in callback_power
#     display.set_standby_onoff(False)
#   File "/home/pi/wladio/radio/display.py", line 292, in set_standby_onoff
#     viewport_thread.name = 'stop'  # trigger stop for old thread
# UnboundLocalError: local variable 'viewport_thread' referenced before assignment


def viewport_loop():
    t = threading.current_thread()
    while t.name == 'run':
        virtual.refresh()
        t_sleep(sleep_time)
    # logger.info('Viewport thread ended')


viewport_thread = threading.Thread(target=viewport_loop)
viewport_thread.name = 'run'
viewport_thread.start()
