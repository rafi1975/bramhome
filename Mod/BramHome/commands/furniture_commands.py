# SPDX-License-Identifier: LGPL-2.1-or-later
"""Furniture commands."""

from __future__ import annotations

import FreeCADGui as Gui

from .base import _Command, open_dimension_dialog
from ..models import furniture as furniture_models


class CmdTable(_Command):
    def __init__(self):
        super().__init__("BramHome_Table", "Table", "Create a parametric table", "table.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Table",
            [
                {"key": "length", "label": "Length", "value": 1600, "minimum": 400},
                {"key": "width", "label": "Width", "value": 900, "minimum": 400},
                {"key": "height", "label": "Height", "value": 750, "minimum": 300},
                {"key": "top", "label": "Top thickness", "value": 30, "minimum": 10},
                {"key": "leg", "label": "Leg section", "value": 60, "minimum": 20},
                {"key": "inset", "label": "Leg inset", "value": 50, "minimum": 0},
            ],
            furniture_models.make_table,
            {
                "length": "Length",
                "width": "Width",
                "height": "Height",
                "top": "TopThickness",
                "leg": "LegSection",
                "inset": "LegInset",
            },
        )


class CmdChair(_Command):
    def __init__(self):
        super().__init__("BramHome_Chair", "Chair", "Create a parametric chair", "chair.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Chair",
            [
                {"key": "seat_w", "label": "Seat width", "value": 450, "minimum": 300},
                {"key": "seat_d", "label": "Seat depth", "value": 420, "minimum": 300},
                {"key": "seat_h", "label": "Seat height", "value": 450, "minimum": 300},
                {"key": "back_h", "label": "Back height", "value": 400, "minimum": 100},
                {"key": "seat_t", "label": "Seat thickness", "value": 25, "minimum": 10},
                {"key": "back_t", "label": "Back thickness", "value": 20, "minimum": 10},
                {"key": "leg", "label": "Leg section", "value": 40, "minimum": 15},
            ],
            furniture_models.make_chair,
            {
                "seat_w": "SeatWidth",
                "seat_d": "SeatDepth",
                "seat_h": "SeatHeight",
                "back_h": "BackHeight",
                "seat_t": "SeatThickness",
                "back_t": "BackThickness",
                "leg": "LegSection",
            },
        )


class CmdCabinet(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_Cabinet", "Cabinet", "Create a parametric cabinet", "cabinet.svg"
        )

    def Activated(self):
        open_dimension_dialog(
            "New Cabinet",
            [
                {"key": "width", "label": "Width", "value": 800, "minimum": 200},
                {"key": "depth", "label": "Depth", "value": 400, "minimum": 200},
                {"key": "height", "label": "Height", "value": 900, "minimum": 400},
                {"key": "panel", "label": "Panel thickness", "value": 18, "minimum": 8},
                {
                    "key": "shelves",
                    "label": "Interior shelves",
                    "value": 2,
                    "minimum": 0,
                    "maximum": 20,
                    "integer": True,
                },
                {"key": "kick", "label": "Toe-kick height", "value": 80, "minimum": 0},
            ],
            furniture_models.make_cabinet,
            {
                "width": "Width",
                "depth": "Depth",
                "height": "Height",
                "panel": "PanelThickness",
                "shelves": "Shelves",
                "kick": "ToeKick",
            },
        )


class CmdBed(_Command):
    def __init__(self):
        super().__init__("BramHome_Bed", "Bed", "Create a parametric bed", "bed.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Bed",
            [
                {"key": "length", "label": "Mattress length", "value": 2000, "minimum": 1500},
                {"key": "width", "label": "Mattress width", "value": 1600, "minimum": 800},
                {"key": "matt_h", "label": "Mattress height", "value": 200, "minimum": 80},
                {"key": "frame_h", "label": "Frame height", "value": 300, "minimum": 150},
                {"key": "frame_t", "label": "Frame thickness", "value": 40, "minimum": 20},
                {"key": "head_h", "label": "Headboard height", "value": 900, "minimum": 400},
                {"key": "head_t", "label": "Headboard thickness", "value": 30, "minimum": 15},
                {"key": "leg", "label": "Leg section", "value": 60, "minimum": 30},
            ],
            furniture_models.make_bed,
            {
                "length": "Length",
                "width": "Width",
                "matt_h": "MattressHeight",
                "frame_h": "FrameHeight",
                "frame_t": "FrameThickness",
                "head_h": "HeadboardHeight",
                "head_t": "HeadboardThickness",
                "leg": "LegSection",
            },
        )


class CmdShelf(_Command):
    def __init__(self):
        super().__init__("BramHome_Shelf", "Shelf", "Create a parametric shelf unit", "shelf.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Shelf",
            [
                {"key": "width", "label": "Width", "value": 1000, "minimum": 200},
                {"key": "depth", "label": "Depth", "value": 300, "minimum": 100},
                {"key": "height", "label": "Height", "value": 1800, "minimum": 400},
                {"key": "thickness", "label": "Thickness", "value": 20, "minimum": 8},
                {
                    "key": "shelves",
                    "label": "Shelf count",
                    "value": 5,
                    "minimum": 2,
                    "maximum": 30,
                    "integer": True,
                },
            ],
            furniture_models.make_shelf,
            {
                "width": "Width",
                "depth": "Depth",
                "height": "Height",
                "thickness": "Thickness",
                "shelves": "Shelves",
            },
        )


def register():
    Gui.addCommand("BramHome_Table", CmdTable())
    Gui.addCommand("BramHome_Chair", CmdChair())
    Gui.addCommand("BramHome_Cabinet", CmdCabinet())
    Gui.addCommand("BramHome_Bed", CmdBed())
    Gui.addCommand("BramHome_Shelf", CmdShelf())
