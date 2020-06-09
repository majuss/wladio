import pulseio
from time import sleep
import adafruit_irremote

pulses = pulseio.PulseIn(22, maxlen=200, idle_state=False)
decoder = adafruit_irremote.GenericDecode()

while True:
    pulse = decoder._read_pulses_non_blocking(pulses)
    print(pulse)
    # try:
    #     for pulse in pulses:
    #         print(pulse)
    # except Exception as e:
    #     print(e)

    sleep(0.1)