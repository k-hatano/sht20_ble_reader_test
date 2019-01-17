import logging
import time
import uuid

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import DeviceInformation

SERVICE_UUID = uuid.UUID('0000AA20-0000-1000-8000-00805F9B34FB')
CHAR_UUID    = uuid.UUID('0000AA21-0000-1000-8000-00805F9B34FB')

ble = Adafruit_BluefruitLE.get_provider()

def main():
    global chara, interrupted
    ble.clear_cached_data()

    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('using adapter: {0}'.format(adapter.name))

    print('searching for device...')
    device_found = False
    device = None

    try:
        adapter.start_scan()
        
        while device_found == False :
            found_now = ble.find_device(service_uuids=[SERVICE_UUID])
            if found_now is not None:
                device = found_now
                printDeviceInfo(device)
                device_found = True
            else:
                print('device not found...')
                device_found = True

            time.sleep(1)

    except KeyboardInterrupt:
        print('stopping searching...')      

    finally:
        adapter.stop_scan()

    if device is None:
        return

    print('connecting to device...')
    device.connect()

    try:
        print('discovering services...')
        device.discover([SERVICE_UUID], [CHAR_UUID])

        service = device.find_service(SERVICE_UUID)
        chara = service.find_characteristic(CHAR_UUID)

        print('Listening to characteristic changes...')
        print('(Press Ctrl + C to exit)')
        chara.start_notify(received)

        interrupted = False
        for i in range(30):
            if interrupted == True:
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print('disconnecting device, please wait...')
        device.disconnect()
    
    finally:
        print('disconnecting device...')
        device.disconnect()


def printDeviceInfo(device):
    print(device)
    print(device.id)
    if device.name is not None:
        print(device.name.encode('utf-8'))
    else:
        print(device.name)

def received(data):
    global chara, interrupted
    print(data)
    srh = ord(data[0]) * 0x100 + ord(data[1])
    st = ord(data[2]) * 0x100 + ord(data[3])
    rh = -6.0 + 125.0 * (srh / 65536.0)
    t = -46.85 + 175.72 * (st / 65536.0)
    print('humidity : ' + str(rh) + ' %')
    print('temperature : ' + str(t) + ' deg C')
    chara.stop_notify()
    interrupted = True


ble.initialize()

ble.run_mainloop_with(main)


