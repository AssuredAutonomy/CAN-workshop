# CAN-workshop
This project was developed to run Controller Area Network (CAN) bus introduction workshops at The Ohio State University. When run, it displays an Instrument Panel Cluster (IPC) which is backed by a virtual CAN interface (vcan). Users can interact with the IPC by using the keyboard to accelerate, brake, turn, and enable blinkers. The program's internal state both produces and is updated by messages on the vcan. Inspired by OpenGarage's [ICSim](https://github.com/zombieCraig/ICSim).

TODO: image

## Background

TODO: powerpoint? links? or in readme?

## Dependencies
The python dependencies for this program are `cantools`, `pygame`, `Pillow`, `matplotlib`, and `numpy`, which will be taken care of during the [Setup](#setup) stage. For system-level dependencies, `pygame` is built on top of `SDL` (NOT SDL2!) so make sure to install the appropriate packages for your operating system according to `pygame`'s guidelines. Additionally, this program requires `socketcan` to provide support for virtual CAN interfaces to your operating system.

## Setup
To set up the vcan and install the appropriate python packages, run `setup.sh` located in the main directory. If no arguments are specified, one vcan will be created (`vcan0`) for your own use. If a numerical argument is specified, the appropriate number of vcans will be created (e.g. entering `19` produces `vcan0, vcan1, ... vcan17, vcan18`). This is useful for setting up a workshop in the case that many students will be working on the same VM. An administrator with `sudo` access can create enough vcans to have 1 per student so that students can experiment with CAN messages without interfering with other students' IPCs and so students do not require `sudo` access.

## Running

TODO: fill out

## Troubleshooting
If you see the following output when trying to run this script, you need to install packages for your operating system for `pygame`'s dependencies, NOT python packages.
```
Hunting dependencies...
    SDL     : found 1.2.15
    FONT    : not found
    IMAGE   : found
    MIXER   : not found
    PNG     : found
    JPEG    : found
    SCRAP   : found
    PORTMIDI: found
    PORTTIME: found
    FREETYPE: found 23.1.17
    Missing dependencies
```

If you see the following output, you are missing python dependencies. See [Setup](#setup).
```
python writeCan.py 
Traceback (most recent call last):
  File "writeCan.py", line 4, in <module>
    import pygame
ModuleNotFoundError: No module named 'pygame'
```