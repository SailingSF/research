"""Detailed radiator panel: the part the drawing (make_drawing.py) documents.

The satellite model (build_satellite.py) treats each radiator panel as a solid block with a
target mass. This script designs the panel inside that block, as a real sandwich panel,
so it can be drawn and toleranced:

    face sheet  0.25 mm aluminum, both sides radiate (white paint / OSR on top)
    core        vented aluminum honeycomb, 24.5 mm
    flow tubes  aluminum extrusions (tube + web + two flanges) at 150 mm pitch, bonded to both face
                sheets, carrying the pumped coolant loop across the panel
    manifolds   supply and return tubes along the two long edges; their stubs stick out of
                both hinge edges, where flex hoses jump the hinge to the next panel
    closeouts   aluminum C-channels around the edge
    inserts     16 potted M6 inserts for the hinge fittings (same pattern on both hinge
                edges, so one part number serves every panel on the satellite)
    bushings    6 through-bushings for the launch hold-down rods that clamp the stack

Run from the repo root with SolidWorks open:
    .venv\\Scripts\\python.exe cad\\radiator\\build_radiator.py

Frame (mm on the drawing, meters in SolidWorks): origin at the datum corner.
    X = panel length (hinge edge to hinge edge), Y = panel width, Z = thickness.
    Datum A = the Z=0 face, datum B = the X=0 hinge edge, datum C = the Y=0 edge.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import sw_api                                    # noqa: E402
from sw_api import Box, Cylinder                 # noqa: E402

OUT = HERE / "parts"

# ==== Design parameters [mm] ===============================================================
# The panel envelope and count come from the notebook (via cad/params.json), so the drawn panel
# is always the one the satellite carries. Length is rounded to an even mm so the tube pattern
# below lands on whole millimeters.
_FLATPACK = json.loads((HERE.parent / "params.json").read_text())["flatpack"]["radiator"]
L = 2.0 * round(_FLATPACK["panel_length"] * 1000 / 2)      # panel length, hinge edge to hinge edge
W = float(round(_FLATPACK["panel_width"] * 1000))           # panel width
T = float(round(_FLATPACK["thickness"] * 1000, 1))          # panel thickness
N_PANELS = _FLATPACK["n_panels"]                            # identical panels per satellite
SKIN = 0.25                           # face sheet thickness (notebook: RADIATOR_SKIN_THICKNESS_M)
CORE_H = T - 2 * SKIN                 # the core and everything bonded between the skins
ZC = T / 2                            # panel mid-plane

CLOSEOUT_WALL, CLOSEOUT_FLANGE = 1.0, 12.0     # C-channel around the edge

TUBE_PITCH = 150.0                             # flow tubes run along Y (notebook: RADIATOR_TUBE_PITCH_M)
TUBE_EDGE_MIN = 100.0                          # first tube at least this far from a hinge edge (clears the inserts)
N_TUBES = int((L - 2 * TUBE_EDGE_MIN) // TUBE_PITCH) + 1
N_TUBES -= N_TUBES % 2                         # even, so the panel's center line falls between two tubes
TUBE_X0 = (L - (N_TUBES - 1) * TUBE_PITCH) / 2     # first tube; the pattern is centered
TUBE_X = [TUBE_X0 + k * TUBE_PITCH for k in range(N_TUBES)]
EXTR_FLANGE_W, EXTR_FLANGE_T = 20.0, 1.0       # flow tube extrusion: flanges bond to the skins
EXTR_WEB_T = 1.2
EXTR_TUBE_OD, EXTR_BORE = 8.0, 4.93
STUB_OD = 6.35                                 # 1/4 in tube, 0.71 wall: joins extrusion to manifold
TUBE_CHANNEL = EXTR_FLANGE_W + 2.0             # core is cut back 1 mm either side of a flange

MANIFOLD_OD, MANIFOLD_WALL = 15.88, 0.89       # 5/8 in x 0.035 in tube
MANIFOLD_Y = (60.0, W - 60.0)                  # supply, return
MANIFOLD_STICKOUT = 25.0                       # beyond each hinge edge, for the flex hose fitting
EXTR_Y0 = 80.0                                 # extrusions run from Y=80 to Y=W-80

INSERT_OD, INSERT_TAP = 12.0, 5.0              # potted thru-insert, M6x1.0 (5.0 = tap drill)
HINGE_Y = (1025.0, 3675.0)                     # two hinge fittings per hinge edge (insert rows land on 1000/1050, 3650/3700)
HINGE_DX = (25.0, 65.0)                        # insert rows, measured in from each hinge edge
HINGE_DY = 25.0                                # inserts at hinge Y +/- this

BUSHING_OD, BUSHING_ID = 20.0, 12.0            # hold-down rod bushing
HOLDDOWN_X = (TUBE_X0 + TUBE_PITCH / 2, L / 2,   # midway between flow tubes
              L - TUBE_X0 - TUBE_PITCH / 2)
HOLDDOWN_Y = (300.0, W - 300.0)

# Densities [kg/m^3]
AL = 2700.0
AL_7075 = 2810.0
CORE_DENSITY = 32.0                            # 2.0 lb/ft^3 aluminum honeycomb
# Not modeled as solids; added to the mass estimate:
ADHESIVE_KG_M2 = 0.15                          # per bondline (two bondlines)
COATING_KG_M2 = 0.10                           # per radiating face (two faces)
AMMONIA_KG_L = 0.56                            # liquid ammonia near 60 C


def m(*mm):
    """mm -> m for SolidWorks."""
    return tuple(v / 1000 for v in mm) if len(mm) > 1 else mm[0] / 1000


def hinge_inserts():
    return [(x, y + s * HINGE_DY) for edge in (0.0, L) for dx in HINGE_DX
            for x in [abs(edge - dx)] for y in HINGE_Y for s in (-1, 1)]


def holddowns():
    return [(x, y) for x in HOLDDOWN_X for y in HOLDDOWN_Y]


def box(x0, x1, y0, y1, z0, z1):
    return Box(m((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), m(x1 - x0, y1 - y0, z1 - z0))


def punch(part, z0, z1):
    """Holes for the inserts and bushings through a layer from z0 to z1."""
    for x, y in hinge_inserts():
        part.cut(Cylinder("z", m(x, y, (z0 + z1) / 2), m(INSERT_OD / 2), m(z1 - z0 + 1)))
    for x, y in holddowns():
        part.cut(Cylinder("z", m(x, y, (z0 + z1) / 2), m(BUSHING_OD / 2), m(z1 - z0 + 1)))


# ==== Parts (each in its own local frame; see placements below) ============================
def face_sheet(p):
    p.add(box(0, L, 0, W, 0, SKIN))
    punch(p, 0, SKIN)
    return AL_7075, "FACE SHEET", "AL 7075-T6 SHEET, 0.25 THK"


def core(p):
    z0, z1 = SKIN, T - SKIN
    inner = CLOSEOUT_FLANGE                                        # core starts where the closeout flanges end
    x0, x1, y0, y1 = inner, L - inner, inner, W - inner
    half_channel = 10.0                                            # manifold channel half width
    p.add(box(x0, x1, y0, MANIFOLD_Y[0] - half_channel, z0, z1))   # strip outside each manifold
    p.add(box(x0, x1, MANIFOLD_Y[1] + half_channel, y1, z0, z1))
    ya, yb = MANIFOLD_Y[0] + half_channel, MANIFOLD_Y[1] - half_channel
    edges = [x0] + [e for x in TUBE_X for e in (x - TUBE_CHANNEL / 2, x + TUBE_CHANNEL / 2)] + [x1]
    for xa, xb in zip(edges[::2], edges[1::2]):                    # strips between flow tubes
        p.add(box(xa, xb, ya, yb, z0, z1))
    punch(p, z0, z1)
    return CORE_DENSITY, "HONEYCOMB CORE", "AL 5056 HEX CORE 1/4-.001, 2.0 PCF, VENTED"


def closeout_long(p):
    """Along X, web on the outside edge (local Y=0), flanges pointing +Y."""
    channel(p, L, along="x")
    return AL, "CLOSEOUT, LONG EDGE", "AL 6061-T6 C-CHANNEL 24.5 x 12 x 1.0"


def closeout_short(p):
    """Along Y on a hinge edge, web at local X=0, flanges pointing +X; holes pass the manifolds."""
    channel(p, W - 2 * CLOSEOUT_WALL, along="y", start=CLOSEOUT_WALL)
    for y in MANIFOLD_Y:
        p.cut(Cylinder("x", m(CLOSEOUT_WALL / 2, y, ZC), m(MANIFOLD_OD / 2 + 0.3), m(CLOSEOUT_WALL + 2)))
    return AL, "CLOSEOUT, HINGE EDGE", "AL 6061-T6 C-CHANNEL 24.5 x 12 x 1.0"


def channel(p, length, along, start=0.0):
    z0, z1 = SKIN, T - SKIN
    if along == "x":
        p.add(box(start, start + length, 0, CLOSEOUT_WALL, z0, z1))                         # web
        p.add(box(start, start + length, 0, CLOSEOUT_FLANGE, z0, z0 + CLOSEOUT_WALL))       # flanges
        p.add(box(start, start + length, 0, CLOSEOUT_FLANGE, z1 - CLOSEOUT_WALL, z1))
    else:
        p.add(box(0, CLOSEOUT_WALL, start, start + length, z0, z1))
        p.add(box(0, CLOSEOUT_FLANGE, start, start + length, z0, z0 + CLOSEOUT_WALL))
        p.add(box(0, CLOSEOUT_FLANGE, start, start + length, z1 - CLOSEOUT_WALL, z1))


def manifold(p):
    """Along X through both hinge edges, local Y=0."""
    length = L + 2 * MANIFOLD_STICKOUT
    p.add(Cylinder("x", m(L / 2, 0, ZC), m(MANIFOLD_OD / 2), m(length), m(MANIFOLD_OD / 2 - MANIFOLD_WALL)))
    return AL, "MANIFOLD TUBE", "AL 6061-T6 TUBE 15.88 OD x 0.89 WALL"


def flow_tube(p):
    """One extrusion along Y at local X=0, with a stub into each manifold."""
    z0, z1 = SKIN, T - SKIN
    y0, y1 = EXTR_Y0, W - EXTR_Y0
    p.add(box(-EXTR_FLANGE_W / 2, EXTR_FLANGE_W / 2, y0, y1, z0, z0 + EXTR_FLANGE_T))
    p.add(box(-EXTR_FLANGE_W / 2, EXTR_FLANGE_W / 2, y0, y1, z1 - EXTR_FLANGE_T, z1))
    p.add(box(-EXTR_WEB_T / 2, EXTR_WEB_T / 2, y0, y1, z0, z1))
    p.add(Cylinder("y", m(0, W / 2, ZC), m(EXTR_TUBE_OD / 2), m(y1 - y0)))
    p.cut(Cylinder("y", m(0, W / 2, ZC), m(EXTR_BORE / 2), m(y1 - y0 + 2)))
    manifold_inner = MANIFOLD_OD / 2 - MANIFOLD_WALL
    for ym, sign in ((MANIFOLD_Y[0], 1), (MANIFOLD_Y[1], -1)):     # stubs reach the manifold bore
        ya = ym + sign * manifold_inner
        yb = y0 if sign > 0 else y1
        p.add(Cylinder("y", m(0, (ya + yb) / 2, ZC), m(STUB_OD / 2), m(abs(yb - ya)), m(EXTR_BORE / 2)))
    return AL, "FLOW TUBE EXTRUSION", "AL 6063-T6 EXTRUSION, INTEGRAL TUBE"


def insert(p):
    p.add(Cylinder("z", m(0, 0, ZC), m(INSERT_OD / 2), m(T), m(INSERT_TAP / 2)))
    return AL, "INSERT, POTTED, THRU", "M6x1.0, AL, POTTED (EPOXY)"


def bushing(p):
    p.add(Cylinder("z", m(0, 0, ZC), m(BUSHING_OD / 2), m(T), m(BUSHING_ID / 2)))
    return AL, "BUSHING, HOLD-DOWN", "AL 6061-T6, POTTED"


PARTS = {f.__name__: f for f in (face_sheet, core, closeout_long, closeout_short, manifold,
                                  flow_tube, insert, bushing)}


def placements():
    """(part, position [mm], rotation) for every component of the panel."""
    flip = sw_api.rotation("z", 180)            # turns an edge part to the opposite edge
    out = [("face_sheet", (0, 0, 0), None), ("face_sheet", (0, 0, T - SKIN), None), ("core", (0, 0, 0), None),
           ("closeout_long", (0, 0, 0), None), ("closeout_long", (L, W, 0), flip),
           ("closeout_short", (0, 0, 0), None), ("closeout_short", (L, W, 0), flip)]
    out += [("manifold", (0, y, 0), None) for y in MANIFOLD_Y]
    out += [("flow_tube", (x, 0, 0), None) for x in TUBE_X]
    out += [("insert", (x, y, 0), None) for x, y in hinge_inserts()]
    out += [("bushing", (x, y, 0), None) for x, y in holddowns()]
    return out


def main():
    sw = sw_api.connect()
    sw_api.close_documents_in(sw, HERE)
    info = {}
    for name, build in PARTS.items():
        part = sw_api.Part(sw)
        density, description, material = build(part)
        part.set_density(density)
        part_no = f"SDC-RAD-1{list(PARTS).index(name) + 1:02d}"
        sw_api.set_properties(part.model, {"Description": f"{description}; {material}", "Material": material,
                                           "PartNo": part_no})
        config = sw_api._typed(part.model.GetActiveConfiguration(), "IConfiguration")
        config.AlternateName = part_no              # the BOM shows the part number, not the file
        config.UseAlternateNameInBOM = True         # name (set the name first, or this won't stick)
        part.set_color((0.75, 0.75, 0.78))
        info[name] = part.mass_properties()["mass"]
        part.save(OUT / f"{name}.SLDPRT")
        print(f"{name:15s} {info[name]:8.3f} kg")

    assembly = sw_api.Assembly(sw)
    for name, position, rotation in placements():
        assembly.add(OUT / f"{name}.SLDPRT", m(*position), rotation)
    props = assembly.mass_properties()
    area = L * W / 1e6
    bore_litres = (N_TUBES * (W - 2 * EXTR_Y0) * math.pi / 4 * EXTR_BORE**2
                   + 2 * (L + 2 * MANIFOLD_STICKOUT) * math.pi / 4 * (MANIFOLD_OD - 2 * MANIFOLD_WALL)**2) / 1e6
    coolant = bore_litres * AMMONIA_KG_L
    extras = 2 * ADHESIVE_KG_M2 * area + 2 * COATING_KG_M2 * area + coolant
    print(f"coolant {bore_litres:.1f} L = {coolant:.1f} kg")
    total = props["mass"] + extras
    sw_api.set_properties(assembly.model, {
        "Description": "RADIATOR PANEL ASSY", "PartNo": "SDC-RAD-100",
        "Material": "SEE BOM", "Finish": "SEE NOTE 7", "Weight": f"{total:.0f} kg"})
    assembly.save(HERE / "radiator_panel.SLDASM")
    print(f"\nCAD solids {props['mass']:.1f} kg + adhesive/coating/coolant {extras:.1f} kg "
          f"= {total:.1f} kg  ({total / area:.2f} kg/m^2 of panel, {total / (2 * area):.2f} per radiating m^2)")
    (HERE / "mass.json").write_text(json.dumps(
        {"panel_mm": [L, W, T], "n_panels": N_PANELS, "n_tubes": N_TUBES, "tube_pitch_mm": TUBE_PITCH,
         "parts_kg": info, "solids_kg": props["mass"], "coolant_kg": coolant, "extras_kg": extras, "total_kg": total}, indent=2))


if __name__ == "__main__":
    main()
