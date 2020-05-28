import threading
bme280_temp = 0
bme680_temp = 0

def init_sensors():
    import board
    import digitalio
    from busio import I2C
    import adafruit_bme280
    import adafruit_bme680

    i2c = I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
    bme280.sea_level_pressure = 1013.25
    bme680.sea_level_pressure = 1013.25
    return bme280, bme680

def sensor_handler():
    global bme280_temp
    global bme680_temp
    bme280, bme680 = init_sensors()
    while True:
        # print("BME280: %0.1f")
        # print("\nTemperature: %0.1f C" % bme280.temperature)
        # print("Humidity: %0.1f %%" % bme280.humidity)
        # print("Pressure: %0.1f hPa" % bme280.pressure)
        # print("Altitude = %0.2f meters" % bme280.altitude)

        # print("\nTemperature: %0.1f C" % bme680.temperature)
        # print("Gas: %d ohm" % bme680.gas)
        # print("Humidity: %0.1f %%" % bme680.humidity)
        # print("Pressure: %0.3f hPa" % bme680.pressure)
        # print("Altitude = %0.2f meters" % bme680.altitude)
        bme280_temp = bme280.temperature
        bme680_temp = bme680.temperature


        sleep(60)

def get_data():
    global bme280_temp
    global bme680_temp
    return bme280_temp, bme680_temp

sensor_thread = threading.Thread(target=sensor_handler)
sensor_thread.start()