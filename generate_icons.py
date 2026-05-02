#!/usr/bin/env python3
"""Generate PWA icons for ChocoLog app."""
import struct, zlib, math

def png_chunk(chunk_type, data):
    c = chunk_type + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

def make_png(size):
    def to_bytes(pixels):
        raw = b''
        for row in pixels:
            raw += b'\x00'
            for r,g,b,a in row:
                raw += bytes([r,g,b,a])
        return zlib.compress(raw)

    pixels = [[(0,0,0,0)]*size for _ in range(size)]
    cx, cy, r = size//2, size//2, size//2

    # Background circle: dark navy
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            if dx*dx + dy*dy <= r*r:
                pixels[y][x] = (15, 23, 42, 255)  # #0f172a

    # Inner circle: cyan accent
    r2 = int(r * 0.85)
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            if dx*dx + dy*dy <= r2*r2:
                pixels[y][x] = (15, 23, 42, 255)

    # Draw "C" letter shape in cyan
    font_r = int(r * 0.55)
    thick = max(2, size // 20)
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            # Draw arc from ~200deg to ~160deg (clockwise, leaving gap on right)
            gap_start = -0.4
            gap_end = 0.4
            if abs(dist - font_r) <= thick and not (gap_start <= angle <= gap_end):
                pixels[y][x] = (34, 211, 238, 255)  # #22d3ee

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    # RGBA
    ihdr_data = struct.pack('>II', size, size) + bytes([8, 6, 0, 0, 0])
    idat = make_png_idat(pixels, size)
    chunks = (
        sig +
        png_chunk(b'IHDR', ihdr_data) +
        png_chunk(b'IDAT', idat) +
        png_chunk(b'IEND', b'')
    )
    return chunks

def make_png_idat(pixels, size):
    raw = b''
    for row in pixels:
        raw += b'\x00'
        for r,g,b,a in row:
            raw += bytes([r,g,b,a])
    return zlib.compress(raw)

def make_icon_png(size):
    """Create a simple icon PNG."""
    pixels = [[(0,0,0,0)]*size for _ in range(size)]
    cx, cy = size//2, size//2
    r = size//2 - 1

    # Outer circle bg
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            if dx*dx + dy*dy <= r*r:
                pixels[y][x] = (15, 23, 42, 255)

    # Draw C arc
    font_r = int(r * 0.6)
    thick = max(2, size // 16)
    for y in range(size):
        for x in range(size):
            dx, dy = x-cx, y-cy
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            if abs(dist - font_r) <= thick:
                # gap on right side
                if not (-0.5 <= angle <= 0.5):
                    pixels[y][x] = (34, 211, 238, 255)

    # Horizontal bar (crossbar of C)
    bar_y_top = cy - thick//2
    bar_y_bot = cy + thick//2
    bar_x_left = cx - font_r + thick
    bar_x_right = cx + int(font_r * 0.3)
    for y in range(bar_y_top, bar_y_bot+1):
        for x in range(bar_x_left, bar_x_right+1):
            if 0 <= y < size and 0 <= x < size:
                dx2, dy2 = x-cx, y-cy
                if dx2*dx2 + dy2*dy2 <= r*r:
                    pixels[y][x] = (34, 211, 238, 255)

    # Assemble PNG
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>II', size, size) + bytes([8, 6, 0, 0, 0])
    idat = make_png_idat(pixels, size)
    return (
        sig +
        png_chunk(b'IHDR', ihdr_data) +
        png_chunk(b'IDAT', idat) +
        png_chunk(b'IEND', b'')
    )

import os
os.makedirs('icons', exist_ok=True)
for sz in [192, 512]:
    data = make_icon_png(sz)
    with open(f'icons/icon-{sz}.png', 'wb') as f:
        f.write(data)
    print(f'Generated icons/icon-{sz}.png ({sz}x{sz})')
