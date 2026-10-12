#!/usr/bin/env python3
"""Build attic staircase parts as BRep solids and export STEP for Fusion 360.

Open these .step files in Fusion 360 via Insert → Insert Mesh is NOT needed:
use File → Open or Upload, then you get editable solid bodies (Push/Pull, holes, etc.).

Usage:
    python3 export_fusion.py
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

OUT = Path(__file__).resolve().parent


def catching_piece(*, use_printed_bar: bool = False) -> cq.Workplane:
    hole_d = 50.0
    hole_depth = 31.0
    plug_clearance = 0.5
    plug_od = hole_d - 2 * plug_clearance
    flange_od = 80.0
    flange_thickness = 5.0
    dome_bulge = 8.0
    plug_cyl_h = hole_depth - dome_bulge - 0.5

    pocket_w = 34.0
    pocket_h = 26.0
    pocket_len = 38.0
    bar_z = 10.0
    m8_clearance_d = 8.4
    printed_bar_d = 10.0

    screw_d = 4.5
    screw_head_d = 9.0
    screw_head_h = 3.0
    screw_circle_r = 33.0
    screw_count = 4

    floor_screw_d = 4.0
    floor_screw_r = 12.0
    floor_screw_count = 3

    plug_r = plug_od / 2

    body = (
        cq.Workplane("XY")
        .circle(flange_od / 2)
        .extrude(flange_thickness)
    )
    plug = (
        cq.Workplane("XY")
        .circle(plug_od / 2)
        .extrude(plug_cyl_h)
        .translate((0, 0, flange_thickness))
    )
    body = body.union(plug)

    sphere = (
        cq.Workplane("XY")
        .sphere(plug_r)
        .translate((0, 0, flange_thickness + plug_cyl_h - plug_r + dome_bulge))
    )
    clip = (
        cq.Workplane("XY")
        .box(plug_od + 2, plug_od + 2, dome_bulge + 0.2, centered=(True, True, False))
        .translate((0, 0, flange_thickness + plug_cyl_h))
    )
    body = body.union(sphere.intersect(clip))

    pocket = (
        cq.Workplane("XY")
        .box(pocket_w, pocket_len, pocket_h + 0.02, centered=(True, True, False))
        .translate((0, 0, -0.01))
    )
    body = body.cut(pocket)

    if use_printed_bar:
        bar = (
            cq.Workplane("YZ")
            .circle(printed_bar_d / 2)
            .extrude(pocket_w + 4)
            .translate((-(pocket_w / 2 + 2), 0, bar_z))
        )
        body = body.union(bar)
    else:
        bore = (
            cq.Workplane("YZ")
            .circle(m8_clearance_d / 2)
            .extrude(flange_od + 4)
            .translate((-(flange_od + 4) / 2, 0, bar_z))
        )
        body = body.cut(bore)
        for sx in (-1.0, 1.0):
            hex_cut = (
                cq.Workplane("YZ")
                .polygon(6, 15.2)
                .extrude(8.5)
                .translate((sx * (pocket_w / 2 + 4.0) - 4.25, 0, bar_z))
            )
            body = body.cut(hex_cut)

    for i in range(screw_count):
        ang = math.radians(i * 360 / screw_count + 45)
        x = screw_circle_r * math.cos(ang)
        y = screw_circle_r * math.sin(ang)
        through = (
            cq.Workplane("XY")
            .circle(screw_d / 2)
            .extrude(flange_thickness + plug_cyl_h + dome_bulge + 1)
            .translate((x, y, -0.01))
        )
        cs = (
            cq.Workplane("XY")
            .workplane(offset=flange_thickness - screw_head_h)
            .center(x, y)
            .circle(screw_d / 2)
            .workplane(offset=screw_head_h + 0.05)
            .circle(screw_head_d / 2)
            .loft()
        )
        body = body.cut(through).cut(cs)

    for i in range(floor_screw_count):
        ang = math.radians(i * 360 / floor_screw_count + 90)
        x = floor_screw_r * math.cos(ang)
        y = floor_screw_r * math.sin(ang)
        z0 = flange_thickness + plug_cyl_h - 1
        floor = (
            cq.Workplane("XY")
            .circle(floor_screw_d / 2)
            .extrude(dome_bulge + 3)
            .translate((x, y, z0))
        )
        body = body.cut(floor)

    return body


def _cyl_y(d: float, x: float, z: float, width: float) -> cq.Workplane:
    """Cylinder whose axis is Y, centred at (x, 0, z)."""
    return (
        cq.Workplane("XZ")
        .center(x, z)
        .circle(d / 2)
        .extrude(width / 2, both=True)
    )


def pole_hook() -> cq.Workplane:
    pole_d = 28.0
    sleeve_clearance = 0.35
    sleeve_id = pole_d + 2 * sleeve_clearance
    wall = 6.0
    sleeve_od = sleeve_id + 2 * wall
    sleeve_length = 55.0

    screw_d = 4.5
    screw_z1 = 14.0
    screw_z2 = 36.0
    countersink_d = 9.0
    countersink_h = 2.5

    throat = 11.0
    hook_width = 16.0
    arm_t = 7.0
    crook_rise = 10.0
    tip_back = 11.0
    spine_drop = 28.0
    spine_w = 10.0

    r_out = sleeve_od / 2
    seat_x = r_out + throat / 2
    seat_z = sleeve_length + crook_rise
    outer = throat + 2 * arm_t

    sleeve = cq.Workplane("XY").circle(sleeve_od / 2).extrude(sleeve_length)
    bore = (
        cq.Workplane("XY")
        .circle(sleeve_id / 2)
        .extrude(sleeve_length + 2)
        .translate((0, 0, -1))
    )
    body = sleeve.cut(bore)

    crook = _cyl_y(outer, seat_x, seat_z, hook_width)

    # Neck: tapered block from sleeve wall up into the crook (union, no hull)
    neck = (
        cq.Workplane("XY")
        .box(arm_t + 4, hook_width, crook_rise + 12, centered=(True, True, False))
        .translate((r_out + (arm_t + 4) / 2 - 1, 0, sleeve_length - 10))
    )

    # Top cap of the J
    top_cap = (
        cq.Workplane("XY")
        .box(outer, hook_width, arm_t, centered=True)
        .translate((seat_x, 0, seat_z + throat / 2 + arm_t / 2 - 0.5))
    )

    # Tip lip curling back toward the handle
    tip_h = throat / 2 + tip_back
    tip = (
        cq.Workplane("XY")
        .box(arm_t, hook_width, tip_h, centered=(True, True, False))
        .translate(
            (
                seat_x + throat / 2 + arm_t / 2 - 0.5,
                0,
                seat_z - tip_h + arm_t / 2,
            )
        )
    )

    # Spine rib down the +X face
    spine = (
        cq.Workplane("XY")
        .box(wall + 1.5, spine_w, spine_drop, centered=(True, True, False))
        .translate((r_out - 0.5 + (wall + 1.5) / 2, 0, sleeve_length - spine_drop))
    )
    spine_flare = (
        cq.Workplane("XY")
        .box(wall + 1.5, hook_width, 8, centered=(True, True, False))
        .translate((r_out - 0.5 + (wall + 1.5) / 2, 0, sleeve_length - 8))
    )

    hook = crook.union(neck).union(top_cap).union(tip).union(spine).union(spine_flare)

    seat = _cyl_y(throat, seat_x, seat_z, hook_width + 0.2)
    mouth = (
        cq.Workplane("XY")
        .box(throat / 2 + arm_t + 8, hook_width + 1, throat, centered=True)
        .translate((seat_x - 1 + (throat / 2 + arm_t + 8) / 2, 0, seat_z))
    )
    lead = (
        cq.Workplane("XY")
        .box(6, hook_width + 1, 8, centered=True)
        .translate(
            (
                seat_x + throat / 2 + 3.5,
                0,
                seat_z - throat / 2 - tip_back + 4,
            )
        )
        .rotate(
            (seat_x + throat / 2 + 0.5, 0, seat_z - throat / 2 - tip_back),
            (0, 1, 0),
            -35,
        )
    )
    hook = hook.cut(seat).cut(mouth).cut(lead)
    body = body.union(hook).cut(bore)

    for z in (screw_z1, screw_z2):
        screw = (
            cq.Workplane("YZ")
            .circle(screw_d / 2)
            .extrude(sleeve_od + 2)
            .translate((-(sleeve_od + 2) / 2, 0, z))
        )
        body = body.cut(screw)
        # Countersink on +X outer wall
        cs = (
            cq.Workplane("YZ")
            .workplane(offset=sleeve_od / 2 - countersink_h)
            .circle(screw_d / 2)
            .workplane(offset=countersink_h + 0.05)
            .circle(countersink_d / 2)
            .loft()
            .translate((0, 0, z))
        )
        body = body.cut(cs)

    return body


def export_step(solid: cq.Workplane, path: Path) -> None:
    cq.exporters.export(solid, str(path))
    print(f"wrote {path.name} ({path.stat().st_size // 1024} KB)")


def main() -> None:
    print("Building catching_piece …")
    catch = catching_piece(use_printed_bar=False)
    print("Building catching_piece_printed_bar …")
    catch_bar = catching_piece(use_printed_bar=True)
    print("Building pole_hook …")
    hook = pole_hook()

    export_step(catch, OUT / "catching_piece.step")
    export_step(catch_bar, OUT / "catching_piece_printed_bar.step")
    export_step(hook, OUT / "pole_hook.step")

    assembly = (
        cq.Assembly()
        .add(catch, name="catching_piece", loc=cq.Location(cq.Vector(0, 0, 0)))
        .add(hook, name="pole_hook", loc=cq.Location(cq.Vector(120, 0, 0)))
    )
    asm_path = OUT / "attic_staircase_assembly.step"
    assembly.save(str(asm_path))
    print(f"wrote {asm_path.name} ({asm_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
