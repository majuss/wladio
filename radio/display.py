# -*- coding: utf-8 -*-
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
from enums import DrawType, PowerState

logger = utils.create_logger(__name__)
STATE = utils.state()

spi_for_display = spi(device=0, port=0)
display_device = ssd1322(spi_for_display)

virtual = viewport(display_device, width=display_device.width,
                   height=display_device.height)


sleep_time = 1 / CONST.FPS
main_text_dirty = True  # main text was overdrawn
forced_visualisation = False  # forced visualisation for a time frame


def get_font(font_size, font_path='ressources/hel_new.otf'):
    return ImageFont.truetype(font_path, font_size)


font_18 = get_font(18)
font_20 = get_font(20)
font_28 = get_font(28)
font_16_seg = get_font(
    16, 'ressources/DSEG14ClassicMini-Regular.ttf')
font_32_seg = get_font(
    32, 'ressources/DSEG14ClassicMini-Regular.ttf')


def make_text_dict(text, next=0, font_size=28, main_text=True):
    logger.debug('make_text_dict {} {} {} {}'.format(
        text, next, font_size, main_text))

    (foo, bar, width, height) = font_28.getbbox(text)

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
shuffle_cd_image = Image.open('ressources/random.png').convert('RGBA')


def top_snap(draw, width, height):
    logger.debug('draw top row (temps, time, bt, weather)')

    sensor_data = sensors.get_data()

    draw.text((0, 4), '{:.1f}°  {:.1f}°'.format(
        *(sensor_data[0:2])), fill='white', font=font_18)

    draw.text((100, 2), '{:02d}:{:02d}'.format(*utils.get_local_hours_minutes()),
              fill='white', font=font_16_seg)

    if STATE['draw_rain_cloud_icon']:
        draw.bitmap((255 - 16, 1), cloud_image)
    if STATE['draw_bluetooth_icon']:
        draw.bitmap((255-32-5, 1), bt_image)
    if STATE['shuffle_cd']:
        draw.bitmap((255-32-5-16-5, 1), shuffle_cd_image)


def standby_snap(draw, width, height):
    logger.debug('draw standby (temps, time, weather)')
    temp_in, temp_out, hum_in, hum_out = sensors.get_data()

    draw.text((145, 16), '{:02d}:{:02d}'.format(*utils.get_local_hours_minutes()),
              fill='white', font=font_32_seg)

    draw.text((5, 10), '{:.1f}°'.format(temp_out), fill='white', font=font_20)
    draw.text((5, 35), '{:.1f}°'.format(temp_in), fill='white', font=font_20)

    draw.text((70, 10), '{:.0f}%'.format(hum_out), fill='white', font=font_20)
    draw.text((70, 35), '{:.0f}%'.format(hum_in), fill='white', font=font_20)

    if (STATE['draw_rain_cloud_icon']):
        draw.bitmap((255 - 16, 1), cloud_image)


top_viewport = None
main_viewport = None

standby_viewport = {}

update_text_line = True
current_rendered_main = make_text_dict('M & M Radio')
prev_rendered_main = make_text_dict('')


class Main_Hotspot(hotspot):
    def __init__(self, width, height):
        super(Main_Hotspot, self).__init__(width, height)

    def should_redraw(self):
        global current_rendered_main
        global forced_visualisation
        # print(self._data['next'], str(time.time()), str(self._data['next'] \
        # < time.time()), str(self._data['next'] - time.time()))

        if update_text_line:
            logger.debug('received update text line')
            return True

        currentTime = time.time()

        # as long as we dont need to rerender
        if (current_rendered_main['next'] == 0) or (currentTime < current_rendered_main['next']):
            return False

        if current_rendered_main['main_text'] is False:
            current_rendered_main = prev_rendered_main
            logger.debug('reset current_rendered_main to prev main')

        # print('should_redraw True')

        forced_visualisation = False

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

        # draw text
        if DrawType.Text is data['type']:

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
        if DrawType.Rect is data['type']:
            draw.rectangle((0, 0, data['x'], 64), fill='white', outline=None)


def get_viewport():
    return virtual


def tag_text(text):
    global current_rendered_main
    global update_text_line

    if STATE['muted'] is True or STATE['paused'] is True:
        return

    if forced_visualisation or (current_rendered_main['text'] == text):
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
    global forced_visualisation
    global update_text_line

    logger.debug('overlay_rect')

    current_rendered_main = {
        'type': DrawType.Rect,
        'x': x,
        'main_text': False,
        'next': time.time() + CONST.RECT_TIMEOUT,
        'text': 'rect_' + str(time.time())
    }

    forced_visualisation = update_text_line = True


def forced_text(text, timeout):
    global current_rendered_main
    global forced_visualisation
    global update_text_line

    logger.debug('forced text: ' + text)

    current_rendered_main = make_text_dict(
        text, time.time() + timeout, 28, False)
    forced_visualisation = update_text_line = True


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
    logger.debug('hard_refresh_top_viewport')

    new_top_viewport = snapshot(256, 27, top_snap, 60.0)
    virtual.remove_hotspot(top_viewport, (0, 0))

    top_viewport = new_top_viewport
    virtual.add_hotspot(top_viewport, (0, 0))


def enter_standby():
    logger.debug('enter standby')

    display_device.contrast(CONST.BRIGHTNESS_STANDBY)

    _remove_powered_viewport()
    _setup_state_standby()

    t_sleep(1)
    virtual.refresh()


def _restart_viewport_thread():
    global viewport_thread

    if viewport_thread is not None:
        viewport_thread.name = 'stop'  # trigger stop for old thread

    viewport_thread = threading.Thread(target=viewport_loop)
    viewport_thread.name = 'run'
    viewport_thread.start()


def leave_standby():
    logger.debug('leave standby')
    global viewport_thread

    display_device.contrast(CONST.BRIGHTNESS)

    _remove_standby_viewport()

    current_rendered_main['next'] = time.time()

    _setup_state_powered()

    virtual.refresh()

    _restart_viewport_thread()


def viewport_loop():
    t = threading.current_thread()
    while t.name == 'run':
        virtual.refresh()
        t_sleep(sleep_time)
    # logger.info('Viewport thread ended')


viewport_thread = None


def _setup_state_powered():
    global top_viewport
    global main_viewport
    global sleep_time

    sleep_time = 1 / CONST.FPS

    top_viewport = snapshot(256, 27, top_snap, 60)
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
    global sleep_time

    sleep_time = 60

    standby_viewport = snapshot(256, 64, standby_snap, 60)

    virtual.add_hotspot(standby_viewport, (0, 0))

    display_device.contrast(CONST.BRIGHTNESS_STANDBY)


def _remove_standby_viewport():
    global standby_viewport

    # virtual.remove_hotspot(standby_viewport, (0, 0))
    # standby_viewport = None
    if standby_viewport is not None:
        try:
            virtual.remove_hotspot(standby_viewport, (0, 0))
        except ValueError:
            print(f"Hotspot {(standby_viewport, (0, 0))} not found in virtual._hotspots")
        standby_viewport = None


def initalize():  # 1 PowerState.Powered / 0 PowerState.Standby
    global viewport_thread
    t_sleep(0.5)
    logger.debug('intialize radio display to state {}'.format(
        STATE['power_state']))

    if STATE['power_state'] is PowerState.Powered:
        _setup_state_powered()

    elif STATE['power_state'] is PowerState.Standby:
        _setup_state_standby()

    elif STATE['power_state'] is PowerState.Unknown:
        logger.debug('POWER STATE NOT SET')

    _restart_viewport_thread()
