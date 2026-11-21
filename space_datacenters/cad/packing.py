"""How many stowed satellites fit in Starship's payload bay?

The bay is round, and it narrows toward the nose. Satellites stand in layers along its
axis, and each layer is a set of identical rectangles packed into the circle available at
that height.

Used by both the Part 2 notebook and cad/build_satellite.py, so the satellite count and
the SolidWorks stack assembly always agree. Pure Python: no SolidWorks needed.
"""
import math


def pack_circle(width: float, depth: float, diameter: float, steps: int = 41) -> list[tuple[float, float, bool]]:
    """Pack width × depth rectangles into a circle, in straight rows.

    A simple search rather than an optimal packing: it tries the rectangles both ways
    round, slides the block of rows across the circle in `steps` positions, and keeps the
    layout that fits the most.

    Returns one (x, z, turned) per rectangle: its center, and whether it is turned 90°.
    """
    radius = diameter / 2
    best = []
    for turned, (w, d) in ((False, (width, depth)), (True, (depth, width))):
        slack = diameter - (diameter // d) * d          # room left over beside the rows
        for step in range(steps):
            z = -radius + slack * step / (steps - 1)    # near edge of the first row
            layout = []
            while z + d <= radius + 1e-9:
                # A row is limited by the shortest chord it touches: the one farthest from center.
                farthest = max(abs(z), abs(z + d))
                chord = 2 * math.sqrt(max(radius**2 - farthest**2, 0.0))
                n = int((chord + 1e-9) // w)
                layout += [((i - (n - 1) / 2) * w, z + d / 2, turned) for i in range(n)]
                z += d
            if len(layout) > len(best):
                best = layout
    return best


def bay_radius(profile, height: float) -> float:
    """Radius of the payload envelope at a given height. `profile` is a list of
    (height, radius) points joined by straight lines; above the last point there is no room."""
    for (h0, r0), (h1, r1) in zip(profile, profile[1:]):
        if h0 <= height <= h1:
            return r0 + (r1 - r0) * (height - h0) / (h1 - h0)
    return 0.0


def sats_per_flight(stowed_size_xyz, profile) -> dict:
    """Satellites per flight by volume, given the stowed bounding box (x, y, z) and the bay
    profile. The satellite's y axis lies along the bay axis. Layers are added from the floor
    up, and each must fit inside the narrowest part of the bay it spans, so layers in the
    tapered nose hold fewer satellites, or none.

    Returns the count in each layer, the totals, and `layout`: for each layer, its floor
    height and the (x, z, turned) position of every satellite in it.
    """
    size_x, size_y, size_z = stowed_size_xyz
    layout, floor = [], 0.0
    while True:
        radius = min(bay_radius(profile, floor), bay_radius(profile, floor + size_y))
        layer = pack_circle(size_x, size_z, 2 * radius)
        if not layer:
            break
        layout.append((floor, layer))
        floor += size_y
    per_layer = [len(layer) for _, layer in layout]
    return dict(per_layer=per_layer, layers=len(layout), total=sum(per_layer), layout=layout)
