from busio import I2C
import adafruit_bme680
import time
import board

# Create library object using our Bus I2C port
# i2c = I2C(3, 2)
# # Valid I2C ports: ((3, 3, 2), (1, 3, 2), (0, 1, 0))
# # i2c = I2C(6, 70)
# print(board.SCL)
# print(board.SDA)

i2c = I2C(board.SCL, board.SDA)
 
# Lock the I2C device before we try to scan
while not i2c.try_lock():
    pass
# Print the addresses found once
print("I2C addresses found:", [hex(device_address)
                               for device_address in i2c.scan()])
 
# Unlock I2C now that we're done scanning.
i2c.unlock()
print(i2c._i2c.__dict__)

bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1013.25

while True:
    print("\nTemperature: %0.1f C" % bme680.temperature)
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)

    time.sleep(2)