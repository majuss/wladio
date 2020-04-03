sudo usermod -a -G i2c,spi,gpio pi


# Linux packages
sudo apt install libmpv1

# For luma.oled
sudo apt install python-dev python3-dev python-pip libfreetype6-dev libjpeg-dev build-essential libopenjp2-7 libtiff5

# For IR
sudo apt install lirc python-pylirc --yes
sudo modprobe lirc_dev
sudo modprobe lirc_rpi gpio_in_pin=17 gpio_out_pin=23


# sudo nano /boot/config.txt
# dtoverlay=lirc-rpi,gpio_in_pin=17,gpio_out_pin=23

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install python-mpv luma.oled wheel cython mfrc522