#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import can
import cantools
import secrets
import numpy as np
import random
import time


if __name__ == '__main__':
    bus = can.interface.Bus(bustype='socketcan', channel='vcan1', bitrate=250000)
    db = cantools.database.load_file('../src/workshop.dbc')
    while True:
        message=bus.recv()
        try:
            m = db.decode_message(message.arbitration_id, message.data)
            for key in m:
                if key == 'Vehicle_Speed':
                    print(m[key])
        except:
            pass
