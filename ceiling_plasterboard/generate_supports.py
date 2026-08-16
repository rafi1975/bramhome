#!/usr/bin/env python3
"""
Ceiling plasterboard supports for Bambu Lab P1S.

Problem
-------
New board is 13 mm; existing ceiling board is 17 mm. The room faces only
line up if the new board is packed 4 mm off the timber. Joist / beam
soffits are also at different heights, so each fixing needs extra packing
down to a common plane.

Printed parts are spacers and alignment clips. Drywall screws must pass
through the plastic and bite timber (or tap into the seam-biscuit flanges).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh
from stl import mesh as stl_mesh
from trimesh.creation import box as _box
from trimesh.creation import cylinder as _cylinder
from trimesh.creation import revolve as _revolve

# ---------------------------------------------------------------------------
# Known measurements (mm) — edit here or pass CLI flags
# ---------------------------------------------------------------------------
NEW_BOARD = 13.0
OLD_BOARD = 17.0

# Part 1 — measured strip (mm): along joist × across joist × pack thickness
SUPPORT_1_LENGTH = 220.0
SUPPORT_1_DEPTH = 20.0
SUPPORT_1_HEIGHT = 8.0

# Part 2 — measured strip (mm)
SUPPORT_2_LENGTH = 190.0
SUPPORT_2_DEPTH = 20.0
SUPPORT_2_HEIGHT = 4.0

# Part 3 — same as part 2, shorter
SUPPORT_3_LENGTH = 130.0
SUPPORT_3_DEPTH = 20.0
SUPPORT_3_HEIGHT = 4.0

# 3.5 × 30 mm countersunk wood screws (DIN 7997 / typical SPAX)
SCREW_SHANK = 3.5
SCREW_LENGTH = 30.0
SCREW_CLEARANCE = 4.0  # through-hole, FDM clearance on a 3.5 mm shank
SCREW_HEAD_OD = 8.2  # recess — hides ~7 mm CSK head plus print tolerance
SCREW_SINK_EXTRA = 0.4  # head sits slightly below the strip face

# Common timber joist widths (EU 45 / 60 / 80 / 100, UK/IE dressed 47)
JOIST_WIDTHS = (45.0, 47.0, 60.0, 80.0, 100.0)

# Stackable leveling shims. 4 mm is the board-thickness compensator.
SHIM_THICKNESSES = (1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 10.0, 15.0, 20.0)

# Drywall / wood screws: 3.5–4.2 mm shank → clearance; pilots for PETG
CLEARANCE_HOLE = 4.8
PILOT_HOLE = 3.2

# Bambu Lab P1S build volume
P1S = (256.0, 256.0, 256.0)

ENGINE = "manifold"


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def aabb(xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float) -> trimesh.Trimesh:
    m = _box(extents=[xmax - xmin, ymax - ymin, zmax - zmin])
    m.apply_translation([(xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0])
    return m


def cyl(radius: float, height: float, cx: float, cy: float, cz: float, axis: str = "z") -> trimesh.Trimesh:
    m = _cylinder(radius=radius, height=height, sections=48)
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [0, 1, 0]))
    elif axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0]))
    m.apply_translation([cx, cy, cz])
    return m


def _mesh(vertices: np.ndarray, faces: list[tuple[int, int, int]]) -> trimesh.Trimesh:
    m = trimesh.Trimesh(vertices=np.asarray(vertices, dtype=np.float64), faces=np.asarray(faces), process=True)
    return clean(m)


def teardrop_y(radius: float, length: float, cx: float, cy: float, cz: float) -> trimesh.Trimesh:
    """Horizontal hole along Y with a +Z teardrop so it prints without supports."""
    body = cyl(radius, length, cx, cy, cz, axis="y")
    tip = radius * 1.15
    y0, y1 = cy - length / 2.0, cy + length / 2.0
    verts = [
        [cx - radius, y0, cz],
        [cx + radius, y0, cz],
        [cx, y0, cz + tip],
        [cx - radius, y1, cz],
        [cx + radius, y1, cz],
        [cx, y1, cz + tip],
    ]
    faces = [
        (0, 1, 2),
        (3, 5, 4),
        (0, 2, 5),
        (0, 5, 3),
        (1, 4, 5),
        (1, 5, 2),
        (0, 3, 4),
        (0, 4, 1),
    ]
    return union(body, _mesh(verts, faces))


def wedge_gusset(x0: float, x1: float, y: float, z: float, leg: float) -> trimesh.Trimesh:
    """Right-angle 45° gusset: legs along +Y and +Z, extruded x0→x1."""
    verts = [
        [x0, y, z],
        [x1, y, z],
        [x0, y + leg, z],
        [x1, y + leg, z],
        [x0, y, z + leg],
        [x1, y, z + leg],
    ]
    faces = [
        (0, 1, 3),
        (0, 3, 2),  # bottom
        (0, 4, 5),
        (0, 5, 1),  # back
        (2, 3, 5),
        (2, 5, 4),  # hypotenuse
        (0, 2, 4),  # left
        (1, 5, 3),  # right
    ]
    return _mesh(verts, faces)


def union(*meshes: trimesh.Trimesh) -> trimesh.Trimesh:
    acc = meshes[0]
    for m in meshes[1:]:
        acc = acc.union(m, engine=ENGINE)
    return clean(acc)


def subtract(base: trimesh.Trimesh, *tools: trimesh.Trimesh) -> trimesh.Trimesh:
    acc = base
    for t in tools:
        acc = acc.difference(t, engine=ENGINE)
    return clean(acc)


def clean(m: trimesh.Trimesh) -> trimesh.Trimesh:
    m.merge_vertices()
    m.update_faces(m.unique_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    if m.volume < 0:
        m.invert()
    return m


def rounded_plate(length: float, width: float, thick: float, radius: float = 3.0) -> trimesh.Trimesh:
    r = min(radius, length / 2.0 - 0.4, width / 2.0 - 0.4)
    if r < 0.6:
        return aabb(0, length, 0, width, 0, thick)
    core = aabb(r, length - r, 0, width, 0, thick)
    core = union(core, aabb(0, length, r, width - r, 0, thick))
    for x, y in ((r, r), (length - r, r), (r, width - r), (length - r, width - r)):
        core = union(core, cyl(r, thick, x, y, thick / 2.0))
    return core


def drop_to_bed(m: trimesh.Trimesh) -> trimesh.Trimesh:
    m.apply_translation(-m.bounds[0])
    return m


def screw_cutter(
    cx: float,
    cy: float,
    thick: float,
    shank: float = SCREW_CLEARANCE,
    head: float = SCREW_HEAD_OD,
    extra: float = SCREW_SINK_EXTRA,
) -> trimesh.Trimesh:
    """Through-hole + 90° countersink + shallow spotface. Recess is on +Z (top).

    3.5 × 30 CSK: Ø4.0 shank hole, Ø8.2 head recess. Print this face up.
    """
    shank_r = shank / 2.0
    head_r = head / 2.0
    cone = head_r - shank_r  # 90° included angle: radial drop = axial drop
    floor = 0.9  # keep a solid washer of plastic under the head
    extra = min(extra, max(0.2, thick - floor - cone))
    cone = min(cone, max(0.6, thick - floor - extra))
    z_top = thick + 0.3
    z_spot = thick - extra
    z_cone = z_spot - cone
    profile = np.array(
        [
            [0.0, -0.6],
            [shank_r, -0.6],
            [shank_r, z_cone],
            [head_r, z_spot],
            [head_r, z_top],
            [0.0, z_top],
            [0.0, -0.6],
        ],
        dtype=np.float64,
    )
    cutter = _revolve(profile, sections=48)
    if cutter.volume < 0:
        cutter.invert()
    cutter.apply_translation([cx, cy, 0.0])
    return cutter


# ---------------------------------------------------------------------------
# 7-segment thickness label (recessed)
# ---------------------------------------------------------------------------
_SEGS = {
    "A": (1.2, 5.0, 8.6, 10.0),
    "B": (5.0, 6.4, 5.0, 8.8),
    "C": (5.0, 6.4, 1.2, 5.0),
    "D": (1.2, 5.0, 0.0, 1.4),
    "E": (0.0, 1.4, 1.2, 5.0),
    "F": (0.0, 1.4, 5.0, 8.8),
    "G": (1.2, 5.0, 4.3, 5.7),
}
_DIGIT = {
    0: "ABCDEF",
    1: "BC",
    2: "ABGED",
    3: "ABGCD",
    4: "FGBC",
    5: "AFGCD",
    6: "AFGCDE",
    7: "ABC",
    8: "ABCDEFG",
    9: "ABGFCD",
}


def _digit_boxes(n: int, x0: float, y0: float, z0: float, z1: float, scale: float = 1.0) -> list[trimesh.Trimesh]:
    out = []
    for seg in _DIGIT[n]:
        x1, x2, y1, y2 = _SEGS[seg]
        out.append(
            aabb(
                x0 + x1 * scale,
                x0 + x2 * scale,
                y0 + y1 * scale,
                y0 + y2 * scale,
                z0,
                z1,
            )
        )
    return out


def thickness_label_cutters(value: float, length: float, width: float, thick: float) -> list[trimesh.Trimesh]:
    """Recessed digits on the top face. Skipped on 1 mm parts (would punch through)."""
    depth = min(0.7, thick * 0.35)
    if depth < 0.35:
        return []
    z0, z1 = thick - depth, thick + 0.2
    n = int(round(value))
    scale = 0.85
    digit_w, digit_h = 6.4 * scale, 10.0 * scale
    if n >= 10:
        tens, ones = divmod(n, 10)
        gap = 1.2
        total = 2 * digit_w + gap
        x0 = (length - total) / 2.0
        y0 = (width - digit_h) / 2.0
        return _digit_boxes(tens, x0, y0, z0, z1, scale) + _digit_boxes(
            ones, x0 + digit_w + gap, y0, z0, z1, scale
        )
    x0 = (length - digit_w) / 2.0
    y0 = (width - digit_h) / 2.0
    return _digit_boxes(n, x0, y0, z0, z1, scale)


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------
SHIM_L = 50.0
SHIM_W = 40.0
HOLE_SPAN = 30.0  # centre-to-centre along the joist


def hole_xs(length: float = SHIM_L) -> tuple[float, float]:
    mid = length / 2.0
    return mid - HOLE_SPAN / 2.0, mid + HOLE_SPAN / 2.0


def make_shim(thick: float, hole: float = CLEARANCE_HOLE) -> trimesh.Trimesh:
    plate = rounded_plate(SHIM_L, SHIM_W, thick, radius=3.0)
    x1, x2 = hole_xs()
    y = SHIM_W / 2.0
    overlap = 0.4
    tools = [
        cyl(hole / 2.0, thick + 2 * overlap, x1, y, thick / 2.0),
        cyl(hole / 2.0, thick + 2 * overlap, x2, y, thick / 2.0),
    ]
    tools.extend(thickness_label_cutters(thick, SHIM_L, SHIM_W, thick))
    return drop_to_bed(subtract(plate, *tools))


def make_packer_strip(
    length: float = SUPPORT_1_LENGTH,
    width: float = SUPPORT_1_DEPTH,
    thick: float = SUPPORT_1_HEIGHT,
    hole: float = SCREW_CLEARANCE,
    countersink: bool = True,
    label: bool = False,
) -> trimesh.Trimesh:
    """Strip on the joist soffit. 3.5 × 30 screws, heads recessed on the top face."""
    radius = 2.0 if width <= 24.0 else 4.0
    end_inset = 15.0 if length >= 80.0 else max(8.0, length * 0.12)
    plate = rounded_plate(length, width, thick, radius=radius)
    y = width / 2.0
    pitch = 48.0
    n = max(2, int(round((length - 2.0 * end_inset) / pitch)) + 1)
    xs = np.linspace(end_inset, length - end_inset, n)
    if countersink:
        tools = [screw_cutter(float(x), y, thick) for x in xs]
    else:
        tools = [cyl(hole / 2.0, thick + 0.8, float(x), y, thick / 2.0) for x in xs]
    if label:
        tools.extend(thickness_label_cutters(thick, min(60.0, length), width, thick))
    return drop_to_bed(subtract(plate, *tools))


def make_joist_saddle(
    joist_width: float,
    length: float = 50.0,
    arm_h: float = 28.0,
    wall: float = 4.5,
    base: float = 4.0,
    clearance: float = 1.2,
    hole: float = CLEARANCE_HOLE,
) -> trimesh.Trimesh:
    """
    U-clip: base on the joist soffit (4 mm already = board compensator),
    arms hug the joist cheeks. Print base-down, arms up, no supports.
    Extra leveling shims stack on the room-facing side of the base
    (same 30 mm hole span).
    """
    inner = joist_width + clearance
    outer = inner + 2.0 * wall
    # Outer block minus joist pocket
    solid = aabb(0, length, 0, outer, 0, base + arm_h)
    pocket = aabb(-0.2, length + 0.2, wall, wall + inner, base, base + arm_h + 0.4)
    body = subtract(solid, pocket)

    # Base holes (into soffit) — same pattern as shims, centred on the joist
    x1, x2 = hole_xs(length)
    y_mid = wall + inner / 2.0
    body = subtract(
        body,
        cyl(hole / 2.0, base + 1.0, x1, y_mid, base / 2.0),
        cyl(hole / 2.0, base + 1.0, x2, y_mid, base / 2.0),
    )

    # One teardrop in each arm, into the joist cheek (print-friendly)
    arm_z = base + arm_h * 0.55
    body = subtract(
        body,
        teardrop_y(hole / 2.0, wall + 2.0, length / 2.0, wall / 2.0, arm_z),
        teardrop_y(hole / 2.0, wall + 2.0, length / 2.0, outer - wall / 2.0, arm_z),
    )
    return drop_to_bed(body)


def make_side_hanger(
    plate_w: float = 50.0,
    plate_h: float = 85.0,
    thick: float = 5.5,
    flange: float = 40.0,
    slot_w: float = 5.5,
    slot_len: float = 46.0,
    gusset: float = 20.0,
    hole: float = CLEARANCE_HOLE,
) -> trimesh.Trimesh:
    """
    Slotted L-hanger for uneven beams.

    Screw the plate to the joist cheek through the slots, slide to a laser
    line, tighten. The flange is the packing face: stack shims on it, then
    screw the 13 mm board through shims + flange into a timber batten — or
    through into the joist soffit if the flange sits under the joist.

    Print: plate on the bed, flange standing up. Gusset is a 45° wedge
    printed from the bed so the L-corner is not a layer-adhesion joint.
    ~45 mm of drop adjustment in the slots.
    """
    plate = aabb(0, plate_w, 0, plate_h, 0, thick)
    # Flange stands up in +Z from the y=0 edge (bottom of hanger)
    fl = aabb(0, plate_w, 0, thick, 0, thick + flange)
    body = union(plate, fl)

    # 45° gusset from the plate (bed) into the flange wall
    body = union(body, wedge_gusset(2.0, plate_w - 2.0, thick, thick, gusset))

    # Two vertical slots through the plate (into joist cheek)
    slot_x1 = plate_w / 2.0 - 11.0
    slot_x2 = plate_w / 2.0 + 11.0
    slot_y0 = plate_h - 10.0 - slot_len
    slot_y1 = plate_h - 10.0
    r = slot_w / 2.0
    for sx in (slot_x1, slot_x2):
        slot = aabb(sx - r, sx + r, slot_y0 + r, slot_y1 - r, -0.4, thick + 0.4)
        slot = union(
            slot,
            cyl(r, thick + 0.8, sx, slot_y0 + r, thick / 2.0),
            cyl(r, thick + 0.8, sx, slot_y1 - r, thick / 2.0),
        )
        body = subtract(body, slot)

    # Flange holes, same 30 mm span as the shims, centred on the 40 mm flange
    x1, x2 = hole_xs(plate_w)
    z_hole = thick + SHIM_W / 2.0
    body = subtract(
        body,
        teardrop_y(hole / 2.0, thick + 2.0, x1, thick / 2.0, z_hole),
        teardrop_y(hole / 2.0, thick + 2.0, x2, thick / 2.0, z_hole),
    )
    return drop_to_bed(body)


def make_stepped_backer(
    old_board: float = OLD_BOARD,
    new_board: float = NEW_BOARD,
    length: float = 120.0,
    width: float = 50.0,
    plate: float = 8.0,
    pilot: float = PILOT_HOLE,
) -> trimesh.Trimesh:
    """
    Hidden backer for a cut joint (not on a joist).

    Sits in the cavity on the backs of both boards. The 4 mm step on the
    new-board half pushes 13 mm board down so the room faces are flush.
    Drywall screws from the room tap into the Ø3.2 pilots.

    Print: cavity face (flat back) on the bed, step up, no supports.
    """
    step = old_board - new_board
    if step <= 0:
        raise ValueError("old board must be thicker than new board")
    # z=0 cavity face; +z toward the room
    body = aabb(0, length, 0, width, 0, plate)
    # New-board half is x=0..length/2 — extra `step` toward the room
    pad = aabb(0, length / 2.0, 0, width, plate - 0.05, plate + step)
    body = union(body, pad)

    def pilots(x0: float, x1: float, z_face: float) -> list[trimesh.Trimesh]:
        xs = np.linspace(x0 + 14.0, x1 - 14.0, 3)
        ys = (width * 0.28, width * 0.72)
        out = []
        for x in xs:
            for y in ys:
                out.append(cyl(pilot / 2.0, plate + step + 1.0, float(x), float(y), z_face / 2.0))
        return out

    z_new = plate + step
    z_old = plate
    tools = pilots(0.0, length / 2.0, z_new) + pilots(length / 2.0, length, z_old)
    # Tiny joint groove on the room-facing step edge so you can feel the centre
    tools.append(aabb(length / 2.0 - 0.4, length / 2.0 + 0.4, -0.1, width + 0.1, plate + step - 0.6, plate + step + 0.2))
    return drop_to_bed(subtract(body, *tools))


def make_seam_biscuit(
    old_board: float = OLD_BOARD,
    new_board: float = NEW_BOARD,
    along: float = 60.0,
    flange: float = 20.0,
    web: float = 1.4,
    face_gap: float = 1.6,
    back: float = 3.5,
    pilot: float = PILOT_HOLE,
) -> trimesh.Trimesh:
    """
    Hidden H-clip at the old/new joint.

    Slide the 17 mm jaw onto the cut edge of the existing board (from the
    opening). Offer up the 13 mm board onto the lower flange and screw
    from the room into the flange. The web sits in a ~2 mm taping gap and
    stops 1.6 mm short of the room face so it never shows.

    Print: extrude along the joint (profile in XY, 60 mm in Z) — no supports.
    """
    step = old_board - new_board
    if step <= 0:
        raise ValueError("old board must be thicker than new board")
    top = old_board + back  # cavity-side of old flange
    # x=0 at old-board far edge of flange; room at y=0
    old_fl = aabb(0, flange, old_board, top, 0, along)
    web_body = aabb(flange, flange + web, face_gap, top, 0, along)
    new_fl = aabb(flange + web, flange + web + flange, new_board, top, 0, along)
    body = union(old_fl, web_body, new_fl)

    # Pilots through each flange, along the joint (Z), from the room side
    y_old = (old_board + top) / 2.0
    y_new = (new_board + top) / 2.0
    x_old = flange / 2.0
    x_new = flange + web + flange / 2.0
    zs = (along * 0.28, along * 0.72)
    tools = []
    for z in zs:
        tools.append(cyl(pilot / 2.0, old_board + back + 1.0, x_old, y_old, z, axis="y"))
        tools.append(cyl(pilot / 2.0, (top - new_board) + 1.0, x_new, y_new, z, axis="y"))
    return drop_to_bed(subtract(body, *tools))


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def export_stl(tri: trimesh.Trimesh, path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    tri = drop_to_bed(clean(tri))
    data = stl_mesh.Mesh(np.zeros(tri.faces.shape[0], dtype=stl_mesh.Mesh.dtype))
    for i, face in enumerate(tri.faces):
        data.vectors[i] = tri.vertices[face]
    data.save(str(path))
    ext = tri.extents
    if any(ext[i] > P1S[i] + 0.05 for i in range(3)):
        raise ValueError(f"{path.name} exceeds P1S volume: {ext}")
    return {
        "file": path.name,
        "watertight": bool(tri.is_watertight),
        "triangles": int(len(tri.faces)),
        "volume_mm3": round(float(tri.volume), 1),
        "extents_mm": [round(float(v), 2) for v in ext],
    }


def build_all(
    out_dir: Path,
    new_board: float = NEW_BOARD,
    old_board: float = OLD_BOARD,
    joist_widths: tuple[float, ...] = JOIST_WIDTHS,
    shim_thicknesses: tuple[float, ...] = SHIM_THICKNESSES,
) -> list[dict]:
    pack = old_board - new_board
    out_dir.mkdir(parents=True, exist_ok=True)
    reports: list[dict] = []

    def add(name: str, mesh: trimesh.Trimesh, note: str) -> None:
        info = export_stl(mesh, out_dir / name)
        info["note"] = note
        reports.append(info)
        print(
            f"  {name:32s}  {info['extents_mm'][0]:6.1f}×{info['extents_mm'][1]:5.1f}×"
            f"{info['extents_mm'][2]:5.1f}  wt={info['watertight']}"
        )

    print("Measured parts")
    add(
        "support_220x20x8.stl",
        make_packer_strip(SUPPORT_1_LENGTH, SUPPORT_1_DEPTH, SUPPORT_1_HEIGHT),
        "part 1: 220 × 20 × 8 mm, 3.5×30 CSK recesses",
    )
    add(
        "support_190x20x4.stl",
        make_packer_strip(SUPPORT_2_LENGTH, SUPPORT_2_DEPTH, SUPPORT_2_HEIGHT),
        "part 2: 190 × 20 × 4 mm, 3.5×30 CSK recesses",
    )
    add(
        "support_130x20x4.stl",
        make_packer_strip(SUPPORT_3_LENGTH, SUPPORT_3_DEPTH, SUPPORT_3_HEIGHT),
        "part 3: 130 × 20 × 4 mm, 3.5×30 CSK recesses",
    )

    print("Shims / packers")
    for t in shim_thicknesses:
        tag = str(int(t)) if t == int(t) else str(t).replace(".", "p")
        note = "board-thickness compensator (13→17 mm)" if abs(t - pack) < 0.05 else "leveling shim"
        add(f"shim_{tag}mm.stl", make_shim(t), note)

    add(
        f"packer_strip_{int(pack)}mm.stl",
        make_packer_strip(length=200.0, width=40.0, thick=pack),
        f"{pack:.0f} mm strip for 13 mm board on a level joist",
    )

    print("Joist saddles")
    for w in joist_widths:
        add(
            f"joist_saddle_{int(w)}mm.stl",
            make_joist_saddle(w, base=pack),
            f"U-clip for {w:.0f} mm timber; {pack:.0f} mm base",
        )

    print("Hangers / joint")
    add("side_hanger_slotted.stl", make_side_hanger(), "slotted L-hanger, ~45 mm drop adjustment")
    add(
        "stepped_edge_backer.stl",
        make_stepped_backer(old_board=old_board, new_board=new_board),
        "cavity backer at a cut joint",
    )
    add(
        "seam_biscuit.stl",
        make_seam_biscuit(old_board=old_board, new_board=new_board),
        "H-clip onto 17 mm cut edge, ledge for 13 mm",
    )

    summary = {
        "new_board_mm": new_board,
        "old_board_mm": old_board,
        "pack_mm": pack,
        "measured": {
            "part_1_mm": [SUPPORT_1_LENGTH, SUPPORT_1_DEPTH, SUPPORT_1_HEIGHT],
            "part_2_mm": [SUPPORT_2_LENGTH, SUPPORT_2_DEPTH, SUPPORT_2_HEIGHT],
            "part_3_mm": [SUPPORT_3_LENGTH, SUPPORT_3_DEPTH, SUPPORT_3_HEIGHT],
            "screw": "3.5x30 CSK",
            "shank_hole_mm": SCREW_CLEARANCE,
            "head_recess_mm": SCREW_HEAD_OD,
        },
        "joist_widths_mm": list(joist_widths),
        "parts": reports,
    }
    (out_dir / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    return reports


def main() -> None:
    p = argparse.ArgumentParser(description="Generate ceiling plasterboard support STLs for Bambu P1S")
    p.add_argument("--new-board", type=float, default=NEW_BOARD)
    p.add_argument("--old-board", type=float, default=OLD_BOARD)
    p.add_argument(
        "--joist-width",
        type=str,
        default=",".join(str(int(w)) if w == int(w) else str(w) for w in JOIST_WIDTHS),
        help="comma-separated joist widths in mm",
    )
    p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "stls",
    )
    args = p.parse_args()
    widths = tuple(float(x) for x in args.joist_width.split(",") if x.strip())
    print(f"Pack = {args.old_board - args.new_board:.1f} mm  (old {args.old_board} − new {args.new_board})")
    reports = build_all(args.output_dir, args.new_board, args.old_board, widths)
    bad = [r for r in reports if not r["watertight"]]
    if bad:
        names = ", ".join(r["file"] for r in bad)
        raise SystemExit(f"Non-watertight meshes: {names}")
    print(f"Wrote {len(reports)} STLs to {args.output_dir}")


if __name__ == "__main__":
    main()
