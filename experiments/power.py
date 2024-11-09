from ina219 import INA219
from time import sleep

SHUNT_OHMS = 0.1

ina = INA219(SHUNT_OHMS, busnum=1)
ina.configure()

while True:
    voltage = ina.voltage()

    print(voltage)

    sleep(1)
