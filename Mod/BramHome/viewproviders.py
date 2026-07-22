# SPDX-License-Identifier: LGPL-2.1-or-later
"""ViewProviders for BramHome FeaturePython objects."""

from __future__ import annotations

import os

import FreeCADGui as Gui

_ICON_DIR = os.path.join(os.path.dirname(__file__), "Resources", "icons")

_ICON_MAP = {
    "room": "room.svg",
    "wall": "wall.svg",
    "floorplan": "floorplan.svg",
    "door": "door.svg",
    "window": "window.svg",
    "table": "table.svg",
    "chair": "chair.svg",
    "cabinet": "cabinet.svg",
    "bed": "bed.svg",
    "shelf": "shelf.svg",
    "wheel": "wheel.svg",
    "brakedisc": "brakedisc.svg",
    "controlarm": "controlarm.svg",
    "mountbracket": "mountbracket.svg",
}

_COLORS = {
    "room": (0.85, 0.82, 0.76),
    "wall": (0.78, 0.76, 0.72),
    "floorplan": (0.80, 0.78, 0.74),
    "door": (0.55, 0.35, 0.20),
    "window": (0.70, 0.85, 0.92),
    "table": (0.62, 0.42, 0.22),
    "chair": (0.45, 0.45, 0.48),
    "cabinet": (0.50, 0.38, 0.25),
    "bed": (0.75, 0.78, 0.85),
    "shelf": (0.58, 0.40, 0.24),
    "wheel": (0.20, 0.20, 0.22),
    "brakedisc": (0.45, 0.45, 0.48),
    "controlarm": (0.35, 0.38, 0.42),
    "mountbracket": (0.55, 0.55, 0.58),
}


class ViewProviderBramHome:
    def __init__(self, vobj, kind="room"):
        self.kind = kind
        vobj.Proxy = self

    def attach(self, vobj):
        self.Object = vobj.Object
        color = _COLORS.get(self.kind, (0.7, 0.7, 0.7))
        vobj.ShapeColor = color

    def getIcon(self):
        filename = _ICON_MAP.get(self.kind, "bramhome.svg")
        return os.path.join(_ICON_DIR, filename)

    def claimChildren(self):
        return []

    def __getstate__(self):
        return {"kind": getattr(self, "kind", "room")}

    def __setstate__(self, state):
        if isinstance(state, dict):
            self.kind = state.get("kind", "room")
        else:
            self.kind = "room"
