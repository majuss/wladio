import threading
import random
from time import sleep
bme280_temp = 0
bme680_temp = 0

def sensor_handler():
    global bme280_temp
    global bme680_temp
    while True:
        bme280_temp = random.randrange(10, 30)
        bme680_temp = random.randrange(10, 30)
        sleep(60)

def get_data():
    global bme280_temp
    global bme680_temp
    return bme280_temp, bme680_temp

sensor_thread = threading.Thread(target=sensor_handler)
sensor_thread.start()