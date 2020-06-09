import os
import sys
import logging
import logging.handlers
import signal
import dbus
import dbus.service
import dbus.mainloop.glib
# import glib
try:
    import gobject
except ImportError:
    from gi.repository import GObject as gobject


def device_property_changed():
    print('foo')

if __name__ == '__main__':

    # Get the system bus
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
    except Exception as ex:
        logger.error('Unable to get the system dbus: "{0}". Exiting. Is dbus running?'.format(ex.message))
        sys.exit(1)

    bus.add_signal_receiver(
        device_property_changed,
        bus_name='org.bluez',
        signal_name='PropertiesChanged',
        dbus_interface='org.freedesktop.DBus.Properties',
        path_keyword='path'
    )

    try:
        mainloop = gobject.MainLoop()
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
        # logger.error('Unable to run the gobject main loop')
        sys.exit(1)

    # logger.info('Shutting down')
    sys.exit(0)