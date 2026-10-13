# Editable Fusion 360 models

Imported **STEP/STL files are not feature-editable** in Fusion 360. STEP opens as a
single *Base Feature* (a “dumb” solid). You can Press/Pull faces a little, but you
**cannot** open sketches, change parameters, or edit the timeline the way a native
Fusion design allows.

To get a **real editable model**, run the script in this folder. It rebuilds both
parts inside Fusion with:

- User Parameters (`hole_d`, `pole_d`, `flange_od`, …)
- Timeline sketches / extrudes / revolves
- Two components: `CatchingPiece` and `PoleHook`

## Download the script folder

GitHub’s folder “⋯” menu has **no Download** for a single folder. Use one of these:

### Easiest — ZIP of just the Fusion script
Open this file and click **Download** (raw file download icon):

https://github.com/rafi1975/bramhome/raw/cursor/attic-staircase-hook-catch-b525/attic_staircase/fusion360/AtticStaircaseParts.zip

Unzip it. You should get a folder `AtticStaircaseParts` containing `.py` + `.manifest`.

### Or — whole branch ZIP
1. Open https://github.com/rafi1975/bramhome/tree/cursor/attic-staircase-hook-catch-b525  
2. Green **Code** button → **Download ZIP**  
3. Unzip, then go to `attic_staircase/fusion360/AtticStaircaseParts`

## Install & run in Fusion

1. In Fusion 360: **Utilities → Add-Ins → Scripts and Add-Ins**
2. Next to **My Scripts**, click **+**
3. Choose the unzipped **`AtticStaircaseParts`** folder
4. Select **AtticStaircaseParts** → **Run**
5. Edit sizes with **Modify → Change Parameters**
6. For printing: right-click a body → **Save as Mesh** (3MF/STL) for the P1S

## Main parameters

| Parameter | Default | Meaning |
|-----------|--------:|---------|
| `hole_d` | 50 mm | Hatch opening diameter |
| `hole_depth` | 31 mm | Hatch opening depth |
| `flat_top_d` | 30 mm | Flat floor at top of dome |
| `flange_od` | 80 mm | Cover flange |
| `pole_d` | 28 mm | Wooden pole diameter |
| `sleeve_wall` | 6 mm | Hook sleeve wall thickness |
| `hook_throat` | 11 mm | Opening that grabs the M8 bar |
| `m8_d` | 8.4 mm | Catch-bar bolt hole |

## Files

| Path | Role |
|------|------|
| `AtticStaircaseParts/AtticStaircaseParts.py` | Fusion script |
| `AtticStaircaseParts/AtticStaircaseParts.manifest` | Script manifest |

Save the resulting Fusion document as `.f3d` on your machine if you want a native
Fusion archive to reopen later.
