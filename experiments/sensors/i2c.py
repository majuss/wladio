# CircuitPython demo - I2C scan
    
import time
    
import board
import busio
    
i2c = busio.I2C(board.SCL, board.SDA)
    
while not i2c.try_lock():
    pass
    
while True:
    print(board.SCL)
    print(board.SDA)
    print("I2C addresses found:", [hex(device_address)
                                    for device_address in i2c.scan()])
    time.sleep(2)
