#!/usr/bin/env python
import os, sys
import json
import pygame
from pygame.locals import K_w
from pygame.locals import K_s
from pygame.locals import K_a
from pygame.locals import K_d
from pygame.locals import K_q
from pygame.locals import K_e
import can
import cantools
import argparse
import signal
import math
import subprocess
import secrets
from time import sleep
from threading import Thread, Event
from can.interface import Bus
from graphics2 import Gui

'''
    pressing a button will send a message on the bus, the reader thread will read the message and send it to the controller decoder, the controller will respond to the message

'''
class Control():
    def __init__(self, source, bus):
        self.db = cantools.database.load_file(source)
        self.running = True
        self.bus = bus
        self.acceleration = 0
        self.speed = 0
        self.rpm = 0
        self.ipc_speed = 0
        self.ipc_rpm = 0
        self.dt = .12
        self.steering_angle = 0
        self.isSteering = 0
        self.isDriving = 0
        self.isStopped = 1
        self.turnSig_state = 0

    def decodeMessage(self, message):

        try:
            m = self.db.decode_message(message.arbitration_id, message.data)
            for key in m:
                if key == 'Vehicle_Speed':
                    self.ipc_speed = m[key]
                elif key == 'RPM':
                    self.ipc_rpm = m[key]
        except:
            pass

        if message.arbitration_id == 0x112:
            if message.data[0] & 0x3 == 0x1:
                self.accelerate()
            elif message.data[0] & 0x3 == 0x2:
                self.brake()
        elif message.arbitration_id == 0x113:
            if message.data[0] & 0x3 == 0x1:
                self.steer_L()
            elif message.data[0] & 0x3 == 0x2:
                self.steer_R()
        elif message.arbitration_id == 0x115:
            if message.data[0] & 0x3 == 0x1:
                self.turn_L()
            elif message.data[0] & 0x3 == 0x2:
                self.turn_R()

    def update(self):

        if self.isDriving == 0:
            self.speed -= 1
        #self.speed += self.acceleration * self.dt
        if self.speed < 0:
            self.speed = 0
        elif self.speed > 220:
            self.speed = 220
        self.get_rpm()

        if self.isSteering == 0:
            if -180 <= self.steering_angle <= -30:
                self.steering_angle += 30
            elif 180 >= self.steering_angle >= 30:
                self.steering_angle -= 30
            elif self.steering_angle <= -180:
                self.steering_angle += 60
            elif self.steering_angle >= 180:
                self.steering_angle -= 60
            elif -5 >= self.steering_angle > -30:
                self.steering_angle += 5
            elif 30 > self.steering_angle >= 5:
                self.steering_angle -= 5
            elif 5 >= self.steering_angle >= -5:
                self.steering_angle = 0

        self.phys()
        sys.stdout.write("\rspeed: {} rpm: {} Steer Angle: {} TurnSig: {}".format(self.speed, self.rpm, self.steering_angle, self.turnSig_state))
        sys.stdout.flush()

    def get_rpm(self):
        # We'll say our tires are .05 meters
        circ = math.pi * .5

        # speed is in km/h
        s = self.speed*1000/60
        #print("s {}, c {}".format(s, circ))
        # s is m/minute
        # rpm is meters/minute divided by circumference per 1000
        self.rpm = (s/circ)/1000

    # Loops over messages imported from dbc and tries to find one with name
    # data should be a dictionary encoding values for signals in the message
    def send_message(self, name, data):

        try:
            m = list(filter(lambda x:x.name == name, self.db.messages))[0]
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
        self.bus.send(can.Message(arbitration_id=m.frame_id, data=data, is_extended_id=False))

    def phys(self):
        self.send_message('PhysSensors', {'Service_Light':0,'RPM':int(self.rpm*10), 'Vehicle_Speed':self.speed})

    def accelerate(self):
        self.speed += 1.5

    def brake(self):
        self.speed -= 1.2

    def steer_L(self):
        self.steering_angle -= 7

    def steer_R(self):
        self.steering_angle += 7

    def turn_L(self):
        self.turnSig_state = 1

    def turn_R(self):
        self.turnSig_state = 2

class MainLoop():
    def __init__(self, controller, network):
        self.controller = controller
        self.releaseEvent = Event()
        self.c_thread = ControlThread(self.controller)
        self.t_thread = TimerThread(self.controller, self.releaseEvent)
        self.g_thread = GraphicsThread(self.controller)
        self.r_thread = ReadThread(self.controller,network)
        self.q_state = 0
        self.e_state = 0

    def parse_events(self):
        for event in pygame.event.get():
            if event.type ==pygame.QUIT:
                pass

            elif event.type == pygame.KEYDOWN:
                if event.key == K_w:
                    if self.controller.isDriving == 0:
                        self.t_thread.pressed.add('w')
                        self.controller.isDriving = 1
                    else:
                        self.t_thread.pressed.remove('w')
                        self.controller.isDriving = 0

                elif event.key == K_s:
                    pass

                elif event.key == K_a:
                    if self.controller.isSteering == 0:
                        self.t_thread.pressed.add('a')
                        self.controller.isSteering = 1
                    else:
                        if 'd' in self.t_thread.pressed:
                            self.t_thread.pressed.remove('d')
                            self.t_thread.pressed.add('a')
                        else:
                            self.t_thread.pressed.remove('a')
                            self.controller.isSteering = 0
                elif event.key == K_d:
                    if self.controller.isSteering == 0:
                        self.t_thread.pressed.add('d')
                        self.controller.isSteering = 1
                    else:
                        if 'a' in self.t_thread.pressed:
                            self.t_thread.pressed.remove('a')
                            self.t_thread.pressed.add('d')
                        else:
                            self.t_thread.pressed.remove('d')
                            self.controller.isSteering = 0

                elif event.key == K_q:
                    #self.t_thread.pressed.add('q')
                    if self.controller.turnSig_state == 1:
                        self.g_thread.gui.turnSig_state(0)
                        self.controller.turnSig_state = 0
                    elif self.controller.turnSig_state == 0:
                        self.g_thread.gui.turnSig_state(1)
                        self.controller.turnSig_state = 1
                    else:
                        self.g_thread.gui.turnSig_state(1)
                        self.controller.turnSig_state = 1
                elif event.key == K_e:
                    #self.t_thread.pressed.add('e')
                    if self.controller.turnSig_state == 1:
                        self.g_thread.gui.turnSig_state(2)
                        self.controller.turnSig_state = 2
                    elif self.controller.turnSig_state == 0:
                        self.g_thread.gui.turnSig_state(2)
                        self.controller.turnSig_state = 2
                    else:
                        self.g_thread.gui.turnSig_state(0)
                        self.controller.turnSig_state = 0
                self.releaseEvent.set()

            elif event.type == pygame.KEYUP:
                if event.key == K_w:
                    pass

                elif event.key == K_s:
                    pass

                elif event.key == K_a:
                    pass
                    #self.t_thread.pressed.remove('a')
                    #self.controller.isSteering = 0

                elif event.key == K_d:
                    pass
                    #self.t_thread.pressed.remove('d')
                    #self.controller.isSteering = 0

                elif event.key == K_q:
                    pass
                elif event.key == K_e:
                    pass

    def mainLoop(self):
        # Collect events until released
        os.system("stty -echo")
        print("\nControls: W (accelerate), S (brake), A (steer left), D (steer right), Q (left turn signal), "
              "E (right turn signal)\n")
        self.c_thread.start()
        self.t_thread.start()
        self.g_thread.start()
        self.r_thread.start()

        while True:
             self.parse_events()

class TimerThread(Thread):
    def __init__(self, controller, event):
        super().__init__()
        self.released = event
        self.controller = controller
        self.pressed = set()

    def run(self):
        while self.controller.running:
            if self.released.wait():
                if 'w' in self.pressed and 's' not in self.pressed:
                    self.controller.send_message('AcceleratorBrake', {'Accelerator':1,'Brake':0})
                elif 's' in self.pressed:
                    self.controller.send_message('AcceleratorBrake', {'Accelerator':0,'Brake':1})
                if 'a' in self.pressed and 'd' not in self.pressed:
                    self.controller.send_message('Steering', {'Steer_L':1,'Steer_R':0})
                elif 'd' in self.pressed:
                    self.controller.send_message('Steering', {'Steer_L':0,'Steer_R':1})
                if 'q' in self.pressed and 'd' not in self.pressed:
                    self.controller.send_message('TurnSignals', {'Turn_Sig_L': 1, 'Turn_Sig_R': 0})
                elif 'e' in self.pressed:
                    self.controller.send_message('TurnSignals', {'Turn_Sig_L': 0, 'Turn_Sig_R': 1})
                sleep(0.1)

class ControlThread(Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        while self.controller.running:
            self.controller.update()
            sleep(.1)

class GraphicsThread(Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.gui = Gui()

    def run(self):
        while self.controller.running:
            self.updateGui()

    def updateGui(self):
        if self.controller.speed >= 1:
            self.gui.rotate_speed_needle(self.controller.ipc_speed)
        self.gui.rotate_tac_needle((self.controller.ipc_rpm/10) * (220/8))
        self.gui.rotate_steering_wheel(self.controller.steering_angle)
        self.gui.turnSig_state(self.controller.turnSig_state)
        #self.gui.refresh_gui()
        self.gui.on_execute()

class ReadThread(Thread):
    def __init__(self, controller,network):
        super().__init__()
        self.controller = controller
        #filters = [{"can_id": 0x118, "can_mask": 0xFF8, "extended": False}]
        self.bus = can.interface.Bus(network, bustype='socketcan')

    def run(self):
        while controller.running:
            for msg in self.bus:
                self.controller.decodeMessage(msg)


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("File does not exist {}".format(arg))
    else:
        return arg

def getArgs():
    parser = argparse.ArgumentParser(description="Script to write CAN messages to given virtual CAN socket.")
    parser.add_argument("-s", "--socket", metavar="SOCKET", help="Name of virtual CAN socket, e.g. vcan0.", default='vcan0')
    parser.add_argument("dbc",metavar="DBC_FILE", help="dbc file to import messages from.",type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-r", "--random", help="run cangen while this script is running", action='store_true')

    args = parser.parse_args()

    return args

def signal_handler(sig, frame):
    os.system('stty echo')
    sys.exit(0)

if __name__ =="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    args = getArgs()
    bustype = 'socketcan'
    #filters = [{"can_id": 0x118, "can_mask": 0xFF8, "extended": False}]
    bus = can.ThreadSafeBus(args.socket, bustype=bustype)
    controller = Control(args.dbc, bus)
    if not args.random:
        subprocess.Popen(["cangen", args.socket,"-L","8","-g","50"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    m = MainLoop(controller,args.socket)
    m.mainLoop()


