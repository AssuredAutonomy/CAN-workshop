#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import can
import numpy as np


bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=250000)
bus.set_filters([{"can_id": 0x111, "can_mask": 0x7FF, "extended": False}])

recorder = can.BufferedReader()
notifier = can.Notifier(bus,[recorder])

#Queue to store data
data = np.array([])
data_point = 0
max_data_points = 1000

#for plotting
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)

#empty queues
x = []
y = []


def animate(i,x,y):
    recv_msg=recorder.get_message()

    if recv_msg != None:

        #read messages
        speed = recv_msg.data[1]*256+recv_msg.data[2]
        speed = float(speed)/256

        #drop older frames to make room for new ones
        if len(x) > 1000:
            x.pop(0)
            y.pop(0)

        #add data to Queue
        global data_point
        current_point = data_point
        x.append(current_point)
        y.append(speed)
        data_point = data_point +1

    print(y)
    ax1.clear()
    ax1.plot(x,y)

    plt.xlabel('Sample')
    plt.ylabel('Speed [km/hr]')
    plt.grid(True)
    plt.xticks(rotation=45, ha='right')

#animated plot
ani = animation.FuncAnimation(fig, animate, fargs=(x, y), interval=1)
plt.show()
