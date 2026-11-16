"""Build the Part 2 reference satellite in SolidWorks from cad/params.json.

Run from the repo root with SolidWorks open:
    .venv\\Scripts\\python.exe cad\\build_satellite.py              # all concepts
    .venv\\Scripts\\python.exe cad\\build_satellite.py flatpack     # one concept

Two stowed-packaging concepts share the same deployed layout (layout B radiators):
    tower     first pass: bus stands along the Starship axis, wings rolled (ROSA-style),
              radiator panels stacked against the sides
    flatpack  Starlink-style plates stacked along the bay axis: compute trays laid flat,
              wings z-folded flat, full-footprint radiator panels on top, corner posts carry the stack

Outputs per concept, under cad/<concept>/:
    parts/*.SLDPRT, satellite_deployed.SLDASM, satellite_stowed.SLDASM, starship_stack.SLDASM,
    images/*.jpg, mass_props.json (read back by the notebook)

Model frame: +X = velocity, +Y = zenith (Starship axis when stowed), +Z = toward the Sun.
Parts whose internals are not modeled get a uniform density that yields their target mass;
primary structure is drawn as CFRP tubes and its mass comes from the geometry.
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

# display colors (r, g, b)
C_COMPUTE, C_FRAME, C_EQUIP = (0.25, 0.25, 0.28), (0.15, 0.15, 0.15), (0.75, 0.62, 0.25)
C_ARRAY, C_RAD, C_BAY = (0.10, 0.20, 0.55), (0.92, 0.92, 0.90), (0.80, 0.80, 0.82)
FLIP_Y = S.rot_matrix("y", 180)


class Builder:
    """Collects parts for one concept and writes them under cad/<concept>/."""

    def __init__(self, sw, concept):
        self.sw, self.concept = sw, concept
        self.out = os.path.join(HERE, concept)
        self.paths, self.masses = {}, {}

    def part(self, name, draw, mass=None, density=None, color=None):
        p = S.Part(self.sw)
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
        self.paths[name] = p.save(os.path.join(self.out, "parts", f"{name}.SLDPRT"))
        self.masses[name] = p.mass_props()["mass"]
        print(f"  {name:22s} {self.masses[name]:9.1f} kg")

    def assembly(self, name, placements):
        """placements: list of (part_name_or_path, pos, rot)."""
        a = S.Assembly(self.sw)
        for ref, pos, rot in placements:
            a.add(self.paths.get(ref, ref), pos=pos, rot=rot)
        path = a.save(os.path.join(self.out, f"{name}.SLDASM"))
        return a, path

    def image(self, assy, name, view="*Isometric"):
        try:
            assy.model.ShowNamedView2(view, -1)
            assy.model.ViewZoomtofit2()
            path = os.path.normpath(os.path.join(self.out, "images", f"{name}.jpg"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            assy.ext.SaveAs3(path, 0, 1, None, None, 0, 0)
            return path if os.path.exists(path) else None
        except Exception as e:
            print(f"  (image {name} skipped: {e})")
            return None


def place(name, pos=(0, 0, 0), rot=None):
    return (name, pos, rot)


# ======================================================================================
# Concept 1: tower
# ======================================================================================
def build_tower(b: Builder, P: dict):
    cx, cy, cz = P["compute"]["size"]
    fx, fy, fz = P["frame"]["size"]
    tb, tw = P["frame"]["tube_outer"], P["frame"]["tube_wall"]
    top = fy / 2 + tb / 2
    W = P["wing"]
    wing_w = W["width"]
    wing_len = W["area_each"] / wing_w
    roll_r = math.sqrt(W["stowed_volume_each"] / (math.pi * wing_w))
    root_x = fx / 2 + tb / 2 + 0.05 + roll_r
    R = P["radiator"]
    fin_len = R["panel_area_total"] / 2 / R["fin_width"]
    n_pan = math.ceil(fin_len / R["panel_max_length"] - 1e-9)
    pan_len = fin_len / n_pan
    E = P["equipment"]

    b.part("compute_module", lambda p: p.box((0, 0, 0), (cx, cy, cz)), mass=P["compute"]["mass"], color=C_COMPUTE)

    def frame(p):
        for sx in (-1, 1):
            for sz in (-1, 1):
                p.square_tube("y", (sx * fx / 2, 0, sz * fz / 2), tb, tw, fy + tb)
        for y in (-fy / 2, 0.0, fy / 2):
            for sz in (-1, 1):
                p.square_tube("x", (0, y, sz * fz / 2), tb, tw, fx - tb)
            for sx in (-1, 1):
                p.square_tube("z", (sx * fx / 2, y, 0), tb, tw, fz - tb)
    b.part("frame", frame, density=P["frame"]["density"], color=C_FRAME)

    yt, yb = (cy / 2 + fy / 2) / 2, -(cy / 2 + fy / 2) / 2
    b.part("avionics", lambda p: p.box((0, yt + 0.2, -0.35), (0.4, 0.3, 0.3)), mass=E["avionics"], color=C_EQUIP)
    b.part("reaction_wheels", lambda p: [p.cylinder("y", (sx * 0.4, yt - 0.15, sz * 0.35), 0.16, 0.12)
                                         for sx in (-1, 1) for sz in (-1, 1)], mass=E["reaction_wheels"], color=C_EQUIP)
    b.part("laser_terminals", lambda p: [p.cylinder("y", c, 0.13, 0.3) for c in
                                         ((0.45, yt + 0.25, 0.4), (-0.45, yt + 0.25, 0.4), (0.45, yb - 0.25, -0.4))],
           mass=E["laser_terminals"], color=C_EQUIP)
    b.part("power_conditioning", lambda p: p.box((0.25, yb, 0.0), (0.7, 0.45, 0.8)), mass=E["power_conditioning"], color=C_EQUIP)
    b.part("propellant_tank", lambda p: p.cylinder("z", (-0.4, yb, 0.0), 0.2, 0.7),
           mass=E["propellant_tank"] + P["propellant"], color=C_EQUIP)
    b.part("ep_thrusters", lambda p: [p.cylinder("x", (-(fx / 2 + tb / 2 + 0.12), yb, sz * 0.5), 0.09, 0.24)
                                      for sz in (-1, 1)], mass=E["electric_propulsion"], color=C_EQUIP)
    b.part("array_drives", lambda p: [p.cylinder("x", (sx * (fx / 2 + tb / 2 + 0.03), 0, 0), 0.14, 0.06)
                                      for sx in (-1, 1)], mass=E["array_drives"], color=C_EQUIP)
    b.part("stack_interfaces", lambda p: [p.box((sx * fx / 2, sy * (fy / 2 - 0.1), sz * fz / 2), (0.12, 0.08, 0.12))
                                          for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)],
           mass=E["stack_interfaces"], color=C_EQUIP)

    def wing_deployed(p):
        p.cylinder("y", (root_x, 0, 0), 0.12, wing_w + 0.1)
        x0 = root_x + 0.15
        p.box((x0 + wing_len / 2, 0, 0), (wing_len, wing_w, 0.003))
        for sy in (-1, 1):
            p.cylinder("x", (x0 + wing_len / 2, sy * (wing_w / 2 + 0.06), 0), 0.06, wing_len, inner_radius=0.057)
    b.part("wing_deployed", wing_deployed, mass=W["mass_each"], color=C_ARRAY)
    b.part("wing_stowed", lambda p: p.cylinder("y", (root_x, 0, 0), roll_r, wing_w + 0.1), mass=W["mass_each"], color=C_ARRAY)
    b.part("radiator_panel", lambda p: p.box((0, 0, 0), (R["thickness"], pan_len, R["fin_width"])),
           mass=R["mass_total"] / (2 * n_pan), color=C_RAD)

    core = ["compute_module", "frame", "avionics", "reaction_wheels", "laser_terminals", "power_conditioning",
            "propellant_tank", "ep_thrusters", "array_drives", "stack_interfaces"]
    deployed = [place(n) for n in core] + [place("wing_deployed"), place("wing_deployed", rot=FLIP_Y)]
    deployed += [place("radiator_panel", (0, sy * (top + (i + 0.5) * pan_len), 0)) for sy in (-1, 1) for i in range(n_pan)]
    stowed = [place(n) for n in core] + [place("wing_stowed"), place("wing_stowed", rot=FLIP_Y)]
    pitch = R["thickness"] * 2
    stowed += [place("radiator_panel", (0, 0, sz * (fz / 2 + tb / 2 + 0.05 + R["thickness"] / 2 + i * pitch)),
                     S.rot_matrix("y", 90)) for sz in (-1, 1) for i in range(n_pan)]
    counts = {n: 1 for n in core}
    counts.update(wing_deployed=2, radiator_panel=2 * n_pan)
    geometry = {"wing_length": wing_len, "roll_radius": roll_r, "radiator_panels": 2 * n_pan, "panel_length": pan_len}
    return deployed, stowed, counts, "frame", geometry


# ======================================================================================
# Concept 2: flatpack
# ======================================================================================
def build_flatpack(b: Builder, P: dict):
    cx, cy, cz = P["compute"]["size"]
    D = P["deck"]
    Lx, Lz = D["footprint"]
    h, tube, wall, g = D["height"], D["tube"], D["wall"], D["gap"]
    po, pw_ = D["post_outer"], D["post_wall"]
    eq_y0, eq_h, rad_y0 = D["eq_y0"], D["eq_h"], D["rad_y0"]
    eq_yc = eq_y0 + eq_h / 2
    W = P["wing"]
    px, pt, pz = W["pack"]
    wing_w = W["width"]
    wing_len = W["area_each"] / wing_w
    R = P["radiator"]
    n_pan, pl, pwid, th, pitch = R["n_panels"], R["panel_length"], R["panel_width"], R["thickness"], R["pitch"]
    E = P["equipment"]

    # Satellite origin: deck center at mid-height, so stowed layer spans y in [-h/2, h/2]
    y0 = -h / 2

    b.part("compute_module", lambda p: p.box((0, y0 + eq_yc, 0), (cx, cy, cz)), mass=P["compute"]["mass"], color=C_COMPUTE)

    def deck(p):
        yb = y0 + tube / 2
        for sz in (-1, 1):                                        # long sides (along X)
            p.square_tube("x", (0, yb, sz * (Lz / 2 - tube / 2)), tube, wall, Lx)
        for sx in (-1, 1):                                        # short sides and compute supports (along Z)
            p.square_tube("z", (sx * (Lx / 2 - tube / 2), yb, 0), tube, wall, Lz - 2 * tube)
            p.square_tube("z", (sx * (cx / 2 + tube / 2), yb, 0), tube, wall, Lz - 2 * tube)
        for sx in (-1, 1):                                        # corner posts carry the stack
            for sz in (-1, 1):
                p.square_tube("y", (sx * (Lx / 2 - po / 2), 0.0, sz * (Lz / 2 - po / 2)), po, pw_, h)
    b.part("deck", deck, density=D["density"], color=C_FRAME)

    # equipment in the two strips beside the compute module (|z| > cz/2), within the equipment layer
    zs = (cz / 2 + Lz / 2 - po) / 2                               # strip centerline
    ye = y0 + eq_yc
    eh = min(eq_h, 0.30)
    b.part("power_conditioning", lambda p: p.box((-0.4, ye, zs), (0.9, eh, 0.8)), mass=E["power_conditioning"], color=C_EQUIP)
    b.part("propellant_tank", lambda p: p.cylinder("x", (0.6, ye, zs), min(eh / 2, 0.14), 0.8),
           mass=E["propellant_tank"] + P["propellant"], color=C_EQUIP)
    b.part("reaction_wheels", lambda p: [p.cylinder("y", (sx * 0.7, ye, -zs + dz), 0.16, min(eh, 0.12))
                                         for sx in (-1, 1) for dz in (-0.3, 0.3)], mass=E["reaction_wheels"], color=C_EQUIP)
    b.part("avionics", lambda p: p.box((0.0, ye, -zs), (0.4, min(eh, 0.25), 0.35)), mass=E["avionics"], color=C_EQUIP)
    b.part("laser_terminals", lambda p: [p.cylinder("y", (x, ye, -zs + dz), 0.13, min(eh, 0.25))
                                         for x, dz in ((-0.4, 0.0), (0.4, 0.0), (0.0, 0.4))],
           mass=E["laser_terminals"], color=C_EQUIP)
    b.part("ep_thrusters", lambda p: [p.cylinder("x", (-cx / 2 + 0.15, ye, sz * (zs + 0.3)), 0.09, 0.24)
                                      for sz in (-1, 1)], mass=E["electric_propulsion"], color=C_EQUIP)
    b.part("array_drives", lambda p: [p.cylinder("x", (sx * (Lx / 2 - 0.08), ye, 0), min(eh / 2, 0.12), 0.12)
                                      for sx in (-1, 1)], mass=E["array_drives"], color=C_EQUIP)
    b.part("stack_interfaces", lambda p: [p.box((sx * (Lx / 2 - po / 2), sy * (h / 2 - 0.03), sz * (Lz / 2 - po / 2)),
                                                (po + 0.02, 0.06, po + 0.02))
                                          for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)],
           mass=E["stack_interfaces"], color=C_EQUIP)

    # wings: z-folded blanket packs on each side of the compute module when stowed
    pack_cx = cx / 2 + g + px / 2
    b.part("wing_stowed", lambda p: p.box((pack_cx, y0 + eq_y0 + pt / 2, 0), (px, pt, pz)), mass=W["mass_each"], color=C_ARRAY)
    root_x = Lx / 2 + 0.1

    def wing_deployed(p):
        p.box((root_x, 0, 0), (0.2, wing_w, 0.1))                                  # root hinge/drive bracket
        x0 = root_x + 0.1
        p.box((x0 + wing_len / 2, 0, 0), (wing_len, wing_w, 0.003))                 # blanket faces +Z (Sun)
        for sy in (-1, 1):
            p.cylinder("x", (x0 + wing_len / 2, sy * (wing_w / 2 + 0.06), 0), 0.06, wing_len, inner_radius=0.057)
    b.part("wing_deployed", wing_deployed, mass=W["mass_each"], color=C_ARRAY)

    # radiator panel in deployed orientation: thickness X, length Y, width Z
    b.part("radiator_panel", lambda p: p.box((0, 0, 0), (th, pl, pwid)), mass=R["mass_total"] / n_pan, color=C_RAD)

    core = ["compute_module", "deck", "power_conditioning", "propellant_tank", "reaction_wheels", "avionics",
            "laser_terminals", "ep_thrusters", "array_drives", "stack_interfaces"]
    half = n_pan // 2
    deployed = [place(n) for n in core] + [place("wing_deployed"), place("wing_deployed", rot=FLIP_Y)]
    deployed += [place("radiator_panel", (0, sy * (h / 2 + (i + 0.5) * pl), 0)) for sy in (-1, 1) for i in range(half)]
    stowed = [place(n) for n in core] + [place("wing_stowed"), place("wing_stowed", rot=FLIP_Y)]
    to_flat = S.rot_matrix("z", 90)     # panel length (local Y) -> X, thickness (local X) -> Y
    stowed += [place("radiator_panel", (0, y0 + rad_y0 + th / 2 + i * pitch, 0), to_flat) for i in range(n_pan)]
    counts = {n: 1 for n in core}
    counts.update(wing_deployed=2, radiator_panel=n_pan)
    geometry = {"wing_length": wing_len, "wing_width": wing_w, "radiator_panels": n_pan, "panel_length": pl,
                "panel_width": pwid, "layer_height": h}
    return deployed, stowed, counts, "deck", geometry


BUILDERS = {"tower": build_tower, "flatpack": build_flatpack}


def build(sw, concept: str, P: dict):
    print(f"=== {concept} ===")
    b = Builder(sw, concept)
    S.close_matching(sw, b.out, untitled=False)
    deployed, stowed, counts, structure, geometry = BUILDERS[concept](b, P)

    print("Assembling deployed / stowed")
    dep, _ = b.assembly("satellite_deployed", deployed)
    dep_mp, dep_box = dep.mass_props(), dep.box()
    imgs = [b.image(dep, "satellite_deployed")]
    sto, sto_path = b.assembly("satellite_stowed", stowed)
    sto_mp, sto_box = sto.mass_props(), sto.box()
    imgs.append(b.image(sto, "satellite_stowed"))

    print("Packing Starship")
    Dbay, Hbay = P["bay"]["diameter"], P["bay"]["height"]
    pack = sats_per_flight(sto_box["size"], Dbay, Hbay)
    b.part("starship_bay", lambda p: p.cylinder("y", (0, Hbay / 2, 0), Dbay / 2 + 0.05, Hbay, inner_radius=Dbay / 2),
           mass=1.0, color=C_BAY)
    c = [(lo + hi) / 2 for lo, hi in zip(sto_box["min"], sto_box["max"])]
    sy = sto_box["size"][1]
    stack = [place("starship_bay")]
    for k in range(pack["layers"]):
        for (x, z, rotated) in pack["layout"]:
            rc = [c[2], c[1], -c[0]] if rotated else c
            target = (x, k * sy + sy / 2, z)
            stack.append(place(sto_path, tuple(t - r for t, r in zip(target, rc)), S.rot_matrix("y", 90) if rotated else None))
    st, _ = b.assembly("starship_stack", stack)
    imgs.append(b.image(st, "starship_stack"))

    out = {
        "concept": concept,
        "params": P,
        "part_masses": {n: b.masses[n] * k for n, k in counts.items()},
        "structure_part": structure,
        "geometry": geometry,
        "deployed": {**dep_mp, "size": dep_box["size"]},
        "stowed": {**sto_mp, "size": sto_box["size"]},
        "stack": {k: v for k, v in pack.items() if k != "layout"},
        "images": [os.path.relpath(i, HERE) for i in imgs if i],
    }
    with open(os.path.join(b.out, "mass_props.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"Deployed {dep_mp['mass']:,.0f} kg, span {dep_box['size'][0]:.1f} × {dep_box['size'][1]:.1f} m;  "
          f"stowed {' × '.join(f'{v:.2f}' for v in sto_box['size'])} m;  "
          f"Starship {pack['per_layer']} × {pack['layers']} = {pack['total']}")
    S.close_matching(sw, b.out, untitled=False)
    return out


def main():
    with open(os.path.join(HERE, "params.json")) as f:
        params = json.load(f)
    concepts = sys.argv[1:] or list(params)
    sw = S.connect()
    for c in concepts:
        build(sw, c, params[c])


if __name__ == "__main__":
    main()
