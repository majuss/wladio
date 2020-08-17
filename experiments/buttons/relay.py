import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

pin = 14

GPIO.setup(pin, GPIO.OUT) # relay door

GPIO.output(pin, GPIO.HIGH)

while True:
    sleep(1)