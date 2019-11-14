#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import can
import cantools
import secrets
import numpy as np
import random
import time

def send_message(name, data, bus):

        db = cantools.database.load_file('../src/workshop.dbc')
        try:
            m = list(filter(lambda x:x.name == name, db.messages))[0]
        except:
            print("Message name {} not found in the loaded dbc. No Message sent.".format(name))
            return

        try:
            data = m.encode(data)
        except:
            print("Error encoding data {}.\nValid signals are {}\nNo message sent".format(data, m.signals))
            return
        byte_arr = list(data)
        for sig in m.signals:
            for x in range(sig.offset+sig.length,len(byte_arr)):
                byte_arr[x] = int.from_bytes(secrets.token_bytes(1), byteorder="little")
        data = list(byte_arr)
        bus.send(can.Message(arbitration_id=m.frame_id, data=data, is_extended_id=False))


if __name__ == '__main__':
    bus = can.interface.Bus(bustype='socketcan', channel='vcan1', bitrate=250000)
    while True:
        send_message('PhysSensors', {'Service_Light':0,'RPM':6, 'Vehicle_Speed':120},bus)
        time.sleep(0.1)