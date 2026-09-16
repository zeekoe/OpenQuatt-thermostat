"""Desktop viewer for the OpenQuatt thermostat framebuffer.

Renders the same 400x300 MONO_HLSB framebuffer as the ESP32 firmware
and displays it. Saves a PNG when pillow is installed, otherwise writes
a portable bitmap (P4).

Installs minimal CPython shims for the MicroPython-only builtins
(``framebuf``, ``micropython``) so the shared MicroPython modules
(``hpdisplayer``, ``microfont``) run unmodified on the desktop.
"""

import math
import os
import sys
import types
import builtins

_framebuf_MONO_HLSB = 3


class _FrameBuffer:
    def __init__(self, buf, width, height, mode):
        self._buf = buf
        self.width = width
        self.height = height

    def fill(self, value):
        pattern = 0xFF if value else 0x00
        for i in range(len(self._buf)):
            self._buf[i] = pattern

    def __len__(self):
        return len(self._buf)

    def __getitem__(self, index):
        return self._buf[index]

    def __setitem__(self, index, value):
        self._buf[index] = value

    def _write(self, x, y, color):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        idx = (y * self.width + x) >> 3
        bit = 7 - (x & 7)
        if color:
            self._buf[idx] |= 1 << bit
        else:
            self._buf[idx] &= ~(1 << bit)

    def pixel(self, x, y, color=1):
        self._write(x, y, color)

    def hline(self, x, y, w, color=1):
        for dx in range(w):
            self._write(x + dx, y, color)

    def vline(self, x, y, h, color=1):
        for dy in range(h):
            self._write(x, y + dy, color)

    def line(self, x1, y1, x2, y2, color=1):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self._write(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            err2 = 2 * err
            if err2 > -dy:
                err -= dy
                x1 += sx
            if err2 < dx:
                err += dx
                y1 += sy

    # actually this can only draw a circle :)
    def ellipse(self, x0, y0, r, ignore, color=1):
        x = 0
        y = r
        f = 1 - r
        dd_fx = 1
        dd_fy = -2 * r
        while x <= y:
            for px, py in (
                (x0 + x, y0 + y),
                (x0 - x, y0 + y),
                (x0 + x, y0 - y),
                (x0 - x, y0 - y),
                (x0 + y, y0 + x),
                (x0 - y, y0 + x),
                (x0 + y, y0 - x),
                (x0 - y, y0 - x),
            ):
                self._write(px, py, color)
            if f >= 0:
                y -= 1
                dd_fy += 2
                f += dd_fy
            x += 1
            dd_fx += 2
            f += dd_fx

_framebuf = types.ModuleType("framebuf")
_framebuf.MONO_HLSB = 3
_framebuf.RGB565 = 1
_framebuf.FrameBuffer = _FrameBuffer
sys.modules["framebuf"] = _framebuf

_micropython = types.ModuleType("micropython")
_micropython.viper = lambda func: func
sys.modules["micropython"] = _micropython
builtins.micropython = _micropython

builtins.const = lambda value: value
builtins.ptr8 = lambda value: value
builtins.ptr16 = lambda value: value

import hpdisplayer


def _new_framebuffer():
    try:
        buf = hpdisplayer.load_pbm_image(
            hpdisplayer._resource_path("background.pbm")
        )
    except Exception as exc:
        print("Error loading image: %s" % exc)
        buf = bytearray([0xFF]) * (
            hpdisplayer.DISPLAY_WIDTH * hpdisplayer.DISPLAY_HEIGHT // 8
        )
    return (
        buf,
        _framebuf.FrameBuffer(
            buf,
            hpdisplayer.DISPLAY_WIDTH,
            hpdisplayer.DISPLAY_HEIGHT,
            _framebuf_MONO_HLSB,
        ),
    )


def _image_from_framebuffer(buf):
    from PIL import Image

    return Image.frombytes(
        "1", (hpdisplayer.DISPLAY_WIDTH, hpdisplayer.DISPLAY_HEIGHT), buf
    )


def _write_pbm(buf, path):
    with open(path, "wb") as f:
        f.write(b"P4\n%d %d\n" % (hpdisplayer.DISPLAY_WIDTH, hpdisplayer.DISPLAY_HEIGHT))
        f.write(buf)


def main():
    buf, fb = _new_framebuffer()
    hpdisplayer.render_to_framebuffer(fb)

    try:
        img = _image_from_framebuffer(buf)
    except ImportError:
        out = os.path.join(os.getcwd(), "screen.pbm")
        _write_pbm(buf, out)
        print("Saved %s (install pillow for PNG preview)" % out)
        return

    out = os.path.join(os.getcwd(), "screen.png")
    img.convert("RGB").save(out)
    print("Saved %s" % out)
    img.show()


if __name__ == "__main__":
    main()