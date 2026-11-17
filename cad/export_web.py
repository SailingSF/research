"""Export the satellite design to JSON for the web viewer (labs: satellite-explorer).

Runs anywhere, no SolidWorks needed: the satellite is already plain data (boxes, cylinders
and square tubes, plus where each part sits deployed and stowed) before SolidWorks draws it.

    python cad/export_web.py [out.json]       # default: cad/web/satellite.json

Input:  cad/params.json and cad/<concept>/mass_props.json (part masses from the last SolidWorks build).
"""
import json
import sys
from pathlib import Path
from unittest import mock

# sw_api imports the Windows COM libraries at the top; this script only needs its shape classes.
for name in ("pythoncom", "win32com", "win32com.client"):
    sys.modules.setdefault(name, mock.MagicMock())

import build_satellite as bs   # noqa: E402
from packing import sats_per_flight   # noqa: E402

HERE = Path(__file__).parent


def shape_json(s) -> dict:
    kind = type(s).__name__
    d = {"type": kind, **{k: list(v) if isinstance(v, tuple) else v for k, v in s._asdict().items()}}
    return d


def shape_bounds(s):
    """Axis-aligned (min, max) of a shape in its part's frame."""
    if isinstance(s, bs.Box):
        half = [v / 2 for v in s.size]
    else:
        across = s.radius if isinstance(s, bs.Cylinder) else s.outer / 2
        half = [s.length / 2 if axis == s.axis else across for axis in "xyz"]
    return [c - h for c, h in zip(s.center, half)], [c + h for c, h in zip(s.center, half)]


def placed_bounds(design, placements):
    """Bounding box of an assembly: every shape's box corners, rotated and moved into place."""
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3
    for name, pos, rot in placements:
        R = rot or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        for s in design.parts[name].shapes:
            a, b = shape_bounds(s)
            for corner in ([x, y, z] for x in (a[0], b[0]) for y in (a[1], b[1]) for z in (a[2], b[2])):
                p = [sum(R[i][j] * corner[j] for j in range(3)) + pos[i] for i in range(3)]
                lo = [min(l, v) for l, v in zip(lo, p)]
                hi = [max(h, v) for h, v in zip(hi, p)]
    return lo, hi


def export(concept: str, P: dict) -> dict:
    design = bs.CONCEPTS[concept](P)
    props = json.loads((HERE / concept / "mass_props.json").read_text())
    lo, hi = placed_bounds(design, design.stowed)
    size = [h - l for l, h in zip(lo, hi)]
    packing = sats_per_flight(size, P["bay"]["profile"])
    place = lambda pl: [{"part": n, "position": list(p), "rotation": r} for n, p, r in pl]
    return {
        "parts": {name: {"shapes": [shape_json(s) for s in spec.shapes], "color": list(spec.color),
                         "mass": props["part_masses"].get(name, spec.mass)
                         / (sum(1 for n, _, _ in design.deployed if n == name) or 1)}
                  for name, spec in design.parts.items()},
        "deployed": place(design.deployed),
        "stowed": place(design.stowed),
        "stowed_box": {"min": lo, "max": hi, "size": size},
        "stack": [{"floor": floor, "slots": [list(slot) for slot in layer]} for floor, layer in packing["layout"]],
        "per_flight": packing["total"],
        "mass_as_drawn": props["deployed"]["mass"],
        "geometry": design.geometry,
    }


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "web" / "satellite.json"
    params = json.loads((HERE / "params.json").read_text())
    data = {"bay_profile": params["flatpack"]["bay"]["profile"],
            "concepts": {c: export(c, params[c]) for c in params}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, separators=(",", ":")))
    for c, d in data["concepts"].items():
        print(f"{c}: {len(d['parts'])} parts, stowed {' × '.join(f'{v:.2f}' for v in d['stowed_box']['size'])} m, "
              f"{d['per_flight']} per flight")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
