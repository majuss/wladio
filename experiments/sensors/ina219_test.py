#!/usr/bin/env python
from ina219 import INA219

SHUNT_OHMS = 0.1

def read():
    ina = INA219(SHUNT_OHMS)
    ina.configure()

    print("Bus Voltage: %.3f V" % ina.voltage())

if __name__ == "__main__":
    read()