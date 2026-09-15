"""
	Example for 4.2 inch black & white Waveshare E-ink screen
	Run on ESP32
"""

import machine
import epaper4in2
from machine import Pin, SPI

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

w = 400
h = 300
x = 0
y = 0

# --------------------

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

# use a frame buffer
# 400 * 300 / 8 = 15000 - thats a lot of pixels
import framebuf

buf = bytearray(w * h // 8)
fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
black = 0
white = 1
fb.fill(white)


def print_results(metrics):
    label_width = max(len(item["label"]) for item in metrics["results"])
    display_row = 0
    for item in metrics["results"]:
        fb.text("%-*s : %s" % (label_width, item["label"], item["value"]), 0, display_row * 8, black)
        display_row = display_row + 1

    if metrics["missing"]:
        print(
            "\nMissing keys: %s" % ", ".join(str(item) for item in metrics["missing"]),
            file=sys.stderr,
        )
    if metrics["errors"]:
        print("\nErrors: %s" % metrics["errors"], file=sys.stderr)


try:
    metrics = fetch_openquatt_metrics(
        url="http://openquatt.lan:80/openquatt/entities",
        display_fields=fields_to_fetch
    )
except FetchError as exc:
    print(str(exc), file=sys.stderr)

if not metrics["ok"]:
    print("Request failed: %s" % metrics["payload"], file=sys.stderr)

fb.fill(white)
print_results(metrics)
e.display_frame(buf)

