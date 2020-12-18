"""
Display the Raspberry Pi logo (loads image as .png).
"""

import os.path
# from demo_opts import get_device
from PIL import Image
from PIL import ImageDraw

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322


serial = spi(device=0, port=0)
device = ssd1322(serial)


def main():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'images', '../../../radio/ressources/cloud.png'))
    logo = Image.open(img_path).convert("RGBA")
    # fff = Image.new(logo.mode, logo.size, (255,) * 4)
    # draw2 = ImageDraw.Draw(logo)
    # logo.resize((256,64), resample=Image.BILINEAR)
    # print(logo.size)
    background = Image.new("RGBA", device.size, "black")
    background.paste(logo, (100, 30))
    x = background.convert(device.mode)

    # img = Image.composite(background, logo)
    # posn = ((device.width - logo.width) // 2, 0)
    # print(posn)
    # while True:
    #     for angle in range(0, 360, 2):
    #         # rot = logo.rotate(angle, resample=Image.BILINEAR)
    #         # img = Image.composite(rot, fff, rot)
    #         background.paste(fff, posn)
    #         device.display(logo.convert(device.mode))
    while True:
        device.display(x)
        # with canvas(device) as draw:
        # draw.png(logo)
        # draw(logo)
        # print(draw.__dir__())
        # print(type(fff))


if __name__ == "__main__":
    try:
        # device = get_device()
        main()
    except KeyboardInterrupt:
        pass
