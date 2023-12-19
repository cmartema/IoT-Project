# main server sent
from machine import Pin, UART
import sys
import time
import network
import socket
import urequests as requests

# Packet Code
STARTCODE = 0xEF01
COMMANDPACKET = 0x01
DATAPACKET = 0x02
ACKPACKET = 0x07
ENDDATAPACKET = 0x08

# Instruction code
VERIFYPASSWORD = 0x13
READSYSPARA = 0x0F
SETSYSPARA = 0x0E
GETIMAGE = 0x01
IMAGE2TZ = 0x02
REGMODEL = 0x05
STORE = 0x06
DELETE = 0x0C
EMPTY = 0x0D
FINGERPRINTSEARCH = 0x04

# Confirmation code
OK = 0x00
NOFINGER = 0x02


class FingerPrintSensor:
    debug = False

    password = None
    address = [0xFF, 0xFF, 0xFF, 0xFF]
    finger_id = None
    confidence = None
    templates = []
    template_count = None
    library_size = None
    security_level = None
    device_address = None
    data_packet_size = None
    baudrate = None
    system_id = None
    status_register = None

    def __init__(self, passwd=(0, 0, 0, 0)):

        self.uart = UART(2, 57600)
        self.uart.init(57600, bits=8, parity=None, stop=1, tx=17, rx=16, timeout=2000)
        self.password = passwd
        if self.verify_password() != OK:
            raise RuntimeError("Failed to find sensor, check wiring!")
        if self.read_sysparam() != OK:
            raise RuntimeError("Failed to read system parameters!")

    def verify_password(self):
        self.send_packet([VERIFYPASSWORD] + list(self.password))
        return bool(self.get_packet(12)[0])

    def read_sysparam(self):
        self.send_packet([READSYSPARA])
        r = self.get_packet(28)
        if r[0] != OK:
            raise RuntimeError("Command failed.")
        self.status_register = bytes(r[1:3])
        self.system_id = bytes(r[3:5])
        self.library_size = bytes(r[5:7])
        self.security_level = bytes(r[7:9])
        self.device_address = bytes(r[9:13])
        self.data_packet_size = bytes(r[13:15])
        self.baudrate = bytes(r[15:17])
        return r[0]

    def set_sysparam(self, param_num, param_val):
        self.send_packet([SETSYSPARA, param_num, param_val])
        r = self.get_packet(12)
        if r[0] != OK:
            raise RuntimeError("Command failed.")
        if param_num == 4:
            self.baudrate = param_val
        elif param_num == 5:
            self.security_level = param_val
        elif param_num == 6:
            self.data_packet_size = param_val
        return r[0]

    def get_image(self):
        self.send_packet([GETIMAGE])
        return self.get_packet(12)[0]

    def image_2_tz(self, slot):
        self.send_packet([IMAGE2TZ, slot])
        return self.get_packet(12)[0]

    def create_model(self):
        self.send_packet([REGMODEL])
        return self.get_packet(12)[0]

    def store_model(self, location, slot=1):
        self.send_packet([STORE, slot, location >> 8, location & 0xFF])
        return self.get_packet(12)[0]

    def delete_model(self, location):
        self.send_packet([DELETE, location >> 8, location & 0xFF, 0x00, 0x01])
        return self.get_packet(12)[0]

    def empty_library(self):
        self.send_packet([EMPTY])
        return self.get_packet(12)[0]

    def finger_search(self):
        self.read_sysparam()
        capacity = int.from_bytes(self.library_size, 'big')
        self.send_packet(
            [FINGERPRINTSEARCH, 0x01, 0x00, 0x00, capacity >> 8, capacity & 0xFF]
        )
        r = self.get_packet(16)
        self.finger_id = r[1:3]
        self.confidence = r[3:5]
        self.print_debug("finger_search packet:", r, data_type="hex")
        return r[0]

    def send_packet(self, data):
        packet = [STARTCODE >> 8, STARTCODE & 0xFF]
        packet = packet + self.address
        packet.append(COMMANDPACKET)

        length = len(data) + 2
        packet.append(length >> 8)
        packet.append(length & 0xFF)

        packet = packet + data

        checksum = sum(packet[6:])
        packet.append(checksum >> 8)
        packet.append(checksum & 0xFF)

        self.print_debug("send_packet length: ", len(packet))
        self.print_debug("send_packet data: ", packet, data_type='hex')
        self.uart.write(bytearray(packet))

    def get_packet(self, expected):
        res = self.uart.read(expected)
        self.print_debug("get_packet received data:", res, data_type="hex")
        if (not res) or (len(res) != expected):
            raise RuntimeError("Failed to read data from sensor")

        start = (res[0] << 8) + res[1]
        if start != STARTCODE:
            raise RuntimeError("Incorrect packet data")
        addr = list(i for i in res[2:6])
        if addr != self.address:
            raise RuntimeError("Incorrect address")
        packet_type = res[6]
        length = (res[7] << 8) + res[8]
        if packet_type != ACKPACKET:
            raise RuntimeError("Incorrect packet data")

        reply = list(i for i in res[9:9 + (length - 2)])
        self.print_debug("get_packet reply:", reply, data_type="hex")
        return reply  # reply a list contain int

    def print_debug(self, info, data, data_type='str'):
        if not self.debug:
            return
        if data_type == "hex":
            print("*** DEBUG ==>", info, ["{:02x}".format(i) for i in data])
        elif data_type == "str":
            print("*** DEBUG ==>", info, data)


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # print(wlan.scan())
    if not wlan.isconnected():
        print('connecting to network...')
        # wlan.connect('Verizon_Q9J9MQ', 'baloon9-gnp-paw')
        wlan.connect('Columbia University', '')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan.ifconfig()


def add_fingerprint(store_location):
    global socket_sent
    # Adding Fingerprint
    start_time = time.time()
    while True:
        socket_sent = '[0] Getting First Image'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)
        print("-----Start Getting First Image-----")

        process_time = time.time() - start_time
        if process_time > 5:
            socket_sent = '[0] Time out'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            print("Time Out")
            time.sleep(2)
            socket_sent = '[1]'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            print("-----End-----")
            return 'time_out'
        ack_get_1 = fps.get_image()
        if ack_get_1 == OK:
            ack_i2t_1 = fps.image_2_tz(1)
            if ack_i2t_1 == OK:
                socket_sent = '[0] Get Image 1 Success'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
                print("-----Get Image 1 Success-----")
                time.sleep(1)
                break
            else:
                socket_sent = '[0] Img2Tz Wrong, try again'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
                print("Img2Tz Wrong")
                while True:
                    if fps.get_image() != NOFINGER:
                        continue
                    else:
                        break
                continue
        elif ack_get_1 == NOFINGER:
            continue
        else:
            socket_sent = '[0] Get Image wrong, release and try again'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            print("Get Image wrong")
            while True:
                if fps.get_image() != NOFINGER:
                    continue
                else:
                    break
            continue

    # Detect release
    while True:
        socket_sent = '[0] Release your finger'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)
        if fps.get_image() == 0x02:
            break
        else:
            continue

    start_time = time.time()
    while True:
        socket_sent = '[0] Getting Second Image'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)
        print("\n-----Start Getting Second Image-----")

        process_time = time.time() - start_time
        if process_time > 5:
            socket_sent = '[0] Time out'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            print("Time Out")
            time.sleep(2)
            socket_sent = '[1]'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            print("-----End-----")
            return 'time_out'

        ack_get_2 = fps.get_image()
        if ack_get_2 == OK:
            ack_i2t_2 = fps.image_2_tz(2)
            if ack_i2t_2 == OK:
                socket_sent = '[0] Get Image 2 Success'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
                print("-----Get Image 2 Success-----")
                time.sleep(1)
                break
            else:
                socket_sent = '[0] Img2Tz Wrong, release and try again'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
                print("Img2Tz Wrong")
                while True:
                    if fps.get_image() != NOFINGER:
                        continue
                    else:
                        break
                continue
        elif ack_get_2 == NOFINGER:
            continue
        else:
            socket_sent = '[0] Get Image wrong, release and try again'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            print("Get Image wrong")
            while True:
                if fps.get_image() != NOFINGER:
                    continue
                else:
                    break
            continue

    print("\n------CP1-----\n")

    ack_reg = fps.create_model()
    if ack_reg != OK:
        socket_sent = '[0] RegModel Wrong'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)
        time.sleep(1)
        print("RegModel Wrong")
        return 'reg_wrong'

    ack_store = fps.store_model(location=store_location)
    if ack_store != OK:
        socket_sent = '[0] Store Wrong'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)
        time.sleep(1)
        print("Store Wrong")
        return 'store_wrong'

    socket_sent = '[0] Successful Add Fingerprint'
    DataSocket.send(socket_sent.encode())
    DataSocket.recv(512)
    print("Successful add model at %s" % store_location)
    time.sleep(1)
    DataSocket.send('[1]'.encode())
    DataSocket.recv(512)
    return 'success'


def open_door1():
    print('open Door 1')
    DataSocket.send('[0] Main Door Unlock')
    lock_1p_pin.value(0)
    lock_1n_pin.value(1)
    DataSocket.recv(512)
    time.sleep(25)
    DataSocket.send('[0] Main Door Locking')
    lock_1p_pin.value(1)
    lock_1n_pin.value(0)
    DataSocket.recv(512)
    time.sleep(15)
    DataSocket.send('[1]')
    lock_1p_pin.value(0)
    lock_1n_pin.value(0)
    DataSocket.recv(512)


def open_door2():
    print('open Door 2')
    DataSocket.send('[0] Delivery Door Unlock')
    lock_2p_pin.value(0)
    lock_2n_pin.value(1)
    DataSocket.recv(512)
    time.sleep(25)
    DataSocket.send('[0] Delivery Door Locking')
    lock_2p_pin.value(1)
    lock_2n_pin.value(0)
    DataSocket.recv(512)
    time.sleep(15)
    DataSocket.send('[1]')
    lock_2p_pin.value(0)
    lock_2n_pin.value(0)
    DataSocket.recv(512)


def open_both():
    print('open both')


mode_pin = Pin(13, Pin.IN, Pin.PULL_UP)
if mode_pin.value() == 0:
    print('-----Exit Program-----')
    sys.exit()

lock_1p_pin = Pin(14, Pin.OUT, drive=Pin.DRIVE_3)
lock_1n_pin = Pin(12, Pin.OUT, drive=Pin.DRIVE_3)
lock_1p_pin.value(1)
lock_1n_pin.value(0)

lock_2p_pin = Pin(33, Pin.OUT, drive=Pin.DRIVE_3)
lock_2n_pin = Pin(32, Pin.OUT, drive=Pin.DRIVE_3)
lock_2p_pin.value(1)
lock_2n_pin.value(0)

socket_recv = None
socket_sent = '[1]'
mode = 'normal'
url = "http://34.173.109.117:5000"
code_count = 0

ip_addr = do_connect()

lock_1p_pin.value(0)
lock_1n_pin.value(0)
lock_2p_pin.value(0)
lock_2n_pin.value(0)

fps = FingerPrintSensor()
print("-----System Parameters-----")
print("Status_register: ", ["{:02x}".format(i) for i in fps.status_register])
print("System_id: ", ["{:02x}".format(i) for i in fps.system_id])
print("Library_size: ", ["{:02x}".format(i) for i in fps.library_size])
print("Security_level: ", ["{:02x}".format(i) for i in fps.security_level])
print("Device_address: ", ["{:02x}".format(i) for i in fps.device_address])
print("Data_packet_size: ", ["{:02x}".format(i) for i in fps.data_packet_size])
print("Baudrate: ", ["{:02x}".format(i) for i in fps.baudrate])
print("-----End-----\n")


sockaddr = socket.getaddrinfo(ip_addr[0], 50000)[0][-1]
print('Socket Address: ', sockaddr)
ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ListenSocket.bind(sockaddr)
ListenSocket.listen(1)
print(f'Enable server, Listen on 50000')
DataSocket, addr = ListenSocket.accept()
print('Accept a client', addr)

while True:
    time.sleep(0.2)
    DataSocket.send('[1]'.encode())
    socket_recv = DataSocket.recv(512).decode()
    print(socket_recv)

    code_input = None
    mode = None
    if socket_recv == 'ack':
        mode = 'fingerprint'
    elif int(socket_recv[1]) == 1:
        mode = 'code'
        code_input = int(socket_recv[-4:])
    elif int(socket_recv[1]) == 2:
        mode = 'add_fingerprint'
        code_input = int(socket_recv[-4:])
    else:
        mode = 'fingerprint'
    socket_recv = None
    print(mode)

    if mode == 'fingerprint':
        finger_detect = fps.get_image()
        if finger_detect == NOFINGER:
            continue
        elif finger_detect == OK:
            finger2tz = fps.image_2_tz(1)
            if finger2tz == OK:
                finger_search = fps.finger_search()
                if finger_search == OK:
                    socket_sent = '[0] Checking Fingerprint'
                    DataSocket.send(socket_sent.encode())
                    DataSocket.recv(512)
                    formdata = {
                        'mode': 'fingerprint',
                        'code': None,
                        'fingerprint': str((fps.finger_id[0] << 8) + fps.finger_id[1])
                    }
                    print(formdata)
                    response = requests.post(url, json=formdata).json()
                    print(response)

                    if response['approve']:
                        code_count = 0
                        socket_sent = '[0] Welcome %s, Choose Door' % response['name']
                        DataSocket.send(socket_sent.encode())
                        DataSocket.recv(512)
                        time.sleep(2)
                        while True:
                            DataSocket.send('[1]'.encode())
                            socket_recv = DataSocket.recv(512).decode()
                            print(socket_recv)
                            if '[1] 1' in socket_recv:
                                open_door1()
                                break
                            elif '[1] 2' in socket_recv:
                                open_door2()
                                break
                            else:
                                time.sleep(1)
                                continue
                        socket_recv = None
                        socket_sent = '[1]'
                        DataSocket.send(socket_sent.encode())
                    else:
                        socket_sent = '[0] Unauthorized'
                        DataSocket.send(socket_sent.encode())
                        DataSocket.recv(512)
                        time.sleep(2)
                        socket_sent = '[1]'
                        DataSocket.send(socket_sent.encode())
                        DataSocket.recv(512)
                        continue

                elif finger_search == 0x09:
                    socket_sent = '[0] Invalid fingerprint'
                    DataSocket.send(socket_sent.encode())
                    DataSocket.recv(512)
                    time.sleep(2)
                    socket_sent = '[1]'
                    DataSocket.send(socket_sent.encode())
                    DataSocket.recv(512)
                    continue
                else:
                    continue
            else:
                continue
        else:
            continue

    elif mode == 'code':
        socket_sent = '[0] Checking Code'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)

        formdata = {
            'mode': 'code',
            'code': str(code_input),
            'fingerprint': None
        }
        print(formdata)
        response = requests.post(url, json=formdata).json()
        print(response)

        if response['approve'] and response['name'] != 'delivery':
            code_count = 0
            socket_sent = '[0] Welcome %s, Choose Door' % response['name']
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            time.sleep(2)
            while True:
                DataSocket.send('[1]'.encode())
                socket_recv = DataSocket.recv(512).decode()
                print(socket_recv)
                if '[1] 1' in socket_recv:
                    open_door1()
                    break
                elif '[1] 2' in socket_recv:
                    open_door2()
                    break
                else:
                    time.sleep(1)
                    continue
            socket_recv = None
            socket_sent = '[1]'
            DataSocket.send(socket_sent.encode())

        elif response['approve'] and response['name'] == 'delivery':
            code_count = 0
            socket_sent = '[0] Please place package in the opening door'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            open_door2()
            time.sleep(2)
            socket_sent = '[1]'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)

        else:
            if code_count < 3:
                code_count += 1
                socket_sent = '[0] Wrong Code'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
                time.sleep(2)
                socket_sent = '[1]'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
            else:
                socket_sent = '[0] Wrong Code more than 3 times, sending report to owner'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)
                postmsg = 'Someone try to open your lock with wrong code more than 3 times'
                requests.post("http://ntfy.sh/iot_2023fall_g5", data=postmsg.encode())
                code_count = 0
                time.sleep(5)
                socket_sent = '[1]'
                DataSocket.send(socket_sent.encode())
                DataSocket.recv(512)

    elif mode == 'add_fingerprint':
        socket_sent = '[0] Checking Code'
        DataSocket.send(socket_sent.encode())
        DataSocket.recv(512)

        formdata = {
            'mode': 'add',
            'code': str(code_input),
            'fingerprint_data': None
        }
        print(formdata)
        response = requests.post(url, json=formdata).json()
        print(response)
        if response['registration']:
            while True:
                result = add_fingerprint(response['serial'])
                if result == 'time_out':
                    break
                elif result == 'success':
                    break
                else:
                    continue
        else:
            socket_sent = '[0] Invalid passcode'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
            time.sleep(2)
            socket_sent = '[1]'
            DataSocket.send(socket_sent.encode())
            DataSocket.recv(512)
