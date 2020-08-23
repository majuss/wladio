import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

k1 = 17
k2 = 22
k3 = 23

GPIO.setup(17, GPIO.OUT) # relay door
GPIO.setup(22, GPIO.OUT) # relay door
GPIO.setup(23, GPIO.OUT) # relay door

# GPIO.output(k1, GPIO.LOW)
# GPIO.output(k2, GPIO.LOW)
# GPIO.output(k3, GPIO.LOW)

GPIO.output(k1, GPIO.HIGH)
sleep(1)
GPIO.output(k2, GPIO.HIGH)
sleep(1)
GPIO.output(k3, GPIO.HIGH)
sleep(1)
GPIO.output(k1, GPIO.LOW)
sleep(1)
GPIO.output(k2, GPIO.LOW)
sleep(1)
GPIO.output(k3, GPIO.LOW)

while True:
    sleep(1)