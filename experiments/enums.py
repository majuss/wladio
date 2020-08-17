
from enum import Enum


class DrawType(Enum):
    Text = 1
    Rect = 2


class PowerState(Enum):
    Standby = 1
    Powered = 2

    Unknown = 0xff


class PlaybackMode(Enum):
    Radio = 1
    CD = 2
    BT = 3

    Unknown = 0xff
