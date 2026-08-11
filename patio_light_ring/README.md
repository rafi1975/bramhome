# Patio floor-light support ring

3D-printable trim / support ring that:
- drops into a drilled pavement hole (sleeve)
- covers an uneven hole edge (flange)
- leaves a clear bore for a patio floor light

Modeled from photos of the existing part (scale referenced to 400 ml spray cans ≈ 66 mm OD).

## Download

| File | Description |
|------|-------------|
| [`patio_light_support_ring.stl`](patio_light_support_ring.stl) | Ready to slice for Bambu Lab P1S |
| [`patio_light_support_ring.scad`](patio_light_support_ring.scad) | OpenSCAD source (same dimensions) |
| [`generate_stl.py`](generate_stl.py) | Parametric Python generator |

## Photo-estimated dimensions

| Parameter | Value | Notes |
|-----------|------:|-------|
| Flange OD | **98 mm** | Covers uneven pavement |
| Sleeve OD | **82 mm** | Must fit your drilled hole |
| Bore ID | **76 mm** | Clearance for the light body |
| Flange thickness | **2.5 mm** | Height above pavement |
| Sleeve length | **28 mm** | Depth into the hole |
| Wall thickness | **3 mm** | `(82 − 76) / 2` |
| Bottom chamfer | **1.2 mm** | Easier insertion |
| Fillet under flange | **1.0 mm** | Strength |

Total height: **30.5 mm**. Footprint fits easily on a P1S bed (256 × 256 mm).

> These sizes are estimates from the photos. Measure your pavement hole and light, then regenerate if needed (see below).

## Bambu Lab P1S print settings

**Orientation:** flange flat on the build plate (sleeve pointing up). No supports.

| Setting | Suggestion |
|---------|------------|
| Layer height | 0.20 mm (0.16 mm for cleaner flange) |
| Walls / perimeters | 3–4 |
| Infill | 25–40% gyroid or grid |
| Material | **PETG** or **ASA** for outdoor UV/weather; PLA fine for a fit check |
| Bed adhesion | Soft brim 3–5 mm optional if corners lift |
| Ironing | Optional on top surface for a smoother flange |

Black filament will match the original part.

## Resize / regenerate

```bash
pip install numpy numpy-stl trimesh
python generate_stl.py \
  --flange-od 98 \
  --sleeve-od 82 \
  --bore-id 76 \
  --flange-thickness 2.5 \
  --sleeve-length 28 \
  -o patio_light_support_ring.stl
```

Or edit the variables at the top of `patio_light_support_ring.scad` and export STL from OpenSCAD.
