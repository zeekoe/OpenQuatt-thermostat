#!/bin/bash

pip3 install mpy-cross --break-system-packages
mpy-cross uftpd.py
mpy-cross epaper4in2.py
ampy -p /dev/ttyACM0 put uftpd.mpy
ampy -p /dev/ttyACM0 put epaper4in2.mpy
rm uftpd.mpy
rm epaper4in2.mpy