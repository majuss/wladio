sudo usermod -a -G i2c,spi,gpio pi

# Linux packages
sudo apt install -y libmpv1
sudo apt install -y python3-venv libdbus-1-dev libudev-dev libical-dev libreadline-dev bluez-tools libglib2.0-dev libgirepository1.0-dev libcairo2-dev

# For luma.oled
sudo apt install -y python-dev python3-dev python-pip libfreetype6-dev libjpeg-dev build-essential libopenjp2-7 libtiff5

# For IR
sudo apt install -y lirc python-pylirc liblirc-dev
# sudo modprobe lirc_dev
# sudo modprobe lirc_rpi gpio_in_pin=17 gpio_out_pin=23


# sudo nano /boot/config.txt
# dtoverlay=lirc-rpi,gpio_in_pin=17,gpio_out_pin=23



# autologin pi
https://maker-tutorials.com/raspberry-pi-benutzer-automatisch-anmelden-booten/
cat /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I 38400 linux



# keep app running (may not work becuase of xdg_ and dbus session bus address env variables 
sudo loginctl enable-linger pi
=======
# enable feature when installing pillow
(venv) pip3.9 install --upgrade Pillow --global-option="build_ext" --global-option="--enable-[feature]"



# Python venv
python3 -m venv venv
source venv/bin/activate
pip3 install wheel cython
pip3 install python-mpv luma.oled pi-rc522 adafruit-circuitpython-bme680 adafruit-circuitpython-bme280 pygobject requests xmltodict pi-ina219 evdev dbus-python


sudo mv /etc/lirc/lircd.conf.dist /etc/lirc/lircd.conf
git clone https://github.com/tompreston/python-lirc.git
find python-lirc -name '*.pyx' -exec cython {} \;
pip3 install python-lirc/
rm -rf python-lirc



## Bluetooth
# git clone https://github.com/bluez/bluez.git
# pactl load-module module-bluetooth-discover

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
# set RST, IRQ an CE Pins to match documentation (16, 26, 1)

# at line 40 and 41, all settings depend on wiering wiring
#def __init__(self, bus=0, device=1, speed=1000000, pin_rst=16,
#    pin_ce=1, pin_irq=26, pin_mode=GPIO.BCM):



# IN mpv.py change line ~50 `backend = CDLL(sofile)` to `backend = CDLL('/usr/local/lib/libmpv.so')`

# setup to autologin user in console mode

# Systemd service
# $ systemctl --user daemon-reload
# $ systemctl --user enable wladio@pi.service
# # reboot or $ systemctl --user start wladio@pi.service

# $ cat ~/.config/systemd/user/wladio@pi.service 
# [Unit]
# Description=wladio
# After=time-sync.target
# RestartSec=2
# StartLimitIntervalSec=10
# StartLimitBurst=100


# [Service]
# Type=simple
# TimeoutStartSec=5

# Restart=always
# RestartSec=10
# ExecStart=/home/pi/wladio/venv/bin/python3 main.py
# WorkingDirectory=/home/pi/wladio/radio

# [Install]
# WantedBy=default.target






# pi update
## ic2
check i2c devices with i2cdetect -l / i2cdetect -y busnum eg

    i2cdetect -l
    
    i2cdetect -y 1
