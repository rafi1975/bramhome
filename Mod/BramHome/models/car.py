# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric car parts: wheel, brake disc, control arm, mount bracket."""

from __future__ import annotations

import math

import FreeCAD as App
import Part

from ..utils import cut_shapes, fuse_shapes, make_box, make_cylinder, set_shape


def _add_length(obj, name, default_mm, group, tip):
    if not hasattr(obj, name):
        obj.addProperty("App::PropertyLength", name, group, tip)
        setattr(obj, name, default_mm)


def _add_int(obj, name, default, group, tip):
    if not hasattr(obj, name):
        obj.addProperty("App::PropertyInteger", name, group, tip)
        setattr(obj, name, default)


def _moved(shape, vector):
    shape = shape.copy()
    shape.translate(vector)
    return shape


def _rotated(shape, angle_deg, axis=App.Vector(0, 0, 1), center=App.Vector(0, 0, 0)):
    shape = shape.copy()
    shape.rotate(center, axis, angle_deg)
    return shape


class _BaseProxy:
    def __init__(self, obj):
        obj.Proxy = self
        self._setup(obj)

    def execute(self, obj):
        raise NotImplementedError

    def _setup(self, obj):
        raise NotImplementedError

    def __getstate__(self):
        return None

    def __setstate__(self, _state):
        return None


class WheelProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "TireOuterDiameter", 650, "Dimensions", "Tire outer diameter")
        _add_length(obj, "TireWidth", 225, "Dimensions", "Tire section width")
        _add_length(obj, "RimDiameter", 450, "Dimensions", "Rim outer diameter")
        _add_length(obj, "RimWidth", 200, "Dimensions", "Rim width")
        _add_length(obj, "HubDiameter", 60, "Dimensions", "Center hub bore diameter")
        _add_length(obj, "HubDepth", 40, "Dimensions", "Hub depth")
        _add_int(obj, "BoltCount", 5, "Dimensions", "Wheel bolt count")
        _add_length(obj, "BoltCircleDiameter", 112, "Dimensions", "PCD (bolt circle)")
        _add_length(obj, "BoltHoleDiameter", 14, "Dimensions", "Bolt hole diameter")

    def execute(self, obj):
        tod = float(obj.TireOuterDiameter)
        tw = float(obj.TireWidth)
        rd = float(obj.RimDiameter)
        rw = float(obj.RimWidth)
        hd = float(obj.HubDiameter)
        hdepth = float(obj.HubDepth)
        bolts = max(int(obj.BoltCount), 0)
        pcd = float(obj.BoltCircleDiameter)
        bhd = float(obj.BoltHoleDiameter)

        tire = make_cylinder(tod / 2, tw)
        tire = tire.cut(_moved(make_cylinder(max(rd / 2 - 10, 1), tw + 2), App.Vector(0, 0, -1)))

        rim = _moved(make_cylinder(rd / 2, rw), App.Vector(0, 0, (tw - rw) / 2))
        rim = rim.cut(
            _moved(make_cylinder(hd / 2, rw + 2), App.Vector(0, 0, (tw - rw) / 2 - 1))
        )

        hub = _moved(
            make_cylinder(max(pcd / 2 + 20, hd / 2 + 10), hdepth),
            App.Vector(0, 0, (tw - hdepth) / 2),
        )
        hub = hub.cut(
            _moved(make_cylinder(hd / 2, hdepth + 2), App.Vector(0, 0, (tw - hdepth) / 2 - 1))
        )

        holes = []
        for i in range(bolts):
            angle = 2 * math.pi * i / bolts
            x = (pcd / 2) * math.cos(angle)
            y = (pcd / 2) * math.sin(angle)
            holes.append(
                _moved(
                    make_cylinder(bhd / 2, hdepth + 2),
                    App.Vector(x, y, (tw - hdepth) / 2 - 1),
                )
            )
        if holes:
            hub = cut_shapes(hub, holes)

        set_shape(obj, fuse_shapes([tire, rim, hub]))


def make_wheel(doc, name="Wheel"):
    obj = doc.addObject("Part::FeaturePython", name)
    WheelProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome

        ViewProviderBramHome(obj.ViewObject, "wheel")
    return obj


class BrakeDiscProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "OuterDiameter", 300, "Dimensions", "Disc outer diameter")
        _add_length(obj, "Thickness", 25, "Dimensions", "Friction ring thickness")
        _add_length(obj, "InnerDiameter", 160, "Dimensions", "Friction ring inner diameter")
        _add_length(obj, "HatOuterDiameter", 150, "Dimensions", "Hat outer diameter")
        _add_length(obj, "HatHeight", 40, "Dimensions", "Hat height")
        _add_length(obj, "CenterBore", 68, "Dimensions", "Center bore diameter")
        _add_int(obj, "BoltCount", 5, "Dimensions", "Mounting bolt count")
        _add_length(obj, "BoltCircleDiameter", 112, "Dimensions", "Bolt circle diameter")
        _add_length(obj, "BoltHoleDiameter", 14, "Dimensions", "Bolt hole diameter")

    def execute(self, obj):
        od = float(obj.OuterDiameter)
        th = float(obj.Thickness)
        id_ = float(obj.InnerDiameter)
        hod = float(obj.HatOuterDiameter)
        hh = float(obj.HatHeight)
        cb = float(obj.CenterBore)
        bolts = max(int(obj.BoltCount), 0)
        pcd = float(obj.BoltCircleDiameter)
        bhd = float(obj.BoltHoleDiameter)

        ring = make_cylinder(od / 2, th)
        ring = ring.cut(_moved(make_cylinder(id_ / 2, th + 2), App.Vector(0, 0, -1)))

        hat = _moved(make_cylinder(hod / 2, hh), App.Vector(0, 0, th))
        hat = hat.cut(_moved(make_cylinder(cb / 2, hh + 2), App.Vector(0, 0, th - 1)))

        body = fuse_shapes([ring, hat])
        holes = []
        for i in range(bolts):
            angle = 2 * math.pi * i / bolts
            x = (pcd / 2) * math.cos(angle)
            y = (pcd / 2) * math.sin(angle)
            holes.append(_moved(make_cylinder(bhd / 2, hh + th + 2), App.Vector(x, y, -1)))
        if holes:
            body = cut_shapes(body, holes)
        set_shape(obj, body)


def make_brake_disc(doc, name="BrakeDisc"):
    obj = doc.addObject("Part::FeaturePython", name)
    BrakeDiscProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome

        ViewProviderBramHome(obj.ViewObject, "brakedisc")
    return obj


class ControlArmProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "Length", 350, "Dimensions", "Arm length (pivot to ball joint)")
        _add_length(obj, "Width", 180, "Dimensions", "Spread at chassis mounts")
        _add_length(obj, "Height", 40, "Dimensions", "Arm section height")
        _add_length(obj, "Thickness", 25, "Dimensions", "Arm section thickness")
        _add_length(obj, "BushingInnerDiameter", 14, "Dimensions", "Bushing ID")
        _add_length(obj, "BushingOuterDiameter", 40, "Dimensions", "Bushing OD")
        _add_length(obj, "BushingWidth", 30, "Dimensions", "Bushing width")
        _add_length(obj, "BallJointDiameter", 30, "Dimensions", "Ball joint housing OD")

    def execute(self, obj):
        L = float(obj.Length)
        W = float(obj.Width)
        H = float(obj.Height)
        T = float(obj.Thickness)
        bi = float(obj.BushingInnerDiameter)
        bo = float(obj.BushingOuterDiameter)
        bw = float(obj.BushingWidth)
        bj = float(obj.BallJointDiameter)

        half = W / 2.0
        leg_len = math.hypot(L, half)
        angle = math.degrees(math.atan2(half, L))

        def arm_leg(sign):
            box = make_box(leg_len, T, H)
            box = _moved(box, App.Vector(0, -T / 2, 0))
            return _rotated(box, sign * angle)

        def bushing(y):
            cyl = Part.makeCylinder(bo / 2, bw, App.Vector(0, y - bw / 2, H / 2), App.Vector(0, 1, 0))
            bore = Part.makeCylinder(
                bi / 2, bw + 2, App.Vector(0, y - bw / 2 - 1, H / 2), App.Vector(0, 1, 0)
            )
            return cyl.cut(bore)

        ball = Part.makeCylinder(bj / 2, H, App.Vector(L, 0, 0))
        set_shape(obj, fuse_shapes([arm_leg(1), arm_leg(-1), bushing(half), bushing(-half), ball]))


def make_control_arm(doc, name="ControlArm"):
    obj = doc.addObject("Part::FeaturePython", name)
    ControlArmProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome

        ViewProviderBramHome(obj.ViewObject, "controlarm")
    return obj


class MountBracketProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "BaseLength", 120, "Dimensions", "Base flange length")
        _add_length(obj, "BaseWidth", 80, "Dimensions", "Base flange width")
        _add_length(obj, "UprightHeight", 100, "Dimensions", "Upright flange height")
        _add_length(obj, "Thickness", 8, "Dimensions", "Plate thickness")
        _add_length(obj, "HoleDiameter", 10, "Dimensions", "Mounting hole diameter")
        _add_length(obj, "HoleEdgeOffset", 20, "Dimensions", "Hole offset from edges")
        _add_int(obj, "BaseHoleCount", 2, "Dimensions", "Holes in base flange")
        _add_int(obj, "UprightHoleCount", 2, "Dimensions", "Holes in upright flange")

    def execute(self, obj):
        bl = float(obj.BaseLength)
        bw = float(obj.BaseWidth)
        uh = float(obj.UprightHeight)
        t = float(obj.Thickness)
        hd = float(obj.HoleDiameter)
        off = float(obj.HoleEdgeOffset)
        nb = max(int(obj.BaseHoleCount), 0)
        nu = max(int(obj.UprightHoleCount), 0)

        base = make_box(bl, bw, t)
        upright = make_box(bl, t, uh)
        body = fuse_shapes([base, upright])

        holes = []
        if nb > 0:
            usable = max(bl - 2 * off, 0)
            for i in range(nb):
                x = off if nb == 1 else off + usable * i / (nb - 1)
                holes.append(_moved(make_cylinder(hd / 2, t + 2), App.Vector(x, bw / 2, -1)))

        if nu > 0:
            usable_x = max(bl - 2 * off, 0)
            usable_z = max(uh - 2 * off, 0)
            for i in range(nu):
                x = off if nu == 1 else off + usable_x * i / (nu - 1)
                z = off if nu == 1 else off + usable_z * i / (nu - 1)
                z = max(z, t + hd / 2)
                holes.append(
                    Part.makeCylinder(hd / 2, t + 2, App.Vector(x, -1, z), App.Vector(0, 1, 0))
                )

        if holes:
            body = cut_shapes(body, holes)
        set_shape(obj, body)


def make_mount_bracket(doc, name="MountBracket"):
    obj = doc.addObject("Part::FeaturePython", name)
    MountBracketProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome

        ViewProviderBramHome(obj.ViewObject, "mountbracket")
    return obj
