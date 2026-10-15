"""Remove Scaniverse's distant placeholder splats from the Quest model."""

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
SPLAT = np.dtype([
    ("position", "<f4", (3,)),
    ("scale", "<f4", (3,)),
    ("color", "u1", (4,)),
    ("rotation", "u1", (4,)),
])

source = np.fromfile(ROOT / "murales.splat", dtype=SPLAT)
distance = np.linalg.norm(source["position"], axis=1)
keep = np.isfinite(distance) & (distance <= 20)
keep &= np.isfinite(source["scale"]).all(axis=1)
keep &= (source["scale"] > 0).all(axis=1)
cleaned = source[keep]
cleaned.tofile(ROOT / "murales-quest.splat")
print(f"Kept {len(cleaned):,} of {len(source):,} splats; removed {len(source) - len(cleaned):,} distant/invalid splats")
