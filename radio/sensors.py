import utils as utils

logger = utils.create_logger(__name__)


class DummySensor:
    def __init__(self):
        self.temperature = 99.9
        self.humidity = -1
        self.sea_level_pressure = 0


def init_sensors():
    import board

    from busio import I2C
    import adafruit_bme280
    import adafruit_bme680

    i2c = I2C(board.SCL, board.SDA)
    bme280 = None
    bme680 = None

    try:
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    except Exception as e:
        logger.debug('Couldnt init BME280: {}'.format(e))
        bme280 = DummySensor()

    try:
        bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    except Exception as e:
        logger.debug('Couldnt init BME680: {}'.format(e))
        bme680 = DummySensor()

    bme280.sea_level_pressure = 1013.25
    bme680.sea_level_pressure = 1013.25

    return bme280, bme680


bme280, bme680 = init_sensors()


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
    return bme280.temperature, bme680.temperature, bme280.humidity, bme680.humidity
