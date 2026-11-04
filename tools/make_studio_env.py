#!/usr/bin/env python3
"""
Write assets/studio.hdr: a product-photo studio for the 3D viewer and the poster renders.

Dark surroundings with a few soft-edged softboxes (big key at front-left and above, a fill at
front-right, a strong rim behind, a top strip, a faint floor bounce), stored as an equirectangular
Radiance .hdr so highlights can be brighter than white. model-viewer reads it through
environment-image; the strong key/rim contrast is what makes edges, lettering and ports read.

    python3 tools/make_studio_env.py
"""
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 512, 256


def directions():
    # three.js equirectangular convention: u = atan2(z, x) / 2pi + 0.5, v = asin(y) / pi + 0.5 (v up)
    u = (np.arange(W) + 0.5) / W
    v = 1.0 - (np.arange(H) + 0.5) / H
    lon = (u - 0.5) * 2 * np.pi
    lat = (v - 0.5) * np.pi
    lon, lat = np.meshgrid(lon, lat)
    return np.stack([np.cos(lat) * np.cos(lon), np.sin(lat), np.cos(lat) * np.sin(lon)], -1)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def softbox(d, center, w, h, soft=0.35):
    """Rectangular light facing the origin. w, h: half-sizes as tangents of the half-angles."""
    c = np.asarray(center, float); c /= np.linalg.norm(c)
    up = np.array([0.0, 1.0, 0.0])
    if abs(c @ up) > 0.95: up = np.array([0.0, 0.0, 1.0])
    right = np.cross(up, c); right /= np.linalg.norm(right)
    up2 = np.cross(c, right)
    dc = d @ c
    x = (d @ right) / np.maximum(dc, 1e-3)
    y = (d @ up2) / np.maximum(dc, 1e-3)
    m = smooth(w * (1 + soft), w * (1 - soft * 0.4), np.abs(x)) * smooth(h * (1 + soft), h * (1 - soft * 0.4), np.abs(y))
    return m * (dc > 0)


def main():
    d = directions()
    y = d[..., 1]
    # base: near-black studio, slightly lighter toward the horizon, darker floor
    base = 0.035 + 0.05 * np.exp(-(y / 0.35) ** 2)
    base = np.where(y < 0, 0.02 + 0.03 * np.exp(-(y / 0.25) ** 2), base)
    img = np.repeat(base[..., None], 3, -1)

    def add(mask, rgb, k):
        nonlocal img
        img = img + mask[..., None] * np.asarray(rgb, float)[None, None, :] * k

    # camera looks toward -z from +z in the viewer's default frame; "front" lights sit on +z
    add(softbox(d, [-0.75, 0.55, 0.65], 0.55, 0.42), [1.0, 0.97, 0.92], 7.0)   # key, front-left, high
    add(softbox(d, [0.85, 0.15, 0.55], 0.35, 0.5), [0.92, 0.96, 1.0], 1.6)     # fill, front-right
    add(softbox(d, [0.25, 0.45, -0.9], 0.75, 0.22), [0.95, 0.98, 1.0], 6.0)    # rim, behind
    add(softbox(d, [0.0, 1.0, 0.05], 0.9, 0.18), [1.0, 1.0, 1.0], 2.2)         # top strip
    add(softbox(d, [-0.9, 0.05, -0.4], 0.2, 0.6), [1.0, 0.95, 0.9], 2.5)       # kicker, back-left
    add(np.clip(-y, 0, 1) ** 2 * 0.0 + (y < -0.2) * smooth(-0.2, -0.6, y), [0.9, 0.9, 0.92], 0.06)  # floor bounce

    write_hdr(os.path.join(ROOT, 'assets', 'studio.hdr'), img.astype(np.float32))
    print('wrote assets/studio.hdr', img.shape, 'max', round(float(img.max()), 2))


def write_hdr(path, rgb):
    """Uncompressed Radiance RGBE (readers fall back to flat scanlines when there is no RLE marker)."""
    m = rgb.max(-1)
    e = np.where(m > 1e-32, np.floor(np.log2(np.maximum(m, 1e-32))) + 1, 0)
    scale = np.where(m > 1e-32, 256.0 / np.exp2(e), 0)
    rgbe = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    rgbe[..., :3] = np.clip(rgb * scale[..., None], 0, 255).astype(np.uint8)
    rgbe[..., 3] = np.where(m > 1e-32, e + 128, 0).astype(np.uint8)
    with open(path, 'wb') as f:
        f.write(b'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n')
        f.write(f'-Y {rgb.shape[0]} +X {rgb.shape[1]}\n'.encode())
        f.write(rgbe.tobytes())


if __name__ == '__main__':
    main()
