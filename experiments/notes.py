    # @cdPlayer.property_observer('eof-reached')
    # def time_observer(name, value):
    #     print('eof-reached')
    #     print(name)
    #     print(value)

    # @cdPlayer.event_callback('end-file')
    # def my_handler(event):
    #     print('EVENT <<---------------')
    #     print('end-file')

    #     global playback_mode

    #     cdPlayer.command('stop')

    #     # switch back to radio
    #     radioPlayer.pause = False
    #     playback_mode = PlaybackMode.Radio
    # import pulseio
    # import adafruit_irremote

    # pulses = pulseio.PulseIn(22, maxlen=200, idle_state=False)
    # decoder = adafruit_irremote.GenericDecode()

    # while True:
    #     # pulse = decoder.read_pulses(pulses)
    #     # print(pulse)
    #     try:
    #         for pulse in pulses:
    #             print(pulse)
    #     except Exception as e:
    #         print(e)

    #     sleep(0.1)