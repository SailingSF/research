"""Engineering drawing of the radiator panel (ASME Y14.5-2018, mm), built in SolidWorks.

Run after build_radiator.py, with SolidWorks open:
    .venv\\Scripts\\python.exe cad\\radiator\\make_drawing.py

Writes radiator_panel.SLDDRW (editable in SolidWorks) and radiator_panel.pdf / .png.
Everything is placed by computing sheet coordinates from model coordinates, so changes to
build_radiator.py's parameters flow through.
"""
import json
import math
import sys
from pathlib import Path

from win32com.client import gencache

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import sw_api                                        # noqa: E402
from sw_api import _typed, _save                     # noqa: E402
import build_radiator as R                           # noqa: E402

C = gencache.EnsureModule("{4687F359-55D0-4CD3-B6CF-2EB42C11F989}", 0, 34, 0).constants  # swconst
SHEET_FORMAT = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\english\sheetformat\e - landscape.slddrt"
ASSEMBLY = HERE / "radiator_panel.SLDASM"
OUT = HERE / "radiator_panel"

MM = 1e-3


def _placements():
    """Component instance name ("bushing-3") -> function mapping its own coordinates [m] to
    panel coordinates [mm]. SolidWorks numbers instances in the order they were inserted."""
    out, count = {}, {}
    for name, pos, rot in R.placements():
        count[name] = count.get(name, 0) + 1
        r = rot or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        out[f"{name}-{count[name]}"] = (lambda p, r=r, pos=pos:
                                        tuple(sum(r[i][j] * p[j] for j in range(3)) / MM + pos[i] for i in range(3)))
    return out


PLACEMENTS = _placements()


class Sheet:
    """A drawing sheet plus helpers that work in sheet millimeters."""

    @classmethod
    def attach(cls, model):
        """Wrap a drawing that is already open (e.g. one the user has rearranged by hand)."""
        sheet = cls.__new__(cls)
        sheet.model = _typed(model, "IModelDoc2")
        sheet.dwg = _typed(sheet.model, "IDrawingDoc")
        sheet.ext = _typed(sheet.model.Extension, "IModelDocExtension")
        sheet.sketch = _typed(sheet.model.SketchManager, "ISketchManager")
        sheet._edges = {}
        return sheet

    def __init__(self, sw):
        template = sw.GetUserPreferenceStringValue(C.swDefaultTemplateDrawing)
        self.model = _typed(sw.NewDocument(template, C.swDwgPaperEsize, 0, 0), "IModelDoc2")
        self.dwg = _typed(self.model, "IDrawingDoc")
        self.ext = _typed(self.model.Extension, "IModelDocExtension")
        self.dwg.SetupSheet5("Sheet1", C.swDwgPaperEsize, C.swDwgTemplateEsize, 1, 1, False,
                             SHEET_FORMAT, 0, 0, "Default", True)
        self.ext.SetUserPreferenceInteger(C.swUnitSystem, 0, C.swUnitSystem_MMGS)
        self.ext.SetUserPreferenceInteger(C.swDetailingDimensionStandard, 0, C.swDetailingStandardANSI)
        self.sketch = _typed(self.model.SketchManager, "ISketchManager")
        self.sketch.AddToDB = True
        self._edges = {}
        # Annotations go on a black layer: SolidWorks otherwise draws reference dimensions gray.
        layers = _typed(self.model.GetLayerManager(), "ILayerMgr")
        layers.AddLayer("ANNOTATIONS", "Dimensions, GD&T and notes", 0, 0, 0)
        layers.SetCurrentLayer("ANNOTATIONS")

    def model_view(self, view_name, center_mm, scale):
        view = _typed(self.dwg.CreateDrawViewFromModelView3(str(ASSEMBLY), view_name,
                                                            center_mm[0] * MM, center_mm[1] * MM, 0), "IView")
        view.ScaleDecimal = scale
        return view

    def activate(self, view):
        self.dwg.ActivateView(view.GetName2())

    @staticmethod
    def sketch_xy(view, point_mm):
        """Sheet point [mm] -> coordinates for sketching inside `view` (which are measured
        from the view's position and scaled up by 1/view scale)."""
        px, py = view.Position
        return ((point_mm[0] * MM - px) / view.ScaleDecimal, (point_mm[1] * MM - py) / view.ScaleDecimal)

    def section(self, parent, p0, p1, label, center_mm):
        """Section view cut along the sheet line p0-p1 [mm] drawn in `parent`."""
        self.activate(parent)
        (x0, y0), (x1, y1) = self.sketch_xy(parent, p0), self.sketch_xy(parent, p1)
        line = self.sketch.CreateLine(x0, y0, 0, x1, y1, 0)
        self.model.ClearSelection2(True)
        _typed(line, "ISketchSegment").Select4(False, None)
        view = self.dwg.CreateSectionViewAt5(center_mm[0] * MM, center_mm[1] * MM, 0, label, 0, None, 0)
        if view is None:
            raise RuntimeError(f"section {label} failed")
        return _typed(view, "IView")

    def detail(self, parent, corners, label, center_mm, scale, shows):
        """Detail view of a rectangle in `parent`. `corners(parent)` returns its two corners
        [sheet mm]; `shows` lists parts that must be visible in it. SolidWorks occasionally
        cuts a detail from a stale view and crops it wrong; that is checked and retried once."""
        for attempt in range(2):
            self.model.ForceRebuild3(False)
            self.activate(parent)
            self.model.ClearSelection2(True)
            (x0, y0), (x1, y1) = (self.sketch_xy(parent, c) for c in corners(parent))
            segments = self.sketch.CreateCornerRectangle(x0, y0, 0, x1, y1, 0)
            for i, segment in enumerate(segments):
                _typed(segment, "ISketchSegment").Select4(i > 0, None)
            view = _typed(self.dwg.CreateDetailViewAt4(center_mm[0] * MM, center_mm[1] * MM, 0,
                                                       C.swDetViewSTANDARD, 1, 1 / scale, label, 1,
                                                       True, False, False, 5), "IView")
            if view is None:
                raise RuntimeError(f"detail {label} failed")
            self.model.ForceRebuild3(False)
            visible = {_typed(c, "IComponent2").Name2.split("/")[-1].rsplit("-", 1)[0]
                       for c in view.GetVisibleComponents() or []}
            if set(shows) <= visible:
                return view
            print(f"detail {label} is missing {set(shows) - visible}; recreating it")
            self.model.ClearSelection2(True)
            self.ext.SelectByID2(view.GetName2(), "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0)
            self.model.Extension.DeleteSelection2(0)
        raise RuntimeError(f"detail {label} does not show {shows}")

    # ---- selecting model geometry shown in a view -------------------------------------
    # Edges are found by geometry, not by clicking a sheet point: section edges can't be
    # picked by point, and at 1:15 neighboring edges are a fraction of a millimeter apart.
    # A view lists its visible edges per component, in that component's own coordinates;
    # PLACEMENTS turns those into panel coordinates [mm].
    def edges(self, view):
        """[(edge, part, ("line", p0, p1) | ("circle", center, radius))] in panel mm, cached."""
        key = view.GetName2()
        if key not in self._edges:
            found = []
            for comp in view.GetVisibleComponents() or []:
                comp = _typed(comp, "IComponent2")
                instance = comp.Name2.split("/")[-1]            # e.g. "bushing-3"
                part = instance.rsplit("-", 1)[0]
                to_panel = PLACEMENTS[instance]
                for edge in view.GetVisibleEntities2(comp, C.swViewEntityType_Edge) or []:
                    edge = _typed(edge, "IEdge")
                    curve = _typed(edge.GetCurve(), "ICurve")
                    if curve.IsCircle():
                        p = curve.CircleParams
                        found.append((edge, part, ("circle", to_panel(p[0:3]), p[6] / MM)))
                    elif curve.IsLine():
                        a, b = (_typed(v, "IVertex").GetPoint() for v in (edge.GetStartVertex(), edge.GetEndVertex()))
                        found.append((edge, part, ("line", to_panel(a), to_panel(b))))
            self._edges[key] = found
        return self._edges[key]

    def _select(self, view, edge, append, what):
        if not view.SelectEntity(edge, append):
            raise RuntimeError(f"could not select {what} in {view.GetName2()}")

    def pick_point(self, view, x, y, z=0.0):
        """Select the model edge drawn at model point (x, y, z) [mm] by clicking it, so a leader
        attached next lands on that point. Works on ordinary edges, not on section-cut edges."""
        sx, sy = to_sheet(view, x, y, z)
        self.model.ClearSelection2(True)
        if not self.ext.SelectByID2("", "EDGE", sx * MM, sy * MM, 0, False, 0, None, 0):
            raise RuntimeError(f"no edge at {x, y, z} in {view.GetName2()}")

    def check_leaders_attached(self):
        """Every leader on the sheet must end on model geometry, or it won't follow its view."""
        loose = []
        view = _typed(self.dwg.GetFirstView(), "IView")
        while view is not None:
            for ann in view.GetAnnotations() or []:
                ann = _typed(ann, "IAnnotation")
                if ann.GetLeaderCount() > 0 and ann.GetAttachedEntityCount3() == 0:
                    loose.append(f"{view.GetName2()}: {ann.GetName()}")
            view = _typed(view.GetNextView(), "IView")
        if loose:
            raise RuntimeError(f"leaders not attached to geometry: {loose}")

    def pick_line(self, view, part, append=False, **at):
        """Select the longest straight edge of `part` lying at the given coordinates [mm],
        e.g. pick_line(v, "face_sheet", x=0) is the face sheet's edge along X=0."""
        axis = {"x": 0, "y": 1, "z": 2}
        best = None
        for edge, p, (kind, *g) in self.edges(view):
            if p != part or kind != "line":
                continue
            a, b = g
            if all(abs(a[axis[k]] - v) < 0.01 and abs(b[axis[k]] - v) < 0.01 for k, v in at.items()):
                length = sum((a[i] - b[i]) ** 2 for i in range(3))
                if best is None or length > best[0]:
                    best = (length, edge)
        if best is None:
            raise RuntimeError(f"no {part} line at {at} in {view.GetName2()}")
        self._select(view, best[1], append, f"{part} line {at}")

    def pick_circle(self, view, part, radius, append=False, **at):
        """Select a circular edge of `part` with this radius whose center has the given coordinates."""
        axis = {"x": 0, "y": 1, "z": 2}
        for edge, p, (kind, *g) in self.edges(view):
            if p == part and kind == "circle" and abs(g[1] - radius) < 0.01 and \
                    all(abs(g[0][axis[k]] - v) < 0.01 for k, v in at.items()):
                return self._select(view, edge, append, f"{part} circle r={radius} {at}")
        raise RuntimeError(f"no {part} circle r={radius} at {at} in {view.GetName2()}")

    # ---- annotations -----------------------------------------------------------------
    def dimension(self, expect, at_mm, kind=None, tol=(0.0, 0.0), decimals=0, tol_decimals=None,
                  prefix="", suffix="", below=""):
        """Dimension the current selection, text at sheet point `at_mm`, and check that it
        measures `expect` [mm] (None skips the check).
        kind: None (general tolerance), "basic", "sym" (+/-tol[1]) or "bilat" (tol = (minus, plus))."""
        dd = _typed(self.model.AddDimension2(at_mm[0] * MM, at_mm[1] * MM, 0), "IDisplayDimension")
        if dd is None:
            raise RuntimeError(f"dimension at {at_mm} failed")
        dim = _typed(dd.GetDimension2(0), "IDimension")
        if expect is not None and abs(dim.Value - expect) > 0.005:
            raise RuntimeError(f"dimension measured {dim.Value}, expected {expect}")
        t = _typed(dim.Tolerance, "IDimensionTolerance")
        if kind == "basic":
            t.Type = C.swTolBASIC
        elif kind in ("sym", "bilat"):
            t.Type = C.swTolSYMMETRIC if kind == "sym" else C.swTolBILAT
            t.SetValues(tol[0] * MM, tol[1] * MM)
        dd.SetPrecision3(decimals, -1, decimals if tol_decimals is None else tol_decimals, -1)
        if prefix:
            dd.SetText(C.swDimensionTextPrefix, prefix)
        if suffix:
            dd.SetText(C.swDimensionTextSuffix, suffix)
        if below:
            dd.SetText(C.swDimensionTextCalloutBelow, below)
        self.model.ClearSelection2(True)
        return dd

    def fcf(self, symbol, tolerance, datums=(), diameter=False, mmc=False, at_mm=None,
            attach_to=None, below_mm=7.0):
        """Feature control frame (top-left corner at `at_mm`).
        attach_to: a display dimension; the frame goes `below_mm` under its text.
        Otherwise the frame gets a leader to whatever edge is selected: at the picked point if
        it was selected with pick_point, else at an end of the edge. (Moving a leader's end
        afterwards with SetLeaderAttachmentPointAtIndex detaches it from the model, and it
        then stays behind when the view is dragged.)"""
        if attach_to is not None:
            self.model.ClearSelection2(True)
            sm = _typed(self.model.SelectionManager, "ISelectionMgr")
            dim_ann = _typed(attach_to.GetAnnotation(), "IAnnotation")
            dim_ann.Select3(False, sm.CreateSelectData())
            x, y, _ = dim_ann.GetPosition()
            at_mm = at_mm or (x / MM - 2, y / MM - below_mm)
        g = _typed(self.model.InsertGtol(), "IGtol")
        if g is None:
            raise RuntimeError("InsertGtol failed")
        datums = list(datums) + [""] * (3 - len(datums))
        g.SetFrameSymbols2(1, f"<GTOL-{symbol}>", diameter, "<MOD-MMC>" if mmc else "", False, "", "", "", "")
        g.SetFrameValues2(1, tolerance, "", *datums)
        ann = _typed(g.GetAnnotation(), "IAnnotation")
        if at_mm is not None:
            ann.SetPosition2(at_mm[0] * MM, at_mm[1] * MM, 0)
        self.model.ClearSelection2(True)
        return g

    def datum(self, label, at_mm):
        """Datum feature symbol on the current selection."""
        tag = _typed(self.model.InsertDatumTag2(), "IDatumTag")
        if tag is None:
            raise RuntimeError(f"datum {label} failed")
        tag.SetLabel(label)
        _typed(tag.GetAnnotation(), "IAnnotation").SetPosition2(at_mm[0] * MM, at_mm[1] * MM, 0)
        self.model.ClearSelection2(True)
        return tag

    def note(self, text, at_mm, height_mm=None):
        """A note; with something selected it gets a leader to it (see fcf for where it lands)."""
        n = _typed(self.model.InsertNote(text), "INote")
        if n is None:
            raise RuntimeError(f"note failed: {text[:30]}")
        ann = _typed(n.GetAnnotation(), "IAnnotation")
        ann.SetPosition2(at_mm[0] * MM, at_mm[1] * MM, 0)
        if height_mm:
            fmt = ann.GetTextFormat(0)
            fmt.CharHeight = height_mm * MM
            ann.SetTextFormat(0, False, fmt)
        self.model.ClearSelection2(True)
        return n


def to_sheet(view, x_mm, y_mm, z_mm=0.0):
    """Model point [mm] -> sheet point [mm] for a view."""
    t = list(_typed(view.ModelToViewTransform, "IMathTransform").ArrayData)
    rot, shift, scale = t[0:9], t[9:12], t[12]
    p = [x_mm * MM, y_mm * MM, z_mm * MM]
    # SolidWorks transforms are row vectors: p' = p * R * scale + shift
    out = [sum(p[i] * rot[3 * i + j] for i in range(3)) * scale + shift[j] for j in range(3)]
    return out[0] / MM, out[1] / MM


# ==== Layout: where each view's center goes on the E-size sheet [mm] ======================
# Upper three-quarters: views. Bottom band (below y ~ 175): notes, parts list, title block.
PLAN_AT = (250, 630)        # 1:15, ~304 x 313 mm, with dimensions on all four sides
SECTION_A_AT = (250, 393)   # below the plan
SECTION_B_AT = (485, 630)   # right of the plan
ISO_AT = (330, 240)         # pictorial with BOM balloons, lower left
ISO_SCALE = 1 / 35
DETAIL_C_AT = (815, 765)    # 3:1, edge closeout + first flow tube (top right)
DETAIL_E_AT = (680, 455)    # 2:1, hinge insert pattern (middle)
DETAIL_E_SCALE = 2
DETAIL_D_AT = (1005, 470)   # 3:1, manifold at the long edge (panel width runs vertically)
NOTES_AT = (27, 97)         # top-left corner of the notes block (bottom left)
BOM_AT = (669, 96)          # top-left corner of the parts list (bottom, beside the title block)
BOM_TEMPLATE = r"E:\max\solidworks\SOLIDWORKS\lang\english\bom-standard.sldbomtbt"


def build_views(sheet):
    plan = sheet.model_view("*Front", PLAN_AT, 1 / 15)
    sheet.model.ForceRebuild3(False)

    # Section A-A: horizontal cut across the flow tubes at mid-width.
    y_mid = to_sheet(plan, 0, R.W / 2)[1]
    x0, x1 = to_sheet(plan, -60, 0)[0], to_sheet(plan, R.L + 60, 0)[0]
    sec_a = sheet.section(plan, (x0, y_mid), (x1, y_mid), "A", SECTION_A_AT)
    # Section B-B: vertical cut through the first column of hold-down bushings.
    x_cut = to_sheet(plan, R.HOLDDOWN_X[0], 0)[0]
    y0, y1 = to_sheet(plan, 0, -60)[1], to_sheet(plan, 0, R.W + 60)[1]
    sec_b = sheet.section(plan, (x_cut, y1), (x_cut, y0), "B", SECTION_B_AT)
    sheet.model.ForceRebuild3(False)

    # Detail C (from A-A): hinge-edge closeout, manifold stub and the first flow tube.
    det_c = sheet.detail(sec_a, lambda v: (to_sheet(v, -47, R.W / 2, R.T + 10), to_sheet(v, 136, R.W / 2, -10)),
                         "C", DETAIL_C_AT, 3, shows=["closeout_short", "flow_tube", "manifold", "face_sheet"])
    # Detail D (from B-B): long-edge closeout and supply manifold.
    x_d = R.HOLDDOWN_X[0]
    det_d = sheet.detail(sec_b, lambda v: (to_sheet(v, x_d, -12, R.T + 10), to_sheet(v, x_d, 90, -10)),
                         "D", DETAIL_D_AT, 3, shows=["closeout_long", "manifold", "face_sheet"])
    # Detail E (from the plan): the inserts for one hinge fitting.
    y_h = R.HINGE_Y[0]
    det_e = sheet.detail(plan, lambda v: (to_sheet(v, -30, y_h - 65), to_sheet(v, 100, y_h + 65)),
                         "E", DETAIL_E_AT, DETAIL_E_SCALE, shows=["insert", "face_sheet"])

    iso = sheet.model_view("*Isometric", ISO_AT, ISO_SCALE)
    sheet.model.ForceRebuild3(False)
    sheet.dwg.ActivateSheet("Sheet1")
    views = dict(plan=plan, sec_a=sec_a, sec_b=sec_b, det_c=det_c, det_d=det_d, det_e=det_e, iso=iso)
    # What each section/detail view shows, as model-space corners, so its label can sit right under it
    # (SolidWorks drops detail labels far below the view, farther the larger the scale).
    views["_extents"] = {
        "sec_a": [(-R.MANIFOLD_STICKOUT, R.W / 2, 0), (R.L + R.MANIFOLD_STICKOUT, R.W / 2, R.T)],
        "sec_b": [(x_d, 0, 0), (x_d, R.W, R.T)],
        "det_c": [(-47, R.W / 2, R.T + 10), (136, R.W / 2, -10)],
        "det_d": [(x_d, -12, R.T + 10), (x_d, 90, -10)],
        "det_e": [(-30, y_h - 65, 0), (100, y_h + 65, 0)],
    }
    return views


def place_view_labels(sheet, views, gap_mm=5.0):
    """Center each section/detail view's label ("SECTION A-A / SCALE 1:15") just under the view."""
    for key, corners in views["_extents"].items():
        view = views[key]
        pts = [to_sheet(view, *c) for c in corners]
        x_mid = sum(p[0] for p in pts) / len(pts)
        y_low = min(p[1] for p in pts)
        for ann in view.GetAnnotations() or []:
            ann = _typed(ann, "IAnnotation")
            # The view label is linked text ("SECTION A-A / SCALE 1 : 15") that reads back blank
            if ann.GetType() == C.swNote and not _typed(ann.GetSpecificAnnotation(), "INote").GetText().strip():
                ann.SetPosition2(x_mid * MM, (y_low - gap_mm) * MM, 0)


def annotate_plan(sheet, plan):
    """Envelope, datums B and C, and the bushing / hinge locations (basic) in the plan view."""
    L, W, T = R.L, R.W, R.T
    left, bottom = to_sheet(plan, 0, 0)
    right, top = to_sheet(plan, L, W)
    edge_b = lambda append=False: sheet.pick_line(plan, "face_sheet", append=append, x=0, z=T)
    edge_c = lambda append=False: sheet.pick_line(plan, "face_sheet", append=append, y=0, z=T)

    # Envelope
    edge_b(); sheet.pick_line(plan, "face_sheet", append=True, x=L, z=T)
    sheet.dimension(L, (to_sheet(plan, L / 2, 0)[0], top + 45), "sym", (1.0, 1.0), 0, 1)
    edge_c(); sheet.pick_line(plan, "face_sheet", append=True, y=W, z=T)
    sheet.dimension(W, (left - 44, to_sheet(plan, 0, W / 2)[1]), "sym", (1.0, 1.0), 0, 1)

    # Hinge fittings at the X=0 edge: Y of their outer insert rows from C (left side).
    # Detail E gives the insert pattern from B; the far edge's fittings are located below.
    x_near = R.HINGE_DX[0]
    for i, y in enumerate((R.HINGE_Y[0] - R.HINGE_DY, R.HINGE_Y[1] + R.HINGE_DY)):
        edge_c(); sheet.pick_circle(plan, "insert", R.INSERT_TAP / 2, append=True, x=x_near, y=y)
        sheet.dimension(y, (left - 8 - 8 * i, to_sheet(plan, 0, y / 2)[1]), "basic")
    # Hinge fittings at the X=L edge: the pattern is mirrored, so locate its rows from B (top).
    for i, dx in enumerate(reversed(R.HINGE_DX)):          # inner row (L-65), then outer row (L-25)
        x = L - dx
        y = R.HINGE_Y[1] + R.HINGE_DY
        edge_b(); sheet.pick_circle(plan, "insert", R.INSERT_TAP / 2, append=True, x=x, y=y)
        sheet.dimension(x, (to_sheet(plan, L * 0.8, 0)[0], top + 29 + 7 * i), "basic")

    # Datum features B (hinge edge) and C (long edge), each perpendicular to A
    y_b = to_sheet(plan, 0, 0.80 * W)[1]
    edge_b(); sheet.datum("B", (left - 10, y_b))
    sheet.pick_point(plan, 0, 0.87 * W, T)              # the arrow lands where the edge is picked
    sheet.fcf("PERP", "0.5", ["A"], at_mm=(left - 34, y_b + 16))
    x_c = to_sheet(plan, 0.15 * L, 0)[0]
    edge_c(); sheet.datum("C", (x_c, bottom - 10))
    sheet.pick_point(plan, 0.21 * L, 0, T)
    sheet.fcf("PERP", "0.5", ["A", "B"], at_mm=(x_c + 14, bottom - 8))

    # Hold-down bushings: X from B along the top row (above the plan); Y from C on the right,
    # together with the outer insert rows of the hinge fittings.
    y_top_row = R.HOLDDOWN_Y[1]
    for i, x in enumerate(R.HOLDDOWN_X):
        edge_b(); sheet.pick_circle(plan, "bushing", R.BUSHING_ID / 2, append=True, x=x, y=y_top_row)
        sheet.dimension(x, (to_sheet(plan, x / 2, 0)[0], top + 8 + 7 * i), "basic")
    x_col = R.HOLDDOWN_X[-1]
    x_ins = L - R.HINGE_DX[0]
    stack = [(y, "bushing", x_col, R.BUSHING_ID / 2) for y in R.HOLDDOWN_Y]
    stack += [(R.HINGE_Y[0] - R.HINGE_DY, "insert", x_ins, R.INSERT_TAP / 2),
              (R.HINGE_Y[1] + R.HINGE_DY, "insert", x_ins, R.INSERT_TAP / 2)]
    for i, (y, part, x, r) in enumerate(sorted(stack)):
        edge_c(); sheet.pick_circle(plan, part, r, append=True, x=x, y=y)
        sheet.dimension(y, (right + 8 + 7 * i, to_sheet(plan, 0, y / 2)[1]), "basic")

    # Bushing callout with its position tolerance
    sheet.pick_circle(plan, "bushing", R.BUSHING_ID / 2, x=x_col, y=y_top_row)
    dd = sheet.dimension(R.BUSHING_ID, to_sheet(plan, 0.70 * L, 0.78 * W), "bilat", (0.0, 0.05), 2,
                         prefix="6X <MOD-DIAM>", below="THRU BUSHING")
    sheet.fcf("POSI", "0.8", ["A", "B", "C"], diameter=True, mmc=True, attach_to=dd, below_mm=12)


def annotate_detail_c(sheet, v):
    """Thickness, flatness, datum A, first flow tube and manifold stub, in the edge section."""
    y, T = R.W / 2, R.T                   # section A-A plane; panel thickness
    sx = lambda x, z: to_sheet(v, x, y, z)
    face_a = lambda append=False: sheet.pick_line(v, "face_sheet", append=append, y=y, z=0)
    face_top = lambda append=False: sheet.pick_line(v, "face_sheet", append=append, y=y, z=T)
    edge_b = lambda append=False: sheet.pick_line(v, "closeout_short", append=append, y=y, x=0)
    out_a = 1 if sx(0, 0)[1] > sx(0, T)[1] else -1    # +1: the datum A face is drawn on top
    y_a, y_top = sx(0, 0)[1], sx(0, T)[1]             # sheet heights of the two faces

    # Thickness (a size, with independency: flatness is controlled separately), left of the panel
    face_a(); face_top(True)
    sheet.dimension(T, (sx(-37, 0)[0], (y_a + y_top) / 2), "sym", (0.3, 0.3), 1, 1, suffix=" <MOD-IND>")
    # Datum A with its flatness; the opposite face parallel to A
    face_a(); sheet.datum("A", (sx(40, 0)[0], y_a + out_a * 12))
    # Section edges can't be picked at a point, so these leaders land on the face sheets' end at
    # the hinge edge (X=0); the frames sit right beside it to keep the leaders short.
    face_a(); sheet.fcf("FLAT", "1.5", at_mm=(sx(6, 0)[0], y_a + out_a * 14))
    face_top(); sheet.fcf("PARA", "2.0", ["A"], at_mm=(sx(6, 0)[0], y_top - out_a * 8))
    # First flow tube from datum B, and the pattern
    edge_b(); sheet.pick_circle(v, "flow_tube", R.EXTR_BORE / 2, append=True, x=R.TUBE_X[0])
    sheet.dimension(R.TUBE_X[0], (sx(R.TUBE_X[0] / 2, 0)[0], y_a + out_a * 26), "basic")
    sheet.pick_circle(v, "flow_tube", R.EXTR_TUBE_OD / 2, x=R.TUBE_X[0])
    n = R.N_TUBES
    sheet.note(f"{n}X FLOW TUBE EXTRUSION, {R.TUBE_PITCH:.0f} PITCH\n"
               f"{n - 1}X {R.TUBE_PITCH:.0f} = {(n - 1) * R.TUBE_PITCH:.0f} BASIC\n"
               f"BONDED TO BOTH FACE SHEETS", (sx(90, 0)[0], y_top - out_a * 14))
    # Manifold stub beyond the hinge edge
    sheet.pick_circle(v, "manifold", R.MANIFOLD_OD / 2, x=-R.MANIFOLD_STICKOUT); edge_b(True)
    sheet.dimension(R.MANIFOLD_STICKOUT, (sx(-R.MANIFOLD_STICKOUT / 2, 0)[0], y_a + out_a * 10),
                    "sym", (2.0, 2.0), 0, 0, below="4X, EACH STUB\nFROM ITS HINGE EDGE")


def annotate_detail_d(sheet, v):
    """Manifold location from datum C, in the long-edge section."""
    x, my = R.HOLDDOWN_X[0], R.MANIFOLD_Y[0]
    c0, c1 = to_sheet(v, x, 0, 0), to_sheet(v, x, my, 0)          # datum C and manifold, on face A
    across = to_sheet(v, x, 0, R.T)                                # the other face
    vertical = abs(c1[1] - c0[1]) > abs(c1[0] - c0[0])             # panel width runs up the sheet?
    sheet.pick_line(v, "closeout_long", x=x, y=0)
    sheet.pick_circle(v, "manifold", R.MANIFOLD_OD / 2, append=True, y=my)
    if vertical:   # dimension to the side of the section, away from the far face
        side = -1 if across[0] > c0[0] else 1
        at = (c0[0] + side * 14, (c0[1] + c1[1]) / 2)
    else:
        side = -1 if across[1] > c0[1] else 1
        at = ((c0[0] + c1[0]) / 2, c0[1] + side * 14)
    sheet.dimension(my, at, "sym", (1.0, 1.0), 0, 1,
                    below="2X, EACH MANIFOLD\nFROM ITS LONG EDGE")
    sheet.pick_circle(v, "manifold", R.MANIFOLD_OD / 2, y=my)
    if vertical:   # note beside the section, on the far-face side, level with the manifold
        p = to_sheet(v, x, my + 45, R.T)
        at = (p[0] - 100 if across[0] < c0[0] else p[0] + 20, p[1])
    else:
        p = to_sheet(v, x, my + 20, R.T)
        at = (p[0], p[1] - 14)
    sheet.note(f"MANIFOLD TUBE Ø{R.MANIFOLD_OD:.2f} x {R.MANIFOLD_WALL:.2f} WALL (2X)\n"
               "POTTED IN CORE CHANNEL", at)


def annotate_detail_e(sheet, v):
    """Hinge insert pattern (identical at all four fittings) and its position tolerance."""
    x0, x1 = R.HINGE_DX
    y0, y1 = R.HINGE_Y[0] - R.HINGE_DY, R.HINGE_Y[0] + R.HINGE_DY
    r = R.INSERT_TAP / 2
    insert = lambda x, y, append=False: sheet.pick_circle(v, "insert", r, append=append, x=x, y=y)
    top = to_sheet(v, 0, y1 + 30)[1]
    sheet.pick_line(v, "face_sheet", x=0, z=R.T); insert(x0, y1, True)
    sheet.dimension(x0, (to_sheet(v, x0 / 2, 0)[0], top), "basic")
    insert(x0, y1); insert(x1, y1, True)
    sheet.dimension(x1 - x0, (to_sheet(v, (x0 + x1) / 2, 0)[0], top), "basic")
    insert(x1, y0); insert(x1, y1, True)
    sheet.dimension(y1 - y0, (to_sheet(v, x1 + 22, 0)[0], to_sheet(v, 0, R.HINGE_Y[0])[1]), "basic")
    sheet.note(f"PATTERN TYP 4 FITTINGS.\nAT THE X={R.L:.0f} HINGE EDGE\nTHE PATTERN IS MIRRORED;\n"
               "ROW LOCATIONS IN PLAN VIEW.", (to_sheet(v, -28, 0)[0], to_sheet(v, 0, y0 - 45)[1]))
    insert(x1, y0)
    frame_right = to_sheet(v, 100, 0)[0]          # the detail spans X = -30..100
    dd = sheet.dimension(R.INSERT_TAP, (frame_right + 8, to_sheet(v, 0, y0 - 30)[1]))
    dd.SetText(C.swDimensionTextAll, "16X M6x1.0-6H")     # a thread callout, not the drilled size
    dd.SetText(C.swDimensionTextCalloutBelow, "POTTED INSERT, THRU")
    sheet.fcf("POSI", "0.4", ["A", "B", "C"], diameter=True, attach_to=dd, below_mm=12)


NOTES = """NOTES: UNLESS OTHERWISE SPECIFIED
1.  INTERPRET DIMENSIONS AND TOLERANCES PER ASME Y14.5-2018. DIMENSIONS IN MILLIMETERS.
2.  UNTOLERANCED DIMENSIONS: X \u00b11   X.X \u00b10.5   X.XX \u00b10.10   ANGLES \u00b10.5\u00b0.
3.  FLATNESS AND PARALLELISM APPLY WITH THE PANEL RESTRAINED AT THE 6 HOLD-DOWN BUSHINGS
     (AS IN THE LAUNCH STACK). FREE-STATE SAG IS NOT CONTROLLED.
4.  FACE SHEETS: AL 7075-T6, 0.25 ±0.03 THK, BOTH SIDES. BOND WITH EPOXY FILM ADHESIVE, 0.15 kg/m\u00b2 PER BONDLINE.
5.  CORE: AL 5056 HEX HONEYCOMB, 6.4 mm CELL, 32 kg/m\u00b3, PERFORATED FOR VENTING.
     RIBBON DIRECTION PARALLEL TO X.
6.  COOLANT LOOP: ANHYDROUS AMMONIA. MEOP 3.4 MPa. PROOF TEST 1.5 x MEOP.
     HELIUM LEAK RATE \u2264 1E-6 scc/s PER PANEL. CAP MANIFOLD STUBS UNTIL INTEGRATION.
7.  BOTH FACES: WHITE SILICATE PAINT OR SILVERED-FEP OSR. \u03b5 \u2265 0.88, \u03b1 \u2264 0.20 (BEGINNING OF LIFE).
     MASK INSERT AND BUSHING FACES.
8.  INSERTS: 100% PROOF LOAD 1.0 kN AXIAL. BUSHINGS: POTTED, FLUSH \u00b10.1 WITH BOTH FACES.
9.  BOND INSPECTION: 100% ULTRASONIC C-SCAN. NO DISBOND LARGER THAN \u00d825.
10. ONE PART NUMBER FOR ALL {n_panels} PANELS PER SATELLITE: HINGE PATTERN IS IDENTICAL AT BOTH
     HINGE EDGES, SO ANY PANEL FITS ANY POSITION IN THE FIN.
11. MASS {mass:.0f} kg EST, INCL. COOLANT, ADHESIVE AND COATING."""


def add_general_notes(sheet):
    """The notes block. Inserted before any view exists, so it belongs to the sheet: a note
    inserted while a view is active belongs to that view and moves when the view is dragged."""
    mass = json.loads((HERE / "mass.json").read_text())["total_kg"]
    sheet.note(NOTES.format(mass=mass, n_panels=R.N_PANELS), NOTES_AT, height_mm=3.5)


# BOM items to balloon in the isometric: (part, which visible edge to attach to). Items 2 (core) and
# 6 (flow tubes) are inside the panel and get a note instead.
ISO_BALLOONS = [("face_sheet", "line"), ("closeout_long", "line"), ("closeout_short", "line"),
                ("manifold", "circle"), ("insert", "circle"), ("bushing", "circle")]


def annotate_iso(sheet, v):
    """Label the pictorial and balloon every BOM item visible from outside, so the parts list
    points at real geometry."""
    edges = sheet.edges(v)
    x0, y0, x1, y1 = (c / MM for c in v.GetOutline())     # before balloons widen it
    center = ((x0 + x1) / 2, (y0 + y1) / 2)
    placed = []
    for part, kind in ISO_BALLOONS:
        # the longest visible line, or the first visible circle, of that part
        candidates = [(e, g) for e, p, (k, *g) in edges if p == part and k == kind]
        if not candidates:
            raise RuntimeError(f"no visible {kind} of {part} in the isometric")
        if kind == "line":
            edge = max(candidates, key=lambda c: sum((c[1][0][i] - c[1][1][i]) ** 2 for i in range(3)))[0]
        else:
            edge = candidates[0][0]
        sheet.model.ClearSelection2(True)
        sheet._select(v, edge, False, part)
        balloon = sheet.model.InsertBOMBalloon2(C.swBS_Circular, C.swBF_2Chars, C.swBalloonTextItemNumber, "", 0, "")
        if balloon is None:
            raise RuntimeError(f"balloon on {part} failed")
        ann = _typed(_typed(balloon, "INote").GetAnnotation(), "IAnnotation")
        # Push the balloon out from the view's center, past where its arrow lands; if another
        # balloon is already there (two arrows can land on the same corner), swing it around.
        tip = ann.GetLeaderPointsAtIndex(0)[-3:-1]
        tip = (tip[0] / MM, tip[1] / MM)
        base = math.atan2(tip[1] - center[1], tip[0] - center[0])
        for turn in (0, 40, -40, 80, -80, 120, -120):
            a = base + math.radians(turn)
            spot = (tip[0] + 22 * math.cos(a), tip[1] + 22 * math.sin(a))
            if all((spot[0] - p[0]) ** 2 + (spot[1] - p[1]) ** 2 > 14 ** 2 for p in placed):
                break
        placed.append(spot)
        ann.SetPosition2(spot[0] * MM, spot[1] * MM, 0)
    sheet.model.ClearSelection2(True)
    # Label and the internal-items note belong to the view, so they move with it
    sheet.activate(v)
    sheet.note(f"ISOMETRIC VIEW\nSCALE 1 : {round(1 / v.ScaleDecimal)}", ((x0 + x1) / 2 - 14, y0 - 6))
    sheet.note("ITEMS 2 (CORE) AND 6 (FLOW TUBES) ARE\nINTERNAL: SEE SECTION A-A, DETAILS C AND D.",
               ((x0 + x1) / 2 - 40, y0 - 18))
    sheet.model.ClearSelection2(True)


def annotate(sheet, views):
    steps = [("plan", annotate_plan, views["plan"]), ("detail C", annotate_detail_c, views["det_c"]),
             ("detail D", annotate_detail_d, views["det_d"]), ("detail E", annotate_detail_e, views["det_e"]), ("isometric", annotate_iso, views["iso"])]
    for name, fn, view in steps:
        try:
            fn(sheet, view)
        except Exception as e:                      # keep going; report what failed
            print(f"annotate {name}: {e}")
            sheet.model.ClearSelection2(True)
    sheet.check_leaders_attached()
    bom = views["plan"].InsertBomTable4(False, BOM_AT[0] * MM, BOM_AT[1] * MM, 1, C.swBomType_PartsOnly,
                                        "Default", BOM_TEMPLATE, False, 0, False)
    if bom is None:
        raise RuntimeError("BOM table failed")


PM = "<MOD-PM>"
TITLE_BLOCK = {   # stock SolidWorks ANSI title block text (start of note) -> what this drawing says
    "DIMENSIONS ARE IN INCHES": f"DIMENSIONS ARE IN MILLIMETERS\r\nTOLERANCES:\r\nX {PM}1    X.X {PM}0.5\r\n"
                                f"X.XX {PM}0.10\r\nANGULAR {PM}0.5°",
    "INTERPRET GEOMETRIC": "INTERPRET GEOMETRIC\r\nTOLERANCING PER: ASME Y14.5-2018",
    "PROPRIETARY AND CONFIDENTIAL": "CONCEPT DRAWING",
    "THE INFORMATION CONTAINED": "FEASIBILITY STUDY FOR DISCUSSION.\r\nNOT FOR MANUFACTURE.\r\n"
                                 "MATERIALS AND TOLERANCES ARE\r\nREPRESENTATIVE, NOT QUALIFIED.",
    "SCALE:": "SCALE: 1:15",
}
DRAWING_PROPERTIES = {"DwgNo": "SDC-RAD-100", "Revision": "A", "DrawnDate": "2026-11-16"}


def fill_title_block(sheet):
    """Replace the stock template's inch tolerances and placeholders. The drawing number
    field shows the file name by default; point it at the DwgNo property instead."""
    sw_api.set_properties(sheet.model, DRAWING_PROPERTIES)
    sheet.dwg.EditTemplate()
    note = _typed(sheet.dwg.GetFirstView(), "IView").GetFirstNote()
    while note is not None:
        note = _typed(note, "INote")
        if "SW-File Name" in (note.PropertyLinkedText or ""):
            note.PropertyLinkedText = '$PRP:"DwgNo"'
            note.SetHeight(5 * MM)                  # the stock size overruns the SIZE box
        for start, text in TITLE_BLOCK.items():
            if note.GetText().startswith(start):
                note.SetText(text)
        note = note.GetNext()
    sheet.dwg.EditSheet()


PNG_DPI = 150      # E size at 150 dpi = 6600 x 5100 px


def export(sw, sheet):
    """SLDDRW (editable), PDF, and a full-sheet PNG for the blog. The PNG uses SolidWorks'
    print-style capture at the real sheet size; the user's export settings are restored."""
    sheet.model.ForceRebuild3(False)
    _save(sheet.model, str(OUT) + ".SLDDRW")
    _save(sheet.model, str(OUT) + ".pdf")
    ints = {C.swTiffScreenOrPrintCapture: 1, C.swTiffImageType: C.swTiffImageRGB,
            C.swTiffPrintDPI: PNG_DPI, C.swTiffPrintPaperSize: 12}             # 12 = custom size
    doubles = {C.swTiffPrintDrawingPaperWidth: 1.1176, C.swTiffPrintDrawingPaperHeight: 0.8636}
    toggles = {C.swTiffPrintUseSheetSize: True, C.swTiffPrintScaleToFit: True}
    saved = ({k: sw.GetUserPreferenceIntegerValue(k) for k in ints},
             {k: sw.GetUserPreferenceDoubleValue(k) for k in doubles},
             {k: sw.GetUserPreferenceToggle(k) for k in toggles})
    try:
        for k, v in ints.items():
            sw.SetUserPreferenceIntegerValue(k, v)
        for k, v in doubles.items():
            sw.SetUserPreferenceDoubleValue(k, v)
        for k, v in toggles.items():
            sw.SetUserPreferenceToggle(k, v)
        _save(sheet.model, str(OUT) + ".png")
    finally:
        for k, v in saved[0].items():
            sw.SetUserPreferenceIntegerValue(k, v)
        for k, v in saved[1].items():
            sw.SetUserPreferenceDoubleValue(k, v)
        for k, v in saved[2].items():
            sw.SetUserPreferenceToggle(k, v)
    write_blog_jpeg()


BLOG_JPEG = HERE / "images" / "radiator_panel_drawing.jpg"
BLOG_JPEG_WIDTH = 3300      # px: half the 150 dpi sheet, still sharp when zoomed in a browser


def write_blog_jpeg():
    """The blog's copy of the drawing: the full-sheet PNG, downsized, as a JPEG."""
    from PIL import Image
    image = Image.open(str(OUT) + ".png").convert("L")
    height = round(image.height * BLOG_JPEG_WIDTH / image.width)
    BLOG_JPEG.parent.mkdir(exist_ok=True)
    image.resize((BLOG_JPEG_WIDTH, height), Image.LANCZOS).save(BLOG_JPEG, quality=90, optimize=True)
    return BLOG_JPEG


def main():
    sw = sw_api.connect()
    sw.CloseDoc("radiator_panel - Sheet1")
    sheet = Sheet(sw)
    add_general_notes(sheet)
    views = build_views(sheet)
    annotate(sheet, views)
    place_view_labels(sheet, views)
    fill_title_block(sheet)
    export(sw, sheet)
    return sheet, views


if __name__ == "__main__":
    main()
