from time import sleep
import threading
import subprocess

import utils
import radio
import display
from enums import PlaybackMode, PowerState

logger = utils.create_logger(__name__)
STATE = utils.state()

# thread start stop
bluetooth_thread = None
bluetooth_pairable_thread = None


def _bluetooth():
    logger.debug('setup callback')

    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    from gi.repository import GLib

    DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    def device_property_changed(interface, changed, invalidated, path):
        iface = interface[interface.rfind(".") + 1:]

        print(interface)
        print(iface)
        print(changed)

        if iface == 'Device1':
            if "Connected" in changed:
                if changed['Connected']:

                    radio.mute_radio_and_pause_cd()
                    STATE['playback_mode'] = PlaybackMode.BT
                    logger.debug('Radio mode set to Bluetooth')

                    STATE['draw_bluetooth_icon'] = True
                    display.hard_refresh_top_viewport()
                    display.main_text('Bluetoothmodus eingeschalten')

                else:
                    logger.debug('Radio mode set to Radio')
                    STATE['playback_mode'] = PlaybackMode.Radio
                    radio.unmute_unpause_current_player()

                    STATE['draw_bluetooth_icon'] = False

                    if STATE['power_state'] is PowerState.Powered:
                        display.hard_refresh_top_viewport()

        elif iface == 'MediaPlayer1':
            if 'Track' in changed:
                track = changed['Track']
                txt = []

                if 'Title' in track:
                    txt.append(track['Title'])
                if 'Artist' in track:
                    txt.append(track['Artist'])
                if 'Album' in track:
                    txt.append(track['Album'])

                txt = ' - '.join(txt)

                logger.debug(
                    "BT track has changed to : {} detected".format(txt))
                display.main_text(txt)

    bus.add_signal_receiver(
        device_property_changed,
        bus_name='org.bluez',
        signal_name='PropertiesChanged',
        dbus_interface='org.freedesktop.DBus.Properties',
        path_keyword='path'
    )

    loop = GLib.MainLoop()
    loop.run()


def _bluetooth_pairable():
    t = threading.current_thread()
    while t.name == 'run':
        try:
            subprocess.call(['bluetoothctl', 'discoverable', 'on'])
        except:
            logger.error('bluetoothctl discoverable on failed')
        # 3 minutes https://www.linux-magazine.com/Issues/2017/197/Command-Line-bluetoothctl

        try:
            subprocess.call(['bluetoothctl', "pairable", 'on'])
        except:
            logger('bluetoothctl pairable on failed')

        logger.debug('renewed pairable')
        sleep(120)


def start_thread():
    global bluetooth_thread
    global bluetooth_pairable_thread

    if bluetooth_thread is None:
        bluetooth_thread = threading.Thread(target=_bluetooth)
        bluetooth_thread.name = 'run'
        bluetooth_thread.start()

    if bluetooth_pairable_thread is None:
        bluetooth_pairable_thread = threading.Thread(target=_bluetooth_pairable)
        bluetooth_pairable_thread.name = 'run'
        bluetooth_pairable_thread.start()


def stop_thread():
    global bluetooth_pairable_thread

    if bluetooth_pairable_thread is None:
        return

    bluetooth_pairable_thread.name = 'stop'
    bluetooth_pairable_thread = None
