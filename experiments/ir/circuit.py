# import pulseio
# from time import sleep
# import adafruit_irremote

# pulses = pulseio.PulseIn(18, maxlen=200, idle_state=False)
# decoder = adafruit_irremote.GenericDecode()

# while True:
#     pulse = decoder._read_pulses_non_blocking(pulses)
#     print(pulse)
#     # try:
#     #     for pulse in pulses:
#     #         print(pulse)
#     # except Exception as e:
#     #     print(e)

#     sleep(0.1)

# Circuit Playground Express Demo Code
# Adjust the pulseio 'board.PIN' if using something else
import pulseio
import board
import adafruit_irremote

pulsein = pulseio.PulseIn(18, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()


while True:
    pulses = decoder.read_pulses(pulsein)
    print("Heard", len(pulses), "Pulses:", pulses)
    try:
        code = decoder.decode_bits(pulses)
        print(type(code))
        print("Decoded:", code)
    except adafruit_irremote.IRNECRepeatException:  # unusual short code!
        print("NEC repeat!")
    except adafruit_irremote.IRDecodeException as e:     # failed to decode
        print("Failed to decode: ", e.args)

    print("----------------------------")