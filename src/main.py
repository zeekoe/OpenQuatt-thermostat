"""
	Example for 4.2 inch black & white Waveshare E-ink screen
	Run on ESP32
"""

import machine
import epaper4in2
from machine import Pin, SPI
import framebuf
import struct

# HSPI (3) on ESP32 - but with SCK and MISO swapped?! (this is the E-Paper_ESP32_Driver_Board)
sck = Pin(13)
miso = Pin(12)
mosi = Pin(14)
dc = Pin(27)
cs = Pin(15)
rst = Pin(26)
busy = Pin(25)
spi = machine.SoftSPI(baudrate=2000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)

e = epaper4in2.EPD(spi, cs, dc, rst, busy)
e.init()

# Display dimensions
w = 400
h = 300

# --------------------

# Initialize frame buffer
black = 0
white = 1

def load_pbm_image(file_path):
    """Load a PBM (Portable Bitmap) image file"""
    with open(file_path, 'rb') as f:
        # Read header
        magic = f.readline().strip()
        if magic != b'P4':
            raise ValueError("Only P4 (binary PBM) format is supported")

        # Skip comments
        while True:
            line = f.readline()
            if not line.startswith(b'#'):
                break

        # Read dimensions
        width, height = map(int, line.split())
        if width != w or height != h:
            raise ValueError(f"Image dimensions {width}x{height} don't match display {w}x{h}")

        # Read image data
        return bytearray(f.read())

try:
    buf = load_pbm_image('background.pbm')
    fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
except Exception as e:
    print(f"Error loading image: {e}")
    buf = bytearray(w * h // 8)
    fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
    fb.fill(white)  # Fallback to white background


import sys

from fetch_openquatt_metrics import (
    FetchError,
    fetch_openquatt_metrics,
)

fields_to_fetch = (
    ("hp1OutsideTemp", "sensor", "HP1 - Outside temperature"),
    ("roomTemp", "sensor", "Room Temperature (Selected)"),
    ("supplyTemp", "sensor", "Water Supply Temp (Selected)"),
    ("totalHeat", "sensor", "Total Heat Power"),
    ("totalCoolingPower", "sensor", "Total Cooling Power"),
    ("totalCop", "sensor", "Total COP"),
    ("hp1Freq", "sensor", "HP1 - Compressor frequency"),
    ("hp1WaterIn", "sensor", "HP1 - Water in temperature"),
    ("hp1WaterOut", "sensor", "HP1 - Water out temperature"),
    ("hp1Power", "sensor", "HP1 - Power Input"),
    ("hp1EvaporatorCoilTemp", "sensor", "HP1 - Evaporator coil temperature"),
)

try:
    metrics = fetch_openquatt_metrics(
        url="http://openquatt.lan:80/openquatt/entities",
        display_fields=fields_to_fetch
    )
except FetchError as exc:
    print(str(exc), file=sys.stderr)

if not metrics["ok"]:
    print("Request failed: %s" % metrics["payload"], file=sys.stderr)

def get_value_by_key(key):
    for item in metrics["results"]:
        if item["key"] == key:
            return item["value"]
    return None  # Return None if key not found

import microfont
from microfont import MicroFont

font = MicroFont("dejavub12.mfnt",cache_index=True)


def print_text(text, x, y):
    font.write(text, fb, framebuf.MONO_HLSB, 400, 300, x, y, black, rot=0)


print_text(get_value_by_key("roomTemp"), 250, 140)
print_text(get_value_by_key("hp1Power"), 125, 77)
print_text(get_value_by_key("hp1Freq"), 77, 210)
print_text(get_value_by_key("hp1WaterIn"), 110, 200)
print_text(get_value_by_key("hp1WaterOut"), 105, 143)
print_text(get_value_by_key("supplyTemp"), 172, 140)
print_text(get_value_by_key("totalHeat"), 105, 160)
print_text(get_value_by_key("hp1OutsideTemp"), 84, 35)
print_text(get_value_by_key("hp1EvaporatorCoilTemp"), 23, 142)
e.display_frame(buf)

