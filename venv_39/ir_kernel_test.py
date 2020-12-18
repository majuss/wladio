from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/input/event1')

# print(dev.capabilities(verbose=True))

# print(dev)
for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        print(categorize(event))
        print(dir(event))
        print((event.code))
        print(event.usec)
        print(event.type)
        print(event.value)

