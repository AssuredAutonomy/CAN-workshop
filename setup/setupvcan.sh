#!/bin/sh

sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
pip3 install Pillow cantools numpy pygame matplotlib
