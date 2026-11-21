"""Build the Part 2 reference satellite in SolidWorks.

Run from the repo root, with SolidWorks open:
    .venv\\Scripts\\python.exe cad\\build_satellite.py              # both concepts
    .venv\\Scripts\\python.exe cad\\build_satellite.py flatpack     # just one

Input:  cad/params.json, written by the notebook (sizes and masses from the sizing model).
Output: cad/<concept>/ with the parts, three assemblies (satellite_deployed,
        satellite_stowed, starship_stack), a picture of each, and mass_props.json,
        which the notebook reads back.

The satellite is the same in orbit either way. The two concepts differ in how it folds
for launch:
    tower     First pass. The bus stands upright in the bay, the solar wings are rolled
              up, and the radiator panels are stacked against its sides.
    flatpack  Starlink-style. Each satellite is a wide, thin plate, and the plates are
              stacked along the bay. Corner posts carry the weight of the stack.

How mass is modeled:
    Structure (frame or deck) is drawn as real carbon-fiber tubes, so its mass comes
    from the geometry. Everything else is a simple placeholder shape given its target
    mass from the notebook. That is enough for total mass, stowed size and inertia.

Axes: +X = direction of travel, +Y = zenith (the Starship axis when stowed), +Z = toward the Sun.
"""
import json
import math
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import sw_api
from packing import sats_per_flight
from sw_api import Box, Cylinder, SquareTube

HERE = Path(__file__).parent

# Display colors (r, g, b)
DARK_GRAY, BLACK, GOLD = (0.25, 0.25, 0.28), (0.15, 0.15, 0.15), (0.75, 0.62, 0.25)
BLUE, WHITE, LIGHT_GRAY = (0.10, 0.20, 0.55), (0.92, 0.92, 0.90), (0.80, 0.80, 0.82)

# Appearances, for photoreal rendering in SolidWorks Visualize (cad/render/README.md).
# Paths are inside SolidWorks' own appearance library, matched to the display colors above.
APPEARANCES = {
    DARK_GRAY: "painted/powder coat/dark powdercoat.p2m",       # compute module housing
    BLACK: "plastic/composite/carbon fiber eproxy 2d.p2m",      # deck / frame tubes
    GOLD: "metal/gold/matte gold.p2m",                          # gold insulation blanket over the equipment
    WHITE: "plastic/low gloss/white low gloss plastic.p2m",     # white radiator paint
    BLUE: "plastic/composite/carbon fiber eproxy 2d.p2m",       # wing booms and hinges; the blanket gets cells
}
CELL_PARTS = {"wing_deployed", "wing_stowed"}   # solar cells go on their big faces toward and away from the Sun
SOLAR_TEXTURE = HERE / "render" / "textures" / "solar_cells_color.png"   # from cad/render/make_solar_texture.py
SOLAR_TILE_M = 0.66                                                      # one texture tile covers 0.66 m x 0.66 m
SUN_DIRECTION = (0, 0, 1)       # dawn-dusk orbit: the Sun is along +Z (the deployed assembly's only light)

SIDES = (-1, 1)                         # mirror a shape to both sides of the satellite
FLIPPED = sw_api.rotation("y", 180)     # turns the +X wing into the -X wing


@dataclass
class PartSpec:
    """One part: its shapes, its color, and either a target mass or a material density."""
    shapes: list
    color: tuple
    mass: float | None = None       # kg, spread evenly over the shapes
    density: float | None = None    # kg/m³; the mass then follows from the geometry


@dataclass
class Design:
    """A packaging concept: its parts, and where each one sits when deployed and stowed.
    A placement is (part name, position, rotation)."""
    parts: dict[str, PartSpec]
    deployed: list
    stowed: list
    structure: str      # name of the part that is the primary structure
    geometry: dict      # a few derived dimensions, passed back to the notebook


def at(name, position=(0, 0, 0), rotation=None):
    return (name, position, rotation)


def deployed_wing(root_fitting, blanket_start_x, length, width):
    """The +X solar wing, unrolled: a 3 mm blanket facing the Sun (+Z), held flat by a
    hollow boom along each long edge."""
    mid_x = blanket_start_x + length / 2
    booms = [Cylinder("x", (mid_x, side * (width / 2 + 0.06), 0), 0.06, length, inner_radius=0.057)
             for side in SIDES]
    return [root_fitting, Box((mid_x, 0, 0), (length, width, 0.003)), *booms]


def deployed_layout(bus, fin_root_y, panel_length, panels_per_fin):
    """On orbit, both concepts look alike: the bus in the middle, a solar wing out each
    side along ±X, and a radiator fin of hinged panels running up and down along ±Y."""
    wings = [at("wing_deployed"), at("wing_deployed", rotation=FLIPPED)]
    fins = [at("radiator_panel", (0, side * (fin_root_y + (i + 0.5) * panel_length), 0))
            for side in SIDES for i in range(panels_per_fin)]
    return [at(name) for name in bus] + wings + fins


# ============================================================================================
# Concept 1: tower
# ============================================================================================
def tower(P: dict) -> Design:
    cx, cy, cz = P["compute"]["size"]
    fx, fy, fz = P["frame"]["size"]             # frame size, between tube centerlines
    tube, wall = P["frame"]["tube_outer"], P["frame"]["tube_wall"]
    W, R, E = P["wing"], P["radiator"], P["equipment"]

    wing_length = W["area_each"] / W["width"]
    roll_radius = math.sqrt(W["stowed_volume_each"] / (math.pi * W["width"]))   # wing rolled into a cylinder
    roll_x = fx / 2 + tube / 2 + 0.05 + roll_radius                             # roll sits just outside the frame

    # Each radiator fin is split into equal panels short enough to fold against the bus.
    fin_length = R["panel_area_total"] / 2 / R["fin_width"]
    panels_per_fin = math.ceil(fin_length / R["panel_max_length"] - 1e-9)
    panel_length = fin_length / panels_per_fin

    # Bus equipment goes in the two bays above and below the compute module.
    y_top = (cy / 2 + fy / 2) / 2
    y_bottom = -y_top
    outside_x = fx / 2 + tube / 2               # outer face of the frame

    frame = [SquareTube("y", (sx * fx / 2, 0, sz * fz / 2), tube, wall, fy + tube)     # 4 uprights
             for sx in SIDES for sz in SIDES]
    for y in (-fy / 2, 0, fy / 2):                                                      # 3 rings of cross-members
        frame += [SquareTube("x", (0, y, sz * fz / 2), tube, wall, fx - tube) for sz in SIDES]
        frame += [SquareTube("z", (sx * fx / 2, y, 0), tube, wall, fz - tube) for sx in SIDES]

    equipment = lambda mass, *shapes: PartSpec(list(shapes), GOLD, mass=mass)
    parts = {
        "compute_module": PartSpec([Box((0, 0, 0), (cx, cy, cz))], DARK_GRAY, mass=P["compute"]["mass"]),
        "frame": PartSpec(frame, BLACK, density=P["frame"]["density"]),
        "avionics": equipment(E["avionics"], Box((0, y_top + 0.2, -0.35), (0.4, 0.3, 0.3))),
        "reaction_wheels": equipment(E["reaction_wheels"], *[
            Cylinder("y", (sx * 0.4, y_top - 0.15, sz * 0.35), 0.16, 0.12) for sx in SIDES for sz in SIDES]),
        "laser_terminals": equipment(E["laser_terminals"], *[
            Cylinder("y", center, 0.13, 0.3)
            for center in ((0.45, y_top + 0.25, 0.4), (-0.45, y_top + 0.25, 0.4), (0.45, y_bottom - 0.25, -0.4))]),
        "power_conditioning": equipment(E["power_conditioning"], Box((0.25, y_bottom, 0), (0.7, 0.45, 0.8))),
        "propellant_tank": equipment(E["propellant_tank"] + P["propellant"],     # tank and its propellant
                                     Cylinder("z", (-0.4, y_bottom, 0), 0.2, 0.7)),
        "ep_thrusters": equipment(E["electric_propulsion"], *[
            Cylinder("x", (-(outside_x + 0.12), y_bottom, sz * 0.5), 0.09, 0.24) for sz in SIDES]),
        "array_drives": equipment(E["array_drives"], *[
            Cylinder("x", (sx * (outside_x + 0.03), 0, 0), 0.14, 0.06) for sx in SIDES]),
        "stack_interfaces": equipment(E["stack_interfaces"], *[
            Box((sx * fx / 2, sy * (fy / 2 - 0.1), sz * fz / 2), (0.12, 0.08, 0.12))
            for sx in SIDES for sy in SIDES for sz in SIDES]),
    }
    bus = list(parts)

    spool = Cylinder("y", (roll_x, 0, 0), 0.12, W["width"] + 0.1)
    parts["wing_deployed"] = PartSpec(deployed_wing(spool, roll_x + 0.15, wing_length, W["width"]),
                                      BLUE, mass=W["mass_each"])
    parts["wing_stowed"] = PartSpec([Cylinder("y", (roll_x, 0, 0), roll_radius, W["width"] + 0.1)],
                                    BLUE, mass=W["mass_each"])
    # Drawn in its deployed orientation: thin along X, long along Y, wide along Z.
    parts["radiator_panel"] = PartSpec([Box((0, 0, 0), (R["thickness"], panel_length, R["fin_width"]))],
                                       WHITE, mass=R["mass_total"] / (2 * panels_per_fin))

    # Stowed: wings rolled beside the bus, radiator panels stacked flat against its ±Z faces.
    first_panel_z = fz / 2 + tube / 2 + 0.05 + R["thickness"] / 2
    stowed = [at(name) for name in bus] + [at("wing_stowed"), at("wing_stowed", rotation=FLIPPED)]
    stowed += [at("radiator_panel", (0, 0, side * (first_panel_z + i * 2 * R["thickness"])), sw_api.rotation("y", 90))
               for side in SIDES for i in range(panels_per_fin)]

    return Design(
        parts=parts,
        deployed=deployed_layout(bus, fy / 2 + tube / 2, panel_length, panels_per_fin),
        stowed=stowed,
        structure="frame",
        geometry={"wing_length": wing_length, "roll_radius": roll_radius,
                  "radiator_panels": 2 * panels_per_fin, "panel_length": panel_length},
    )


# ============================================================================================
# Concept 2: flatpack
#
# One stowed satellite is one layer of the stack. Side view, looking along Z:
#
#     post |  =========== radiator panels, folded flat ===========  | post
#     tube [] [ folded wing ] [] [ compute trays ] [] [ folded wing ] [] tube   <- equipment layer
#
# Everything sits inside the depth of the deck frame, not on top of it, which keeps the
# layer thin. The compute trays hang between two rails ([] either side of them). The rest
# of the bus equipment sits beside the trays, toward ±Z.
# ============================================================================================
def flatpack(P: dict) -> Design:
    cx, cy, cz = P["compute"]["size"]
    D, W, R, E = P["deck"], P["wing"], P["radiator"], P["equipment"]
    Lx, Lz = D["footprint"]
    height = D["height"]                        # full layer height = spacing between satellites in the stack
    tube, wall, post, gap = D["tube"], D["wall"], D["post_outer"], D["gap"]

    # The origin is at the middle of the layer, so a stowed satellite spans y = ±height/2.
    floor = -height / 2
    equipment_y = floor + D["eq_h"] / 2                     # mid-height of the equipment layer
    radiator_floor = floor + D["rad_y0"]
    post_x, post_z = Lx / 2 - post / 2, Lz / 2 - post / 2   # corner post centerlines

    deck_y = floor + tube / 2
    deck = [SquareTube("x", (0, deck_y, sz * (Lz / 2 - tube / 2)), tube, wall, Lx) for sz in SIDES]    # long edges
    for sx in SIDES:
        deck += [SquareTube("z", (sx * (Lx / 2 - tube / 2), deck_y, 0), tube, wall, Lz - 2 * tube),    # short edges
                 SquareTube("z", (sx * (cx / 2 + tube / 2), deck_y, 0), tube, wall, Lz - 2 * tube)]    # compute rails
    deck += [SquareTube("y", (sx * post_x, 0, sz * post_z), post, D["post_wall"], height)              # corner posts
             for sx in SIDES for sz in SIDES]

    # Equipment sits in the two strips beside the compute trays, each item shrunk to fit the layer.
    strip_z = (cz / 2 + Lz / 2 - post) / 2      # centerline of the +Z strip
    fit = lambda dimension: min(dimension, D["eq_h"])
    drive_radius = min(0.12, (D["eq_h"] - tube) / 2)
    equipment = lambda mass, *shapes: PartSpec(list(shapes), GOLD, mass=mass)
    parts = {
        "compute_module": PartSpec([Box((0, equipment_y, 0), (cx, cy, cz))], DARK_GRAY, mass=P["compute"]["mass"]),
        "deck": PartSpec(deck, BLACK, density=D["density"]),
        "power_conditioning": equipment(E["power_conditioning"], Box((-0.4, equipment_y, strip_z), (0.9, fit(0.30), 0.8))),
        "propellant_tank": equipment(E["propellant_tank"] + P["propellant"],     # tank and its propellant
                                     Cylinder("x", (0.6, equipment_y, strip_z), fit(0.28) / 2, 0.8)),
        "reaction_wheels": equipment(E["reaction_wheels"], *[
            Cylinder("y", (sx * 0.7, equipment_y, -strip_z + dz), 0.16, fit(0.12)) for sx in SIDES for dz in (-0.3, 0.3)]),
        "avionics": equipment(E["avionics"], Box((0, equipment_y, -strip_z), (0.4, fit(0.25), 0.35))),
        "laser_terminals": equipment(E["laser_terminals"], *[
            Cylinder("y", (x, equipment_y, -strip_z + dz), 0.13, fit(0.25)) for x, dz in ((-0.4, 0), (0.4, 0), (0, 0.4))]),
        "ep_thrusters": equipment(E["electric_propulsion"], *[
            Cylinder("x", (-cx / 2 + 0.15, equipment_y, sz * (strip_z + 0.3)), 0.09, 0.24) for sz in SIDES]),
        "array_drives": equipment(E["array_drives"], *[                          # on top of the end tubes
            Cylinder("x", (sx * (Lx / 2 - tube / 2), floor + tube + drive_radius, 0), drive_radius, tube) for sx in SIDES]),
        "stack_interfaces": equipment(E["stack_interfaces"], *[                  # caps on both ends of each post
            Box((sx * post_x, sy * (height / 2 - 0.03), sz * post_z), (post + 0.02, 0.06, post + 0.02))
            for sx in SIDES for sy in SIDES for sz in SIDES]),
    }
    bus = list(parts)

    # Each wing folds like a concertina into a flat pack, between a compute rail and the end of the deck.
    pack_x, pack_thickness, pack_z = W["pack"]
    wing_length = W["area_each"] / W["width"]
    root_x = Lx / 2 + 0.1                       # the deployed wing starts just beyond the deck edge
    parts["wing_stowed"] = PartSpec(
        [Box((cx / 2 + tube + gap + pack_x / 2, floor + pack_thickness / 2, 0), (pack_x, pack_thickness, pack_z))],
        BLUE, mass=W["mass_each"])
    hinge = Box((root_x, 0, 0), (0.2, W["width"], 0.1))
    parts["wing_deployed"] = PartSpec(deployed_wing(hinge, root_x + 0.1, wing_length, W["width"]),
                                      BLUE, mass=W["mass_each"])
    # Drawn in its deployed orientation: thin along X, long along Y, wide along Z.
    n_panels, panel_length, thickness = R["n_panels"], R["panel_length"], R["thickness"]
    parts["radiator_panel"] = PartSpec([Box((0, 0, 0), (thickness, panel_length, R["panel_width"]))],
                                       WHITE, mass=R["mass_total"] / n_panels)

    # Stowed: wings folded inside the deck frame, radiator panels laid flat in a stack on top.
    lay_flat = sw_api.rotation("z", 90)
    stowed = [at(name) for name in bus] + [at("wing_stowed"), at("wing_stowed", rotation=FLIPPED)]
    stowed += [at("radiator_panel", (0, radiator_floor + thickness / 2 + i * R["pitch"], 0), lay_flat)
               for i in range(n_panels)]

    return Design(
        parts=parts,
        deployed=deployed_layout(bus, height / 2, panel_length, n_panels // 2),
        stowed=stowed,
        structure="deck",
        geometry={"wing_length": wing_length, "wing_width": W["width"], "radiator_panels": n_panels,
                  "panel_length": panel_length, "panel_width": R["panel_width"], "layer_height": height},
    )


CONCEPTS = {"tower": tower, "flatpack": flatpack}


# ============================================================================================
# Driving SolidWorks
# ============================================================================================
def solar_cell_appearance(folder: Path) -> Path:
    """Write a SolidWorks appearance that tiles the solar-cell texture: a glossy surface (the
    cells sit under cover glass). The texture path inside has to be absolute, so the file is
    written fresh on each build."""
    if not SOLAR_TEXTURE.exists():
        raise FileNotFoundError(f"{SOLAR_TEXTURE} is missing: run cad/render/make_solar_texture.py first")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "solar_cells.p2m"
    path.write_text("\n".join([
        '"sw_shader" texture',
        f'color texture "color_texname" "{SOLAR_TEXTURE.resolve()}"',
        '"col1" 1 1 1', '"num_cols" 0', '"diffuse_factor" 1',
        '"roughness" 0.05', '"blurryReflections" on', '"reflectivity" 0.1', '"mtl_ior" 1.5',
        '"specular_color" 1 1 1', '"specular_factor" 0.8',
        f'"initTextureWidth" {SOLAR_TILE_M}', f'"initTextureHeight" {SOLAR_TILE_M}',
        '"doubleSided" on', '"transparency" 0', '"swP2M" on', '',
    ]))
    return path


def make_part(sw, spec: PartSpec, path: Path, transparency: float = 0.0, name: str = "") -> tuple[str, float]:
    """Draw and save one part. Returns its file path and mass [kg]."""
    part = sw_api.Part(sw)
    for shape in spec.shapes:
        part.add(shape)
    if spec.mass is not None:
        part.set_mass(spec.mass)
    else:
        part.set_density(spec.density)
    part.set_color(spec.color, transparency)
    if spec.color in APPEARANCES:
        part.set_appearance(Path(sw_api.appearance_library(sw)) / APPEARANCES[spec.color])
    if name in CELL_PARTS:
        cells = part.flat_faces("z", min_area=1.0)
        if cells:
            part.set_appearance(solar_cell_appearance(path.parent.parent / "appearances"), SOLAR_TILE_M, cells)
    return part.save(path), part.mass_properties()["mass"]


def make_assembly(sw, files: dict, placements: list, path: Path, image: Path, sun: bool = False):
    """Place parts, then save the assembly and a picture of it. A placement may name a
    part in `files` or give a file path directly. `sun` replaces the default lights with
    the Sun at +Z, for rendering in Visualize."""
    assembly = sw_api.Assembly(sw)
    for name, position, rotation in placements:
        assembly.add(files.get(name, name), position, rotation)
    if sun:
        assembly.set_sun(SUN_DIRECTION)
    return assembly, assembly.save(path), assembly.save_image(image)


def stack_in_bay(stowed_box: dict, stowed_file: str, bay: dict) -> tuple[dict, list]:
    """Fill the payload bay with stowed satellites. Returns the packing result and the
    placements for the stack assembly."""
    packing = sats_per_flight(stowed_box["size"], bay["profile"])
    # The stowed satellite's origin is not at the center of its bounding box, so each copy
    # is shifted to put the box center (not the origin) on its slot in the bay.
    cx, cy, cz = [(low + high) / 2 for low, high in zip(stowed_box["min"], stowed_box["max"])]
    quarter_turn = sw_api.rotation("y", 90)
    placements = [at("starship_bay")]
    for layer_floor, layer in packing["layout"]:
        for x, z, turned in layer:
            slot = (x, layer_floor + stowed_box["size"][1] / 2, z)
            center = (cz, cy, -cx) if turned else (cx, cy, cz)      # box center after the quarter turn
            position = tuple(s - c for s, c in zip(slot, center))
            placements.append(at(stowed_file, position, quarter_turn if turned else None))
    return packing, placements


def build(sw, concept: str, P: dict) -> dict:
    print(f"=== {concept} ===")
    out = HERE / concept
    sw_api.close_documents_in(sw, out)      # release files left open by an earlier build
    design = CONCEPTS[concept](P)

    # 1. Parts
    files, masses = {}, {}
    for name, spec in design.parts.items():
        files[name], masses[name] = make_part(sw, spec, out / "parts" / f"{name}.SLDPRT", name=name)
        print(f"  {name:22s} {masses[name]:9.1f} kg")

    # 2. The satellite, deployed and stowed
    images = []
    results = {}
    for state, placements in (("deployed", design.deployed), ("stowed", design.stowed)):
        assembly, file, image = make_assembly(sw, files, placements, out / f"satellite_{state}.SLDASM",
                                              out / "images" / f"satellite_{state}.jpg", sun=state == "deployed")
        results[state] = dict(file=file, box=assembly.bounding_box(), mass=assembly.mass_properties())
        images.append(image)
    deployed, stowed = results["deployed"], results["stowed"]

    # 3. As many stowed satellites as fit in Starship's payload bay. The bay is drawn
    #    see-through, as a stack of rings that follow its profile (so the taper looks stepped).
    bay = P["bay"]
    bay_wall = [Cylinder("y", (0, (h0 + h1) / 2, 0), (r0 + r1) / 2 + 0.05, h1 - h0, inner_radius=(r0 + r1) / 2)
                for (h0, r0), (h1, r1) in zip(bay["profile"], bay["profile"][1:])]
    files["starship_bay"], _ = make_part(sw, PartSpec(bay_wall, LIGHT_GRAY, mass=1.0),
                                         out / "parts" / "starship_bay.SLDPRT", transparency=0.75)
    packing, placements = stack_in_bay(stowed["box"], stowed["file"], bay)
    _, _, image = make_assembly(sw, files, placements, out / "starship_stack.SLDASM",
                                out / "images" / "starship_stack.jpg")
    images.append(image)

    # 4. Results for the notebook
    part_counts = Counter(name for name, _, _ in design.deployed)
    summary = {
        "concept": concept,
        "params": P,        # lets the notebook check the model was built from its current inputs
        "part_masses": {name: masses[name] * count for name, count in part_counts.items()},
        "structure_part": design.structure,
        "geometry": design.geometry,
        "deployed": {**deployed["mass"], "size": deployed["box"]["size"]},
        "stowed": {**stowed["mass"], "size": stowed["box"]["size"]},
        "stack": {key: value for key, value in packing.items() if key != "layout"},
        "images": [os.path.relpath(image, HERE) for image in images],
    }
    (out / "mass_props.json").write_text(json.dumps(summary, indent=2))

    span_x, span_y, _ = deployed["box"]["size"]
    print(f"Deployed: {deployed['mass']['mass']:,.0f} kg, {span_x:.1f} m across the wings, {span_y:.1f} m across the fins")
    print("Stowed:   " + " × ".join(f"{v:.2f}" for v in stowed["box"]["size"]) + " m")
    print(f"Starship: {packing['total']} satellites in {packing['layers']} layers")
    sw_api.close_documents_in(sw, out)
    return summary


def main():
    params = json.loads((HERE / "params.json").read_text())
    sw = sw_api.connect()
    for concept in sys.argv[1:] or params:
        build(sw, concept, params[concept])


if __name__ == "__main__":
    main()
