"""Turn Scaniverse's distant spherical splats into a light panorama backdrop."""

from pathlib import Path
import struct
import zlib

import numpy as np


ROOT = Path(__file__).resolve().parent
SPLAT = np.dtype([
    ("position", "<f4", (3,)),
    ("scale", "<f4", (3,)),
    ("color", "u1", (4,)),
    ("rotation", "u1", (4,)),
])
WIDTH, HEIGHT = 2048, 1024


def write_png(path, pixels):
    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload)))

    rows = b"".join(b"\0" + row.tobytes() for row in pixels)
    header = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    path.write_bytes(header + chunk(b"IDAT", zlib.compress(rows, 6)) + chunk(b"IEND", b""))


source = np.fromfile(ROOT / "murales.splat", dtype=SPLAT)
distance = np.linalg.norm(source["position"], axis=1)
near = source[distance <= 20]
far = source[distance > 100]

# Keep roughly half the foreground splats for a lower-cost stereo/VR rendering.
rng = np.random.default_rng(42)
selection = np.sort(rng.choice(len(near), size=min(220000, len(near)), replace=False))
near[selection].tofile(ROOT / "murales-quest.splat")

accum = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
weights = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
for splat in far:
    px, py, pz = splat["position"]
    radius = float(np.sqrt(px * px + py * py + pz * pz))
    longitude = np.arctan2(px, pz)
    latitude = np.arcsin(np.clip(py / radius, -1, 1))
    center_x = (longitude / (2 * np.pi) + .5) * WIDTH
    center_y = (latitude / np.pi + .5) * HEIGHT
    sigma_y = max(2.0, float(splat["scale"].mean() / radius * HEIGHT / np.pi))
    sigma_x = min(90, sigma_y / max(.12, np.cos(latitude)))
    reach_x, reach_y = int(3 * sigma_x), int(3 * sigma_y)
    xs = np.arange(int(center_x) - reach_x, int(center_x) + reach_x + 1)
    ys = np.arange(max(0, int(center_y) - reach_y), min(HEIGHT, int(center_y) + reach_y + 1))
    if not len(ys):
        continue
    dx = ((xs - center_x + WIDTH / 2) % WIDTH) - WIDTH / 2
    spread = np.exp(-.5 * ((dx[None, :] / sigma_x) ** 2 + ((ys[:, None] - center_y) / sigma_y) ** 2))
    spread *= float(splat["color"][3]) / 255
    columns = xs % WIDTH
    accum[np.ix_(ys, columns)] += spread[:, :, None] * splat["color"][:3]
    weights[np.ix_(ys, columns)] += spread

# Broaden the interpolation only where the Scaniverse background has gaps.
for _ in range(6):
    missing = weights < .01
    if not missing.any():
        break
    new_weights = (np.roll(weights, 1, axis=0) + np.roll(weights, -1, axis=0)
                   + np.roll(weights, 1, axis=1) + np.roll(weights, -1, axis=1)) / 4
    new_accum = (np.roll(accum, 1, axis=0) + np.roll(accum, -1, axis=0)
                 + np.roll(accum, 1, axis=1) + np.roll(accum, -1, axis=1)) / 4
    weights[missing] = new_weights[missing]
    accum[missing] = new_accum[missing]

pixels = np.clip(accum / np.maximum(weights[:, :, None], 1e-6), 0, 255).astype(np.uint8)
write_png(ROOT / "murales-background.png", pixels)
print(f"Foreground: {len(near):,} -> {len(selection):,}; panorama splats: {len(far):,}; uncovered pixels: {(weights < .01).sum():,}")
