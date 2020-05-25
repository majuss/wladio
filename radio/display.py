import time, math, threading


from enum import Enum
from time import sleep as t_sleep
from PIL import ImageFont

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.oled.device import ssd1322

display_device = ssd1322(spi(device=0, port=0))

virtual = viewport(display_device, width=display_device.width, height=display_device.height)

draw_lock = threading.Condition() # global draw lock

stop_list = []
frames = 10

class DrawType(Enum):
    Text = 1
    Rect = 2



def make_text_dict(text, timeout = 0):
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

    # print('font size', font_size, 'y', y, 'for', text)

    return {
        'timeout': timeout,
        'type': DrawType.Text,
        'text': text,
        'x': 0,
        'y': y,
        'max_position':0,

        # font stuff
        'font': font,
        'width': width,
        'height': height,
        'extra_size': max(width - display_device.width, 0)
    }





def renderer(obj):
    global obj_main_text

    if 0 != obj['data']['timeout']:
        def timeout(obj):
            t_sleep(obj['data']['timeout'])
            if True == obj['stop']:
                return

            main_text(obj_main_text['data']['text']) # switch back to main text

        timeout_thread =  threading.Thread(target=timeout, kwargs={'obj':obj})
        timeout_thread.start()

    data = obj['data']

    # draw text
    if DrawType.Text == data['type']:
        # draw text that fits completely on display
        if 0 == data['extra_size']:
            with draw_lock:
                with canvas(virtual) as draw:
                    draw.text((0, data['y']), data['text'], fill='white', font=data['font'])

        # draw text that fits not completely on display, has to check for stop

        else:
            while False == obj['stop']:
                # animate rendering
                with draw_lock:
                    with canvas(virtual) as draw:
                        draw.text((-data['x'], data['y']), data['text'], fill='white', font=data['font'])

                if data['x'] == data['extra_size']:
                    # reached end
                    t_sleep(1)
                    print("end reached")
                    data['x'] = 0

                else:
                    if 0 == data['x']:
                        t_sleep(1)
                    else:
                        t_sleep(1/frames)
                    data['x'] += 1
            print('animeated rendering stopped')
            data['x'] = 0 # reset start position
    
    # draw rectangle
    if DrawType.Rect == data['type']:
        with draw_lock:
            with canvas(virtual) as draw:
                draw.rectangle( (0,0, data['x'], 64), fill='white', outline=None)




obj_main_text = {}
obj_overlay_text = {}


def main_text(text):
    print('main_text', text)
    global obj_main_text
    global stop_list

    for obj in stop_list:
        obj['stop'] = True

    text_dict = make_text_dict(text)

    obj_main_text = {
        'data': text_dict,
        'stop': False
    }
    stop_list = [obj_main_text]

    obj_main_text['thread'] = threading.Thread(target=renderer, kwargs={'obj':obj_main_text})
    obj_main_text['thread'].start()



def overlay_text(text, timeout):
    print('overlay_text', text, timeout)
    global stop_list
    global obj_overlay_text

    for obj in stop_list:
        obj['stop'] = True

    text_dict = make_text_dict(text, timeout)

    obj_overlay_text = {
        'data': text_dict,
        'stop': False
    }
    stop_list = [obj_overlay_text]

    obj_overlay_text['thread'] = threading.Thread(target=renderer, kwargs={'obj':obj_overlay_text})
    obj_overlay_text['thread'].start()

def overlay_rect(x, timeout = 2):
    print('overlay_rect')
    global stop_list

    for obj in stop_list:
        obj['stop'] = True

    obj_text = {
        'data': {
            'type': DrawType.Rect,
            'x': x,
            'timeout': timeout
        },
        'stop': False
    }

    stop_list = [obj_text]

    obj_text['thread'] = threading.Thread(target=renderer, kwargs={'obj':obj_text})
    obj_text['thread'].start()


main_text('M & M Radio')


def test_func():
    t_sleep(10)

    overlay_rect(100)


test_trhead = threading.Thread(target=test_func)
#test_trhead.start() # for debugging




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
            draw.text((-latestItem['x'], latestItem['y']), latestItem['text'], fill='white', font=latestItem['font'])


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
