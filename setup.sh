# Linux packages
sudo apt install libmpv1

# For IR
sudo apt install lirc python-pylirc --yes
sudo modprobe lirc_dev
sudo modprobe lirc_rpi gpio_in_pin=17 gpio_out_pin=23


# sudo nano /boot/config.txt
# dtoverlay=lirc-rpi,gpio_in_pin=17,gpio_out_pin=23

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install python-mpv
pip install luma.oled
