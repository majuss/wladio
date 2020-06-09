import dbus

bus = dbus.SystemBus()

obj = bus.get_object("org.bluez", "/org/bluez/hci0/dev_94_87_E0_8C_6C_21")

props = obj.getProperties(dbus_interface='org.bluez.Device1.Connected')

print(obj.__dict__)
