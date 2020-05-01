from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.core.virtual import viewport

from luma.oled.device import ssd1322
from time import sleep

import math
from PIL import ImageFont
main_font = ImageFont.truetype("../radio/fonts/hel_new.otf",68) # 68 max # min 26

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
#serial = i2c(port=1, address=0x3C)
serial = spi(device=0, port=0)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1322(serial)

stringie = 'Deine Mutter Lorem Ipsum'

# font_size = math.floor(-20.226 * math.log(len(stringie)) + 68.882)

font_size = 68
main_font = ImageFont.truetype("../radio/fonts/hel_new.otf", font_size)


while main_font.getsize(stringie)[0] > 256:
    font_size -= 1
    main_font = ImageFont.truetype("../radio/fonts/hel_new.otf", font_size)
    if font_size == 25:
        break


string_size = main_font.getsize(stringie)
print(string_size[1])
ycursor = math.ceil((64 - string_size[1])/2 +1)
print(ycursor)

virtual = viewport(device, width=max(device.width, string_size[0]), height=device.height)

while True:

    with canvas(virtual) as draw:
        draw.text((0, ycursor), stringie, fill="white", font=main_font) 
    i = 0
    sleep(0.5)

    while i < string_size[0] -  device.width :
        virtual.set_position((i, 0))
        if i == 0:
            sleep(0.5)
        i += 1
        sleep(0.03333)


