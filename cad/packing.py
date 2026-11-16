"""Pack identical rectangular satellite footprints into Starship's circular payload bay.

Used by both the Part 2 notebook and cad/build_satellite.py, so the count and the
SolidWorks stack assembly always agree. Pure Python (no SolidWorks dependency).
"""
from __future__ import annotations

import math


def pack_circle(fx: float, fz: float, diameter: float, steps: int = 41) -> list[tuple[float, float, bool]]:
    """Best simple row layout of fx-by-fz rectangles inside a circle.

    Tries both orientations and a sweep of row offsets. Rows run along x; each row holds as
    many rectangles as fit inside the narrowest chord the row spans.
    Returns centers [(x, z, rotated)], where rotated=True means the footprint is turned 90°.
    """
    r = diameter / 2
    best: list[tuple[float, float, bool]] = []
    for rotated, (w, h) in ((False, (fx, fz)), (True, (fz, fx))):
        n_rows_max = int(diameter // h)
        for k in range(steps):
            z0 = -r + (k / (steps - 1)) * (diameter - n_rows_max * h) if n_rows_max else -r
            layout = []
            z = z0
            while z + h <= r + 1e-9:
                zmax = max(abs(z), abs(z + h))
                half_chord = math.sqrt(max(r * r - zmax * zmax, 0.0))
                n = int((2 * half_chord + 1e-9) // w)
                xs = [-(n * w) / 2 + w / 2 + i * w for i in range(n)]
                layout += [(x, z + h / 2, rotated) for x in xs]
                z += h
            if len(layout) > len(best):
                best = layout
    return best


def sats_per_flight(stowed_size_xyz, bay_diameter: float, bay_height: float) -> dict:
    """Stowed satellites stand with their y axis along the bay axis."""
    sx, sy, sz = stowed_size_xyz
    per_layer = pack_circle(sx, sz, bay_diameter)
    layers = int(bay_height // sy)
    return dict(per_layer=len(per_layer), layers=layers, total=len(per_layer) * layers, layout=per_layer)
