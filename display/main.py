from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
#serial = i2c(port=1, address=0x3C)
serial = spi(device=0, port=0)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1322(serial)

while True:
    with canvas(device) as draw:
        draw.rectangle((0, 0, 64, 32), outline="white", fill="white")
       # draw.text((30, 40), "Hello World", fill="white")

