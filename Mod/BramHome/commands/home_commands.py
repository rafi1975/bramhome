# SPDX-License-Identifier: LGPL-2.1-or-later
"""Home layout commands."""

from __future__ import annotations

import FreeCADGui as Gui

from .base import _Command, open_dimension_dialog
from ..models import home as home_models


class CmdRoom(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_Room",
            "Room",
            "Create a parametric room (floor + walls)",
            "room.svg",
        )

    def Activated(self):
        open_dimension_dialog(
            "New Room",
            [
                {"key": "length", "label": "Length", "value": 4000, "minimum": 500},
                {"key": "width", "label": "Width", "value": 3000, "minimum": 500},
                {"key": "height", "label": "Height", "value": 2700, "minimum": 500},
                {"key": "wall", "label": "Wall thickness", "value": 150, "minimum": 50},
                {"key": "floor", "label": "Floor thickness", "value": 50, "minimum": 10},
            ],
            home_models.make_room,
            {
                "length": "Length",
                "width": "Width",
                "height": "Height",
                "wall": "WallThickness",
                "floor": "FloorThickness",
            },
        )


class CmdWall(_Command):
    def __init__(self):
        super().__init__("BramHome_Wall", "Wall", "Create a parametric wall", "wall.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Wall",
            [
                {"key": "length", "label": "Length", "value": 4000, "minimum": 100},
                {"key": "thickness", "label": "Thickness", "value": 150, "minimum": 50},
                {"key": "height", "label": "Height", "value": 2700, "minimum": 500},
            ],
            home_models.make_wall,
            {"length": "Length", "thickness": "Thickness", "height": "Height"},
        )


class CmdFloorPlan(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_FloorPlan",
            "Floor plan",
            "Create a building footprint with exterior walls",
            "floorplan.svg",
        )

    def Activated(self):
        open_dimension_dialog(
            "New Floor Plan",
            [
                {"key": "length", "label": "Building length", "value": 12000, "minimum": 1000},
                {"key": "width", "label": "Building width", "value": 8000, "minimum": 1000},
                {"key": "slab", "label": "Slab thickness", "value": 200, "minimum": 50},
                {"key": "wall_h", "label": "Wall height", "value": 2700, "minimum": 500},
                {"key": "wall_t", "label": "Wall thickness", "value": 200, "minimum": 50},
            ],
            home_models.make_floor_plan,
            {
                "length": "Length",
                "width": "Width",
                "slab": "SlabThickness",
                "wall_h": "WallHeight",
                "wall_t": "WallThickness",
            },
        )


class CmdDoor(_Command):
    def __init__(self):
        super().__init__("BramHome_Door", "Door", "Create a parametric door + frame", "door.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Door",
            [
                {"key": "width", "label": "Opening width", "value": 900, "minimum": 400},
                {"key": "height", "label": "Opening height", "value": 2100, "minimum": 600},
                {"key": "thickness", "label": "Leaf thickness", "value": 40, "minimum": 20},
                {"key": "frame_w", "label": "Frame width", "value": 60, "minimum": 20},
                {"key": "frame_d", "label": "Frame depth", "value": 100, "minimum": 40},
            ],
            home_models.make_door,
            {
                "width": "Width",
                "height": "Height",
                "thickness": "Thickness",
                "frame_w": "FrameWidth",
                "frame_d": "FrameDepth",
            },
        )


class CmdWindow(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_Window", "Window", "Create a parametric window", "window.svg"
        )

    def Activated(self):
        open_dimension_dialog(
            "New Window",
            [
                {"key": "width", "label": "Width", "value": 1200, "minimum": 300},
                {"key": "height", "label": "Height", "value": 1400, "minimum": 300},
                {"key": "frame_w", "label": "Frame width", "value": 50, "minimum": 20},
                {"key": "frame_d", "label": "Frame depth", "value": 80, "minimum": 30},
                {"key": "glass", "label": "Glass thickness", "value": 6, "minimum": 2},
                {"key": "mullion", "label": "Mullion width", "value": 40, "minimum": 10},
            ],
            home_models.make_window,
            {
                "width": "Width",
                "height": "Height",
                "frame_w": "FrameWidth",
                "frame_d": "FrameDepth",
                "glass": "GlassThickness",
                "mullion": "MullionWidth",
            },
        )


def register():
    Gui.addCommand("BramHome_Room", CmdRoom())
    Gui.addCommand("BramHome_Wall", CmdWall())
    Gui.addCommand("BramHome_FloorPlan", CmdFloorPlan())
    Gui.addCommand("BramHome_Door", CmdDoor())
    Gui.addCommand("BramHome_Window", CmdWindow())
