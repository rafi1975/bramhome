# SPDX-License-Identifier: LGPL-2.1-or-later
"""Shared helpers for BramHome parametric objects."""

from __future__ import annotations

import FreeCAD as App
import Part


def ensure_document():
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("BramHome")
    return doc


def make_box(length, width, height, placement=None):
    solid = Part.makeBox(float(length), float(width), float(height))
    if placement is not None:
        solid.Placement = placement
    return solid


def make_cylinder(radius, height, placement=None):
    solid = Part.makeCylinder(float(radius), float(height))
    if placement is not None:
        solid.Placement = placement
    return solid


def fuse_shapes(shapes):
    shapes = [s for s in shapes if s is not None]
    if not shapes:
        return Part.Shape()
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    if hasattr(result, "removeSplitter"):
        try:
            result = result.removeSplitter()
        except Exception:
            pass
    return result


def cut_shapes(base, tools):
    result = base
    for tool in tools:
        if tool is not None:
            result = result.cut(tool)
    return result


def set_shape(obj, shape):
    obj.Shape = shape
    if hasattr(obj, "ViewObject") and obj.ViewObject is not None:
        obj.ViewObject.DisplayMode = "Flat Lines"


def recompute(doc=None):
    doc = doc or App.ActiveDocument
    if doc is not None:
        doc.recompute()
