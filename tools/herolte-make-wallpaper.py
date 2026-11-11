#!/usr/bin/env python3
"""Generate default wallpaper for the herolte drop zone.

  herolte-make-wallpaper.py OUT_IMAGE
"""
import math
import struct
import sys

W, H = 720, 1280


def generate_pixels():
    pixels = []
    for y in range(H):
        row = []
        t = y / H
        for x in range(W):
            a = x / W
            r = int(25 + 60 * t + 60 * math.sin(a * 3 + t * 2) ** 2)
            g = int(20 + 40 * (1 - t) + 50 * math.sin(t * 4 + a) ** 2)
            b = int(90 + 120 * (1 - t) + 40 * math.cos(a * 2 - t * 3) ** 2)
            row.append((min(r, 255), min(g, 255), min(b, 255)))
        pixels.append(row)
    return pixels


import os


def write_bmp(path, pixels):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    row_bytes = (W * 3 + 3) & ~3
    image_size = row_bytes * H
    file_size = 54 + image_size
    with open(path, 'wb') as f:
        # BMP Header
        f.write(struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54))
        # DIB Header (BITMAPINFOHEADER)
        f.write(struct.pack('<IIIHHIIIIII', 40, W, H, 1, 24, 0, image_size, 2835, 2835, 0, 0))
        # Pixel data (bottom to top, BGR)
        pad = b'\x00' * (row_bytes - W * 3)
        for y in range(H - 1, -1, -1):
            row_data = bytearray()
            for r, g, b in pixels[y]:
                row_data.extend((b, g, r))
            row_data.extend(pad)
            f.write(row_data)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__.strip())
        return 0 if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help') else 1

    out_path = sys.argv[1]
    pixels = generate_pixels()

    try:
        from PIL import Image, ImageFilter
        im = Image.new('RGB', (W, H))
        p = im.load()
        for y in range(H):
            for x in range(W):
                p[x, y] = pixels[y][x]
        im = im.filter(ImageFilter.GaussianBlur(6))
        im.save(out_path, optimize=True)
        print(f"Generated wallpaper (PIL): {out_path}")
    except ImportError:
        write_bmp(out_path, pixels)
        print(f"Generated wallpaper (BMP fallback, Pillow not installed): {out_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
