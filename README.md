# BramHome

FreeCAD workbench for **dimension-driven** home layouts, furniture, and car parts — runs inside FreeCAD with GUI task panels.

## Features

| Group | Tools | Driven by |
|-------|--------|-----------|
| Home | Room, Wall, Floor plan, Door, Window | Length / width / height / thickness |
| Furniture | Table, Chair, Cabinet, Bed, Shelf | Overall size, thickness, counts |
| Car | Wheel, Brake disc, Control arm, Mount bracket | Diameters, PCD, section sizes, hole counts |

Each tool opens a task panel (mm). After creation, edit the same values in the **Data** tab (Property editor) and the solid updates.

## Install

### Option A — user Mod folder (recommended)

```bash
./install.sh
```

Or symlink manually:

```bash
# Linux
mkdir -p ~/.local/share/FreeCAD/Mod
ln -s /path/to/bramhome/Mod/BramHome ~/.local/share/FreeCAD/Mod/BramHome

# macOS
mkdir -p ~/Library/Application\ Support/FreeCAD/Mod
ln -s /path/to/bramhome/Mod/BramHome ~/Library/Application\ Support/FreeCAD/Mod/BramHome

# Windows (PowerShell)
# New-Item -ItemType Junction -Path "$env:APPDATA\FreeCAD\Mod\BramHome" -Target "C:\path\to\bramhome\Mod\BramHome"
```

Restart FreeCAD → workbench selector → **BramHome**.

### Option B — developer checkout

If this repo is already on disk, point FreeCAD at `Mod/BramHome` as above. `package.xml` at the repo root is Addon-Manager–compatible metadata.

## Usage

1. Switch to the **BramHome** workbench.
2. Use a toolbar button or **BramHome** menu item.
3. Enter dimensions (mm) → **Create**.
4. Move / rotate with the standard Draft/Part tools; tweak dimensions in the Property editor.

## Layout

```
Mod/BramHome/
  Init.py / InitGui.py     # module + workbench registration
  commands/                # GUI commands
  models/                  # parametric FeaturePython geometry
  taskpanels/              # dimension forms
  Resources/icons/         # toolbar icons
```

## Requirements

- FreeCAD 0.21+ or 1.0+ (Python 3, Part workbench)
- GUI build (task panels use Qt via FreeCAD’s PySide)

## Notes

- Models are simplified solids for layout and concepting, not manufacturing-ready FEA meshes.
- Units are millimetres throughout.
- Car parts (wheel, disc, A-arm, bracket) are parametric envelopes for fit/clearance studies.
