# wladio
Building a WIFI radio based on a Raspberry Pi


## Audio

AMP is a TDA7492. It delivers 50 Watt.

## Display

Links:
- https://de.aliexpress.com/item/32949282762.html?spm=a2g0s.9042311.0.0.26e74c4dSrLkVM

- Oled 3.12"
- Controller: SSD1322

| OLED Pin | Name | Function    | Pi Pin |
|----------|------|-------------|--------|
| 1        | GND  | Ground      | 6      |
| 2        | VCC  | 3.3 V       | 1      |
| 4        | D0   | Clock       | 23     |
| 5        | D1   | MOSI        | 19     |
| 15       | RST  | Reset       | 22     |
| 14       | DC   | Data Common | 18     |
| 16       | CS   | Chip Select | 24     |

## Infrared

Links:
- https://www.instructables.com/id/Setup-IR-Remote-Control-Using-LIRC-for-the-Raspber/
- https://raspberrypi.stackexchange.com/questions/81876/raspberry-pi-3-not-lirc-not-running-working
- https://wiki.d-diot.com/system_administration/manual_installation/8_home_assistant_configuration#lirc

VS1838B
Pinout:
Data | GND | VCC (2.7 - 5 V)

## RFID

Links:
https://codingworld.io/project/rfid-grundlagen

## Bluetooth

Links:
https://circuitdigest.com/microcontroller-projects/diy-raspberry-pi-bluetooth-speaker

## Housing

Links:
https://hobbytischlerei.de/leistungen-hobbytischlerei.php

Max size is 50x25x15 cm

## Power

Links:


Input is Kaltgerätestecker at 230 V

Three powerdomains are needed:
- 12 V for the Amp
- 5 V for Raspberry and other peripheral devices
- 3.3 V for some peripheral devices like the screen and RFID reader 

## Hardware

| Device      | Type                          | Link                                                                                                                                                                                                                                                                                                                                                                                                   | Price | Ordered |
|-------------|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|---|
| Amp         | TDA7492                       | https://de.aliexpress.com/item/4000068636510.html?spm=a2g0s.9042311.0.0.4de84c4dEyjkvM                                                                                                                                                                                                                                                                                                                 | 8     |X
| OLED        | SSD1322                       | https://de.aliexpress.com/item/32988134507.html?spm=a2g0s.9042311.0.0.4de84c4dEyjkvM                                                                                                                                                                                                                                                                                                                   | 17    |X
| Brain       | Raspberry Pi 4 2 GB           | https://www.amazon.de/Raspberry-Basisplatine-ARM-Cortex-A72-Bluetooth-Micro-HDMI/dp/B07TD42S27                                                                                                                                                                                                                                                                                                         | 44    |
| Woofer      | GHXAMP 5 ZOLL 8OHM 90W Woofer | https://de.aliexpress.com/item/32823669204.html?spm=a2g0o.cart.0.0.40e73c00uK2yp6&mp=1                                                                                                                                                                                                                                                                                                                 | 46    |X
| Tweeter     | GHXAMP 2 Zoll 4OHM            | https://de.aliexpress.com/item/32834511016.html?spm=a2g0o.cart.0.0.40e73c00uK2yp6&mp=1                                                                                                                                                                                                                                                                                                                 | 16    |X
| Wood        | Leimholz Eiche                | https://www.hornbach.de/shop/Leimholzplatte-Eiche-B-C-2000x600x18-mm/8203386/artikel.html?varCat=S13937&utm_content=Baustoffe,%20Holz,%20Fenster%20&utm_medium=cpc&utm_source=bing&utm_campaign=P%20-%20Bing%20Shopping%20-%20Alle%20Bereiche&utm_term=4580153126496934&wt_mc=de.paid.sea.bing.alwayson_assortment..pla.279170410.1224855993878720.&msclkid=3f78928e590c124c863dcce135cef13a##v8203381 | 60    |
| Crossover   | GHXAMP 2 Weg Crossover        | https://de.aliexpress.com/item/32824193299.html?spm=a2g0o.cart.0.0.40e73c00uK2yp6&mp=1                                                                                                                                                                                                                                                                                                                 | 24    |
| 12 V Supply | Meanwell                      | https://www.conrad.de/de/p/mean-well-lrs-150-12-ac-dc-netzteilbaustein-geschlossen-12-5-a-150-w-12-v-dc-1439463.html                                                                                                                                                                                                                                                                                   | 23    |
| 5 V Supply  | Meanwell                      | https://www.conrad.de/de/p/mean-well-rs-15-5-ac-dc-netzteilbaustein-geschlossen-3-a-15-w-5-v-dc-1297280.html                                                                                                                                                                                                                                                                                           | 10    |
| SD-Card     | Sandisk Extreme Pro 128 GB    | https://www.amazon.de/SanDisk-microSDXC-Speicherkarte-SD-Adapter-A2-App-Performance/dp/B07G3H5RBT                                                                                                                                                                                                                                                                                                      | 35    |

