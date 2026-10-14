# Bambu Lab P1S — PLA fit-test print

## Which print head / nozzle

For a **PLA test print**, use the stock setup:

| Item | Choice |
|------|--------|
| **Nozzle** | **0.4 mm** (standard) |
| **Hotend** | Stock stainless-steel hotend (the one that came with the P1S) |
| **Extruder** | Standard P1S extruder — **no hardened / HF head required** for PLA |
| **Plate** | Cool Plate / PEI textured — whatever you normally use for PLA |
| **Filament** | Bambu PLA Basic (or any PLA) — Generic PLA / Bambu PLA Basic preset |

Hardened 0.4/0.6 nozzles are only needed for abrasive filaments (CF, glow, etc.).  
**0.6 mm** also works for a quicker rough fit check, but **0.4 mm** is better for the hook details and screw holes.

> PLA is fine to **test fit**. Do **not** rely on PLA for the real loft stairs — use PETG / ASA / PA-CF for the final parts.

## Files to import in Bambu Studio

Folder: `attic_staircase/p1s/`

| File | Use |
|------|-----|
| [`attic_fit_test_plate_p1s.3mf`](attic_fit_test_plate_p1s.3mf) | **Easiest** — catch + hook on one plate, already oriented |
| [`catching_piece_p1s.3mf`](catching_piece_p1s.3mf) | Catch only (M8 bolt version) |
| [`catching_piece_printed_bar_p1s.3mf`](catching_piece_printed_bar_p1s.3mf) | Catch with printed bar — no M8 needed for a dry fit |
| [`pole_hook_p1s.3mf`](pole_hook_p1s.3mf) | Hook only (laid on its side) |
| `*_p1s.stl` | Same meshes if you prefer STL |

## Bambu Studio steps

1. Open **Bambu Studio** → Printer **Bambu Lab P1S 0.4 nozzle**
2. Process preset: **0.20 mm Standard** (or 0.16 mm for cleaner holes)
3. Filament: **Bambu PLA Basic** / Generic PLA
4. **File → Import** the `.3mf` (or drag it in)
5. Check orientation (should already be correct):
   - Catch: **flange on the bed**, plug pointing up
   - Hook: **lying on its side**, opening facing up
6. Slice → Send to P1S / print

## Suggested PLA test settings

| Setting | Catch | Hook |
|---------|------:|-----:|
| Layer height | 0.20 mm | 0.20 mm |
| Walls | 3–4 | **5–6** |
| Infill | 15–25% | **40–50%** gyroid |
| Top/bottom | 4 | 5 |
| Supports | Off | **On** (normal, for the hook arch) |
| Brim | Off / optional | Optional if adhesion is weak |
| Nozzle temp | PLA preset (~210–220 °C) | same |
| Bed temp | PLA preset (~35–65 °C) | same |

## After the PLA test

1. Check plug fit in the Ø50 / flat Ø30 recess  
2. Check sleeve fit on the Ø28 mm pole  
3. Check hook entry into the pocket / bar  
4. For the **real** parts, reprint in **PETG or ASA** with the same orientation and higher walls/infill (see main README)
