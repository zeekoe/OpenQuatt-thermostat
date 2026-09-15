#!/bin/bash

echo "Copying files. This takes longer than you'd think :)"
echo "Make sure you either run setup-libs-compiled.sh (faster at execution, but installs mpy-cross) or setup-libs-uncompiled.sh (no additional dependencies, but slower at execution)"
ampy -p /dev/ttyACM0 put config.py
echo ".."
ampy -p /dev/ttyACM0 put webrepl_cfg.py
echo ".."
ampy -p /dev/ttyACM0 put boot.py
echo ".."
ampy -p /dev/ttyACM0 put main.py
echo ".."
ampy -p /dev/ttyACM0 put epaper4in2.py
echo ".."
ampy -p /dev/ttyACM0 put image_light.py
echo ".."
ampy -p /dev/ttyACM0 put image_dark.py
echo ".."
ampy -p /dev/ttyACM0 reset
