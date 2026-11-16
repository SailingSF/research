"""Thin helpers around the SolidWorks COM API (SolidWorks 2026 / 3DEXPERIENCE), via pywin32.

All lengths passed to the API are in METERS and masses in KG, regardless of document display units.

Model frame used throughout the Part 2 CAD (matches SolidWorks' default axes):
    +X = velocity (ram direction)
    +Y = zenith (away from Earth); also the Starship axis when stowed
    +Z = orbit normal = toward the Sun in a dawn-dusk orbit
"""
from __future__ import annotations

import math
import os

import pythoncom
import win32com.client as w
from win32com.client import gencache, VARIANT

SW_TLB = ("{83A33D31-27C5-11CE-BFD4-00400513BB57}", 0, 34, 0)  # SolidWorks 2026 type library
swmod = gencache.EnsureModule(*SW_TLB)

# SolidWorks enum values used here
SW_END_BLIND = 0
SW_START_SKETCH_PLANE = 0
SW_START_OFFSET = 3
SW_SAVE_AS_CURRENT = 0
SW_SAVE_SILENT = 1
SW_DOC_PART, SW_DOC_ASSEMBLY = 1, 2
SW_PREF_DENSITY = 7  # swMaterialPropertyDensity: document density used when no material is assigned

# Sketch-plane conventions: name, model axis of the extrude direction, and how sketch (u, v)
# map onto model coordinates. Verified by center-of-mass checks in self_test().
PLANES = {
    "Front": dict(name="Front Plane", normal="z"),  # sketch (u,v) -> model (x, y)
    "Top":   dict(name="Top Plane",   normal="y"),  # sketch (u,v) -> model (x, -z)
    "Right": dict(name="Right Plane", normal="x"),  # sketch (u,v) -> model (-z, y)
}


def typed(obj, iface: str):
    """Wrap a raw COM object in the generated early-bound class for `iface`."""
    if obj is None:
        return None
    raw = obj._oleobj_ if hasattr(obj, "_oleobj_") else obj
    return getattr(swmod, iface)(raw)


def connect():
    return typed(w.GetActiveObject("SldWorks.Application"), "ISldWorks")


def _to_sketch(plane: str, a: float, b: float) -> tuple[float, float]:
    """Map in-plane model coordinates to sketch (u, v).
    Front: (a,b)=(x,y);  Top: (a,b)=(x,z);  Right: (a,b)=(z,y)."""
    if plane == "Front":
        return a, b
    if plane == "Top":
        return a, -b
    if plane == "Right":
        return -a, b
    raise ValueError(plane)


class Part:
    """A new part document with primitive-building helpers."""

    def __init__(self, sw):
        self.sw = sw
        self.model = typed(sw.NewPart(), "IModelDoc2")
        if self.model is None:
            raise RuntimeError("NewPart failed")
        self.ext = typed(self.model.Extension, "IModelDocExtension")
        self.skm = typed(self.model.SketchManager, "ISketchManager")
        self.fm = typed(self.model.FeatureManager, "IFeatureManager")
        self.part = typed(self.model, "IPartDoc")
        self.skm.AddToDB = True  # skip snapping/inference while sketching

    # ---- core: extrude closed profiles drawn on a principal plane -------------------------
    def _extrude(self, plane: str, draw, start: float, length: float):
        self.model.ClearSelection2(True)
        ok = self.ext.SelectByID2(PLANES[plane]["name"], "PLANE", 0, 0, 0, False, 0, None, 0)
        if not ok:
            raise RuntimeError(f"could not select {plane}")
        self.skm.InsertSketch(True)
        draw()
        self.skm.InsertSketch(True)  # close sketch; it stays selected
        flip = start < 0
        t0 = SW_START_OFFSET if abs(start) > 1e-12 else SW_START_SKETCH_PLANE
        feat = self.fm.FeatureExtrusion3(
            True, False, False, SW_END_BLIND, SW_END_BLIND, float(length), 0.0,
            False, False, False, False, 0.0, 0.0, False, False, False, False,
            True, True, True, t0, float(abs(start)), flip)
        if feat is None:
            raise RuntimeError(f"extrude failed on {plane}")
        self.model.ClearSelection2(True)
        return feat

    def box(self, center, size):
        """Axis-aligned box. center=(x,y,z), size=(sx,sy,sz)."""
        cx, cy, cz = center
        sx, sy, sz = size
        u0, v0 = _to_sketch("Front", cx - sx / 2, cy - sy / 2)
        u1, v1 = _to_sketch("Front", cx + sx / 2, cy + sy / 2)
        return self._extrude("Front", lambda: self.skm.CreateCornerRectangle(u0, v0, 0, u1, v1, 0),
                             cz - sz / 2, sz)

    def cylinder(self, axis: str, center, radius: float, length: float, inner_radius: float = 0.0):
        """Cylinder (or tube if inner_radius>0) along model axis 'x', 'y', or 'z', centered at center."""
        cx, cy, cz = center
        plane, a, b, s = {"z": ("Front", cx, cy, cz), "y": ("Top", cx, cz, cy), "x": ("Right", cz, cy, cx)}[axis]
        u, v = _to_sketch(plane, a, b)

        def draw():
            self.skm.CreateCircleByRadius(u, v, 0, radius)
            if inner_radius > 0:
                self.skm.CreateCircleByRadius(u, v, 0, inner_radius)
        return self._extrude(plane, draw, s - length / 2, length)

    def square_tube(self, axis: str, center, outer: float, wall: float, length: float):
        """Square tube along a model axis (structural member)."""
        cx, cy, cz = center
        plane, a, b, s = {"z": ("Front", cx, cy, cz), "y": ("Top", cx, cz, cy), "x": ("Right", cz, cy, cx)}[axis]

        def draw():
            for half in (outer / 2, outer / 2 - wall):
                u0, v0 = _to_sketch(plane, a - half, b - half)
                u1, v1 = _to_sketch(plane, a + half, b + half)
                self.skm.CreateCornerRectangle(u0, v0, 0, u1, v1, 0)
        return self._extrude(plane, draw, s - length / 2, length)

    # ---- material, mass --------------------------------------------------------------------
    def material(self, name: str, db: str = "SOLIDWORKS Materials.sldmat"):
        self.part.SetMaterialPropertyName2("", db, name)

    def density(self, rho_kg_m3: float):
        """Uniform document density (no library material), e.g. CFRP at 1,600 kg/m³."""
        self.model.SetUserPreferenceDoubleValue(SW_PREF_DENSITY, float(rho_kg_m3))
        self.model.ForceRebuild3(False)

    def set_mass(self, mass_kg: float):
        """Hit a target mass by setting the document density (no library material assigned),
        so mass is spread uniformly over the drawn geometry and inertia stays physical.
        (SolidWorks' mass override zeroes inertia, so it is not used.)"""
        self.model.SetUserPreferenceDoubleValue(SW_PREF_DENSITY, 1000.0)
        self.model.ForceRebuild3(False)
        vol = self.mass_props()["volume"]
        self.model.SetUserPreferenceDoubleValue(SW_PREF_DENSITY, float(mass_kg) / vol)
        self.model.ForceRebuild3(False)

    def color(self, rgb):
        """Set display color (r,g,b in 0..1)."""
        vals = self.model.MaterialPropertyValues
        vals = list(vals) if vals else [0.5] * 9
        vals[0:3] = rgb
        self.model.MaterialPropertyValues = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, vals)

    def mass_props(self) -> dict:
        return mass_props(self.model)

    def save(self, path: str):
        path = os.path.normpath(os.path.abspath(path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.ForceRebuild3(False)
        res = self.ext.SaveAs3(path, SW_SAVE_AS_CURRENT, SW_SAVE_SILENT, None, None, 0, 0)
        ok = res[0] if isinstance(res, tuple) else res
        if not ok or not os.path.exists(path):
            raise RuntimeError(f"save failed: {path} {res}")
        return path


def mass_props(model) -> dict:
    ext = typed(typed(model, "IModelDoc2").Extension, "IModelDocExtension")
    mp = typed(ext.CreateMassProperty(), "IMassProperty")
    mp.UseSystemUnits = True
    moi = list(mp.GetMomentOfInertia(0))  # about center of mass, aligned with model axes
    return dict(
        mass=mp.Mass, volume=mp.Volume, com=list(mp.CenterOfMass),
        Ixx=moi[0], Iyy=moi[4], Izz=moi[8], Ixy=moi[1], Ixz=moi[2], Iyz=moi[5],
    )


def rot_matrix(axis: str, deg: float):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return {
        "x": [[1, 0, 0], [0, c, -s], [0, s, c]],
        "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
        "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]],
    }[axis]


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


class Assembly:
    def __init__(self, sw):
        self.sw = sw
        self.model = typed(sw.NewAssembly(), "IModelDoc2")
        if self.model is None:
            raise RuntimeError("NewAssembly failed")
        self.assy = typed(self.model, "IAssemblyDoc")
        self.ext = typed(self.model.Extension, "IModelDocExtension")
        self.mu = typed(sw.GetMathUtility(), "IMathUtility")

    def add(self, part_path: str, pos=(0, 0, 0), rot=None):
        """Insert a saved part/assembly with its origin at `pos` and 3x3 rotation `rot`
        (columns = component axes expressed in assembly frame)."""
        part_path = os.path.normpath(os.path.abspath(part_path))
        comp = typed(self.assy.AddComponent5(part_path, 0, "", False, "", 0.0, 0.0, 0.0), "IComponent2")
        if comp is None:
            raise RuntimeError(f"AddComponent5 failed: {part_path}")
        r = rot or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        # SolidWorks transform array: 9 rotation terms (row-major of R^T), 3 translation, scale, 3 unused
        data = [r[0][0], r[1][0], r[2][0], r[0][1], r[1][1], r[2][1], r[0][2], r[1][2], r[2][2],
                float(pos[0]), float(pos[1]), float(pos[2]), 1.0, 0.0, 0.0, 0.0]
        xf = self.mu.CreateTransform(VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
        comp.Transform2 = xf
        return comp

    def box(self):
        b = list(self.assy.GetBox(0))
        return dict(min=b[0:3], max=b[3:6], size=[b[3] - b[0], b[4] - b[1], b[5] - b[2]])

    def mass_props(self) -> dict:
        self.model.ForceRebuild3(False)
        return mass_props(self.model)

    def save(self, path: str):
        path = os.path.normpath(os.path.abspath(path))
        self.model.ForceRebuild3(False)
        res = self.ext.SaveAs3(path, SW_SAVE_AS_CURRENT, SW_SAVE_SILENT, None, None, 0, 0)
        ok = res[0] if isinstance(res, tuple) else res
        if not ok:
            raise RuntimeError(f"save failed: {path} {res}")
        return path


def close_all(sw, titles):
    for t in titles:
        sw.CloseDoc(t)


def close_matching(sw, folder: str | None = None, untitled: bool = True) -> list[str]:
    """Close open docs saved under `folder` and/or untitled new docs. Assemblies first so parts release."""
    folder = os.path.normcase(os.path.normpath(folder)) if folder else None
    docs = [typed(d, "IModelDoc2") for d in (sw.GetDocuments() or [])]
    docs.sort(key=lambda d: 0 if d.GetType() == SW_DOC_ASSEMBLY else 1)
    closed = []
    for d in docs:
        path, title = d.GetPathName(), d.GetTitle()
        mine = (folder and path and os.path.normcase(path).startswith(folder)) or (untitled and not path)
        if mine:
            sw.CloseDoc(title)
            closed.append(title)
    return closed
