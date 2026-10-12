# Attic staircase hook + catching piece

Printable replacements so the existing wooden pole can open the loft hatch
again. Designed for a **Bambu Lab P1S**.

The previous plastic hook broke; the hatch is currently opened with a
makeshift screw. These parts are built for tensile load: steel catch bar,
thick walls, and a print orientation that puts layer lines *with* the pull.

## What you get

| File | Role |
|------|------|
| [`fusion360/AtticStaircaseParts/`](fusion360/AtticStaircaseParts/) | **Editable Fusion 360 model** (native parametric script) |
| [`catching_piece.stl`](catching_piece.stl) | Slice-ready mesh (M8 bolt version) |
| [`catching_piece_printed_bar.stl`](catching_piece_printed_bar.stl) | Mesh fit-check only |
| [`pole_hook.stl`](pole_hook.stl) | Slice-ready mesh |
| `*.scad` | Parametric OpenSCAD sources |
| `*.step` | Exchange solids only (see below) |

## Edit in Fusion 360 (parametric — use this)

**STEP/STL cannot carry Fusion feature history.** A `.step` always imports as one
locked Base Feature, so it feels “not editable”. For a real editable design, run
the Fusion script:

→ See **[`fusion360/README.md`](fusion360/README.md)**

Short version:

1. **Utilities → Add-Ins → Scripts and Add-Ins**
2. **+** under My Scripts → select `fusion360/AtticStaircaseParts`
3. **Run** → get `CatchingPiece` + `PoleHook` with User Parameters
4. **Modify → Change Parameters** (or edit sketches in the Timeline)
5. Right-click body → **Save as Mesh** for the P1S

Save the document as `.f3d` on your computer to keep the native Fusion file.

### STEP files (optional exchange only)

The `.step` files are valid BRep solids for other CAD packages or reference, but
in Fusion they are **not** parametric. Prefer the script above for editing.

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
