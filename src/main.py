"""
    Example for 4.2 inch black & white Waveshare E-ink screen
    Run on ESP32
"""

import machine
import epaper4in2
import framebuf
from machine import Pin

import hpdisplayer

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

try:
    buf = hpdisplayer.load_pbm_image(hpdisplayer._resource_path("background.pbm"))
except Exception as exc:
    print("Error loading image: %s" % exc)
    buf = bytearray([0xFF]) * (hpdisplayer.DISPLAY_WIDTH * hpdisplayer.DISPLAY_HEIGHT // 8)

fb = framebuf.FrameBuffer(
    buf, hpdisplayer.DISPLAY_WIDTH, hpdisplayer.DISPLAY_HEIGHT, framebuf.MONO_HLSB
)

hpdisplayer.render_to_framebuffer(fb)
e.display_frame(buf)