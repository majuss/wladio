
# from PIL import Image
# import os.path
# import display
# import time

# import sensors_dummy

# from luma.core.virtual import viewport, snapshot

# viewport = display.get_viewport()

# font_16 = display.get_font(
#     16)  # , '../fonts-DSEG_v046/DSEG14-Classic-MINI/DSEG14ClassicMini-Regular.ttf')
# font_28 = display.get_font(28)


# font_16_seg = display.get_font(
#     16, '../fonts-DSEG_v046/DSEG14-Classic-MINI/DSEG14ClassicMini-Regular.ttf')

# cloud_image = Image.open('ressources/cloud.png').convert('RGBA')
# bt_image = Image.open('ressources/bt.png').convert('RGBA')


# def top_snap(draw, width, height):
#     print('draw')
#     localTime = time.localtime()
#     temp_out, temp_in = sensors_dummy.get_data()

#     draw.text((0, 0), '{}°  {}°'.format(
#         temp_out, temp_in), fill='white', font=font_16)
#     draw.text((100, 0), '{:02d}:{:02d}'.format(localTime.tm_hour, localTime.tm_min),
#               fill='white', font=font_16_seg)

#     draw.bitmap((255 - 16, 1), cloud_image)
#     draw.bitmap((255-32-5, 0), bt_image)


# top_viewport = snapshot(256, 16, top_snap, 60.0)


# def main_snap(draw, width, height):
#     print('main')
#     draw.text((0, 0), 'Radio eins nur für Erwachsene',
#               fill='white', font=font_28)


# main_viewport = snapshot(256, 28, main_snap, 1.0)

# viewport.add_hotspot(top_viewport, (0, 0))
# viewport.add_hotspot(main_viewport, (0, 64-29))

# while True:
#     viewport.refresh()
#     time.sleep(0.500)


from enum import Enum


class PlaybackMode(Enum):
    Radio = 1
    CD = 2
    BT = 3


test = PlaybackMode.Radio


print(test)


test = PlaybackMode.BT

print(test)
