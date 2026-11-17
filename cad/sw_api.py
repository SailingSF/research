"""A thin wrapper around the SolidWorks COM API (SolidWorks 2026, driven through pywin32).

It offers just enough to build the Part 2 satellite: parts made of boxes, cylinders and
square tubes; assemblies that place saved parts at a position and rotation; and mass
properties read back from either.

Units are SI throughout (meters, kilograms), whatever the document displays.

Model axes, matching SolidWorks' defaults:
    +X = direction of travel
    +Y = zenith (away from Earth); also the Starship axis when stowed
    +Z = orbit normal = toward the Sun in a dawn-dusk orbit
"""
import math
import os
from typing import NamedTuple

import pythoncom
import win32com.client
from win32com.client import VARIANT, gencache

# SolidWorks 2026 type library. Loading it gives early-bound classes (see _typed below).
_sw = gencache.EnsureModule("{83A33D31-27C5-11CE-BFD4-00400513BB57}", 0, 34, 0)

# SolidWorks API constants used below
_END_BLIND = 0                          # extrude a fixed distance
_START_AT_SKETCH, _START_AT_OFFSET = 0, 3
_SAVE_AS_CURRENT_VERSION, _SAVE_SILENTLY = 0, 1
_DOC_ASSEMBLY = 2
_DENSITY_PREFERENCE = 7                 # document density, used when no library material is assigned
_TRANSPARENCY = 7                       # index of transparency in a document's appearance values
_THIS_DISPLAY_STATE = 1                 # apply an appearance to the active display state
_SOLID_BODY = 0
_LIGHT_DIRECTIONAL = 4
_DIRECTIONAL_LIGHT_NAME = "Directional-1"   # SolidWorks' internal name for directional lights


# ---- Shapes: the whole satellite is drawn from these three primitives ---------------------
class Box(NamedTuple):
    center: tuple          # (x, y, z)
    size: tuple            # (size_x, size_y, size_z)


class Cylinder(NamedTuple):
    axis: str              # "x", "y" or "z"
    center: tuple
    radius: float
    length: float
    inner_radius: float = 0.0   # > 0 makes a round tube


class SquareTube(NamedTuple):
    axis: str
    center: tuple
    outer: float           # outside width
    wall: float            # wall thickness
    length: float


# ---- COM plumbing --------------------------------------------------------------------------
def _typed(obj, interface: str):
    """Cast a COM object to a named SolidWorks interface (pywin32 can't always infer it)."""
    if obj is None:
        return None
    return getattr(_sw, interface)(getattr(obj, "_oleobj_", obj))


def _doubles(values):
    """Pack numbers the way SolidWorks expects array arguments."""
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in values])


def connect():
    """Attach to the SolidWorks session that is already open."""
    return _typed(win32com.client.GetActiveObject("SldWorks.Application"), "ISldWorks")


def _save(model, path) -> str:
    """Save a document; the file extension picks the format (.SLDPRT, .SLDASM, .jpg)."""
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    extension = _typed(model.Extension, "IModelDocExtension")
    extension.SaveAs3(path, _SAVE_AS_CURRENT_VERSION, _SAVE_SILENTLY, None, None, 0, 0)
    if not os.path.exists(path):
        raise RuntimeError(f"SolidWorks did not save {path}")
    return path


def mass_properties(model) -> dict:
    """Mass [kg], volume [m³], center of mass [m], and inertia about it [kg·m²] in model axes."""
    props = _typed(_typed(model.Extension, "IModelDocExtension").CreateMassProperty(), "IMassProperty")
    props.UseSystemUnits = True
    inertia = list(props.GetMomentOfInertia(0))     # 3×3 tensor, row by row
    return dict(mass=props.Mass, volume=props.Volume, com=list(props.CenterOfMass),
                Ixx=inertia[0], Iyy=inertia[4], Izz=inertia[8],
                Ixy=inertia[1], Ixz=inertia[2], Iyz=inertia[5])


# To extrude along a model axis, we sketch on the principal plane perpendicular to it. Each
# entry names that plane and maps a model point to (sketch u, sketch v, depth along the axis).
_SKETCH_PLANE = {
    "z": ("Front Plane", lambda x, y, z: (x, y, z)),
    "y": ("Top Plane",   lambda x, y, z: (x, -z, y)),
    "x": ("Right Plane", lambda x, y, z: (-z, y, x)),
}


class Part:
    """A new part document, built up by adding shapes."""

    def __init__(self, sw):
        self.model = _typed(sw.NewPart(), "IModelDoc2")
        if self.model is None:
            raise RuntimeError("SolidWorks could not create a part")
        self._sketch = _typed(self.model.SketchManager, "ISketchManager")
        self._sketch.AddToDB = True     # write sketch geometry directly, with no snapping

    def add(self, shape):
        """Add a Box, Cylinder or SquareTube. Overlapping shapes merge into one solid."""
        if isinstance(shape, Box):
            (x, y, z), (sx, sy, sz) = shape.center, shape.size
            self._extrude("z", (x, y, z), sz, lambda u, v: self._rectangle(u, v, sx / 2, sy / 2))
        elif isinstance(shape, Cylinder):
            def profile(u, v):
                self._sketch.CreateCircleByRadius(u, v, 0, shape.radius)
                if shape.inner_radius > 0:
                    self._sketch.CreateCircleByRadius(u, v, 0, shape.inner_radius)
            self._extrude(shape.axis, shape.center, shape.length, profile)
        elif isinstance(shape, SquareTube):
            def profile(u, v):
                for half_width in (shape.outer / 2, shape.outer / 2 - shape.wall):
                    self._rectangle(u, v, half_width, half_width)
            self._extrude(shape.axis, shape.center, shape.length, profile)
        else:
            raise TypeError(f"unknown shape: {shape!r}")

    def _rectangle(self, u, v, half_u, half_v):
        self._sketch.CreateCornerRectangle(u - half_u, v - half_v, 0, u + half_u, v + half_v, 0)

    def _extrude(self, axis, center, length, draw_profile):
        """Sketch a closed profile on the plane normal to `axis`, then extrude it `length`,
        centered on `center`."""
        plane, to_sketch = _SKETCH_PLANE[axis]
        u, v, depth = to_sketch(*center)
        start = depth - length / 2      # the extrusion starts this far from the sketch plane
        self.model.ClearSelection2(True)
        if not _typed(self.model.Extension, "IModelDocExtension").SelectByID2(
                plane, "PLANE", 0, 0, 0, False, 0, None, 0):
            raise RuntimeError(f"could not select {plane}")
        self._sketch.InsertSketch(True)                 # open a sketch on the selected plane
        draw_profile(u, v)
        self._sketch.InsertSketch(True)                 # close it; the sketch stays selected
        start_type = _START_AT_OFFSET if abs(start) > 1e-12 else _START_AT_SKETCH
        feature = _typed(self.model.FeatureManager, "IFeatureManager").FeatureExtrusion3(
            True, False, False, _END_BLIND, _END_BLIND, float(length), 0.0,
            False, False, False, False, 0.0, 0.0, False, False, False, False,
            True, True, True, start_type, abs(start), start < 0)
        if feature is None:
            raise RuntimeError(f"extrude along {axis} failed")
        self.model.ClearSelection2(True)

    def set_density(self, kg_per_m3: float):
        """Uniform density, so the mass follows from the drawn geometry (used for structure)."""
        self.model.SetUserPreferenceDoubleValue(_DENSITY_PREFERENCE, float(kg_per_m3))
        self.model.ForceRebuild3(False)

    def set_mass(self, kg: float):
        """Hit a target mass by choosing the density that gives it. The mass is then spread
        evenly over the drawn shapes, which keeps the part's inertia realistic. (SolidWorks'
        own mass override would zero the inertia.)"""
        self.set_density(kg / self.mass_properties()["volume"])

    def set_color(self, rgb, transparency: float = 0.0):
        """Display color, with r, g, b and transparency each in 0..1."""
        appearance = list(self.model.MaterialPropertyValues or [0.5] * 9)
        appearance[0:3] = rgb
        appearance[_TRANSPARENCY] = transparency
        self.model.MaterialPropertyValues = _doubles(appearance)

    def set_appearance(self, p2m, tile_size: float | None = None, faces=None):
        """Apply a SolidWorks appearance (.p2m file) to the whole part, or only to `faces`.
        Appearances (unlike the display color) carry over to SolidWorks Visualize.
        `tile_size` [m] sets how much surface one copy of a texture image covers."""
        if not os.path.exists(p2m):
            raise FileNotFoundError(f"appearance not found: {p2m}")
        extension = _typed(self.model.Extension, "IModelDocExtension")
        material = _typed(extension.CreateRenderMaterial(str(p2m)), "IRenderMaterial")
        if material is None:
            raise RuntimeError(f"could not load appearance {p2m}")
        if tile_size:
            material.Width = material.Height = float(tile_size)
        for entity in faces if faces is not None else [self.model]:
            material.AddEntity(entity)
        added, *_ = extension.AddDisplayStateSpecificRenderMaterial(material, _THIS_DISPLAY_STATE, None)
        if not added:
            raise RuntimeError(f"could not apply appearance {p2m}")

    def flat_faces(self, axis: str, min_area: float) -> list:
        """Flat faces of at least `min_area` [m²] whose normal is along ±axis."""
        k = "xyz".index(axis)
        bodies = _typed(self.model, "IPartDoc").GetBodies2(_SOLID_BODY, False) or []
        faces = []
        for body in bodies:
            for face in _typed(body, "IBody2").GetFaces() or []:
                face = _typed(face, "IFace2")
                if abs(face.Normal[k]) > 0.99 and face.GetArea() >= min_area:
                    faces.append(face)
        return faces

    def mass_properties(self) -> dict:
        return mass_properties(self.model)

    def save(self, path) -> str:
        self.model.ForceRebuild3(False)
        return _save(self.model, path)


def appearance_library(sw) -> str:
    """Folder of SolidWorks' built-in appearances (.p2m files)."""
    install = sw.GetExecutablePath()            # the SOLIDWORKS install folder
    if install.lower().endswith(".exe"):
        install = os.path.dirname(install)
    return os.path.join(install, "data", "graphics", "Materials")


class Assembly:
    """A new assembly document: saved parts (or sub-assemblies) placed by position and rotation."""

    def __init__(self, sw):
        self.model = _typed(sw.NewAssembly(), "IModelDoc2")
        if self.model is None:
            raise RuntimeError("SolidWorks could not create an assembly")
        self._assembly = _typed(self.model, "IAssemblyDoc")
        self._math = _typed(sw.GetMathUtility(), "IMathUtility")

    def add(self, path, position=(0, 0, 0), rotation=None):
        """Insert the file at `path` with its origin at `position`. `rotation` is a 3×3 matrix
        (see `rotation()` below); None leaves the component's axes aligned with the assembly's."""
        path = os.path.abspath(path)
        component = _typed(self._assembly.AddComponent5(path, 0, "", False, "", 0, 0, 0), "IComponent2")
        if component is None:
            raise RuntimeError(f"could not insert {path}")
        r = rotation or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        # SolidWorks wants 16 numbers: the rotation column by column, the translation,
        # a scale factor, and three unused values.
        transform = [r[0][0], r[1][0], r[2][0], r[0][1], r[1][1], r[2][1], r[0][2], r[1][2], r[2][2],
                     *position, 1, 0, 0, 0]
        component.Transform2 = self._math.CreateTransform(_doubles(transform))

    def set_sun(self, toward_sun, intensity: float = 1.0):
        """Replace SolidWorks' default directional lights with one "Sun" light shining from
        `toward_sun` (a model-frame direction), locked to the model and enabled for rendering.
        SolidWorks Visualize imports it as a directional light."""
        for i in reversed(range(self.model.GetLightSourceCount())):
            if self.model.GetLightSourceName(i).startswith("Directional"):
                self.model.DeleteLightSource(i)
        self.model.AddLightSource(_DIRECTIONAL_LIGHT_NAME, _LIGHT_DIRECTIONAL, "Sun")
        x, y, z = (float(v) for v in toward_sun)
        # Arguments: name, type, intensity, color (0xBBGGRR), distance (must be nonzero, or
        # the direction is lost), direction, 3 spot-direction values, spot angle,
        # 3 falloff terms, ambient, specular, spot exponent, disabled.
        self.model.SetLightSourcePropertyValuesVB(_DIRECTIONAL_LIGHT_NAME, _LIGHT_DIRECTIONAL, float(intensity),
                                                  0xFFFFFF, 1.0, x, y, z, 0.0, 0.0, 0.0, 0.0,
                                                  0.0, 0.0, 0.0, 0.0, 0.5, 0.0, False)
        sun = self.model.GetLightSourceCount() - 1
        self.model.LockLightToModel(sun, True)
        _typed(self.model.Extension, "IModelDocExtension").SetLightEnabledInRender(sun, True)

    def bounding_box(self) -> dict:
        """Axis-aligned bounding box of everything in the assembly: min, max and size [m]."""
        x0, y0, z0, x1, y1, z1 = self._assembly.GetBox(0)
        return dict(min=[x0, y0, z0], max=[x1, y1, z1], size=[x1 - x0, y1 - y0, z1 - z0])

    def mass_properties(self) -> dict:
        self.model.ForceRebuild3(False)
        return mass_properties(self.model)

    def save(self, path) -> str:
        self.model.ForceRebuild3(False)
        return _save(self.model, path)

    def save_image(self, path, view: str = "*Isometric") -> str:
        """Save a picture of the assembly from a standard view."""
        self.model.ShowNamedView2(view, -1)
        self.model.ViewZoomtofit2()
        return _save(self.model, path)


def rotation(axis: str, degrees: float) -> list:
    """3×3 matrix for a right-handed rotation about a model axis."""
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return {
        "x": [[1, 0, 0], [0, c, -s], [0, s, c]],
        "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
        "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]],
    }[axis]


def close_documents_in(sw, folder) -> None:
    """Close open documents saved under `folder`, so a rebuild can overwrite their files.
    Assemblies go first, because they hold their parts open."""
    folder = os.path.normcase(os.path.abspath(folder))
    documents = [_typed(d, "IModelDoc2") for d in (sw.GetDocuments() or [])]
    documents.sort(key=lambda d: d.GetType() != _DOC_ASSEMBLY)
    # Collect the titles before closing anything: closing an assembly also closes its parts.
    titles = [d.GetTitle() for d in documents if os.path.normcase(d.GetPathName()).startswith(folder)]
    for title in titles:
        sw.CloseDoc(title)
