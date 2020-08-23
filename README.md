# wladio
Building a WIFI radio based on a Raspberry Pi

## Must have until field test


## Nice to haves
- Volume gentle rising
- Bedienungsanleitung
- Error handling kein Internet
- rise volume after mute / pause and rewind for n seconds

## Known Bugs


## Audio

AMP is a TDA7492. It delivers 50 Watt.
USB-Klinke Interface is: Sabrent USB Externe Soundkarte - C-Media Electronics, Inc. Audio Adapter (Unitek Y-247A)

## On / Off button

- Real switch that cuts the 12 V of the AMP
- Connected via voltage divider to GPIO12

## Display

Links:
- https://de.aliexpress.com/item/32949282762.html?spm=a2g0s.9042311.0.0.26e74c4dSrLkVM

- Oled 3.12"
- Controller: SSD1322

| OLED Pin | Name | Function    | BCM Pin| Board Pin |
|----------|------|-------------|--------|---------|
| 1        | GND  | Ground      | GND    |  6      |
| 2        | VCC  | 3.3 V       | VCC    |  1      |
| 4        | D0   | Clock       | 11 SCLK|  23     |
| 5        | D1   | MOSI        | 10 MOSI|  19     |
| 15       | RST  | Reset       | 25     |  22     |
| 14       | DC   | Data Common | 24     |  18     |
| 16       | CS   | Chip Select | 8 CE0  |  24     |

## Infrared

Links:
- https://www.instructables.com/id/Setup-IR-Remote-Control-Using-LIRC-for-the-Raspber/
- https://raspberrypi.stackexchange.com/questions/81876/raspberry-pi-3-not-lirc-not-running-working
- https://wiki.d-diot.com/system_administration/manual_installation/8_home_assistant_configuration#lirc
- https://codingworld.io/project/infrarot-empfaenger-und-sender-am-pi

IR code should get rewritten with more recent lib: https://github.com/adafruit/Adafruit_CircuitPython_IRRemote

VS1838B
Pinout seen from front of sensor:
|1|2|3|
|---|---|---|
|Data | GND | VCC (2.7 - 5 V)|

Data goes on GPIO18 (Board12, see /boot/config.txt)

When install of linux package `lirc` fails do: `sudo mv /etc/lirc/lirc_options.conf.dist /etc/lirc/lirc_options.conf` then install again

Config database: http://lirc-remotes.sourceforge.net/remotes-table.html

Add line to `/boot/config.txt`: `dtoverlay=gpio-ir,gpio_out_pin=17,gpio_in_pin=18,gpio_in_pull=up`

Edit: `/etc/lirc/lirc_options.conf`
Set Driver to `default` and device to `/dev/lirc0`

`sudo nano /etc/lirc/lircrc` 
Example lircrc mapping for Philips AZ1565 is inside `ir` directory.

## Volume knob

Links:
https://www.ebay.de/itm/Drehregler-Drehgeber-Rotary-Encoder-Arduino-KY-040-Potentiometer-Poti-Raspberry/252713917550
https://tutorials-raspberrypi.de/raspberry-pi-ky040-drehregler-lautstaerkeregler/

KY-040 digital encoder with push button. Coverered maybe by the original Sony plastic knob.

The knob should control the system audio, or the player audio, if the player takes the audio from the last player, when it's active.


CLK = Pin 29
DT = Pin 31
SW = Pin 33

## RFID

Links:
https://codingworld.io/project/rfid-grundlagen

|Function|BMC Pin|Board Pin|
|---|---|---|
|RST|16|36|
|IRQ|26 |37|
|MISO|9 MISO| 21|
|MOSI|10 MOSI| |19|
|SCK|11 SCLK |23|
|SDA|7 CE1 |26|

## Bluetooth

Links:
https://circuitdigest.com/microcontroller-projects/diy-raspberry-pi-bluetooth-speaker
https://www.raspberrypi.org/forums/viewtopic.php?t=235519
https://www.raspberrypi.org/forums/viewtopic.php?t=164400

USB-Bluetooth interface: Sabrent Bluetooth-Adapter USB Bluetooth 4.0 - Cambridge Silicon Radio, Ltd Bluetooth Dongle (HCI mode)

When Error: `Sap driver initialization failed appears`:

sudo nano /etc/systemd/system/bluetooth.target.wants/bluetooth.service

ExecStart=/usr/lib/bluetooth/bluetoothd --noplugin=sap

sudo systemctl daemon-reload
sudo service bluetooth restart


## Sensors

Both via I2C, outdoor Bosch BME680 on custom breakout. Indoor Bosch BME280 and standard breakout.

## Housing

Links:
https://hobbytischlerei.de/leistungen-hobbytischlerei.php

Final size will be 520 x 180 x 170

## Power

Links:


Input is Kaltgerätestecker at 230 V

Three powerdomains are needed:
- 12 V for the Amp
- 5 V for Raspberry and other peripheral devices
- 3.3 V for some peripheral devices like the screen and RFID reader, IR sensor, Weather sensors, digital encoder

## Hardware

| Device      | Type                          | Link                                                                                                                                                                                                                                                                                                                                                                                                   | Price | Ordered |
|-------------|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|---|
| Amp         | TDA7492                       | https://de.aliexpress.com/item/4000068636510.html?spm=a2g0s.9042311.0.0.4de84c4dEyjkvM                                                                                                                                                                                                                                                                                                                 | 8     |X
| OLED        | SSD1322                       | https://de.aliexpress.com/item/32988134507.html?spm=a2g0s.9042311.0.0.4de84c4dEyjkvM                                                                                                                                                                                                                                                                                                                   | 17    |X
| Brain       | Raspberry Pi 4 2 GB           | https://www.amazon.de/Raspberry-Basisplatine-ARM-Cortex-A72-Bluetooth-Micro-HDMI/dp/B07TD42S27                                                                                                                                                                                                                                                                                                         | 44    |X
| Woofer      | GHXAMP 5 ZOLL 8OHM 90W Woofer | https://de.aliexpress.com/item/32823669204.html?spm=a2g0o.cart.0.0.40e73c00uK2yp6&mp=1                                                                                                                                                                                                                                                                                                                 | 46    |X
| Tweeter     | GHXAMP 2 Zoll 4OHM            | https://de.aliexpress.com/item/32834511016.html?spm=a2g0o.cart.0.0.40e73c00uK2yp6&mp=1                                                                                                                                                                                                                                                                                                                 | 16    |X
| Wood        | Leimholz Eiche                | https://www.hornbach.de/shop/Leimholzplatte-Eiche-B-C-2000x600x18-mm/8203386/artikel.html?varCat=S13937&utm_content=Baustoffe,%20Holz,%20Fenster%20&utm_medium=cpc&utm_source=bing&utm_campaign=P%20-%20Bing%20Shopping%20-%20Alle%20Bereiche&utm_term=4580153126496934&wt_mc=de.paid.sea.bing.alwayson_assortment..pla.279170410.1224855993878720.&msclkid=3f78928e590c124c863dcce135cef13a##v8203381 | 60    |
| Crossover   | GHXAMP 2 Weg Crossover        | https://de.aliexpress.com/item/32824193299.html?spm=a2g0o.cart.0.0.40e73c00uK2yp6&mp=1                                                                                                                                                                                                                                                                                                                 | 24    |X
| 12 V Supply | Meanwell                      | https://www.conrad.de/de/p/mean-well-lrs-150-12-ac-dc-netzteilbaustein-geschlossen-12-5-a-150-w-12-v-dc-1439463.html                                                                                                                                                                                                                                                                                   | 23    |
| 5 V Supply  | Meanwell                      | https://www.conrad.de/de/p/mean-well-rs-15-5-ac-dc-netzteilbaustein-geschlossen-3-a-15-w-5-v-dc-1297280.html                                                                                                                                                                                                                                                                                           | 10    |
| SD-Card     | Sandisk Extreme Pro 128 GB    | https://www.amazon.de/SanDisk-microSDXC-Speicherkarte-SD-Adapter-A2-App-Performance/dp/B07G3H5RBT                                                                                                                                                                                                                                                                                                      | 35    |

