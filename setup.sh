sudo usermod -a -G i2c,spi,gpio pi

# Linux packages
sudo apt install -y libmpv1
sudo apt install -y python3-venv libdbus-1-dev libudev-dev libical-dev libreadline-dev bluez-tools

# For luma.oled
sudo apt install -y python-dev python3-dev python-pip libfreetype6-dev libjpeg-dev build-essential libopenjp2-7 libtiff5

# For IR
sudo apt install -y lirc python-pylirc liblirc-dev
# sudo modprobe lirc_dev
# sudo modprobe lirc_rpi gpio_in_pin=17 gpio_out_pin=23


# sudo nano /boot/config.txt
# dtoverlay=lirc-rpi,gpio_in_pin=17,gpio_out_pin=23


# Python venv
python3 -m venv venv
source venv/bin/activate
pip3 install wheel cython
pip3 install python-mpv luma.oled pi-rc522 adafruit-circuitpython-bme680 adafruit-circuitpython-bme280 adafruit-circuitpython-ads1x15 pyky040


sudo mv /etc/lirc/lircd.conf.dist /etc/lirc/lircd.conf
git clone https://github.com/tompreston/python-lirc.git
find python-lirc -name '*.pyx' -exec cython {} \;
pip3 install python-lirc/
rm -rf python-lirc


## Bluetooth
# git clone https://github.com/bluez/bluez.git

### Patches

# In venv/lib/python3.7/site-packages/adafruit_bme680.py replace "address=0x77" with "address=0x76". The address is hardcoded for some reason...
# In venv/lib/python3.7/site-packages/pirc522/rfid.py


#    def wait_for_tag(self, timeout = 1):
#        # enable IRQ on detect
#        self.init()
#        self.irq.clear()
#        self.dev_write(0x04, 0x00)
#        self.dev_write(0x02, 0xA0)
#        # wait for it
#        waiting = True
#        waited = 0
#        while waiting:
#            self.dev_write(0x09, 0x26)
#            self.dev_write(0x01, 0x0C)
#            self.dev_write(0x0D, 0x87)
#            waiting = not self.irq.wait(0.1)
#
#            waited += 0.1
#
#            if timeout <= waited:
#                print("waited enough")
#                break
#
#        self.irq.clear()
#        self.init()

# Add timeout


# In venv/lib/python3.7/site-packages/pirc522/rfid.py
# set pinmode to BCM and change the PINs to BCM not Board Pins

# In venv/lib/python3.7/site-packages/pyky040.py
# Line 122 set interval to 100000 instead of 1000