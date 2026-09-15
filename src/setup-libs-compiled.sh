#!/bin/bash

pip3 install mpy-cross --break-system-packages
mpy-cross uftpd.py
mpy-cross epaper4in2.py
ampy -p /dev/ttyACM0 put uftpd.mpy
ampy -p /dev/ttyACM0 put epaper4in2.mpy
ampy -p /dev/ttyACM0 put microfont.py # can't be compiled, probably because of using viper
rm uftpd.mpy
rm epaper4in2.mpy