from gpiozero import Button, InputDevice, DigitalInputDevice

from signal import pause

driveway = Button(21, bounce_time=0.05)


def callback_driveway():
    print("pressed")

driveway.when_pressed = callback_driveway

pause()