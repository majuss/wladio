from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from time import sleep

import os.path
import math
from PIL import ImageFont
from PIL import Image
main_font = ImageFont.truetype("../radio/ressources/hel_new.otf",25) # 68 max # min 25

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
#serial = i2c(port=1, address=0x3C)
serial = spi(device=0, port=0)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1322(serial)

stringie = 'wwwwwwd'

# font_size = math.floor(-20.226 * math.log(len(stringie)) + 68.882)
# print(font_size)
main_font = ImageFont.truetype("../radio/ressources/hel_new.otf", 60)


img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'images', '../../radio/ressources/cloud.png'))
logo = Image.open(img_path).convert("RGBA")
fff = Image.new(logo.mode, logo.size, (255,) * 4)


background = Image.new("RGBA", device.size, "white")
posn = ((device.width - logo.width) // 2, 0)

while True:
    device.display(image)
    # with canvas(device) as draw:
        # draw.rectangle((0, 0, 64, 64), outline="white", fill="white") #xy xy
        # draw.text((0,0),stringie, fill="white", font=main_font) 
        # sleep(5)
    # draw.text((30, 40), "Hello World", fill="white")

        # img = Image.composite(fff)
        background.paste(fff, posn)
        device.display(background.convert(device.mode))
