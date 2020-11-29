from time import sleep
import threading
import subprocess

import utils
import control
import display

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
                    logger.debug('device connected')
                    control.control_bluetooth_device_connected()

                else:
                    logger.debug('Radio mode set to Radio')
                    control.control_bluetooth_device_disconnected()

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
        except Exception as e:
            logger.error('bluetoothctl discoverable on failed: {}'.format(e))
        # 3 minutes https://www.linux-magazine.com/Issues/2017/197/Command-Line-bluetoothctl

        try:
            subprocess.call(['bluetoothctl', "pairable", 'on'])
        except Exception as e:
            logger('bluetoothctl pairable on failed: {}'.format(e))

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
