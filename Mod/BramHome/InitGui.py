# SPDX-License-Identifier: LGPL-2.1-or-later
"""BramHome FreeCAD GUI workbench registration."""

import FreeCADGui
import os

__dirname__ = os.path.dirname(__file__)


class BramHomeWorkbench(FreeCADGui.Workbench):
    """Parametric home layout, furniture, and car parts."""

    MenuText = "BramHome"
    ToolTip = "Home layout, furniture, and car parts (dimension-driven)"
    Icon = os.path.join(__dirname__, "Resources", "icons", "bramhome.svg")

    def Initialize(self):
        try:
            from .commands import home_commands, furniture_commands, car_commands
        except ImportError:
            # FreeCAD may load InitGui outside package context
            import sys

            parent = os.path.dirname(__dirname__)
            if parent not in sys.path:
                sys.path.insert(0, parent)
            from BramHome.commands import home_commands, furniture_commands, car_commands

        home_commands.register()
        furniture_commands.register()
        car_commands.register()

        self.appendToolbar(
            "BramHome Home",
            [
                "BramHome_Room",
                "BramHome_Wall",
                "BramHome_FloorPlan",
                "BramHome_Door",
                "BramHome_Window",
            ],
        )
        self.appendToolbar(
            "BramHome Furniture",
            [
                "BramHome_Table",
                "BramHome_Chair",
                "BramHome_Cabinet",
                "BramHome_Bed",
                "BramHome_Shelf",
            ],
        )
        self.appendToolbar(
            "BramHome Car",
            [
                "BramHome_Wheel",
                "BramHome_BrakeDisc",
                "BramHome_ControlArm",
                "BramHome_MountBracket",
            ],
        )

        self.appendMenu(
            "BramHome",
            [
                "BramHome_Room",
                "BramHome_Wall",
                "BramHome_FloorPlan",
                "BramHome_Door",
                "BramHome_Window",
                "Separator",
                "BramHome_Table",
                "BramHome_Chair",
                "BramHome_Cabinet",
                "BramHome_Bed",
                "BramHome_Shelf",
                "Separator",
                "BramHome_Wheel",
                "BramHome_BrakeDisc",
                "BramHome_ControlArm",
                "BramHome_MountBracket",
            ],
        )

    def Activated(self):
        FreeCADGui.getMainWindow().statusBar().showMessage("BramHome workbench active", 2000)

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(BramHomeWorkbench())
