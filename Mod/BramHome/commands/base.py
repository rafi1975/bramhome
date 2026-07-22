# SPDX-License-Identifier: LGPL-2.1-or-later
"""Command registration helpers and shared create flow."""

from __future__ import annotations

import os

import FreeCAD as App
import FreeCADGui as Gui

from ..taskpanels.dimensions import DimensionTaskPanel
from ..utils import ensure_document, recompute

_ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Resources", "icons")


def icon_path(name):
    return os.path.join(_ICON_DIR, name)


def apply_lengths(obj, mapping):
    for prop, value in mapping.items():
        if hasattr(obj, prop):
            setattr(obj, prop, value)


def open_dimension_dialog(title, fields, factory, prop_map):
    """
    factory(doc) -> FeaturePython object
    prop_map: dict field_key -> object property name
    """

    def on_accept(values):
        doc = ensure_document()
        obj = factory(doc)
        apply_lengths(obj, {prop_map[k]: values[k] for k in prop_map if k in values})
        recompute(doc)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(obj)
        App.Console.PrintMessage(f"BramHome: created {obj.Label}\n")

    panel = DimensionTaskPanel(title, fields, on_accept)
    Gui.Control.showDialog(panel)


class _Command:
    def __init__(self, name, menu, tooltip, icon, pixmap_fallback="bramhome.svg"):
        self._name = name
        self._menu = menu
        self._tooltip = tooltip
        self._icon = icon
        self._pixmap_fallback = pixmap_fallback

    def GetResources(self):
        path = icon_path(self._icon)
        if not os.path.exists(path):
            path = icon_path(self._pixmap_fallback)
        return {
            "Pixmap": path,
            "MenuText": self._menu,
            "ToolTip": self._tooltip,
        }

    def IsActive(self):
        return True

    def Activated(self):
        raise NotImplementedError
