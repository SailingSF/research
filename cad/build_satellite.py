"""Build the Part 2 reference satellite in SolidWorks from cad/params.json.

Run from the repo root with SolidWorks open:
    .venv\\Scripts\\python.exe cad\\build_satellite.py

Outputs (all under cad/):
    parts/*.SLDPRT              one part per subsystem
    satellite_deployed.SLDASM   on-orbit configuration
    satellite_stowed.SLDASM     folded for launch
    starship_stack.SLDASM       stowed satellites packed into the Starship payload bay
    mass_props.json             masses, inertia, stowed envelope, packing (read back by the notebook)
    images/*.jpg                isometric views for the blog

Model frame: +X = velocity, +Y = zenith (Starship axis when stowed), +Z = toward the Sun.
Parts whose internals are not modeled get a uniform density that yields their target mass;
the primary structure is drawn as CFRP tubes and its mass comes from the geometry.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sw_api as S  # noqa: E402
from packing import sats_per_flight  # noqa: E402

PARTS = os.path.join(HERE, "parts")
IMAGES = os.path.join(HERE, "images")

# display colors (r, g, b)
C_COMPUTE, C_FRAME, C_EQUIP = (0.25, 0.25, 0.28), (0.15, 0.15, 0.15), (0.75, 0.62, 0.25)
C_ARRAY, C_RAD, C_BAY = (0.10, 0.20, 0.55), (0.92, 0.92, 0.90), (0.80, 0.80, 0.82)


def build_part(sw, name, draw, mass=None, density=None, color=None):
    p = S.Part(sw)
    draw(p)
    if mass is not None:
        p.set_mass(mass)
    elif density is not None:
        p.density(density)
    if color:
        try:
            p.color(color)
        except Exception as e:  # cosmetic only
            print(f"  (color skipped for {name}: {e})")
    path = p.save(os.path.join(PARTS, f"{name}.SLDPRT"))
    mp = p.mass_props()
    print(f"  {name:22s} {mp['mass']:9.1f} kg")
    return path, mp["mass"]


def save_image(sw, assy, name, view="*Isometric"):
    try:
        m = assy.model
        m.ShowNamedView2(view, -1)
        m.ViewZoomtofit2()
        os.makedirs(IMAGES, exist_ok=True)
        path = os.path.normpath(os.path.join(IMAGES, f"{name}.jpg"))
        res = assy.ext.SaveAs3(path, 0, 1, None, None, 0, 0)
        return path if os.path.exists(path) else None
    except Exception as e:
        print(f"  (image {name} skipped: {e})")
        return None


def main():
    with open(os.path.join(HERE, "params.json")) as f:
        P = json.load(f)
    sw = S.connect()
    S.close_matching(sw, HERE, untitled=False)

    cx, cy, cz = P["compute"]["size"]
    fx, fy, fz = P["frame"]["size"]
    tb, tw = P["frame"]["tube_outer"], P["frame"]["tube_wall"]
    top = fy / 2 + tb / 2                       # outer face of the top frame members
    W = P["wing"]
    wing_w = W["width"]
    wing_len = W["area_each"] / wing_w
    roll_r = math.sqrt(W["stowed_volume_each"] / (math.pi * wing_w))
    root_x = fx / 2 + tb / 2 + 0.05 + roll_r   # roll / canister axis, outside the frame
    R = P["radiator"]
    fin_len = R["panel_area_total"] / 2 / R["fin_width"]
    n_pan = math.ceil(fin_len / R["panel_max_length"] - 1e-9)
    pan_len = fin_len / n_pan
    E = P["equipment"]

    print("Building parts")
    paths, masses = {}, {}

    def add(name, draw, **kw):
        paths[name], masses[name] = build_part(sw, name, draw, **kw)

    add("compute_module", lambda p: p.box((0, 0, 0), (cx, cy, cz)), mass=P["compute"]["mass"], color=C_COMPUTE)

    def frame(p):
        for sx in (-1, 1):
            for sz in (-1, 1):
                p.square_tube("y", (sx * fx / 2, 0, sz * fz / 2), tb, tw, fy + tb)
        for y in (-fy / 2, 0.0, fy / 2):
            for sz in (-1, 1):
                p.square_tube("x", (0, y, sz * fz / 2), tb, tw, fx - tb)
            for sx in (-1, 1):
                p.square_tube("z", (sx * fx / 2, y, 0), tb, tw, fz - tb)
    add("frame", frame, density=P["frame"]["density"], color=C_FRAME)

    # equipment in the top bay (y > cy/2) and bottom bay (y < -cy/2)
    yt, yb = (cy / 2 + fy / 2) / 2, -(cy / 2 + fy / 2) / 2
    add("avionics", lambda p: p.box((0, yt + 0.2, -0.35), (0.4, 0.3, 0.3)), mass=E["avionics"], color=C_EQUIP)
    add("reaction_wheels", lambda p: [p.cylinder("y", (sx * 0.4, yt - 0.15, sz * 0.35), 0.16, 0.12)
                                      for sx in (-1, 1) for sz in (-1, 1)], mass=E["reaction_wheels"], color=C_EQUIP)
    add("laser_terminals", lambda p: [p.cylinder("y", c, 0.13, 0.3) for c in
                                      ((0.45, yt + 0.25, 0.4), (-0.45, yt + 0.25, 0.4), (0.45, yb - 0.25, -0.4))],
        mass=E["laser_terminals"], color=C_EQUIP)
    add("power_conditioning", lambda p: p.box((0.25, yb, 0.0), (0.7, 0.45, 0.8)), mass=E["power_conditioning"], color=C_EQUIP)
    add("propellant_tank", lambda p: p.cylinder("z", (-0.4, yb, 0.0), 0.2, 0.7),
        mass=E["propellant_tank"] + P["propellant"], color=C_EQUIP)
    add("ep_thrusters", lambda p: [p.cylinder("x", (-(fx / 2 + tb / 2 + 0.12), yb, sz * 0.5), 0.09, 0.24)
                                   for sz in (-1, 1)], mass=E["electric_propulsion"], color=C_EQUIP)
    add("array_drives", lambda p: [p.cylinder("x", (sx * (fx / 2 + tb / 2 + 0.03), 0, 0), 0.14, 0.06)
                                   for sx in (-1, 1)], mass=E["array_drives"], color=C_EQUIP)
    add("stack_interfaces", lambda p: [p.box((sx * fx / 2, sy * (fy / 2 - 0.1), sz * fz / 2), (0.12, 0.08, 0.12))
                                       for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)],
        mass=E["stack_interfaces"], color=C_EQUIP)

    # solar wing (+X side; the -X wing is the same part rotated 180° about Y)
    def wing_deployed(p):
        p.cylinder("y", (root_x, 0, 0), 0.12, wing_w + 0.1)                       # empty roll canister
        x0 = root_x + 0.15
        p.box((x0 + wing_len / 2, 0, 0), (wing_len, wing_w, 0.003))               # blanket, faces +Z (Sun)
        for sy in (-1, 1):
            p.cylinder("x", (x0 + wing_len / 2, sy * (wing_w / 2 + 0.06), 0), 0.06, wing_len, inner_radius=0.057)
    add("wing_deployed", wing_deployed, mass=W["mass_each"], color=C_ARRAY)
    add("wing_stowed", lambda p: p.cylinder("y", (root_x, 0, 0), roll_r, wing_w + 0.1), mass=W["mass_each"], color=C_ARRAY)

    # radiator panel, modeled at the origin in its deployed orientation (plane Y-Z, thickness along X)
    add("radiator_panel", lambda p: p.box((0, 0, 0), (R["thickness"], pan_len, R["fin_width"])),
        mass=R["mass_total"] / (2 * n_pan), color=C_RAD)

    core = ["compute_module", "frame", "avionics", "reaction_wheels", "laser_terminals", "power_conditioning",
            "propellant_tank", "ep_thrusters", "array_drives", "stack_interfaces"]
    flip = S.rot_matrix("y", 180)

    # ---- deployed assembly
    print("Assembling deployed satellite")
    dep = S.Assembly(sw)
    for n in core:
        dep.add(paths[n])
    dep.add(paths["wing_deployed"])
    dep.add(paths["wing_deployed"], rot=flip)
    for sy in (-1, 1):
        for i in range(n_pan):
            dep.add(paths["radiator_panel"], pos=(0, sy * (top + (i + 0.5) * pan_len), 0))
    dep_path = dep.save(os.path.join(HERE, "satellite_deployed.SLDASM"))
    dep_mp, dep_box = dep.mass_props(), dep.box()
    img_dep = save_image(sw, dep, "satellite_deployed")

    # ---- stowed assembly: wings rolled, radiator panels stacked flat against the ±Z faces
    print("Assembling stowed satellite")
    sto = S.Assembly(sw)
    for n in core:
        sto.add(paths[n])
    sto.add(paths["wing_stowed"])
    sto.add(paths["wing_stowed"], rot=flip)
    panel_rot = S.rot_matrix("y", 90)        # panel width (local Z) -> X, thickness (local X) -> Z
    pitch = R["thickness"] * 2
    for sz in (-1, 1):
        for i in range(n_pan):
            z = sz * (fz / 2 + tb / 2 + 0.05 + R["thickness"] / 2 + i * pitch)
            sto.add(paths["radiator_panel"], pos=(0, 0, z), rot=panel_rot)
    sto_path = sto.save(os.path.join(HERE, "satellite_stowed.SLDASM"))
    sto_mp, sto_box = sto.mass_props(), sto.box()
    img_sto = save_image(sw, sto, "satellite_stowed")

    # ---- Starship stack
    print("Packing Starship")
    D, H = P["bay"]["diameter"], P["bay"]["height"]
    pack = sats_per_flight(sto_box["size"], D, H)
    add("starship_bay", lambda p: p.cylinder("y", (0, H / 2, 0), D / 2 + 0.05, H, inner_radius=D / 2), mass=1.0, color=C_BAY)
    stack = S.Assembly(sw)
    stack.add(paths["starship_bay"])
    c = [(a + b) / 2 for a, b in zip(sto_box["min"], sto_box["max"])]
    sy_size = sto_box["size"][1]
    for k in range(pack["layers"]):
        for (x, z, rotated) in pack["layout"]:
            rot = S.rot_matrix("y", 90) if rotated else None
            rc = [c[0], c[1], c[2]] if not rotated else [c[2], c[1], -c[0]]   # R_y(90)·c
            target = (x, k * sy_size + sy_size / 2, z)
            stack.add(sto_path, pos=(target[0] - rc[0], target[1] - rc[1], target[2] - rc[2]), rot=rot)
    stack.save(os.path.join(HERE, "starship_stack.SLDASM"))
    img_stack = save_image(sw, stack, "starship_stack")

    counts = {n: 1 for n in core}
    counts.update(wing_deployed=2, radiator_panel=2 * n_pan)
    out = {
        "params": P,
        "part_masses": {n: masses[n] * counts.get(n, 1) for n in list(core) + ["wing_deployed", "radiator_panel"]},
        "geometry": {"wing_length": wing_len, "roll_radius": roll_r, "radiator_panels": 2 * n_pan,
                     "panel_length": pan_len, "fin_length": fin_len},
        "deployed": {**dep_mp, "size": dep_box["size"]},
        "stowed": {**sto_mp, "size": sto_box["size"]},
        "stack": {k: v for k, v in pack.items() if k != "layout"},
        "images": [i for i in (img_dep, img_sto, img_stack) if i],
    }
    with open(os.path.join(HERE, "mass_props.json"), "w") as f:
        json.dump(out, f, indent=2)

    print(f"Deployed: {dep_mp['mass']:,.0f} kg, span {dep_box['size'][0]:.1f} m (X) × {dep_box['size'][1]:.1f} m (Y)")
    print(f"Stowed envelope: {' × '.join(f'{v:.2f}' for v in sto_box['size'])} m")
    print(f"Starship: {pack['per_layer']} per layer × {pack['layers']} layers = {pack['total']} satellites")
    print("Wrote cad/mass_props.json")


if __name__ == "__main__":
    main()
