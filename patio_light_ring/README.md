# Patio LED mounting enclosure

Drop-in mounting can for the stepped LED spotlight, built from **caliper
measurements** (not photo estimates).

The light drops in from above: the metal bezel seats in a top counterbore so it
sits **flush** with the cover flange; the stepped cavity clears the body; the
bottom is open for cable and drainage.

## Measured inputs

| Item | mm |
|------|---:|
| Bezel OD | 79.0 |
| Bezel thickness | 2.5 |
| Upper body OD × length | 72.3 × 15.3 |
| Lower body OD × length | 59.3 × 53.3 |
| Pavement hole | 82.0 |
| Cover lip (radial) | 13.0 |

## Enclosure (derived)

| Feature | mm |
|---------|---:|
| Cover flange OD | **108.0** |
| Sleeve OD | **81.0** (fits Ø82 hole) |
| Bezel seat ID | 80.0 |
| Seat depth (flush recess) | 2.8 |
| Upper cavity ID | 73.9 |
| Lower cavity ID | 60.9 |
| Wall at upper section | ≈ 3.55 |
| Total height | 76.4 |

## Files

| File | Description |
|------|-------------|
| [`patio_led_mounting_enclosure.stl`](patio_led_mounting_enclosure.stl) | Ready to slice (Bambu Lab P1S) |
| [`patio_led_mounting_enclosure.scad`](patio_led_mounting_enclosure.scad) | OpenSCAD source |
| [`generate_enclosure.py`](generate_enclosure.py) | Parametric generator |

## Bambu Lab P1S

- **Orientation:** cover flange on the bed, sleeve up — no supports
- **Layer height:** 0.20 mm (0.16 mm for a cleaner flange top)
- **Walls:** 3–4 · **Infill:** 25–40%
- **Material:** PETG or ASA outdoors (PLA for fit check only)

## Regenerate

```bash
pip install -r requirements.txt
python generate_enclosure.py -o patio_led_mounting_enclosure.stl
```
