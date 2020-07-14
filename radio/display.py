import time
import math
import threading


from time import sleep as t_sleep
from PIL import ImageFont, Image

from luma.core.interface.serial import spi
from luma.core.virtual import viewport, snapshot, hotspot
from luma.oled.device import ssd1322

import constants as CONST
import sensors_dummy as sensors
import utils as utils
from enums import *

display_device = ssd1322(spi(device=0, port=0))

virtual = viewport(display_device, width=display_device.width,
                   height=display_device.height)


sleep_time = 1 / CONST.FPS
main_text_dirty = True  # main text was overdrawn
volume_changes = False  # the volume bar is visible


def get_font(font_size, font_path='ressources/hel_new.otf'):
    return ImageFont.truetype(font_path, font_size)


font_28 = get_font(28)
font_16 = get_font(16)
font_16_seg = get_font(
    16, 'ressources/DSEG14ClassicMini-Regular.ttf')
font_32_seg = get_font(
    32, 'ressources/DSEG14ClassicMini-Regular.ttf')


def make_text_dict(text, next=0, font_size=28, main_text=True):
    print('make_text_dict', text, next, font_size, main_text)

    (width, height) = font_28.getsize(text)

    y = math.ceil((64 - height) / 2 + 1)

    # print('font size', font_size, 'y', y, 'for', text)

    return {
        'type': DrawType.Text,
        'main_text': main_text,
        'text': text,
        'x': 0,
        'y': y,
        'max_position': 0,

        # font stuff
        'font': font_28,
        'width': width,
        'height': height,
        'extra_size': max(width - display_device.width, 0),
        'next': next
    }


########


# TODO: use CONST for paths
cloud_image = Image.open('ressources/cloud.png').convert('RGBA')
bt_image = Image.open('ressources/bt.png').convert('RGBA')


def top_snap(draw, width, height):
    print('draw top row (temps, time, bt, weather)')

    draw.text((0, 0), '{}°  {}°'.format(
        *sensors.get_data()), fill='white', font=font_16)

    draw.text((100, 0), '{:02d}:{:02d}'.format(*utils.get_local_hours_minutes()),
              fill='white', font=font_16_seg)

    if (utils.state()['draw_rain_cloud_icon']):
        draw.bitmap((255 - 16, 1), cloud_image)
    if (utils.state()['draw_bluetooth_icon']):
        draw.bitmap((255-32-5, 0), bt_image)


def standby_snap(draw, width, height):
    print('draw standby (temps, time, weather)')
    temp_out, temp_in = sensors.get_data()

    draw.text((90, 16), '{:02d}:{:02d}'.format(*utils.get_local_hours_minutes()),
              fill='white', font=font_32_seg)

    draw.text((20, 10), '{}°'.format(temp_out), fill='white', font=font_28)
    draw.text((20, 35), '{}°'.format(temp_in), fill='white', font=font_28)

    if (utils.state()['draw_rain_cloud_icon']):
        draw.bitmap((255 - 16, 1), cloud_image)


top_viewport = None
main_viewport = None

standby_viewport = None

update_text_line = True
current_rendered_main = make_text_dict('M & M Radio')
prev_rendered_main = make_text_dict('')


class Main_Hotspot(hotspot):
    def __init__(self, width, height):
        super(Main_Hotspot, self).__init__(width, height)

    def should_redraw(self):
        global current_rendered_main
        global volume_changes
        # print(self._data['next'], str(time.time()), str(self._data['next'] < time.time()), str(self._data['next'] - time.time()))

        if update_text_line:
            print('received update text line')
            return True

        currentTime = time.time()

        # as long as we dont need to rerender
        if (current_rendered_main['next'] is 0) or (currentTime < current_rendered_main['next']):
            return False

        if current_rendered_main['main_text'] is False:
            current_rendered_main = prev_rendered_main
            print('reset current_rendered_main to prev main')

        # print('should_redraw True')

        volume_changes = False

        return True

    def update(self, draw):
        global update_text_line
        global current_rendered_main
        global prev_rendered_main

        update_text_line = False

        data = current_rendered_main

        if data['main_text']:
            # print('save main text')
            prev_rendered_main = data

        # if utils.state()['muted']:
        #     draw.text((0, 0), 'lautlos', fill='white', font=data['font'])
        #     main_text_dirty = True
        #     return

        # if utils.state()['paused']:
        #     draw.text((0, 0), 'pausiert', fill='white', font=data['font'])
        #     main_text_dirty = True
        #     return

        # draw text
        if DrawType.Text == data['type']:

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

        # draw rectangle
        if DrawType.Rect == data['type']:
            draw.rectangle((0, 0, data['x'], 64), fill='white', outline=None)


def get_viewport():
    return virtual


# def main_text(text):
#     global current_rendered_main
#     global current_rendered_main

#     if current_rendered_main['text'] is text and not main_text_dirty:
#         print(volume_changes, main_text_dirty, 'same text and dirty false')
#         return

#     print('set main text to', text)

#     current_rendered_main = make_text_dict(text, 0)
#     main_text_dirty = True


def tag_text(text):
    global current_rendered_main
    global update_text_line

    if utils.state()['muted'] is True or utils.state()['paused'] is True:
        return

    if volume_changes or (current_rendered_main['text'] == text):
        return

    update_text_line = True

    current_rendered_main = make_text_dict(text, 0, 28, True)


def main_text(text):
    global current_rendered_main
    global update_text_line

    if current_rendered_main['text'] == text:
        return

    update_text_line = True

    current_rendered_main = make_text_dict(text, 0, 28, True)


def overlay_rect(x, timeout=CONST.RECT_TIMEOUT):
    global current_rendered_main
    global volume_changes
    global update_text_line

    print('overlay_rect')

    current_rendered_main = {
        'type': DrawType.Rect,
        'x': x,
        'main_text': False,
        'next': time.time() + CONST.RECT_TIMEOUT,
        'text': 'rect_' + str(time.time())
    }

    volume_changes = True
    update_text_line = True


def set_pause_or_mute_text(text):
    global current_rendered_main
    global update_text_line

    update_text_line = True
    current_rendered_main = make_text_dict(text, 0, 28, False)


def remove_pause_or_mute_text():
    global current_rendered_main
    current_rendered_main['next'] = 1  # trigers reset to saved main text


def hard_refresh_top_viewport():
    global top_viewport

    new_top_viewport = snapshot(256, 16, top_snap, 60.0)
    virtual.remove_hotspot(top_viewport, (0, 0))

    top_viewport = new_top_viewport
    virtual.add_hotspot(top_viewport, (0, 0))


def set_standby_onoff(onoff):
    global sleep_time
    global viewport_thread

    if onoff:  # standby is on
        if utils.state()['power_state'] is PowerState.Standby:
            return
        utils.state()['power_state'] = PowerState.Standby

        display_device.contrast(CONST.BRIGHTNESS_STANDBY)
        sleep_time = 60

        _remove_powered_viewport()
        _setup_state_standby()

        t_sleep(1)
        virtual.refresh()

    else:  # standby is off
        if utils.state()['power_state'] is PowerState.Powered:
            return
        utils.state()['power_state'] = PowerState.Powered

        display_device.contrast(CONST.BRIGHTNESS)
        sleep_time = 1 / CONST.FPS

        _remove_standby_viewport()

        current_rendered_main['next'] = time.time()

        _setup_state_powered()

        virtual.refresh()
        viewport_thread.name = 'stop'  # trigger stop for old thread

        viewport_thread = threading.Thread(target=viewport_loop)
        viewport_thread.name = 'run'
        viewport_thread.start()


def viewport_loop():
    t = threading.current_thread()
    while t.name == 'run':
        virtual.refresh()
        t_sleep(sleep_time)
    # logger.info('Viewport thread ended')


viewport_thread = threading.Thread(target=viewport_loop)
viewport_thread.name = 'run'
viewport_thread.start()


def _setup_state_powered():
    global top_viewport
    global main_viewport

    top_viewport = snapshot(256, 16, top_snap, 60.0)
    main_viewport = Main_Hotspot(256, 28)

    virtual.add_hotspot(top_viewport, (0, 0))
    virtual.add_hotspot(main_viewport, (0, 64-29))


def _remove_powered_viewport():
    global top_viewport
    global main_viewport

    virtual.remove_hotspot(top_viewport, (0, 0))
    virtual.remove_hotspot(main_viewport, (0, 64 - 29))

    top_viewport = None
    main_viewport = None


def _setup_state_standby():
    global standby_viewport

    standby_viewport = snapshot(256, 64, standby_snap, 60)

    virtual.add_hotspot(standby_viewport, (0, 0))

    display_device.contrast(CONST.BRIGHTNESS_STANDBY)


def _remove_standby_viewport():
    global standby_viewport

    virtual.remove_hotspot(standby_viewport, (0, 0))
    standby_viewport = None


def initalize():  # 1 PowerState.Powered / 0 PowerState.Standby
    print('intialize radio display to state', utils.state()['power_state'])

    if utils.state()['power_state'] is PowerState.Powered:
        _setup_state_powered()
    elif utils.state()['power_state'] is PowerState.Standby:
        _setup_state_standby()
    elif utils.state()['power_state'] is PowerState.Unknown:
        print('POWER STATE NOT SET')
