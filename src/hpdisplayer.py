"""Shared code for OpenQuatt: fetch metrics and render them into a
MONO_HLSB (400x300) framebuffer.
"""

import math
import sys
import time

from fetch_openquatt_metrics import (
    FetchError,
    fetch_openquatt_metrics,
)
from microfont import MicroFont

DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 300

_framebuf_MONO_HLSB = 3

BLACK = 0
WHITE = 1

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


def _resource_path(name):
    try:
        from os import path as _path

        return _path.join(_path.dirname(__file__), name)
    except (ImportError, AttributeError):
        return name


def load_pbm_image(file_path):
    """Load a PBM (Portable Bitmap) image file"""
    with open(file_path, "rb") as f:
        magic = f.readline().strip()
        if magic != b"P4":
            raise ValueError("Only P4 (binary PBM) format is supported")

        while True:
            line = f.readline()
            if not line.startswith(b"#"):
                break

        width, height = map(int, line.split())
        if width != DISPLAY_WIDTH or height != DISPLAY_HEIGHT:
            raise ValueError(
                "Image dimensions %sx%s don't match display %sx%s"
                % (width, height, DISPLAY_WIDTH, DISPLAY_HEIGHT)
            )

        return bytearray(f.read())


def draw_clock(fb, font, cx, cy, r, hour, minute):
    """Draw an analogue clock centred on (cx, cy) with radius r."""

    def end_point(length, angle_deg):
        rad = math.radians(angle_deg)
        return (
            round(cx + length * math.sin(rad)),
            round(cy - length * math.cos(rad)),
        )

    hour_markers = {0: "12", 3: "3", 6: "6", 9: "9"}

    def marker_text(text, angle_deg):
        x, y = end_point(r - 10, angle_deg)
        width = sum(font.get_ch(c)[2] for c in text)
        font.write(
            text,
            fb,
            _framebuf_MONO_HLSB,
            DISPLAY_WIDTH,
            DISPLAY_HEIGHT,
            x - width // 2,
            y - font.height // 2,
            BLACK,
        )

    fb.ellipse(cx, cy, r, r, BLACK)
    fb.ellipse(cx, cy, r - 2, r - 2, BLACK)

    for hour_index in range(12):
        angle = hour_index * 30
        if hour_index % 3 == 0:
            marker_text(hour_markers[hour_index], angle)
        else:
            x1, y1 = end_point(r - 6, angle)
            x2, y2 = end_point(r - 12, angle)
            fb.line(x1, y1, x2, y2, BLACK)

    hour_angle = (hour % 12) * 30 + minute * 0.5
    minute_angle = minute * 6

    x, y = end_point(r - 20, hour_angle)
    fb.line(cx, cy, x, y, BLACK)
    x, y = end_point(r - 6, minute_angle)
    fb.line(cx, cy, x, y, BLACK)
    fb.ellipse(cx, cy, 2, 2, BLACK)


def render_to_framebuffer(fb):
    """Fetch live metrics and draw them into the given framebuffer."""
    try:
        metrics = fetch_openquatt_metrics(
            url="http://openquatt.lan:80/openquatt/entities",
            display_fields=fields_to_fetch,
        )
    except FetchError as exc:
        print(str(exc), file=sys.stderr)

    if not metrics["ok"]:
        print("Request failed: %s" % metrics["payload"], file=sys.stderr)

    def get_value_by_key(key):
        for item in metrics["results"]:
            if item["key"] == key:
                return item["value"]
        return None

    font = MicroFont(_resource_path("dejavub14.mfnt"), cache_index=True)

    def print_text(text, x, y):
        font.write(
            text,
            fb,
            _framebuf_MONO_HLSB,
            DISPLAY_WIDTH,
            DISPLAY_HEIGHT,
            x,
            y,
            BLACK,
            rot=0,
        )

    print_text(get_value_by_key("roomTemp"), 250, 140)
    print_text(get_value_by_key("hp1Power"), 125, 74)
    print_text(get_value_by_key("hp1Freq"), 77, 210)
    print_text(get_value_by_key("hp1WaterIn"), 110, 200)
    print_text(get_value_by_key("hp1WaterOut"), 107, 144)
    print_text(get_value_by_key("supplyTemp"), 160, 126)
    print_text(get_value_by_key("totalHeat"), 107, 160)
    print_text(get_value_by_key("hp1OutsideTemp"), 84, 33)
    print_text(get_value_by_key("hp1EvaporatorCoilTemp"), 15, 138)

    now = time.localtime()
    draw_clock(fb, font, 356, 46, 40, now[3], now[4])
