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