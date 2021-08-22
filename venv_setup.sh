rm -rf /home/pi/wladio/venv
python3.9 -m venv venv
source venv/bin/activate
pip3.9 install wheel cython
pip3.9 install python-mpv luma.oled pi-rc522 adafruit-circuitpython-bme680 adafruit-circuitpython-bme280 pygobject requests xmltodict pi-ina219 evdev dbus-python
