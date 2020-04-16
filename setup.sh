sudo usermod -a -G i2c,spi,gpio pi

# Linux packages
sudo apt install -y libmpv1
sudo apt install -y python3-venv

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
pip install python-mpv luma.oled wheel cython pi-rc522 Adafruit-DHT


sudo mv /etc/lirc/lircd.conf.dist /etc/lirc/lircd.conf
git clone https://github.com/tompreston/python-lirc.git
find python-lirc -name '*.pyx' -exec cython {} \;
pip3 install python-lirc/
rm -rf python-lirc


# enable spi foo in rapsberry-config see bugs.txt
