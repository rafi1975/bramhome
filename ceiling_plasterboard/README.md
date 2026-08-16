# Ceiling plasterboard supports (Bambu Lab P1S)

New board is **13 mm**. Existing ceiling board is **17 mm**. Joist / beam soffits are not in one plane.

Printed parts are **spacers and clips**. Drywall screws must go through the plastic and bite timber (except the seam biscuit, which the new board screws into).

![4 mm packer, seam biscuit, and shim stack to a laser line](diagrams/pack_and_joint.svg)

## Measured parts — print these

Screws: **3.5 × 30 mm** countersunk. Through-hole Ø4.0, head recess Ø8.2 × 90° so the head sits just below the face. Print **flat, recessed face up**, no supports.

| Part | Length | Depth | Height | File |
|------|-------:|------:|-------:|------|
| 1 | 220 | 20 | 8 | [`stls/support_220x20x8.stl`](stls/support_220x20x8.stl) |
| 2 | 190 | 20 | 4 | [`stls/support_190x20x4.stl`](stls/support_190x20x4.stl) |
| 3 | 130 | 20 | 4 | [`stls/support_130x20x4.stl`](stls/support_130x20x4.stl) |

Screw the strip to the beam first; heads hide in the recesses so the plasterboard sits flat. 30 mm into an 8 mm strip leaves ~22 mm in timber; into a 4 mm strip leaves ~26 mm.

If you later drive the same 30 mm screws *through* 13 mm board + 8 mm strip, only ~9 mm reaches timber — too short. Use longer screws for that, or fix the strip first as above.

PETG preferred; PLA is OK in compression if the screw reaches timber.

## Other parts in the kit

| Situation | Part | File |
|-----------|------|------|
| Level joist, just the 13 vs 17 mm step | 4 mm strip on the soffit | [`stls/packer_strip_4mm.stl`](stls/packer_strip_4mm.stl) |
| Same, small pads | 4 mm shim | [`stls/shim_4mm.stl`](stls/shim_4mm.stl) |
| Beams at different heights | Slotted L-hanger + shim stack | [`stls/side_hanger_slotted.stl`](stls/side_hanger_slotted.stl) + `shim_*mm.stl` |
| Known timber width, clip onto soffit | U-saddle (4 mm base) | `stls/joist_saddle_<width>mm.stl` |
| Cut joint between old and new board | Seam biscuit | [`stls/seam_biscuit.stl`](stls/seam_biscuit.stl) |
| Cut joint with a timber noggin behind | Stepped backer | [`stls/stepped_edge_backer.stl`](stls/stepped_edge_backer.stl) |

Saddles are generated for **45, 47, 60, 80, 100 mm** joists. Measure the timber and pick the matching file (inner opening is width + 1.2 mm).

## How the 4 mm step works

Room at the bottom. Both room faces must end up flush:

```
              JOIST soffit (same timber)
         ────────────────────────────────
         [ 4 mm packer ] [  no packer   ]
         [ 13 mm new   ] [  17 mm old   ]
         ════════════════════════════════  room face, flush
```

`13 + 4 = 17`. Without the packer the new board sits 4 mm up into the ceiling.

## Uneven beams

Set a laser or a string to the **lowest** soffit (the one that already matches the existing 17 mm ceiling).

For every other soffit, measure the gap up to the laser. That gap is extra packing on top of the 4 mm:

| Gap to laser | Stack on the 4 mm packer |
|-------------:|--------------------------|
| 0 mm | 4 mm only |
| 3 mm | 4 + 3 |
| 7 mm | 4 + 5 + 2 |
| 12 mm | 4 + 10 + 2 |
| 18 mm | 4 + 10 + 8 |

Shims are **1, 2, 3, 4, 5, 8, 10, 15, 20 mm**. Two Ø4.8 holes, 30 mm apart — the same pattern as the saddle base and the L-hanger flange, so they stack on the screws.

**Slotted L-hanger** (no joist-width measurement needed):

1. Screw the plate to the **side** of the beam through the slots (do not fully tighten).
2. Slide the flange down to the laser line.
3. Tighten.
4. Drop 4 mm packer + extra shims on the flange if the flange is the board face.
5. Screw the 13 mm board through the stack. Screw length = 13 + packers + **at least 25 mm into timber**.

The slots give about **45 mm** of drop. If a beam is further off than that, add shims or print a thicker shim.

```
 side of joist          room
      │  [==== slotted plate ====]
      │  [ slots: slide to laser ]
      │──────── soffit
      │____ flange  →  shims  →  13 mm board
```

## Joint between 17 mm and 13 mm

Leave a **~2 mm** taping gap.

**Seam biscuit** — slide the 17 mm jaw onto the cut edge of the old board from the opening. The lower flange is the ledge for the new 13 mm board. Screw the new board from the room into the flange (Ø3.2 pilots). The web stays 1.6 mm short of the room face so it does not show under tape.

**Stepped backer** — if you can fit a timber noggin between joists, put this on the cavity side of both boards (4 mm step on the new half) and screw from the room into the pilots.

## Bambu Lab P1S

All parts fit the 256 mm cube. No supports on any of them.

| Setting | Value |
|---------|--------|
| Layer | 0.20 mm |
| Walls | **5** (hangers, biscuits, saddles) / 3 (thin shims) |
| Infill | 40 % gyroid (hangers) / 20 % (shims in compression) |
| Material | **PETG** for hangers and biscuits. PLA is acceptable for shims/packers in **compression** under a screw that goes into timber. Do not hang a ceiling on PLA in bending. |
| Orientation | see table below |
| Brim | optional on the L-hanger |

| Part | On the bed |
|------|------------|
| **Part 1–2** measured strips | Flat face down, **recesses up** |
| Shims, 4 mm packer strip | Flat face down |
| Joist saddle | Base down, arms up |
| Side hanger | Large plate down, flange standing up |
| Stepped backer | Flat (cavity) face down, step up |
| Seam biscuit | As exported (60 mm tall H-profile) |

Hole style: measured strips use Ø4.0 through + Ø8.2 CSK for **3.5 × 30**. Other kit parts still use Ø4.8 clearance / Ø3.2 pilots.

## Screw length

```
screw = 13 mm board + total packers + ≥ 25 mm into timber
```

Example: 13 + 4 + 10 mm shim + 25 = **52 mm** → use 55 or 60 mm screws.

## Regenerating after you measure the beams

```bash
pip install -r requirements.txt
python generate_supports.py --joist-width 45,60
python generate_supports.py --new-board 13 --old-board 17 --joist-width 72
```

Measured so far:

1. **Part 1** — 220 × 20 × 8 mm
2. **Part 2** — 190 × 20 × 4 mm
3. **Part 3** — 130 × 20 × 4 mm
4. Screws — 3.5 × 30 mm countersunk
5. Next: remaining supports (send length × depth × height for each)

## Files

| File | Description |
|------|-------------|
| [`generate_supports.py`](generate_supports.py) | Parametric generator |
| [`stls/`](stls/) | Print-ready STLs + `manifest.json` |
