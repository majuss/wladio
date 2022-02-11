import utils as utils
import json
from requests import get

logger = utils.create_logger(__name__)

feuchtigkeit = "http://127.0.0.1:8123/api/states/sensor.lumi_lumi_weather_humidity"
temperatur = "http://127.0.0.1:8123/api/states/sensor.lumi_lumi_weather_temperature"

headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjNWVlZDE3YTRiOTI0OTAwOGFiOTA2YzRjODMzMzFkMSIsImlhdCI6MTYyOTY3MjcwNiwiZXhwIjoxOTQ1MDMyNzA2fQ.uL83oxghly5BlutNZKSdgxzbMAlwpEUfagQ-MYxc3YM",
    "content-type": "application/json"
}


class DummySensor:
    def __init__(self):
        self.temperature = 99.9
        self.humidity = -1
        self.sea_level_pressure = 0


def init_sensors():
    import board
    from adafruit_bme280 import basic as adafruit_bme280

    from busio import I2C

    i2c = I2C(board.SCL, board.SDA)
    bme280 = None

    try:
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)
    except Exception as e:
        logger.debug('Couldnt init BME280: {}'.format(e))
        bme280 = DummySensor()

    bme280.sea_level_pressure = 1013.25

    return bme280


bme280 = init_sensors()


# def sensor_handler():
#     global bme280_temp
#     global bme680_temp
#     bme280, bme680 = init_sensors()
#     while True:
#         # print("BME280: %0.1f")
#         # print("\nTemperature: %0.1f C" % bme280.temperature)
#         # print("Humidity: %0.1f %%" % bme280.humidity)
#         # print("Pressure: %0.1f hPa" % bme280.pressure)
#         # print("Altitude = %0.2f meters" % bme280.altitude)

#         # print("\nTemperature: %0.1f C" % bme680.temperature)
#         # print("Gas: %d ohm" % bme680.gas)
#         # print("Humidity: %0.1f %%" % bme680.humidity)
#         # print("Pressure: %0.3f hPa" % bme680.pressure)
#         # print("Altitude = %0.2f meters" % bme680.altitude)
#         bme280_temp = bme280.temperature
#         bme680_temp =

#         sleep(60)


def get_data():  # 280 inside 680 outside
    data_feuchtigkeit = -99
    data_temperatur = -99

    try:
        response_feuchtigkeit = get(feuchtigkeit, headers=headers)
        data_feuchtigkeit = json.loads(response_feuchtigkeit.text)['state']

        response_temperatur = get(temperatur, headers=headers)
        data_temperatur = json.loads(response_temperatur.text)['state']
    except Exception as e:
        print('wireless temp sensor requests failed')
        print(e)

    # could be 'unavailable'
    try:
        data_temperatur = float(data_temperatur)
    except Exception as e:
        logger.debug('temp sensor: {}'.format(data_temperatur))
        data_temperatur = 99

    try:
        data_feuchtigkeit = float(data_feuchtigkeit)
    except Exception as e:
        logger.debug('humidity sensor, got: {}'.format(data_feuchtigkeit))
        data_feuchtigkeit = -1

    return bme280.temperature, data_temperatur, bme280.humidity, data_feuchtigkeit
