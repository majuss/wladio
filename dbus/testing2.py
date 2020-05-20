import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import logging

# LOG_LEVEL = logging.INFO
LOG_LEVEL = logging.DEBUG
LOG_FILE = "/home/pi/log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()

logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)

connected = None
state = None
track = None
status = None

def playerHandler(interface, changed, invalidated, path):
    """Handle relevant property change signals"""
    logging.debug("Interface [{}] changed [{}] on path [{}]".format(interface, changed, path))
    iface = interface[interface.rfind(".") + 1:]
    for interfac in interface:
        print(interface)
    if iface == "Device1":
        if "Connected" in changed:
            connected = changed["Connected"]
    if iface == "MediaControl1":
        if "Connected" in changed:
            connected = changed["Connected"]
            if changed["Connected"]:
                logging.debug("MediaControl is connected [{}] and interface [{}]".format(path, iface))
                findPlayer()
    elif iface == "MediaTransport1":
        if "State" in changed:
            logging.debug("State has changed to [{}]".format(changed["State"]))
            state = (changed["State"])
        if "Connected" in changed:
            onnected = changed["Connected"]
    elif iface == "MediaPlayer1":
        if "Track" in changed:
            logging.debug("Track has changed to [{}]".format(changed["Track"]))
            track = changed["Track"]
        if "Status" in changed:
            logging.debug("Status has changed to [{}]".format(changed["Status"]))
            status = (changed["Status"])

def device_property_changed(*args, **kwargs):
    try:
        if args[1]['Connected']:
            print("BT mode engaged")
        else:
            print("bt disconnected")
    except Exception as e:
        print("error")
    print(args)
    print(kwargs)
    
    print(args[1])

bus.add_signal_receiver(
    playerHandler,
    bus_name='org.bluez',
    signal_name='PropertiesChanged',
    dbus_interface='org.freedesktop.DBus.Properties',
    path_keyword='path'
)

loop = GLib.MainLoop()
loop.run()

   