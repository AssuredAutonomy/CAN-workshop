#!/usr/bin/env python
import os, sys
import json
import can
import cantools
import argparse
import signal
import math
import subprocess
from time import sleep
from threading import Thread, Event
from can.interface import Bus
from pynput.keyboard import Key, Listener
from graphics import Gui

class Control():
    def __init__(self, source, bus):
        self.db = cantools.database.load_file(source)
        self.bus = bus
        self.acceleration = 0
        self.speed = 0
        self.rpm = 0
        self.dt = .12
        self.steering_angle = 0
        self.isSteering = 0
        self.isDriving = 0
        self.isStopped = 1
        self.turnSig_state = 0

    def update(self):

        if self.isDriving == 0:
            self.speed -= .5
        #self.speed += self.acceleration * self.dt
        if self.speed < 0:
            self.speed = 0
        elif self.speed > 220:
            self.speed = 220
        self.get_rpm()

        if self.isSteering == 0:
            if self.steering_angle <= -30:
                self.steering_angle += 30
            elif self.steering_angle >= 30:
                self.steering_angle -= 30
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

        self.bus.send(can.Message(arbitration_id=m.frame_id, data=data))

    def phys(self):
        self.send_message('PhysSensors', {'Service_Light':0,'RPM':self.rpm, 'Vehicle_Speed':self.speed})

    def accelerate(self):
        self.speed += 1.5
        self.send_message('AcceleratorBrake', {'Accelerator':1,'Brake':0})

    def brake(self):
        self.speed -= 1.2
        self.send_message('AcceleratorBrake', {'Accelerator':0,'Brake':1})

    def steer_L(self):
        self.steering_angle -= 7
        self.send_message('Steering', {'Steer_L':1,'Steer_R':0})

    def steer_R(self):
        self.steering_angle += 7
        self.send_message('Steering', {'Steer_L':0,'Steer_R':1})

    def turn_L(self):
        self.turnSig_state = 1
        self.send_message('TurnSignals', {'Turn_Sig_L': 1, 'Turn_Sig_R': 0})

    def turn_R(self):
        self.turnSig_state = 2
        self.send_message('TurnSignals', {'Turn_Sig_L': 0, 'Turn_Sig_R': 1})



class MainLoop():
    def __init__(self, controller):
        self.controller = controller
        self.releaseEvent = Event()
        self.c_thread = ControlThread(self.controller)
        self.t_thread = TimerThread(self.controller, self.releaseEvent)
        self.g_thread = GraphicsThread(self.controller)
        self.q_state = 0
        self.e_state = 0

    def on_press(self, key):
        if hasattr(key, 'char'):
            #if key.char=='q':
                #self.controller.turn()
            if key.char=='w':
                self.t_thread.pressed.add('w')
                self.controller.isDriving = 1
            if key.char=='s':
                self.t_thread.pressed.add('s')
                self.controller.isDriving = 1
            if key.char=='a':
                self.t_thread.pressed.add('a')
                self.controller.isSteering = 1
            if key.char=='d':
                self.t_thread.pressed.add('d')
                self.controller.isSteering = 1
            if key.char=='q':
                self.t_thread.pressed.add('q')
            if key.char=='e':
                self.t_thread.pressed.add('e')
        self.releaseEvent.set()

    def on_release(self, key):
        #self.releaseEvent.clear()
        if hasattr(key, 'char'):
            if key.char=='w':
                self.t_thread.pressed.remove('w')
                self.controller.isDriving = 0
            elif key.char=='s':
                self.t_thread.pressed.remove('s')
                self.controller.isDriving = 0
            elif key.char=='a':
                self.t_thread.pressed.remove('a')
                self.controller.isSteering = 0
            elif key.char=='d':
                self.t_thread.pressed.remove('d')
                self.controller.isSteering = 0
            elif key.char=='q':
                if self.q_state==0:
                    self.q_state = 1
                    if self.e_state == 1:
                        self.e_state = 0
                        self.t_thread.pressed.remove('e')
                        self.controller.turnSig_state = 1
                else:
                    self.t_thread.pressed.remove('q')
                    self.q_state = 0
                    self.controller.turnSig_state = 0
            elif key.char=='e':
                if self.e_state==0:
                    self.e_state = 1
                    if self.q_state == 1:
                        self.q_state = 0
                        self.t_thread.pressed.remove('q')
                        self.controller.turnSig_state = 2
                else:
                    self.t_thread.pressed.remove('e')
                    self.e_state = 0
                    self.controller.turnSig_state = 0
        if key == Key.esc:
            # Stop listener
            return False
        self.controller.update()

    def mainLoop(self):
        # Collect events until released
        os.system("stty -echo")
        print("\nControls: W (accelerate), S (brake), A (steer left), D (steer right), Q (left turn signal), "
              "E (right turn signal)\n")
        self.c_thread.start()
        self.t_thread.start()
        self.g_thread.start()
        with Listener(on_press=self.on_press,on_release=self.on_release) as listener:
            listener.join()
        self.thread.join()

class TimerThread(Thread):
    def __init__(self, controller, event):
        super().__init__()
        self.released = event
        self.controller = controller
        self.pressed = set()

    def run(self):
        while True:
            if self.released.wait():
                if 'w' in self.pressed and 's' not in self.pressed:
                    self.controller.accelerate()
                elif 's' in self.pressed:
                    self.controller.brake()
                if 'a' in self.pressed and 'd' not in self.pressed:
                    self.controller.steer_L()
                elif 'd' in self.pressed:
                    self.controller.steer_R()
                if 'q' in self.pressed and 'd' not in self.pressed:
                    self.controller.turn_L()
                elif 'e' in self.pressed:
                    self.controller.turn_R()

                sleep(.05)              

class ControlThread(Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        while True:
            self.controller.update()
            sleep(.3)

class GraphicsThread(Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.gui = Gui()

    def run(self):
        while True:
            self.updateGui()

    def updateGui(self):
        if self.controller.speed >= 1:
            self.gui.rotate_speed_needle(self.controller.speed)
        self.gui.rotate_tac_needle(self.controller.rpm * (220/8))
        self.gui.rotate_steering_wheel(self.controller.steering_angle)
        self.gui.turnSig_state(self.controller.turnSig_state)
        self.gui.refresh_gui()

    

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
    bus = can.interface.Bus(args.socket, bustype=bustype)
    controller = Control(args.dbc, bus)
    if args.random:
        subprocess.Popen(["cangen", "vcan0"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    m = MainLoop(controller)
    m.mainLoop()


