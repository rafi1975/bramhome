# SPDX-License-Identifier: LGPL-2.1-or-later
"""Parametric furniture: table, chair, cabinet, bed, shelf."""

from __future__ import annotations

import FreeCAD as App

from ..utils import fuse_shapes, make_box, set_shape


def _add_length(obj, name, default_mm, group, tip):
    if not hasattr(obj, name):
        obj.addProperty("App::PropertyLength", name, group, tip)
        setattr(obj, name, default_mm)


def _add_int(obj, name, default, group, tip):
    if not hasattr(obj, name):
        obj.addProperty("App::PropertyInteger", name, group, tip)
        setattr(obj, name, default)


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


# --- Table ------------------------------------------------------------------

class TableProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "Length", 1600, "Dimensions", "Tabletop length")
        _add_length(obj, "Width", 900, "Dimensions", "Tabletop width")
        _add_length(obj, "Height", 750, "Dimensions", "Overall height")
        _add_length(obj, "TopThickness", 30, "Dimensions", "Tabletop thickness")
        _add_length(obj, "LegSection", 60, "Dimensions", "Square leg section")
        _add_length(obj, "LegInset", 50, "Dimensions", "Leg inset from edges")

    def execute(self, obj):
        L = float(obj.Length)
        W = float(obj.Width)
        H = float(obj.Height)
        tt = float(obj.TopThickness)
        ls = float(obj.LegSection)
        inset = float(obj.LegInset)
        leg_h = max(H - tt, 1)

        top = make_box(L, W, tt)
        top.translate(App.Vector(0, 0, leg_h))

        legs = []
        positions = [
            (inset, inset),
            (L - inset - ls, inset),
            (inset, W - inset - ls),
            (L - inset - ls, W - inset - ls),
        ]
        for x, y in positions:
            leg = make_box(ls, ls, leg_h)
            leg.translate(App.Vector(x, y, 0))
            legs.append(leg)

        set_shape(obj, fuse_shapes([top] + legs))


def make_table(doc, name="Table"):
    obj = doc.addObject("Part::FeaturePython", name)
    TableProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "table")
    return obj


# --- Chair ------------------------------------------------------------------

class ChairProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "SeatWidth", 450, "Dimensions", "Seat width")
        _add_length(obj, "SeatDepth", 420, "Dimensions", "Seat depth")
        _add_length(obj, "SeatHeight", 450, "Dimensions", "Seat height from floor")
        _add_length(obj, "BackHeight", 400, "Dimensions", "Backrest height above seat")
        _add_length(obj, "SeatThickness", 25, "Dimensions", "Seat thickness")
        _add_length(obj, "BackThickness", 20, "Dimensions", "Backrest thickness")
        _add_length(obj, "LegSection", 40, "Dimensions", "Leg section")

    def execute(self, obj):
        sw = float(obj.SeatWidth)
        sd = float(obj.SeatDepth)
        sh = float(obj.SeatHeight)
        bh = float(obj.BackHeight)
        st = float(obj.SeatThickness)
        bt = float(obj.BackThickness)
        ls = float(obj.LegSection)

        seat = make_box(sw, sd, st)
        seat.translate(App.Vector(0, 0, sh - st))

        back = make_box(sw, bt, bh)
        back.translate(App.Vector(0, sd - bt, sh))

        legs = []
        for x, y in [
            (10, 10),
            (sw - ls - 10, 10),
            (10, sd - ls - 10),
            (sw - ls - 10, sd - ls - 10),
        ]:
            leg = make_box(ls, ls, sh - st)
            leg.translate(App.Vector(x, y, 0))
            legs.append(leg)

        set_shape(obj, fuse_shapes([seat, back] + legs))


def make_chair(doc, name="Chair"):
    obj = doc.addObject("Part::FeaturePython", name)
    ChairProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "chair")
    return obj


# --- Cabinet ----------------------------------------------------------------

class CabinetProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "Width", 800, "Dimensions", "Cabinet width")
        _add_length(obj, "Depth", 400, "Dimensions", "Cabinet depth")
        _add_length(obj, "Height", 900, "Dimensions", "Cabinet height")
        _add_length(obj, "PanelThickness", 18, "Dimensions", "Panel thickness")
        _add_int(obj, "Shelves", 2, "Dimensions", "Number of interior shelves")
        _add_length(obj, "ToeKick", 80, "Dimensions", "Toe-kick height")

    def execute(self, obj):
        W = float(obj.Width)
        D = float(obj.Depth)
        H = float(obj.Height)
        T = float(obj.PanelThickness)
        kick = float(obj.ToeKick)
        n = max(int(obj.Shelves), 0)

        left = make_box(T, D, H - kick)
        left.translate(App.Vector(0, 0, kick))
        right = make_box(T, D, H - kick)
        right.translate(App.Vector(W - T, 0, kick))
        bottom = make_box(W, D, T)
        bottom.translate(App.Vector(0, 0, kick))
        top = make_box(W, D, T)
        top.translate(App.Vector(0, 0, H - T))
        back = make_box(W, T, H - kick)
        back.translate(App.Vector(0, D - T, kick))

        parts = [left, right, bottom, top, back]
        usable = H - kick - 2 * T
        if n > 0 and usable > 0:
            step = usable / (n + 1)
            for i in range(1, n + 1):
                z = kick + T + i * step - T / 2
                shelf = make_box(max(W - 2 * T, 1), max(D - T, 1), T)
                shelf.translate(App.Vector(T, 0, z))
                parts.append(shelf)

        if kick > 0:
            toe = make_box(W, max(D - 40, 1), kick)
            parts.append(toe)

        set_shape(obj, fuse_shapes(parts))


def make_cabinet(doc, name="Cabinet"):
    obj = doc.addObject("Part::FeaturePython", name)
    CabinetProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "cabinet")
    return obj


# --- Bed --------------------------------------------------------------------

class BedProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "Length", 2000, "Dimensions", "Mattress length")
        _add_length(obj, "Width", 1600, "Dimensions", "Mattress width")
        _add_length(obj, "MattressHeight", 200, "Dimensions", "Mattress thickness")
        _add_length(obj, "FrameHeight", 300, "Dimensions", "Frame top height")
        _add_length(obj, "FrameThickness", 40, "Dimensions", "Frame rail thickness")
        _add_length(obj, "HeadboardHeight", 900, "Dimensions", "Headboard overall height")
        _add_length(obj, "HeadboardThickness", 30, "Dimensions", "Headboard thickness")
        _add_length(obj, "LegSection", 60, "Dimensions", "Leg section")

    def execute(self, obj):
        L = float(obj.Length)
        W = float(obj.Width)
        mh = float(obj.MattressHeight)
        fh = float(obj.FrameHeight)
        ft = float(obj.FrameThickness)
        hh = float(obj.HeadboardHeight)
        ht = float(obj.HeadboardThickness)
        ls = float(obj.LegSection)

        # Platform / rails
        left = make_box(ft, L, fh)
        right = make_box(ft, L, fh)
        right.translate(App.Vector(W - ft, 0, 0))
        foot = make_box(W, ft, fh)
        head_rail = make_box(W, ft, fh)
        head_rail.translate(App.Vector(0, L - ft, 0))
        deck = make_box(max(W - 2 * ft, 1), max(L - 2 * ft, 1), 20)
        deck.translate(App.Vector(ft, ft, fh - 20))

        mattress = make_box(W - 20, L - 20, mh)
        mattress.translate(App.Vector(10, 10, fh))

        headboard = make_box(W, ht, hh)
        headboard.translate(App.Vector(0, L, 0))

        legs = []
        for x, y in [(0, 0), (W - ls, 0), (0, L - ls), (W - ls, L - ls)]:
            leg = make_box(ls, ls, fh)
            leg.translate(App.Vector(x, y, 0))
            legs.append(leg)

        set_shape(
            obj,
            fuse_shapes([left, right, foot, head_rail, deck, mattress, headboard] + legs),
        )


def make_bed(doc, name="Bed"):
    obj = doc.addObject("Part::FeaturePython", name)
    BedProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "bed")
    return obj


# --- Shelf unit -------------------------------------------------------------

class ShelfProxy(_BaseProxy):
    def _setup(self, obj):
        _add_length(obj, "Width", 1000, "Dimensions", "Unit width")
        _add_length(obj, "Depth", 300, "Dimensions", "Shelf depth")
        _add_length(obj, "Height", 1800, "Dimensions", "Overall height")
        _add_length(obj, "Thickness", 20, "Dimensions", "Shelf/side thickness")
        _add_int(obj, "Shelves", 5, "Dimensions", "Number of shelves (incl. top/bottom)")

    def execute(self, obj):
        W = float(obj.Width)
        D = float(obj.Depth)
        H = float(obj.Height)
        T = float(obj.Thickness)
        n = max(int(obj.Shelves), 2)

        left = make_box(T, D, H)
        right = make_box(T, D, H)
        right.translate(App.Vector(W - T, 0, 0))

        parts = [left, right]
        span = H - T
        for i in range(n):
            z = 0 if i == 0 else (span * i / (n - 1))
            shelf = make_box(max(W - 2 * T, 1), D, T)
            shelf.translate(App.Vector(T, 0, z))
            parts.append(shelf)

        set_shape(obj, fuse_shapes(parts))


def make_shelf(doc, name="Shelf"):
    obj = doc.addObject("Part::FeaturePython", name)
    ShelfProxy(obj)
    if App.GuiUp:
        from ..viewproviders import ViewProviderBramHome
        ViewProviderBramHome(obj.ViewObject, "shelf")
    return obj
