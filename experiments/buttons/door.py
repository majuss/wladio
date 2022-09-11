# GPIOZERO_PIN_FACTORY=native python3.9

from time import sleep
import threading
from gpiozero import Button


def pressed():
    print("button was pressed")


def released():
    print("button was released")


btn = Button(20)

btn.when_pressed = pressed
btn.when_released = released


def print_tags():
    while True:
        print('hello')
        sleep(1)


tag_thread = threading.Thread(target=print_tags)
tag_thread.start()
