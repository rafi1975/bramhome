#!/usr/bin/env python3
"""
Patio mounting enclosure for a stepped LED spotlight.

The light drops in from above:
  - cover flange hides an uneven pavement hole
  - counterbore seats the light bezel flush with the top
  - stepped cavity clears the light upper / lower body
  - open bottom + side cable slot for wiring and drainage

Default light dimensions are PHOTO ESTIMATES (Lightning cable as
scale). Remeasure the spotlight and regenerate before final print.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh
from stl import mesh as stl_mesh
from trimesh.creation import box, cylinder


# ---------------------------------------------------------------------------
# LED spotlight — PHOTO ESTIMATES (mm). Replace with caliper readings.
# ---------------------------------------------------------------------------
LIGHT_FLANGE_OD = 72.0
LIGHT_FLANGE_THICKNESS = 2.5
LIGHT_UPPER_OD = 58.0
LIGHT_UPPER_LENGTH = 18.0
LIGHT_LOWER_OD = 48.0
LIGHT_LOWER_LENGTH = 72.0
LIGHT_CABLE_NOTCH_W = 14.0
LIGHT_CABLE_NOTCH_H = 16.0

# ---------------------------------------------------------------------------
# Enclosure fit / pavement cover
# ---------------------------------------------------------------------------
RADIAL_CLEARANCE = 0.8
FLANGE_SEAT_CLEARANCE = 0.5
SEAT_DEPTH_EXTRA = 0.3
COVER_FLANGE_OD = 110.0
COVER_FLANGE_THICKNESS = 3.0
WALL_THICKNESS = 3.0
BOTTOM_EXTRA = 8.0
CABLE_SLOT_EXTRA_W = 4.0
CABLE_SLOT_EXTRA_H = 10.0
SEGMENTS = 128


def _cyl(radius: float, height: float, z0: float, sections: int = SEGMENTS) -> trimesh.Trimesh:
    m = cylinder(radius=radius, height=height, sections=sections)
    m.apply_translation([0.0, 0.0, z0 + height / 2.0])
    return m


def derived_dims(
    light_flange_od: float = LIGHT_FLANGE_OD,
    light_flange_thickness: float = LIGHT_FLANGE_THICKNESS,
    light_upper_od: float = LIGHT_UPPER_OD,
    light_upper_length: float = LIGHT_UPPER_LENGTH,
    light_lower_od: float = LIGHT_LOWER_OD,
    light_lower_length: float = LIGHT_LOWER_LENGTH,
    radial_clearance: float = RADIAL_CLEARANCE,
    flange_seat_clearance: float = FLANGE_SEAT_CLEARANCE,
    seat_depth_extra: float = SEAT_DEPTH_EXTRA,
    cover_flange_od: float = COVER_FLANGE_OD,
    cover_flange_thickness: float = COVER_FLANGE_THICKNESS,
    wall_thickness: float = WALL_THICKNESS,
    bottom_extra: float = BOTTOM_EXTRA,
) -> dict[str, float]:
    seat_id = light_flange_od + 2.0 * flange_seat_clearance
    upper_id = light_upper_od + 2.0 * radial_clearance
    lower_id = light_lower_od + 2.0 * radial_clearance
    seat_depth = light_flange_thickness + seat_depth_extra
    max_bore = max(seat_id, upper_id)
    sleeve_od = max_bore + 2.0 * wall_thickness
    total_h = seat_depth + light_upper_length + light_lower_length + bottom_extra
    return {
        "seat_id": seat_id,
        "upper_cavity_id": upper_id,
        "lower_cavity_id": lower_id,
        "seat_depth": seat_depth,
        "sleeve_od": sleeve_od,
        "cover_flange_od": cover_flange_od,
        "cover_flange_thickness": cover_flange_thickness,
        "total_height": total_h,
        "pavement_hole_min": sleeve_od + 1.5,
        "wall_thickness": wall_thickness,
        "bottom_extra": bottom_extra,
        "light_upper_length": light_upper_length,
        "light_lower_length": light_lower_length,
    }


def build_enclosure(
    light_flange_od: float = LIGHT_FLANGE_OD,
    light_flange_thickness: float = LIGHT_FLANGE_THICKNESS,
    light_upper_od: float = LIGHT_UPPER_OD,
    light_upper_length: float = LIGHT_UPPER_LENGTH,
    light_lower_od: float = LIGHT_LOWER_OD,
    light_lower_length: float = LIGHT_LOWER_LENGTH,
    light_cable_notch_w: float = LIGHT_CABLE_NOTCH_W,
    light_cable_notch_h: float = LIGHT_CABLE_NOTCH_H,
    radial_clearance: float = RADIAL_CLEARANCE,
    flange_seat_clearance: float = FLANGE_SEAT_CLEARANCE,
    seat_depth_extra: float = SEAT_DEPTH_EXTRA,
    cover_flange_od: float = COVER_FLANGE_OD,
    cover_flange_thickness: float = COVER_FLANGE_THICKNESS,
    wall_thickness: float = WALL_THICKNESS,
    bottom_extra: float = BOTTOM_EXTRA,
    segments: int = SEGMENTS,
) -> trimesh.Trimesh:
    """
    Watertight enclosure mesh. Z-up, flange on top, z=0 at open bottom.

    Height map when the light is seated (bezel top flush with enclosure top):
      H                 enclosure / light bezel top
      H - seat_depth    seating ledge (light flange underside)
      ...               upper body cavity
      ...               lower body cavity
      0                 open bottom
    """
    d = derived_dims(
        light_flange_od=light_flange_od,
        light_flange_thickness=light_flange_thickness,
        light_upper_od=light_upper_od,
        light_upper_length=light_upper_length,
        light_lower_od=light_lower_od,
        light_lower_length=light_lower_length,
        radial_clearance=radial_clearance,
        flange_seat_clearance=flange_seat_clearance,
        seat_depth_extra=seat_depth_extra,
        cover_flange_od=cover_flange_od,
        cover_flange_thickness=cover_flange_thickness,
        wall_thickness=wall_thickness,
        bottom_extra=bottom_extra,
    )
    if cover_flange_od <= d["sleeve_od"] + 6.0:
        raise ValueError("cover_flange_od must be larger than sleeve OD by ~6 mm+")

    H = d["total_height"]
    seat_depth = d["seat_depth"]
    z_ledge = H - seat_depth
    z_step = z_ledge - light_upper_length  # upper→lower body transition
    z_flange_under = H - cover_flange_thickness

    # Outer solid: cover flange + sleeve (overlap for manifold union)
    flange = _cyl(cover_flange_od / 2.0, cover_flange_thickness + 0.05, z_flange_under - 0.025, segments)
    sleeve = _cyl(d["sleeve_od"] / 2.0, z_flange_under + 0.1, -0.05, segments)
    solid = flange.union(sleeve, engine="manifold")

    # Seat counterbore from top down to ledge
    seat = _cyl(d["seat_id"] / 2.0, seat_depth + 0.2, z_ledge - 0.05, segments)

    # Upper cavity: just below ledge down through upper body (stops at step)
    upper = _cyl(d["upper_cavity_id"] / 2.0, light_upper_length + 0.15, z_step - 0.05, segments)

    # Lower cavity: open bottom through lower body + cable slack
    lower_h = z_step + 0.2
    lower = _cyl(d["lower_cavity_id"] / 2.0, lower_h, -0.1, segments)

    part = solid.difference(seat, engine="manifold")
    part = part.difference(upper, engine="manifold")
    part = part.difference(lower, engine="manifold")

    # Cable exit slot through the sleeve wall at the bottom
    slot_w = light_cable_notch_w + CABLE_SLOT_EXTRA_W
    slot_h = light_cable_notch_h + CABLE_SLOT_EXTRA_H
    slot = box(extents=[d["sleeve_od"], slot_w, slot_h + 0.4])
    slot.apply_translation([d["sleeve_od"] / 2.0, 0.0, slot_h / 2.0 - 0.2])
    part = part.difference(slot, engine="manifold")

    if part.volume < 0:
        part.invert()
    part.merge_vertices()
    trimesh.repair.fix_normals(part)
    return part


def export_stl(tri: trimesh.Trimesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if tri.volume < 0:
        tri.invert()
    data = stl_mesh.Mesh(np.zeros(tri.faces.shape[0], dtype=stl_mesh.Mesh.dtype))
    for i, face in enumerate(tri.faces):
        data.vectors[i] = tri.vertices[face]
    data.save(str(path))


def main() -> None:
    p = argparse.ArgumentParser(description="Generate patio LED mounting enclosure STL")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "patio_led_mounting_enclosure.stl",
    )
    p.add_argument("--light-flange-od", type=float, default=LIGHT_FLANGE_OD)
    p.add_argument("--light-flange-thickness", type=float, default=LIGHT_FLANGE_THICKNESS)
    p.add_argument("--light-upper-od", type=float, default=LIGHT_UPPER_OD)
    p.add_argument("--light-upper-length", type=float, default=LIGHT_UPPER_LENGTH)
    p.add_argument("--light-lower-od", type=float, default=LIGHT_LOWER_OD)
    p.add_argument("--light-lower-length", type=float, default=LIGHT_LOWER_LENGTH)
    p.add_argument("--cover-flange-od", type=float, default=COVER_FLANGE_OD)
    p.add_argument("--radial-clearance", type=float, default=RADIAL_CLEARANCE)
    p.add_argument("--segments", type=int, default=SEGMENTS)
    args = p.parse_args()

    kw = dict(
        light_flange_od=args.light_flange_od,
        light_flange_thickness=args.light_flange_thickness,
        light_upper_od=args.light_upper_od,
        light_upper_length=args.light_upper_length,
        light_lower_od=args.light_lower_od,
        light_lower_length=args.light_lower_length,
        cover_flange_od=args.cover_flange_od,
        radial_clearance=args.radial_clearance,
        segments=args.segments,
    )
    tri = build_enclosure(**kw)
    export_stl(tri, args.output)
    summary = derived_dims(**{k: v for k, v in kw.items() if k != "segments"})
    print(f"Wrote {args.output}")
    print(f"  watertight : {tri.is_watertight}")
    print(f"  triangles  : {len(tri.faces)}")
    print(f"  volume     : {tri.volume:.0f} mm³")
    print(f"  extents    : {tri.extents[0]:.2f} × {tri.extents[1]:.2f} × {tri.extents[2]:.2f} mm")
    print("  enclosure  :")
    for k, v in summary.items():
        print(f"    {k:22s} {v:.2f} mm")
    print("  NOTE: light dimensions are PHOTO ESTIMATES — measure before final print.")


if __name__ == "__main__":
    main()
