
#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import can
import cantools
import secrets
import numpy as np
import random
import time


def send_one():

    bus = can.interface.Bus(bustype='socketcan', channel='vcan1', bitrate=250000)
    msg = can.Message(arbitration_id=0x111,
                      data=[0x33, 0x6C, 0x14, 0x7B, 0x82, 0x7F, 0xFF, 0xFF],
                      is_extended_id=False)

    #some data in the packet
    speed = 140*256
    hex_num = hex(speed)
    hex_num = hex_num[2:6]
    byte_2 = hex_num[0:2]
    byte_3 = hex_num[2:4]

    #put data into the message
    msg.data[1] = int(byte_2,16)
    msg.data[2] = int(byte_3,16)

    while True:

        #attempt to send the message
        try:
            bus.send(msg)
            print("Message sent on {}".format(bus.channel_info))
        except can.CanError:
            print("Message NOT sent")

        #change how fast messages are sent
        time.sleep(0.01)


if __name__ == '__main__':
    send_one()