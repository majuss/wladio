import json

import time, math, threading

from time import sleep as t_sleep
from PIL import ImageFont

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.oled.device import ssd1322

display_device = ssd1322(spi(device=0, port=0))

virtual = viewport(display_device, width=display_device.width, height=display_device.height)

#########


def openFiles():
    with open('stations.json') as stations_file:
        stations = json.load(stations_file)
    with open('music_lib.json') as music_lib_file:
        music_lib = json.load(music_lib_file)

    return [stations, music_lib]

def uid_to_num(uid):
    n = 0
    for i in range(0, 5):
        n = n * 256 + uid[i]
    return n




### display stuff ###



toDisplay = []


def display_make_text_dict(text, timeout):
    font_size = 68
    font = ImageFont.truetype("fonts/hel_new.otf", font_size)
    (width, height) = font.getsize(text)

    while font.getsize(text)[0] > 256: # text longer than display?
        font_size -= 1
        font = ImageFont.truetype("fonts/hel_new.otf", font_size)
        (width, height) = font.getsize(text)

        if font_size == 28:
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

display_add_text('M & M Radio', 86400 * 365 * 1000) # timeout in 100 years




def display_fixed_text(text, timeout = 86400 * 365 * 1000):
        toDisplay = []
        display_add_text('M & M Radio', 86400 * 365 * 1000); # timeout in 100 years

        display_add_text(text, timeout)

#########################################################################################



def display_loop():
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
            t_sleep(0.7)
            latestItem['x'] = 0

        elif 0 != latestItem['extra_size']:
            if 0 == latestItem['x']:
                t_sleep(0.7)
            else:
                t_sleep(1/30)
            latestItem['x'] += 1

        elif 0 == latestItem['x']:
            t_sleep(0.5)



display_thread = threading.Thread(target=display_loop)
display_thread.start()
