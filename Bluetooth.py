from bluetooth import *
import dbus # Used to set up the SDP record
import dbus.service


#
#define a bluez 5 profile object for our keyboard
#
class BTKbBluezProfile(dbus.service.Object):
    fd = -1

    @dbus.service.method("org.bluez.Profile1",
                                    in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1",
                                    in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        print("NewConnection(%s, %d)" % (path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.fd > 0):
            os.close(self.fd)
            self.fd = -1

    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

class Bluetooth:
    """docstring for Gamepad"""
    HOST = 0
    PORT = 1
    P_CTRL = 17
    P_INTR = 19
    PROFILE_DBUS_PATH="/bluez/yaptb/btkb_profile" #dbus path of  the bluez profile we will create
    UUID = "1f16e7c0-b59b-11e3-95d2-0002a5d5c51b"
    MY_ADDRESS="B8:27:EB:CC:FD:01"



    def __init__(self, sdp, classname, devname):

        print("Setting up BT device")

        print("Configuring for name "+devname)

        #set the device class to a keybord and set the name
        os.system("hciconfig hci0 up")
        os.system("hciconfig hcio class 0x002540")
        os.system("hciconfig hcio name " + devname)

        #make the device discoverable
        os.system("hciconfig hcio piscan")


        print("Configuring Bluez Profile")
        try:
            fh = open(sdp,"r")
        except Exception, e:
            sys.exit("Cannot open sdp_record file")
        self.service_record = fh.read()
        fh.close()

        opts = {
            "ServiceRecord":self.service_record,
            "Role":"server",
            "RequireAuthentication":False,
            "RequireAuthorization":False
        }

        #retrieve a proxy for the bluez profile interface
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez","/org/bluez"), "org.bluez.ProfileManager1")

        profile = BTKbBluezProfile(bus, Bluetooth.PROFILE_DBUS_PATH)

        manager.RegisterProfile(Bluetooth.PROFILE_DBUS_PATH, Bluetooth.UUID,opts)

        print("Profile registered ")



    #listen for incoming client connections
    #ideally this would be handled by the Bluez 5 profile 
    #but that didn't seem to work
    def listen(self):
        print("Waiting for connections")
        self.scontrol=BluetoothSocket(L2CAP)
        self.sinterrupt=BluetoothSocket(L2CAP)

        #bind these sockets to a port - port zero to select next available      
        self.scontrol.bind(("",self.P_CTRL))
        self.sinterrupt.bind(("",self.P_INTR ))

        #Start listening on the server sockets 
        self.scontrol.listen(1) # Limit of 1 connection
        self.sinterrupt.listen(1)

        self.ccontrol,cinfo = self.scontrol.accept()
        print ("Got a connection on the control channel from " + cinfo[0])

        self.cinterrupt, cinfo = self.sinterrupt.accept()
        print ("Got a connection on the interrupt channel from " + cinfo[0])



    # def __init__(self, sdp, classname, devname):
    #     self.classname = classname
    #     self.devname = devname
    #     self.soccontrol = BluetoothSocket(L2CAP)
    #     self.sockinter = BluetoothSocket(L2CAP)

    #     self.soccontrol.bind(("", Bluetooth.P_CTRL))
    #     self.sockinter.bind(("",Bluetooth.P_INTR))

    #     self.bus = dbus.SystemBus()
    #     try:

    #         SERVICE_NAME = "org.bluez"
    #         OBJECT_IFACE =  "org.freedesktop.DBus.ObjectManager"
    #         ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
    #         DEVICE_IFACE = SERVICE_NAME + ".Device1"
    #         PROPERTIES_IFACE = "org.freedesktop.DBus.Properties"
    #         bus = dbus.SystemBus()
    #         manager =  dbus.Interface(bus.get_object("org.bluez","/org/bluez"), "org.bluez.ProfileManager1")

    #         objects = manager.GetManagedObjects()
    #         for path, ifaces in objects.iteritems():
    #             adapter = ifaces.get(ADAPTER_IFACE)
    #             if adapter is None:
    #                 continue
    #             obj = bus.get_object(SERVICE_NAME, path)
    #         adapter = dbus.Interface(obj, ADAPTER_IFACE)

    #         self.manager = manager
    #         self.service = dbus.Interface(adapter,"org.bluez.Service")
    #     except Exception, e:
    #         sys.exit("Please turn on bluetooth %s" % e)
        

    #     opts = {
    #         "ServiceRecord":self.service_record,
    #         "Role":"server",
    #         "RequireAuthentication":False,
    #         "RequireAuthorization":False
    #     }

    #     profile = BTKbBluezProfile(bus, Bluetooth.PROFILE_DBUS_PATH)

    #     manager.RegisterProfile(Bluetooth.PROFILE_DBUS_PATH, Bluetooth.UUID,opts)


    # def listen(self):
    #     # self.service.handle = self.service.AddRecord(self.service_record)


    #     os.system("sudo hciconfig hci0 class "+self.classname)
    #     os.system("sudo hciconfig hci0 name "+self.devname)
    #     self.soccontrol.listen(1)
    #     self.sockinter.listen(1)
    #     print "waiting for connection"
    #     self.ccontrol, self.cinfo = self.soccontrol.accept()
    #     print "Control channel connected to "+self.cinfo[Bluetooth.HOST]
    #     self.cinter, self.cinfo = self.sockinter.accept()
    #     print "Interrupt channel connected to "+self.cinfo[Bluetooth.HOST]

    def sendInput(self, inp):
        print "sending input"
        str_inp = ""
        for elem in inp:
            if type(elem) is list:
                tmp_str = ""
                for tmp_elem in elem:
                    tmp_str += str(tmp_elem)
                for i in range(0,len(tmp_str)/8):
                    if((i+1)*8 >= len(tmp_str)):
                        str_inp += chr(int(tmp_str[i*8:],2))
                    else:
                        str_inp += chr(int(tmp_str[i*8:(i+1)*8],2))
            else:
                str_inp += chr(elem)
        self.cinterrupt.send(str_inp)