# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric home-layout objects: room, wall, floor plan, door, window."""

from __future__ import annotations

import FreeCAD as App
import Part

from ..utils import fuse_shapes, make_box, set_shape


def _proxy_cls(name, execute_fn, props_fn):
    class Proxy:
        def __init__(self, obj):
            obj.Proxy = self
            props_fn(obj)

        def execute(self, obj):
            execute_fn(obj)

        def onChanged(self, obj, prop):
            pass

        def __getstate__(self):
            return None

        def __setstate__(self, _state):
            return None

    Proxy.__name__ = name
    Proxy.__qualname__ = name
    return Proxy


def _add_length(obj, name, default_mm, group, tip):
    if not hasattr(obj, name):
        obj.addProperty("App::PropertyLength", name, group, tip)
        setattr(obj, name, default_mm)


# --- Room shell (floor + 4 walls) -------------------------------------------

def _room_props(obj):
    _add_length(obj, "Length", 4000, "Dimensions", "Room length (X)")
    _add_length(obj, "Width", 3000, "Dimensions", "Room width (Y)")
    _add_length(obj, "Height", 2700, "Dimensions", "Wall height (Z)")
    _add_length(obj, "WallThickness", 150, "Dimensions", "Wall thickness")
    _add_length(obj, "FloorThickness", 50, "Dimensions", "Floor slab thickness")


def _room_execute(obj):
    L = float(obj.Length)
    W = float(obj.Width)
    H = float(obj.Height)
    T = float(obj.WallThickness)
    F = float(obj.FloorThickness)

    floor = make_box(L, W, F)
    # Outer box minus inner void for walls sitting on floor
    outer = make_box(L, W, H)
    outer.translate(App.Vector(0, 0, F))
    inner = make_box(max(L - 2 * T, 1), max(W - 2 * T, 1), H + 1)
    inner.translate(App.Vector(T, T, F))
    walls = outer.cut(inner)
    set_shape(obj, fuse_shapes([floor, walls]))


RoomProxy = _proxy_cls("RoomProxy", _room_execute, _room_props)


def make_room(doc, name="Room"):
    obj = doc.addObject("Part::FeaturePython", name)
    RoomProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "room")
    return obj


# --- Single wall ------------------------------------------------------------

def _wall_props(obj):
    _add_length(obj, "Length", 4000, "Dimensions", "Wall length")
    _add_length(obj, "Thickness", 150, "Dimensions", "Wall thickness")
    _add_length(obj, "Height", 2700, "Dimensions", "Wall height")


def _wall_execute(obj):
    set_shape(obj, make_box(float(obj.Length), float(obj.Thickness), float(obj.Height)))


WallProxy = _proxy_cls("WallProxy", _wall_execute, _wall_props)


def make_wall(doc, name="Wall"):
    obj = doc.addObject("Part::FeaturePython", name)
    WallProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "wall")
    return obj


# --- Floor plan footprint (2.5D slab with optional rooms as boxes) ----------

def _floorplan_props(obj):
    _add_length(obj, "Length", 12000, "Dimensions", "Overall building length")
    _add_length(obj, "Width", 8000, "Dimensions", "Overall building width")
    _add_length(obj, "SlabThickness", 200, "Dimensions", "Floor slab thickness")
    _add_length(obj, "WallHeight", 2700, "Dimensions", "Exterior wall height")
    _add_length(obj, "WallThickness", 200, "Dimensions", "Exterior wall thickness")


def _floorplan_execute(obj):
    L = float(obj.Length)
    W = float(obj.Width)
    S = float(obj.SlabThickness)
    H = float(obj.WallHeight)
    T = float(obj.WallThickness)

    slab = make_box(L, W, S)
    outer = make_box(L, W, H)
    outer.translate(App.Vector(0, 0, S))
    inner = make_box(max(L - 2 * T, 1), max(W - 2 * T, 1), H + 1)
    inner.translate(App.Vector(T, T, S))
    walls = outer.cut(inner)
    set_shape(obj, fuse_shapes([slab, walls]))


FloorPlanProxy = _proxy_cls("FloorPlanProxy", _floorplan_execute, _floorplan_props)


def make_floor_plan(doc, name="FloorPlan"):
    obj = doc.addObject("Part::FeaturePython", name)
    FloorPlanProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "floorplan")
    return obj


# --- Door opening block (subtractive-friendly solid / frame) ----------------

def _door_props(obj):
    _add_length(obj, "Width", 900, "Dimensions", "Clear opening width")
    _add_length(obj, "Height", 2100, "Dimensions", "Clear opening height")
    _add_length(obj, "Thickness", 40, "Dimensions", "Door leaf thickness")
    _add_length(obj, "FrameWidth", 60, "Dimensions", "Frame profile width")
    _add_length(obj, "FrameDepth", 100, "Dimensions", "Frame depth (into wall)")


def _door_execute(obj):
    w = float(obj.Width)
    h = float(obj.Height)
    t = float(obj.Thickness)
    fw = float(obj.FrameWidth)
    fd = float(obj.FrameDepth)

    # Outer frame envelope
    outer = make_box(w + 2 * fw, fd, h + fw)
    void = make_box(w, fd + 2, h)
    void.translate(App.Vector(fw, -1, 0))
    frame = outer.cut(void)

    leaf = make_box(w - 4, t, h - 4)
    leaf.translate(App.Vector(fw + 2, (fd - t) / 2, 2))
    set_shape(obj, fuse_shapes([frame, leaf]))


DoorProxy = _proxy_cls("DoorProxy", _door_execute, _door_props)


def make_door(doc, name="Door"):
    obj = doc.addObject("Part::FeaturePython", name)
    DoorProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "door")
    return obj


# --- Window -----------------------------------------------------------------

def _window_props(obj):
    _add_length(obj, "Width", 1200, "Dimensions", "Window width")
    _add_length(obj, "Height", 1400, "Dimensions", "Window height")
    _add_length(obj, "FrameWidth", 50, "Dimensions", "Frame profile width")
    _add_length(obj, "FrameDepth", 80, "Dimensions", "Frame depth")
    _add_length(obj, "GlassThickness", 6, "Dimensions", "Glass thickness")
    _add_length(obj, "MullionWidth", 40, "Dimensions", "Center mullion width")


def _window_execute(obj):
    w = float(obj.Width)
    h = float(obj.Height)
    fw = float(obj.FrameWidth)
    fd = float(obj.FrameDepth)
    gt = float(obj.GlassThickness)
    mw = float(obj.MullionWidth)

    outer = make_box(w, fd, h)
    void = make_box(max(w - 2 * fw, 1), fd + 2, max(h - 2 * fw, 1))
    void.translate(App.Vector(fw, -1, fw))
    frame = outer.cut(void)

    mullion = make_box(mw, fd, max(h - 2 * fw, 1))
    mullion.translate(App.Vector((w - mw) / 2, 0, fw))

    glass = make_box(max(w - 2 * fw, 1), gt, max(h - 2 * fw, 1))
    glass.translate(App.Vector(fw, (fd - gt) / 2, fw))

    set_shape(obj, fuse_shapes([frame, mullion, glass]))


WindowProxy = _proxy_cls("WindowProxy", _window_execute, _window_props)


def make_window(doc, name="Window"):
    obj = doc.addObject("Part::FeaturePython", name)
    WindowProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "window")
    return obj
