# Attic staircase hook + catching piece

Printable replacements so the existing wooden pole can open the loft hatch
again. Designed for a **Bambu Lab P1S**.

The previous plastic hook broke; the hatch is currently opened with a
makeshift screw. These parts are built for tensile load: steel catch bar,
thick walls, and a print orientation that puts layer lines *with* the pull.

## What you get

| File | Role |
|------|------|
| [`catching_piece.step`](catching_piece.step) | **Fusion 360** solid — catch with M8 bolt hole |
| [`catching_piece_printed_bar.step`](catching_piece_printed_bar.step) | Fusion solid — printed-bar fit-check variant |
| [`pole_hook.step`](pole_hook.step) | **Fusion 360** solid — sleeve + hook |
| [`attic_staircase_assembly.step`](attic_staircase_assembly.step) | Both parts side-by-side for one-shot import |
| [`catching_piece.stl`](catching_piece.stl) | Slice-ready mesh (M8 bolt version) |
| [`catching_piece_printed_bar.stl`](catching_piece_printed_bar.stl) | Mesh fit-check only |
| [`pole_hook.stl`](pole_hook.stl) | Slice-ready mesh |
| `*.scad` | Parametric OpenSCAD sources |
| [`export_fusion.py`](export_fusion.py) | Regenerates the `.step` files (CadQuery) |

## Edit in Fusion 360

Use the **`.step`** files (true BRep solids — not meshes):

1. In Fusion: **File → Open** (or drag the `.step` into the window)
2. Units are **millimetres**
3. You get solid bodies you can **Push/Pull**, edit holes, fillet, etc.
4. When ready to print: **File → 3D Print** / export mesh, or keep using the `.stl` files

To regenerate STEPs after changing dimensions in `export_fusion.py`:

```bash
pip install -r requirements.txt
python3 export_fusion.py
```

## Measured inputs

| Item | mm |
|------|---:|
| Hatch opening diameter | 50 |
| Hatch opening depth (domed) | 31 |
| Pole diameter | 28 |

## Catching piece

- **Ø80 mm flange** covers the torn laminate and lands screws in solid wood
  outside the 50 mm hole
- **Ø49 mm plug** with a **domed tip** seats in the cavity so the part cannot tip
- **Pocket** 34 × 38 × 26 mm for the hook head
- **M8 bolt** through the pocket is the real catch bar (steel) — the print only
  holds the bolt and transfers load into the wood screws

### Hardware

- 1× **M8 × 50–60** bolt + nylock nut (washers optional)
- 4× wood screws ~**4 mm / #8** through the flange (countersunk)
- Optional: 3× shorter screws into the dome floor (old pilot-hole area)

### Install

1. Remove the temporary screw in the hatch
2. Push the plug into the Ø50 mm hole (flange toward the room)
3. Align the pocket so the bar is easy to reach with the pole
4. Fit the M8 bolt across the pocket; tighten the nylock
5. Drive the four flange screws into undamaged wood
6. Optional: add the three floor screws into the dome

## Pole hook

- Sleeve **ID 28.7 mm** (0.35 mm clearance on Ø28 pole) — sand if snug
- **~6 mm walls**, dual cross-screw holes, spine rib into the hook
- Side-opening J sized for the M8 bar; head fits the catch pocket

### Install

1. Slide the sleeve onto the pole (hook at the tip)
2. Fix with two ~4 mm / #8 wood screws through the countersunk holes
   (drill pilot holes in the pole)

## Print on Bambu Lab P1S

### Material (important)

Use **PETG, ASA, PA-CF, or PETG-CF**. PLA will creep/break under loft-ladder
spring tension.

### Catching piece

1. Import `catching_piece.stl`
2. **Flange flat on the bed**, plug pointing up
3. **No supports** needed
4. ≥5 walls, 40–60% gyroid, 3+ top/bottom layers

### Pole hook (orientation matters)

1. Import `pole_hook.stl`
2. Lay it on a **flat Y face** so the **pole axis is horizontal** and the
   **hook opening faces up** — layer lines then run with the pull force
3. **Enable supports** for the hook arch
4. ≥6 walls, 50–80% gyroid, 4+ top/bottom layers
5. Optional brim for PETG/ASA

## Regenerate STLs

```bash
openscad -o catching_piece.stl catching_piece.scad
openscad -o catching_piece_printed_bar.stl -D 'use_printed_bar=true' catching_piece.scad
openscad -o pole_hook.stl pole_hook.scad
```

Tune clearances at the top of each `.scad` if your hole or pole measures
differently.
