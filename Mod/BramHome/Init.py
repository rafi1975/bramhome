# SPDX-License-Identifier: LGPL-2.1-or-later
"""BramHome FreeCAD module — always loaded (GUI and console)."""

FreeCAD = __import__("FreeCAD")

FreeCAD.Console.PrintMessage("BramHome: module loaded\n")
