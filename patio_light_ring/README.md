# Patio LED mounting enclosure

Drop-in mounting can for the stepped LED spotlight, designed to sit in a patio
pavement hole and cover an uneven cut edge.

The light drops in from above: its bezel seats in a counterbore so the top sits
flush, the stepped cavity clears the body, and a side slot at the bottom passes
the cable.

> **Photo estimates.** Light sizes below were scaled from the spotlight photo
> (Lightning cable as reference). Measure with calipers and regenerate before
> the final outdoor print.

## Files

| File | Description |
|------|-------------|
| [`patio_led_mounting_enclosure.stl`](patio_led_mounting_enclosure.stl) | Ready to slice (Bambu Lab P1S) |
| [`patio_led_mounting_enclosure.scad`](patio_led_mounting_enclosure.scad) | OpenSCAD source |
| [`generate_enclosure.py`](generate_enclosure.py) | Parametric generator |

Earlier simple trim-ring attempt (superseded): `patio_light_support_ring.*`

## Estimated light dimensions (edit these)

| Measurement | Est. mm | What to measure |
|-------------|--------:|-----------------|
| Flange / bezel OD | 72 | Outer diameter of the top lip |
| Flange thickness | 2.5 | Lip height |
| Upper body OD | 58 | Wider cylinder under the flange |
| Upper body length | 18 | Flange underside → step |
| Lower body OD | 48 | Narrower main cylinder |
| Lower body length | 72 | Step → bottom (before cable) |
| Cable notch W × H | 14 × 16 | Exit cutout at the base |

## Derived enclosure (with clearances)

| Feature | mm |
|---------|---:|
| Cover flange OD | 110 |
| Sleeve OD (into pavement) | 79 |
| Min. pavement hole | ≈ 81 |
| Bezel seat ID | 73 |
| Seat depth | 2.8 |
| Upper cavity ID | 59.6 |
| Lower cavity ID | 49.6 |
| Total height | 100.8 |
| Wall thickness | 3 |

Clearances: **0.8 mm** radial around the body, **0.5 mm** around the bezel.

## How it mounts

1. Drill / core the patio to at least **Ø81 mm**, deep enough for ~101 mm + cable space.
2. Drop the printed enclosure in — cover flange hides the rough hole.
3. Feed the spotlight cable through the bottom side slot.
4. Drop the light in — bezel rests on the internal ledge, top flush with the flange.

## Bambu Lab P1S

- **Orientation:** cover flange on the bed, sleeve pointing up — no supports
- **Layer height:** 0.20 mm (0.16 mm for a cleaner flange)
- **Walls:** 3–4 · **Infill:** 25–40%
- **Material:** PETG or ASA outdoors (PLA only for a fit check)
- Optional brim if the flange warps

## Regenerate after measuring

```bash
pip install -r requirements.txt
python generate_enclosure.py \
  --light-flange-od 72 \
  --light-flange-thickness 2.5 \
  --light-upper-od 58 \
  --light-upper-length 18 \
  --light-lower-od 48 \
  --light-lower-length 72 \
  --cover-flange-od 110 \
  -o patio_led_mounting_enclosure.stl
```
