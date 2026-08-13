# Patio LED mounting enclosure

Drop-in mounting can for the LED spotlight (caliper measurements).

- Flush recess for the metal bezel
- 2 mm anti-trip chamfer on the cover flange
- **30 mm sleeve** (sandstone slab depth — not the full light)
- Straight bore Ø73.9 for the widest body section

## Measured inputs

| Item | mm |
|------|---:|
| Bezel OD × thickness | 79.0 × 2.5 |
| Upper body OD | 72.3 |
| Pavement hole | 82.0 |
| Cover lip (radial) | 13.0 |
| Sleeve depth | **30.0** |

## Enclosure

| Feature | mm |
|---------|---:|
| Cover flange OD | 108.0 |
| Edge chamfer | 2.0 |
| Sleeve OD | 81.0 |
| Sleeve length | 30.0 |
| Bezel seat ID × depth | 80.0 × 2.8 |
| Bore ID | 73.9 |
| Total height | 33.0 |

## Print on Bambu Lab P1S

1. Import `patio_led_mounting_enclosure.stl`
2. Put the **wide flange on the build plate** (sleeve up)
3. **Enable supports** — needed for the bezel recess ledge (that’s what
   failed as spaghetti without supports)
   - Support type: normal / snug
   - Threshold ~30–45°
   - On build plate only is fine if it still supports the recess; otherwise
     allow supports everywhere
4. Optional brim for ASA
5. PLA for fit check; PETG/ASA for outdoors

## Files

| File | Description |
|------|-------------|
| [`patio_led_mounting_enclosure.stl`](patio_led_mounting_enclosure.stl) | Slice this |
| [`patio_led_mounting_enclosure.scad`](patio_led_mounting_enclosure.scad) | OpenSCAD source |
| [`generate_enclosure.py`](generate_enclosure.py) | Regenerator |

```bash
pip install -r requirements.txt
python generate_enclosure.py --sleeve-length 30 -o patio_led_mounting_enclosure.stl
```
