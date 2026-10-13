#!/usr/bin/env python3
"""Build Bambu Lab P1S print-ready STL + 3MF files (bed-oriented)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent


def sit_on_bed(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh = mesh.copy()
    mesh.apply_translation(-mesh.bounds[0])
    return mesh


def prepare_catch(path: Path) -> trimesh.Trimesh:
    # Already flange-down (Z up). Just seat on bed.
    return sit_on_bed(trimesh.load(path))


def prepare_hook(path: Path) -> trimesh.Trimesh:
    # Design: pole along Z, thickness along Y, opening +X.
    # Lay on flat Y face so layer lines run with the pull force.
    m = trimesh.load(path)
    # Rotate +90° about X: (x,y,z) -> (x,-z,y)  => former Y becomes up (Z)
    T = trimesh.transformations.rotation_matrix(np.pi / 2.0, [1.0, 0.0, 0.0])
    m.apply_transform(T)
    return sit_on_bed(m)


def export_pair(mesh: trimesh.Trimesh, stem: str) -> None:
    stl = ROOT / f"{stem}.stl"
    threemf = ROOT / f"{stem}.3mf"
    mesh.export(stl)
    mesh.export(threemf)
    print(f"wrote {stl.name}  extents={np.round(mesh.extents, 1)} mm")
    print(f"wrote {threemf.name}")


def main() -> None:
    catch = prepare_catch(SRC / "catching_piece.stl")
    catch_bar = prepare_catch(SRC / "catching_piece_printed_bar.stl")
    hook = prepare_hook(SRC / "pole_hook.stl")

    export_pair(catch, "catching_piece_p1s")
    export_pair(catch_bar, "catching_piece_printed_bar_p1s")
    export_pair(hook, "pole_hook_p1s")

    # One plate: catch + hook side by side (fit test)
    catch_p = catch.copy()
    hook_p = hook.copy()
    gap = 8.0
    hook_p.apply_translation([catch_p.extents[0] + gap, 0, 0])
    plate = trimesh.util.concatenate([catch_p, hook_p])
    plate = sit_on_bed(plate)
    export_pair(plate, "attic_fit_test_plate_p1s")
    print(f"plate footprint {np.round(plate.extents, 1)} mm (P1S bed is 256×256)")


if __name__ == "__main__":
    main()
