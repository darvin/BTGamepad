from Bluetooth import *
from Gamepad import *
import gtk
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

bt = Bluetooth("sdp_record_gamepad.xml","000508", "BT\ Gamepad")
bt.listen()
gp = Gamepad()
gp.register_keyboard_gobject_events(bt)
gtk.main()

