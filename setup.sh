#!/bin/sh

if [ $# -eq 1 ]; then
    end=$1
else
    end=1
fi

sudo modprobe vcan
interface_num=0
while [ $interface_num -lt $end ]; do
    echo "Creating vcan$interface_num"
    sudo ip link add dev "vcan$interface_num" type vcan
    sudo ip link set up "vcan$interface_num"
    interface_num=$((interface_num+1))
done

pip3 install Pillow cantools numpy pygame matplotlib
