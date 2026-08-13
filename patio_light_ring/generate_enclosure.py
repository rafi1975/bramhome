#!/usr/bin/env python3
"""
Patio mounting enclosure for a stepped LED spotlight.

Measured dimensions (calipers with the user):
  bezel OD 79.0 × 2.5 mm thick
  upper body Ø72.3 × 15.3 mm (sets bore clearance)
  pavement hole Ø82 mm, cover lip 13 mm → flange Ø108 mm
  sleeve depth 30 mm (sandstone slab — not full light length)

Print: flange on the bed, enable supports for the bezel recess ledge.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh
from stl import mesh as stl_mesh
from trimesh.creation import cylinder, revolve


# ---------------------------------------------------------------------------
# LED spotlight — MEASURED (mm)
# ---------------------------------------------------------------------------
LIGHT_BEZEL_OD = 79.0
LIGHT_BEZEL_THICKNESS = 2.5
LIGHT_UPPER_OD = 72.3  # widest body section — sets sleeve bore

# ---------------------------------------------------------------------------
# Patio hole / cover — MEASURED intent (mm)
# ---------------------------------------------------------------------------
PAVEMENT_HOLE_ID = 82.0
COVER_LIP = 13.0  # radial overhang beyond the hole
COVER_FLANGE_OD = PAVEMENT_HOLE_ID + 2.0 * COVER_LIP  # 108
SLEEVE_OD = 81.0  # fits Ø82 hole with ~1 mm total play
SLEEVE_LENGTH = 30.0  # into sandstone slab only

# ---------------------------------------------------------------------------
# Fit clearances
# ---------------------------------------------------------------------------
RADIAL_CLEARANCE = 0.8  # per side around body
BEZEL_SEAT_CLEARANCE = 0.5  # per side around metal bezel in recess
SEAT_DEPTH_EXTRA = 0.3  # bezel sits slightly recessed / flush-safe
COVER_FLANGE_THICKNESS = 3.0  # must be >= seat depth
EDGE_CHAMFER = 2.0  # anti-trip bevel on outer top edge of cover flange
SEGMENTS = 160


def _cyl(radius: float, height: float, z0: float, sections: int = SEGMENTS) -> trimesh.Trimesh:
    m = cylinder(radius=radius, height=height, sections=sections)
    m.apply_translation([0.0, 0.0, z0 + height / 2.0])
    return m


def _cover_flange(
    flange_od: float,
    thickness: float,
    chamfer: float,
    z_under: float,
    sections: int = SEGMENTS,
) -> trimesh.Trimesh:
    """Cover flange disk with optional outer-top anti-trip chamfer baked in."""
    r = flange_od / 2.0
    z_top = z_under + thickness
    ch = min(chamfer, thickness - 0.2) if chamfer > 0.05 else 0.0
    if ch > 0.05:
        profile = np.array(
            [
                [0.0, z_under],
                [r, z_under],
                [r, z_top - ch],
                [r - ch, z_top],
                [0.0, z_top],
                [0.0, z_under],
            ],
            dtype=np.float64,
        )
    else:
        profile = np.array(
            [
                [0.0, z_under],
                [r, z_under],
                [r, z_top],
                [0.0, z_top],
                [0.0, z_under],
            ],
            dtype=np.float64,
        )
    flange = revolve(profile, sections=sections)
    if flange.volume < 0:
        flange.invert()
    return flange


def derived_dims(
    light_bezel_od: float = LIGHT_BEZEL_OD,
    light_bezel_thickness: float = LIGHT_BEZEL_THICKNESS,
    light_upper_od: float = LIGHT_UPPER_OD,
    radial_clearance: float = RADIAL_CLEARANCE,
    bezel_seat_clearance: float = BEZEL_SEAT_CLEARANCE,
    seat_depth_extra: float = SEAT_DEPTH_EXTRA,
    cover_flange_od: float = COVER_FLANGE_OD,
    cover_flange_thickness: float = COVER_FLANGE_THICKNESS,
    sleeve_od: float = SLEEVE_OD,
    sleeve_length: float = SLEEVE_LENGTH,
    edge_chamfer: float = EDGE_CHAMFER,
) -> dict[str, float]:
    seat_id = light_bezel_od + 2.0 * bezel_seat_clearance
    cavity_id = light_upper_od + 2.0 * radial_clearance
    seat_depth = light_bezel_thickness + seat_depth_extra
    if cover_flange_thickness + 1e-9 < seat_depth:
        raise ValueError(
            f"cover_flange_thickness ({cover_flange_thickness}) must be >= seat_depth ({seat_depth})"
        )
    if edge_chamfer >= cover_flange_thickness:
        raise ValueError("edge_chamfer must be smaller than cover flange thickness")
    if cavity_id >= sleeve_od - 1.0:
        raise ValueError(
            f"cavity ID {cavity_id:.2f} leaves too little wall in sleeve OD {sleeve_od:.2f}"
        )
    if seat_id <= cavity_id + 0.8:
        raise ValueError("bezel seat must be wider than cavity to form a ledge")
    lip_to_seat = (cover_flange_od - seat_id) / 2.0
    if edge_chamfer > lip_to_seat - 2.0:
        raise ValueError("edge_chamfer too large for the cover lip / bezel seat")
    # Sleeve length is below the flange underside; seat lives in the flange.
    total_h = cover_flange_thickness + sleeve_length
    wall = (sleeve_od - cavity_id) / 2.0
    return {
        "cover_flange_od": cover_flange_od,
        "cover_flange_thickness": cover_flange_thickness,
        "edge_chamfer": edge_chamfer,
        "sleeve_od": sleeve_od,
        "sleeve_length": sleeve_length,
        "seat_id": seat_id,
        "seat_depth": seat_depth,
        "cavity_id": cavity_id,
        "wall_thickness": wall,
        "total_height": total_h,
        "ledge_width": (seat_id - cavity_id) / 2.0,
    }


def build_enclosure(
    light_bezel_od: float = LIGHT_BEZEL_OD,
    light_bezel_thickness: float = LIGHT_BEZEL_THICKNESS,
    light_upper_od: float = LIGHT_UPPER_OD,
    radial_clearance: float = RADIAL_CLEARANCE,
    bezel_seat_clearance: float = BEZEL_SEAT_CLEARANCE,
    seat_depth_extra: float = SEAT_DEPTH_EXTRA,
    cover_flange_od: float = COVER_FLANGE_OD,
    cover_flange_thickness: float = COVER_FLANGE_THICKNESS,
    sleeve_od: float = SLEEVE_OD,
    sleeve_length: float = SLEEVE_LENGTH,
    edge_chamfer: float = EDGE_CHAMFER,
    segments: int = SEGMENTS,
) -> trimesh.Trimesh:
    """
    Watertight enclosure in normal (installed) orientation:
      z=0  → open sleeve bottom
      +z   → cover flange on top (bezel recess on the top face)

    Slice with the flange on the build plate and supports enabled for the
    bezel recess ledge.
    """
    d = derived_dims(
        light_bezel_od=light_bezel_od,
        light_bezel_thickness=light_bezel_thickness,
        light_upper_od=light_upper_od,
        radial_clearance=radial_clearance,
        bezel_seat_clearance=bezel_seat_clearance,
        seat_depth_extra=seat_depth_extra,
        cover_flange_od=cover_flange_od,
        cover_flange_thickness=cover_flange_thickness,
        sleeve_od=sleeve_od,
        sleeve_length=sleeve_length,
        edge_chamfer=edge_chamfer,
    )

    H = d["total_height"]
    seat_depth = d["seat_depth"]
    z_ledge = H - seat_depth
    z_flange_under = H - cover_flange_thickness  # == sleeve_length

    flange = _cover_flange(
        cover_flange_od,
        cover_flange_thickness,
        edge_chamfer,
        z_flange_under,
        sections=segments,
    )
    sleeve = _cyl(sleeve_od / 2.0, z_flange_under + 0.1, -0.05, segments)
    solid = flange.union(sleeve, engine="manifold")

    seat = _cyl(d["seat_id"] / 2.0, seat_depth + 0.2, z_ledge - 0.05, segments)
    cavity = _cyl(d["cavity_id"] / 2.0, z_ledge + 0.2, -0.1, segments)

    part = solid.difference(seat, engine="manifold")
    part = part.difference(cavity, engine="manifold")

    if part.volume < 0:
        part.invert()
    part.merge_vertices()
    trimesh.repair.fix_normals(part)
    # Keep normal orientation (flange on top). Rotate flange-down in the slicer.
    part.apply_translation([0.0, 0.0, -part.bounds[0, 2]])
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
    p = argparse.ArgumentParser(description="Generate measured patio LED mounting enclosure STL")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "patio_led_mounting_enclosure.stl",
    )
    p.add_argument("--light-bezel-od", type=float, default=LIGHT_BEZEL_OD)
    p.add_argument("--light-bezel-thickness", type=float, default=LIGHT_BEZEL_THICKNESS)
    p.add_argument("--light-upper-od", type=float, default=LIGHT_UPPER_OD)
    p.add_argument("--cover-flange-od", type=float, default=COVER_FLANGE_OD)
    p.add_argument("--sleeve-od", type=float, default=SLEEVE_OD)
    p.add_argument("--sleeve-length", type=float, default=SLEEVE_LENGTH)
    p.add_argument("--radial-clearance", type=float, default=RADIAL_CLEARANCE)
    p.add_argument("--edge-chamfer", type=float, default=EDGE_CHAMFER)
    p.add_argument("--segments", type=int, default=SEGMENTS)
    args = p.parse_args()

    kw = dict(
        light_bezel_od=args.light_bezel_od,
        light_bezel_thickness=args.light_bezel_thickness,
        light_upper_od=args.light_upper_od,
        cover_flange_od=args.cover_flange_od,
        sleeve_od=args.sleeve_od,
        sleeve_length=args.sleeve_length,
        radial_clearance=args.radial_clearance,
        edge_chamfer=args.edge_chamfer,
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
    print("  Slice: put flange on the bed, enable supports for the bezel recess.")


if __name__ == "__main__":
    main()
