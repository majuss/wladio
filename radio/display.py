import time
import math
import threading


from enum import Enum
from time import sleep as t_sleep
from PIL import ImageFont, Image

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.core.virtual import viewport, snapshot, hotspot
from luma.oled.device import ssd1322

import constants

import sensors_dummy

display_device = ssd1322(spi(device=0, port=0))

virtual = viewport(display_device, width=display_device.width,
                   height=display_device.height)

draw_lock = threading.Condition()  # global draw lock
stop_lock = threading.Condition()  # global stop lock

stop_list = []
frames = 60
main_text_dirty = True  # main text was overdrawn
volume_changes = False  # the volume bar is visible

bluetooth_icon = False
weather_icon = False


def get_font(font_size, font_path='ressources/hel_new.otf'):
    return ImageFont.truetype(font_path, font_size)


font_28 = get_font(28)
font_16 = get_font(16)
font_16_seg = get_font(
    16, '../fonts-DSEG_v046/DSEG14-Classic-MINI/DSEG14ClassicMini-Regular.ttf')


class DrawType(Enum):
    Text = 1
    Rect = 2


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
    temp_out, temp_in = sensors_dummy.get_data()

    draw.text((0, 0), '{}°  {}°'.format(
        temp_out, temp_in), fill='white', font=font_16)
    draw.text((100, 0), '{:02d}:{:02d}'.format(localTime.tm_hour, localTime.tm_min),
              fill='white', font=font_16_seg)

    if (weather_icon):
        draw.bitmap((255 - 16, 1), cloud_image)
    if (bluetooth_icon):
        draw.bitmap((255-32-5, 0), bt_image)


top_viewport = snapshot(256, 16, top_snap, 60.0)


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
        print('main')

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
                    print("end reached")
                    data['x'] = 0
                    data['next'] = time.time() + 2

                elif 0 == data['x']:
                    data['next'] = time.time() + 2
                    data['x'] += constants.SCROLL_SPEED

                else:
                    data['x'] += constants.SCROLL_SPEED
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


def renderer(obj):
    global obj_main_text
    global main_text_dirty

    if 0 != obj['data']['timeout']:
        def timeout(obj):
            t_sleep(obj['data']['timeout'])
            with stop_lock:
                print(obj['stop'])
                if True == obj['stop']:
                    return

            # switch back to main text
            main_text(obj_main_text['data']['text'])

        timeout_thread = threading.Thread(target=timeout, kwargs={'obj': obj})
        timeout_thread.start()

    data = obj['data']


obj_main_text = {}
obj_overlay_text = {}


def main_text(text):
    global current_rendered_main
    global main_text_dirty

    if main_text_dirty == False and current_rendered_main['text'] == text:
        print(volume_changes, main_text_dirty, 'same text and dirty false')
        return

    current_rendered_main = make_text_dict(text, 0)
    main_text_dirty = True


def tag_text(text):
    global current_rendered_main

    if volume_changes == True or (main_text_dirty == False and current_rendered_main['text'] == text):
        print(volume_changes, main_text_dirty, 'same text and dirty false')
        return

    current_rendered_main = make_text_dict(text, 0)


def overlay_text(text, timeout):
    return

    with stop_lock:
        print('overlay_text', text, timeout)
        global stop_list
        global obj_overlay_text
        global main_text_dirty

        for obj in stop_list:
            obj['stop'] = True

        text_dict = make_text_dict(text, timeout)

        obj_overlay_text = {
            'data': text_dict,
            'stop': False
        }
        stop_list = [obj_overlay_text]

        main_text_dirty = True
        obj_overlay_text['thread'] = threading.Thread(
            target=renderer, kwargs={'obj': obj_overlay_text})
        obj_overlay_text['thread'].start()


def overlay_rect(x, timeout=2):
    global current_rendered_main
    global main_text_dirty
    global volume_changes

    print('overlay_rect')

    current_rendered_main = {
        'type': DrawType.Rect,
        'x': x,
        'next': time.time() + 2,
        'text': 'rect_' + str(time.time())
    }

    main_text_dirty = True
    volume_changes = True


def set_bt_status(onoff):
    global bluetooth_icon
    global virtual
    global top_viewport
    global top_snap

    bluetooth_icon = onoff

    new_top_viewport = snapshot(256, 16, top_snap, 60.0)
    virtual.remove_hotspot(top_viewport, (0, 0))

    top_viewport = new_top_viewport
    virtual.add_hotspot(top_viewport, (0, 0))


def test_func():
    while True:
        t_sleep(1/60)
        virtual.refresh()


test_trhead = threading.Thread(target=test_func)
test_trhead.start()  # for debugging


def display_loop():
    while True:
        now = time.time()
        try:
            latestItem = toDisplay[-1]
        except Exception as e:
            print(e)
        if latestItem['timeout'] < now:
            print("popped " + toDisplay[-1]['text'])
            toDisplay.pop()
            continue

        # render text
        # print('would print at', latestItem['x'], latestItem['y'], latestItem['text'])

        with canvas(virtual) as draw:
            draw.text((-latestItem['x'], latestItem['y']),
                      latestItem['text'], fill='white', font=latestItem['font'])

        # recalc position for next step
        if latestItem['x'] == latestItem['extra_size']:
            # reached end
            t_sleep(1)
            print("end reached")
            latestItem['x'] = 0

        elif 0 != latestItem['extra_size']:
            if 0 == latestItem['x']:
                t_sleep(1)
            else:
                t_sleep(1/frames)
            latestItem['x'] += 1

        elif 0 == latestItem['x']:
            t_sleep(0.5)
        print(len(toDisplay))
