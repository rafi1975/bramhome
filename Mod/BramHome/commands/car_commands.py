# SPDX-License-Identifier: LGPL-2.1-or-later
"""Car part commands."""

from __future__ import annotations

import FreeCADGui as Gui

from .base import _Command, open_dimension_dialog
from ..models import car as car_models


class CmdWheel(_Command):
    def __init__(self):
        super().__init__("BramHome_Wheel", "Wheel", "Create a parametric wheel", "wheel.svg")

    def Activated(self):
        open_dimension_dialog(
            "New Wheel",
            [
                {"key": "tire_od", "label": "Tire outer Ø", "value": 650, "minimum": 200},
                {"key": "tire_w", "label": "Tire width", "value": 225, "minimum": 80},
                {"key": "rim_od", "label": "Rim outer Ø", "value": 450, "minimum": 150},
                {"key": "rim_w", "label": "Rim width", "value": 200, "minimum": 80},
                {"key": "hub_od", "label": "Hub bore Ø", "value": 60, "minimum": 20},
                {"key": "hub_d", "label": "Hub depth", "value": 40, "minimum": 10},
                {
                    "key": "bolts",
                    "label": "Bolt count",
                    "value": 5,
                    "minimum": 3,
                    "maximum": 12,
                    "integer": True,
                },
                {"key": "pcd", "label": "Bolt circle (PCD)", "value": 112, "minimum": 50},
                {"key": "bolt_d", "label": "Bolt hole Ø", "value": 14, "minimum": 6},
            ],
            car_models.make_wheel,
            {
                "tire_od": "TireOuterDiameter",
                "tire_w": "TireWidth",
                "rim_od": "RimDiameter",
                "rim_w": "RimWidth",
                "hub_od": "HubDiameter",
                "hub_d": "HubDepth",
                "bolts": "BoltCount",
                "pcd": "BoltCircleDiameter",
                "bolt_d": "BoltHoleDiameter",
            },
        )


class CmdBrakeDisc(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_BrakeDisc",
            "Brake disc",
            "Create a parametric brake disc",
            "brakedisc.svg",
        )

    def Activated(self):
        open_dimension_dialog(
            "New Brake Disc",
            [
                {"key": "od", "label": "Outer Ø", "value": 300, "minimum": 100},
                {"key": "th", "label": "Thickness", "value": 25, "minimum": 8},
                {"key": "id", "label": "Inner Ø", "value": 160, "minimum": 50},
                {"key": "hat_od", "label": "Hat outer Ø", "value": 150, "minimum": 50},
                {"key": "hat_h", "label": "Hat height", "value": 40, "minimum": 10},
                {"key": "bore", "label": "Center bore Ø", "value": 68, "minimum": 20},
                {
                    "key": "bolts",
                    "label": "Bolt count",
                    "value": 5,
                    "minimum": 3,
                    "maximum": 12,
                    "integer": True,
                },
                {"key": "pcd", "label": "Bolt circle", "value": 112, "minimum": 50},
                {"key": "bolt_d", "label": "Bolt hole Ø", "value": 14, "minimum": 6},
            ],
            car_models.make_brake_disc,
            {
                "od": "OuterDiameter",
                "th": "Thickness",
                "id": "InnerDiameter",
                "hat_od": "HatOuterDiameter",
                "hat_h": "HatHeight",
                "bore": "CenterBore",
                "bolts": "BoltCount",
                "pcd": "BoltCircleDiameter",
                "bolt_d": "BoltHoleDiameter",
            },
        )


class CmdControlArm(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_ControlArm",
            "Control arm",
            "Create a simplified A-arm control arm",
            "controlarm.svg",
        )

    def Activated(self):
        open_dimension_dialog(
            "New Control Arm",
            [
                {"key": "length", "label": "Length", "value": 350, "minimum": 100},
                {"key": "width", "label": "Mount spread", "value": 180, "minimum": 60},
                {"key": "height", "label": "Section height", "value": 40, "minimum": 15},
                {"key": "thickness", "label": "Section thickness", "value": 25, "minimum": 10},
                {"key": "bush_id", "label": "Bushing ID", "value": 14, "minimum": 6},
                {"key": "bush_od", "label": "Bushing OD", "value": 40, "minimum": 15},
                {"key": "bush_w", "label": "Bushing width", "value": 30, "minimum": 10},
                {"key": "bj", "label": "Ball joint Ø", "value": 30, "minimum": 10},
            ],
            car_models.make_control_arm,
            {
                "length": "Length",
                "width": "Width",
                "height": "Height",
                "thickness": "Thickness",
                "bush_id": "BushingInnerDiameter",
                "bush_od": "BushingOuterDiameter",
                "bush_w": "BushingWidth",
                "bj": "BallJointDiameter",
            },
        )


class CmdMountBracket(_Command):
    def __init__(self):
        super().__init__(
            "BramHome_MountBracket",
            "Mount bracket",
            "Create a parametric L-mount bracket",
            "mountbracket.svg",
        )

    def Activated(self):
        open_dimension_dialog(
            "New Mount Bracket",
            [
                {"key": "base_l", "label": "Base length", "value": 120, "minimum": 40},
                {"key": "base_w", "label": "Base width", "value": 80, "minimum": 30},
                {"key": "up_h", "label": "Upright height", "value": 100, "minimum": 30},
                {"key": "th", "label": "Thickness", "value": 8, "minimum": 2},
                {"key": "hole", "label": "Hole Ø", "value": 10, "minimum": 3},
                {"key": "offset", "label": "Hole edge offset", "value": 20, "minimum": 5},
                {
                    "key": "base_n",
                    "label": "Base holes",
                    "value": 2,
                    "minimum": 0,
                    "maximum": 8,
                    "integer": True,
                },
                {
                    "key": "up_n",
                    "label": "Upright holes",
                    "value": 2,
                    "minimum": 0,
                    "maximum": 8,
                    "integer": True,
                },
            ],
            car_models.make_mount_bracket,
            {
                "base_l": "BaseLength",
                "base_w": "BaseWidth",
                "up_h": "UprightHeight",
                "th": "Thickness",
                "hole": "HoleDiameter",
                "offset": "HoleEdgeOffset",
                "base_n": "BaseHoleCount",
                "up_n": "UprightHoleCount",
            },
        )


def register():
    Gui.addCommand("BramHome_Wheel", CmdWheel())
    Gui.addCommand("BramHome_BrakeDisc", CmdBrakeDisc())
    Gui.addCommand("BramHome_ControlArm", CmdControlArm())
    Gui.addCommand("BramHome_MountBracket", CmdMountBracket())
