#!/usr/bin/env python3
"""Export BRep STEP solids for CAD exchange.

Note: Fusion 360 cannot turn STEP into editable feature history. For a parametric
Fusion model, run fusion360/AtticStaircaseParts instead (see fusion360/README.md).

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
    flat_top_d = 30.0
    plug_clearance = 0.5
    plug_od = hole_d - 2 * plug_clearance
    flat_top_od = flat_top_d - 2 * plug_clearance
    flange_od = 80.0
    flange_thickness = 5.0
    plug_h = hole_depth - 0.5
    cyl_fraction = 0.35
    cyl_h = plug_h * cyl_fraction
    tap_h = plug_h - cyl_h

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

    floor_screw_d = 4.2
    floor_screw_head_d = 8.0
    floor_screw_head_h = 2.5
    floor_screw_r = 9.0
    floor_screw_count = 3
    top_z = flange_thickness + plug_h
    roof_z = pocket_h

    body = cq.Workplane("XY").circle(flange_od / 2).extrude(flange_thickness)
    cyl = (
        cq.Workplane("XY")
        .circle(plug_od / 2)
        .extrude(cyl_h)
        .translate((0, 0, flange_thickness))
    )
    # Truncated cone / frustum → flat Ø30 top
    frustum = (
        cq.Workplane("XY")
        .circle(plug_od / 2)
        .workplane(offset=tap_h)
        .circle(flat_top_od / 2)
        .loft()
        .translate((0, 0, flange_thickness + cyl_h))
    )
    body = body.union(cyl).union(frustum)

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
        # Through hole + counterbore on ROOM face (z = 0), not door side
        through = (
            cq.Workplane("XY")
            .circle(screw_d / 2)
            .extrude(flange_thickness + 2)
            .translate((x, y, -0.01))
        )
        counterbore = (
            cq.Workplane("XY")
            .circle(screw_head_d / 2)
            .extrude(screw_head_h)
            .translate((x, y, -0.01))
        )
        body = body.cut(through).cut(counterbore)

    for i in range(floor_screw_count):
        ang = math.radians(i * 360 / floor_screw_count + 90)
        x = floor_screw_r * math.cos(ang)
        y = floor_screw_r * math.sin(ang)
        # Through-hole opening on flat top; head seat on pocket side of roof
        through = (
            cq.Workplane("XY")
            .circle(floor_screw_d / 2)
            .extrude(top_z - roof_z + 1.5)
            .translate((x, y, roof_z - 0.5))
        )
        head = (
            cq.Workplane("XY")
            .circle(floor_screw_head_d / 2)
            .extrude(floor_screw_head_h)
            .translate((x, y, roof_z - 0.01))
        )
        mouth = (
            cq.Workplane("XY")
            .circle((floor_screw_d + 0.2) / 2)
            .extrude(1.2)
            .translate((x, y, top_z - 0.6))
        )
        body = body.cut(through).cut(head).cut(mouth)

    return body


def pole_hook() -> cq.Workplane:
    """Clean sleeve + J-hook matching pole_hook.scad."""
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
    tip_drop = 10.0
    spine_drop = 26.0

    r_out = sleeve_od / 2
    seat_x = r_out + throat / 2 + 0.2
    seat_z = sleeve_length + crook_rise
    outer_r = throat / 2 + arm_t
    r_in = throat / 2
    tip_z = seat_z - tip_drop

    sleeve = cq.Workplane("XY").circle(sleeve_od / 2).extrude(sleeve_length)
    bore = (
        cq.Workplane("XY")
        .circle(sleeve_id / 2)
        .extrude(sleeve_length + 2)
        .translate((0, 0, -1))
    )
    body = sleeve.cut(bore)

    # 2D hook profile on XZ, extruded in Y (mirrors clean_hook_2d)
    # Build as solid unions of simple shapes — no leftover scraps
    crook = (
        cq.Workplane("XZ")
        .center(seat_x, seat_z)
        .circle(outer_r)
        .extrude(hook_width / 2, both=True)
    )
    neck = (
        cq.Workplane("XY")
        .box(
            seat_x - r_out + arm_t * 0.5 + 0.2,
            hook_width,
            crook_rise + outer_r + 8,
            centered=(True, True, False),
        )
        .translate(
            (
                r_out - 0.2 + (seat_x - r_out + arm_t * 0.5 + 0.2) / 2,
                0,
                sleeve_length - 8,
            )
        )
    )
    tip = (
        cq.Workplane("XY")
        .box(arm_t, hook_width, seat_z - tip_z + r_in, centered=(True, True, False))
        .translate((seat_x + r_in + arm_t / 2, 0, tip_z))
    )
    crown = (
        cq.Workplane("XY")
        .box(throat + 2 * arm_t, hook_width, arm_t, centered=True)
        .translate((seat_x, 0, seat_z + r_in + arm_t / 2))
    )
    spine = (
        cq.Workplane("XY")
        .box(wall * 0.75, hook_width * 0.7, spine_drop + 0.2, centered=(True, True, False))
        .translate((r_out - 0.2 + wall * 0.75 / 2, 0, sleeve_length - spine_drop))
    )

    hook = crook.union(neck).union(tip).union(crown).union(spine)

    throat_cut = (
        cq.Workplane("XZ")
        .center(seat_x, seat_z)
        .circle(throat / 2)
        .extrude(hook_width / 2 + 0.2, both=True)
    )
    mouth = (
        cq.Workplane("XY")
        .box(outer_r + 8, hook_width + 1, throat, centered=(True, True, True))
        .translate((seat_x + (outer_r + 8) / 2, 0, seat_z))
    )
    # Trim anything that invaded the sleeve bore region (x < r_out)
    invade = (
        cq.Workplane("XY")
        .box(sleeve_od, hook_width + 2, sleeve_length + crook_rise + outer_r + 20,
             centered=(True, True, False))
        .translate((-0.05, 0, -2))
    )
    # Only cut the portion with x < r_out - 0.05
    invade = (
        cq.Workplane("XY")
        .box(r_out + sleeve_od, hook_width + 2, sleeve_length + crook_rise + outer_r + 20,
             centered=(False, True, False))
        .translate((-sleeve_od, 0, -2))
    )

    hook = hook.cut(throat_cut).cut(mouth).cut(invade)
    body = body.union(hook).cut(bore)

    for z in (screw_z1, screw_z2):
        screw = (
            cq.Workplane("YZ")
            .circle(screw_d / 2)
            .extrude(sleeve_od + 2)
            .translate((-(sleeve_od + 2) / 2, 0, z))
        )
        body = body.cut(screw)
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
