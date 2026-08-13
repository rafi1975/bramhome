#!/usr/bin/env python3
"""
Generate an STL for a patio floor-light support / trim ring.

Geometry matches the photographed part:
  - flat circular flange that covers an uneven pavement hole
  - cylindrical sleeve that drops into the hole
  - through-bore for the light body
  - small bottom chamfer for easier insertion
  - exterior fillet where flange meets sleeve (strength)

All dimensions are millimetres. Edit the constants below, or pass CLI
flags, if your pavement hole or light differs from the photo estimates.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh
import trimesh


# ---------------------------------------------------------------------------
# Dimensions estimated from photos (400 ml spray cans ≈ 66 mm OD as scale)
# ---------------------------------------------------------------------------
FLANGE_OD = 98.0  # outer diameter of the cover flange
SLEEVE_OD = 82.0  # outer diameter of the sleeve (fits into drilled hole)
BORE_ID = 76.0  # inner through-hole diameter (light clearance)
FLANGE_THICKNESS = 2.5  # vertical thickness of the flange
SLEEVE_LENGTH = 28.0  # sleeve depth below the underside of the flange
BOTTOM_CHAMFER = 1.2  # radial × axial chamfer at sleeve bottom
FILLET_RADIUS = 1.0  # blend in the flange/sleeve underside corner
SEGMENTS = 192  # circumferential resolution (smooth on P1S)


def build_ring_profile(
    flange_od: float,
    sleeve_od: float,
    bore_id: float,
    flange_thickness: float,
    sleeve_length: float,
    bottom_chamfer: float,
    fillet_radius: float,
) -> np.ndarray:
    """Closed (r, z) polyline for revolution. z=0 at sleeve bottom."""
    if not (bore_id < sleeve_od < flange_od):
        raise ValueError("Need bore_id < sleeve_od < flange_od")
    if flange_thickness <= 0 or sleeve_length <= 0:
        raise ValueError("Thicknesses must be positive")

    r_bore = bore_id / 2.0
    r_sleeve = sleeve_od / 2.0
    r_flange = flange_od / 2.0
    z_under = sleeve_length  # flange underside / sleeve top junction plane
    z_top = sleeve_length + flange_thickness

    wall = r_sleeve - r_bore
    overhang = r_flange - r_sleeve
    chamfer = min(bottom_chamfer, wall - 0.3, sleeve_length / 3.0)
    fillet = min(fillet_radius, overhang - 0.3, flange_thickness, sleeve_length / 2.0)
    if fillet < 0.05:
        fillet = 0.0
    if chamfer < 0.05:
        chamfer = 0.0

    pts: list[tuple[float, float]] = [
        (r_bore, z_top),  # 1 top inner
        (r_flange, z_top),  # 2 top outer
        (r_flange, z_under),  # 3 flange outer bottom
    ]

    if fillet > 0:
        # Concave corner fillet under the flange (adds material for strength).
        # Circle center at (r_sleeve + R, z_under - R).
        for t in np.linspace(0.0, 0.5 * np.pi, 12, endpoint=True):
            rr = (r_sleeve + fillet) - fillet * np.sin(t)
            zz = (z_under - fillet) + fillet * np.cos(t)
            pts.append((float(rr), float(zz)))
        # Last fillet point is (r_sleeve, z_under - fillet); continue down sleeve
        sleeve_top_z = z_under - fillet
    else:
        pts.append((r_sleeve, z_under))
        sleeve_top_z = z_under

    if chamfer > 0:
        pts.append((r_sleeve, chamfer))
        pts.append((r_sleeve - chamfer, 0.0))
    else:
        pts.append((r_sleeve, 0.0))

    pts.append((r_bore, 0.0))  # bottom inner
    pts.append((r_bore, z_top))  # close along inner wall

    # Drop consecutive duplicates
    cleaned = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - cleaned[-1][0]) > 1e-9 or abs(p[1] - cleaned[-1][1]) > 1e-9:
            cleaned.append(p)
    return np.asarray(cleaned, dtype=np.float64)


def revolve_profile(profile_rz: np.ndarray, segments: int) -> trimesh.Trimesh:
    """Revolve an (r, z) closed polyline around Z into a triangle mesh."""
    angles = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=False)
    n_ring = len(profile_rz)
    vertices = np.empty((segments * n_ring, 3), dtype=np.float64)
    for i, angle in enumerate(angles):
        c, s = np.cos(angle), np.sin(angle)
        base = i * n_ring
        vertices[base : base + n_ring, 0] = profile_rz[:, 0] * c
        vertices[base : base + n_ring, 1] = profile_rz[:, 0] * s
        vertices[base : base + n_ring, 2] = profile_rz[:, 1]

    faces = []
    for i in range(segments):
        i0 = i * n_ring
        i1 = ((i + 1) % segments) * n_ring
        for j in range(n_ring - 1):
            a = i0 + j
            b = i1 + j
            c = i1 + j + 1
            d = i0 + j + 1
            faces.append((a, b, c))
            faces.append((a, c, d))

    tri = trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=True)
    tri.merge_vertices()
    tri.update_faces(tri.unique_faces())
    tri.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(tri)
    if tri.volume < 0:
        tri.invert()
    return tri


def create_ring(
    flange_od: float = FLANGE_OD,
    sleeve_od: float = SLEEVE_OD,
    bore_id: float = BORE_ID,
    flange_thickness: float = FLANGE_THICKNESS,
    sleeve_length: float = SLEEVE_LENGTH,
    bottom_chamfer: float = BOTTOM_CHAMFER,
    fillet_radius: float = FILLET_RADIUS,
    segments: int = SEGMENTS,
) -> trimesh.Trimesh:
    profile = build_ring_profile(
        flange_od=flange_od,
        sleeve_od=sleeve_od,
        bore_id=bore_id,
        flange_thickness=flange_thickness,
        sleeve_length=sleeve_length,
        bottom_chamfer=bottom_chamfer,
        fillet_radius=fillet_radius,
    )
    return revolve_profile(profile, segments=segments)


def export_stl(tri: trimesh.Trimesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if tri.volume < 0:
        tri.invert()
    data = stl_mesh.Mesh(np.zeros(tri.faces.shape[0], dtype=stl_mesh.Mesh.dtype))
    for i, face in enumerate(tri.faces):
        data.vectors[i] = tri.vertices[face]
    data.save(str(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate patio light support ring STL")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "patio_light_support_ring.stl",
    )
    parser.add_argument("--flange-od", type=float, default=FLANGE_OD)
    parser.add_argument("--sleeve-od", type=float, default=SLEEVE_OD)
    parser.add_argument("--bore-id", type=float, default=BORE_ID)
    parser.add_argument("--flange-thickness", type=float, default=FLANGE_THICKNESS)
    parser.add_argument("--sleeve-length", type=float, default=SLEEVE_LENGTH)
    parser.add_argument("--bottom-chamfer", type=float, default=BOTTOM_CHAMFER)
    parser.add_argument("--fillet-radius", type=float, default=FILLET_RADIUS)
    parser.add_argument("--segments", type=int, default=SEGMENTS)
    args = parser.parse_args()

    tri = create_ring(
        flange_od=args.flange_od,
        sleeve_od=args.sleeve_od,
        bore_id=args.bore_id,
        flange_thickness=args.flange_thickness,
        sleeve_length=args.sleeve_length,
        bottom_chamfer=args.bottom_chamfer,
        fillet_radius=args.fillet_radius,
        segments=args.segments,
    )
    export_stl(tri, args.output)

    extents = tri.extents
    print(f"Wrote {args.output}")
    print(f"  triangles : {len(tri.faces)}")
    print(f"  watertight: {tri.is_watertight}")
    print(f"  volume    : {tri.volume:.1f} mm³")
    print(f"  extents   : {extents[0]:.2f} × {extents[1]:.2f} × {extents[2]:.2f} mm")
    print(
        f"  dims      : flange Ø{args.flange_od:.1f}, sleeve Ø{args.sleeve_od:.1f}, "
        f"bore Ø{args.bore_id:.1f}, height {args.sleeve_length + args.flange_thickness:.1f}"
    )


if __name__ == "__main__":
    main()
