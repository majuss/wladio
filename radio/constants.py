FPS = 60
MUSIC_LIB_PATH = '/home/pi/'
STATIONS_FILE = 'stations.json'
MUSIC_LIB_FILE = 'music_lib.json'
CD_PLAYER_START_VOL = 30
RADIO_PLAYER_START_VOL = 25

SCROLL_SPEED = 3

LAT = "52.360550"
LONG = "14.062827"
ELEV = "10"

PREC_THRESHOLD = 1
PREC_SUM_THRESHOLD = 2

# IR Codes
# Apple Remote
IR_MENU = [9119, 4593, 566, 608, 566, 1738, 566, 1739, 565, 1738, 568, 605, 567, 1739, 564, 1739, 566, 1738, 566, 1738, 566, 1737, 566, 1739, 565, 608, 566, 609, 565, 609, 566, 609,
           565, 1746, 566, 608, 567, 1738, 564, 609, 539, 634, 566, 609, 566, 608, 568, 607, 565, 609, 567, 1739, 565, 607, 566, 609, 565, 1739, 567, 1736, 566, 606, 567, 1739, 566, 609, 540]
IR_PLAY = [9119, 4590, 568, 605, 567, 1736, 568, 1738, 565, 1735, 595, 579, 594, 1708, 569, 1737, 563, 1741, 565, 1735, 567, 1738, 564, 1737, 567, 609, 563, 609, 564, 610, 566, 607,
           566, 1747, 565, 606, 569, 605, 591, 1712, 568, 606, 568, 608, 566, 607, 564, 608, 565, 610, 565, 1738, 567, 606, 568, 605, 567, 1740, 566, 1736, 593, 581, 562, 1742, 567, 605, 568]
IR_UP = [9117, 4590, 566, 607, 593, 1711, 566, 1736, 568, 1737, 567, 606, 566, 1737, 564, 1742, 564, 1737, 563, 1740, 564, 1738, 566, 1737, 566, 608, 565, 609, 566, 607, 567, 606,
         569, 1743, 567, 1737, 566, 1737, 567, 606, 566, 1738, 567, 606, 566, 607, 565, 609, 567, 607, 565, 1739, 565, 608, 566, 606, 567, 1738, 565, 1737, 567, 607, 567, 1736, 567, 609, 565]
IR_DOWN = [9117, 4589, 568, 606, 566, 1737, 566, 1734, 570, 1734, 594, 579, 569, 1733, 593, 1710, 566, 1737, 567, 1735, 569, 1737, 566, 1737, 566, 663, 512, 606, 569, 606, 565, 606,
           569, 1743, 565, 1739, 591, 581, 568, 1735, 567, 1736, 567, 607, 568, 606, 566, 606, 568, 606, 568, 1736, 592, 583, 567, 606, 566, 1737, 569, 1733, 568, 606, 565, 1737, 570, 606, 565]
IR_LEFT = [9117, 4590, 570, 607, 567, 1736, 569, 1732, 569, 1736, 567, 606, 569, 1735, 568, 1735, 569, 1736, 567, 1736, 569, 1733, 569, 1733, 571, 605, 565, 608, 570, 603, 568, 608,
           567, 1744, 594, 582, 590, 581, 569, 604, 567, 1739, 570, 603, 567, 606, 566, 607, 570, 607, 565, 1736, 566, 606, 565, 612, 565, 1736, 570, 1732, 568, 608, 571, 1730, 594, 580, 569]
IR_RIGHT = [9117, 4589, 567, 606, 566, 1736, 566, 1736, 570, 1734, 568, 607, 565, 1737, 568, 1734, 567, 1736, 590, 1712, 564, 1738, 569, 1732, 569, 608, 566, 608, 564, 608, 569, 605,
            566, 1744, 566, 1736, 594, 1709, 567, 1736, 569, 604, 568, 609, 566, 606, 576, 596, 566, 607, 568, 1734, 571, 605, 565, 610, 564, 1734, 571, 1732, 568, 604, 571, 1735, 594, 580, 568]
