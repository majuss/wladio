import RPi.GPIO as GPIO  
from time import sleep     

GPIO.setmode(GPIO.BCM)   

GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, GPIO.PUD_UP)

GPIO.setup(23, GPIO.IN, GPIO.PUD_DOWN)


def callie4(channel):
    print("callie 4")

def callie12(channel):
    print("callie 12")

def callie19(channel):
    print("callie 19")

def callie20(channel):
    print("callie 20")

def callie21(channel):
    print("callie 21")

def callie27(channel):
    print("callie 27")

def callie23(channel):
    sleep(0.01)
    print(GPIO.input(channel))
    print("callie 23")


def callie23r(channel):
    print("callie 12 raising")

GPIO.add_event_detect(4, GPIO.FALLING, callback=callie4, bouncetime=350)
GPIO.add_event_detect(12, GPIO.FALLING, callback=callie12, bouncetime=350)
GPIO.add_event_detect(19, GPIO.FALLING, callback=callie19, bouncetime=350)
GPIO.add_event_detect(20, GPIO.FALLING, callback=callie20, bouncetime=350)
GPIO.add_event_detect(21, GPIO.FALLING, callback=callie21, bouncetime=350)
GPIO.add_event_detect(27, GPIO.FALLING, callback=callie27, bouncetime=350)

GPIO.add_event_detect(23, GPIO.BOTH, callback=callie23, bouncetime=250)
# GPIO.add_event_detect(23, GPIO.RISING, callback=callie23r, bouncetime=350)


try:
  while True:
    # nix Sinnvolles tun

    sleep(1)
except KeyboardInterrupt:
  GPIO.cleanup()
  print("\nBye")

