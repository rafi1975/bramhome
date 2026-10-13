#Author: bramhome
#Description: Builds the attic staircase catching piece + pole hook as NATIVE
#             Fusion 360 parametric features (sketches, extrudes, revolves) with
#             User Parameters. This is editable history — not a mesh and not a
#             dumb imported STEP base feature.
#
#Install / run:
#  1. Utilities → Add-Ins → Scripts and Add-Ins
#  2. Click + next to "My Scripts" → select this AtticStaircaseParts folder
#  3. Select AtticStaircaseParts → Run
#  4. Modify → Change Parameters to edit sizes
#  5. Right-click body → Save as Mesh (3MF/STL) for Bambu Lab P1S

import adsk.core
import adsk.fusion
import math
import traceback


def mm(v: float) -> float:
    """Fusion API lengths are centimetres."""
    return float(v) / 10.0


def add_param(design, name, expression, comment=''):
    p = design.userParameters.itemByName(name)
    if p:
        p.expression = expression
    else:
        design.userParameters.add(
            name,
            adsk.core.ValueInput.createByString(expression),
            'mm',
            comment,
        )


def create_parameters(design):
    # --- Catch ---
    add_param(design, 'hole_d', '50 mm', 'Hatch opening diameter')
    add_param(design, 'hole_depth', '31 mm', 'Hatch opening depth')
    add_param(design, 'flat_top_d', '30 mm', 'Flat floor diameter at top of dome')
    add_param(design, 'plug_clearance', '0.5 mm', 'Radial clearance')
    add_param(design, 'plug_od', 'hole_d - 2 * plug_clearance', 'Plug OD at mouth')
    add_param(design, 'flat_top_od', 'flat_top_d - 2 * plug_clearance', 'Plug flat-top OD')
    add_param(design, 'flange_od', '80 mm', 'Flange OD')
    add_param(design, 'flange_thickness', '5 mm', 'Flange thickness')
    add_param(design, 'plug_h', 'hole_depth - 0.5 mm', 'Plug height into cavity')
    add_param(design, 'cyl_fraction', '0.35', 'Fraction of plug that stays near full Ø')
    add_param(design, 'cyl_h', 'plug_h * cyl_fraction', 'Cylindrical plug height')
    add_param(design, 'tap_h', 'plug_h - cyl_h', 'Taper height to flat top')
    add_param(design, 'pocket_w', '34 mm', 'Pocket width')
    add_param(design, 'pocket_len', '38 mm', 'Pocket length')
    add_param(design, 'pocket_h', '26 mm', 'Pocket depth')
    add_param(design, 'bar_z', '10 mm', 'M8 bar centre from flange face')
    add_param(design, 'm8_d', '8.4 mm', 'M8 clearance')
    add_param(design, 'nut_d', '15.2 mm', 'Nut clearance diameter')
    add_param(design, 'nut_h', '8.5 mm', 'Nut clearance depth')
    add_param(design, 'screw_d', '4.5 mm', 'Flange screw hole')
    add_param(design, 'screw_r', '33 mm', 'Flange screw pitch radius')
    add_param(design, 'floor_screw_d', '4 mm', 'Floor screw hole')
    add_param(design, 'floor_screw_r', '9 mm', 'Floor screw pitch radius (inside Ø30)')

    # --- Hook ---
    add_param(design, 'pole_d', '28 mm', 'Pole diameter')
    add_param(design, 'sleeve_clearance', '0.35 mm', 'Sleeve radial clearance')
    add_param(design, 'sleeve_id', 'pole_d + 2 * sleeve_clearance', 'Sleeve ID')
    add_param(design, 'sleeve_wall', '6 mm', 'Sleeve wall')
    add_param(design, 'sleeve_od', 'sleeve_id + 2 * sleeve_wall', 'Sleeve OD')
    add_param(design, 'sleeve_length', '55 mm', 'Sleeve length')
    add_param(design, 'hook_throat', '11 mm', 'Hook throat')
    add_param(design, 'hook_width', '16 mm', 'Hook width (Y)')
    add_param(design, 'hook_arm_t', '7 mm', 'Hook arm thickness')
    add_param(design, 'hook_crook_rise', '10 mm', 'Seat above sleeve end')
    add_param(design, 'hook_tip_back', '11 mm', 'Tip curl length')
    add_param(design, 'hook_screw_d', '4.5 mm', 'Cross screw hole')
    add_param(design, 'hook_screw_z1', '14 mm', 'Screw 1 from open end')
    add_param(design, 'hook_screw_z2', '36 mm', 'Screw 2 from open end')


def largest_profile(sketch):
    best, area = None, -1.0
    for i in range(sketch.profiles.count):
        p = sketch.profiles.item(i)
        a = abs(p.areaProperties().area)
        if a > area:
            best, area = p, a
    return best


def smallest_profile(sketch):
    best, area = None, 1e100
    for i in range(sketch.profiles.count):
        p = sketch.profiles.item(i)
        a = abs(p.areaProperties().area)
        if 0 < a < area:
            best, area = p, a
    return best


def dim_diameter(sketch, circle, expression):
    g = circle.centerSketchPoint.geometry
    text = adsk.core.Point3D.create(g.x + circle.radius + mm(8), g.y + mm(8), 0)
    d = sketch.sketchDimensions.addDiameterDimension(circle, text)
    d.parameter.expression = expression
    return d


def dim_distance(sketch, sp0, sp1, expression, ox=5, oy=5):
    g0, g1 = sp0.geometry, sp1.geometry
    text = adsk.core.Point3D.create((g0.x + g1.x) / 2 + mm(ox), (g0.y + g1.y) / 2 + mm(oy), 0)
    d = sketch.sketchDimensions.addDistanceDimension(
        sp0, sp1, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, text
    )
    d.parameter.expression = expression
    return d


def extrude_one(comp, profile, expr, operation):
    feats = comp.features.extrudeFeatures
    inp = feats.createInput(profile, operation)
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByString(expr))
    return feats.add(inp)


def extrude_symmetric(comp, profile, half_expr, operation):
    feats = comp.features.extrudeFeatures
    inp = feats.createInput(profile, operation)
    half = adsk.core.ValueInput.createByString(half_expr)
    inp.setTwoSidesDistanceExtent(half, half)
    return feats.add(inp)


def new_component(root, name, tx_mm=0.0):
    t = adsk.core.Matrix3D.create()
    if tx_mm:
        t.translation = adsk.core.Vector3D.create(mm(tx_mm), 0, 0)
    occ = root.occurrences.addNewComponent(t)
    occ.component.name = name
    return occ.component


def build_catch(design, root):
    comp = new_component(root, 'CatchingPiece', 0)
    sketches = comp.sketches
    xy = comp.xYConstructionPlane
    extrudes = comp.features.extrudeFeatures
    planes = comp.constructionPlanes

    # Flange disk
    sk = sketches.add(xy)
    sk.name = '01_Flange'
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(40))
    dim_diameter(sk, c, 'flange_od')
    extrude_one(comp, largest_profile(sk), 'flange_thickness',
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    comp.bRepBodies.item(0).name = 'CatchingPiece'

    # Cylindrical plug section at the mouth (near Ø50)
    pin = planes.createInput()
    pin.setByOffset(xy, adsk.core.ValueInput.createByString('flange_thickness'))
    plug_plane = planes.add(pin)
    plug_plane.name = 'PlugPlane'

    sk2 = sketches.add(plug_plane)
    sk2.name = '02_PlugCyl'
    c2 = sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(24.5))
    dim_diameter(sk2, c2, 'plug_od')
    extrude_one(comp, largest_profile(sk2), 'cyl_h',
                adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # Tapered section → flat Ø30 top (loft between two circles)
    pin2 = planes.createInput()
    pin2.setByOffset(xy, adsk.core.ValueInput.createByString('flange_thickness + cyl_h'))
    taper_plane = planes.add(pin2)
    taper_plane.name = 'TaperStart'

    sk3a = sketches.add(taper_plane)
    sk3a.name = '03a_TaperBase'
    c3a = sk3a.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(24.5))
    dim_diameter(sk3a, c3a, 'plug_od')

    pin3 = planes.createInput()
    pin3.setByOffset(xy, adsk.core.ValueInput.createByString('flange_thickness + plug_h'))
    flat_plane = planes.add(pin3)
    flat_plane.name = 'FlatTop'

    sk3b = sketches.add(flat_plane)
    sk3b.name = '03b_FlatTop'
    c3b = sk3b.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(14.5))
    dim_diameter(sk3b, c3b, 'flat_top_od')

    lofts = comp.features.loftFeatures
    loft_inp = lofts.createInput(adsk.fusion.FeatureOperations.JoinFeatureOperation)
    loft_inp.loftSections.add(largest_profile(sk3a))
    loft_inp.loftSections.add(largest_profile(sk3b))
    loft_inp.isSolid = True
    lofts.add(loft_inp)

    # Pocket cut
    sk4 = sketches.add(xy)
    sk4.name = '04_Pocket'
    hw, hl = mm(17), mm(19)
    sk4.sketchCurves.sketchLines.addCenterPointRectangle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(hw, hl, 0),
    )
    # Dimension rectangle by finding extremal sketch points
    pts = [sk4.sketchPoints.item(i) for i in range(sk4.sketchPoints.count)]

    def near(x, y):
        return min(pts, key=lambda p: (p.geometry.x - x) ** 2 + (p.geometry.y - y) ** 2)

    a, b, cpt = near(-hw, -hl), near(hw, -hl), near(-hw, hl)
    dim_distance(sk4, a, b, 'pocket_w', 0, -5)
    dim_distance(sk4, a, cpt, 'pocket_len', -5, 0)
    extrude_one(comp, largest_profile(sk4), 'pocket_h',
                adsk.fusion.FeatureOperations.CutFeatureOperation)

    # M8 hole along X (sketch on YZ, two-sided cut)
    sk5 = sketches.add(comp.yZConstructionPlane)
    sk5.name = '05_M8'
    bc = sk5.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, mm(10), 0), mm(4.2)
    )
    dim_diameter(sk5, bc, 'm8_d')
    cl = sk5.sketchCurves.sketchLines.addByTwoPoints(
        adsk.core.Point3D.create(0, 0, 0), bc.centerSketchPoint.geometry
    )
    cl.isConstruction = True
    dim_distance(sk5, cl.startSketchPoint, bc.centerSketchPoint, 'bar_z')
    b_inp = extrudes.createInput(largest_profile(sk5), adsk.fusion.FeatureOperations.CutFeatureOperation)
    half = adsk.core.ValueInput.createByString('flange_od / 2 + 2 mm')
    b_inp.setTwoSidesDistanceExtent(half, half)
    extrudes.add(b_inp)

    # Nut clearances (cylindrical) on offset YZ planes
    for name, sign in (('06_NutL', -1), ('07_NutR', 1)):
        pin = planes.createInput()
        pin.setByOffset(
            comp.yZConstructionPlane,
            adsk.core.ValueInput.createByString(f'{sign}*(pocket_w/2 + 4 mm)'),
        )
        pl = planes.add(pin)
        pl.name = name + 'Plane'
        skn = sketches.add(pl)
        skn.name = name
        nc = skn.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, mm(10), 0), mm(7.6)
        )
        dim_diameter(skn, nc, 'nut_d')
        cln = skn.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0), nc.centerSketchPoint.geometry
        )
        cln.isConstruction = True
        dim_distance(skn, cln.startSketchPoint, nc.centerSketchPoint, 'bar_z')
        n_inp = extrudes.createInput(largest_profile(skn), adsk.fusion.FeatureOperations.CutFeatureOperation)
        n_inp.setDistanceExtent(False, adsk.core.ValueInput.createByString('-nut_h'))
        extrudes.add(n_inp)

    # Flange screws
    sk6 = sketches.add(xy)
    sk6.name = '08_FlangeScrews'
    for i in range(4):
        ang = math.radians(45 + 90 * i)
        cx, cy = mm(33) * math.cos(ang), mm(33) * math.sin(ang)
        sc = sk6.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx, cy, 0), mm(2.25)
        )
        dim_diameter(sk6, sc, 'screw_d')
        rad = sk6.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0), sc.centerSketchPoint.geometry
        )
        rad.isConstruction = True
        dim_distance(sk6, rad.startSketchPoint, sc.centerSketchPoint, 'screw_r')

    col = adsk.core.ObjectCollection.create()
    for i in range(sk6.profiles.count):
        col.add(sk6.profiles.item(i))
    s_inp = extrudes.createInput(col, adsk.fusion.FeatureOperations.CutFeatureOperation)
    s_inp.setDistanceExtent(
        False,
        adsk.core.ValueInput.createByString('flange_thickness + plug_h + 1 mm'),
    )
    extrudes.add(s_inp)

    # Floor screws into the flat Ø30 mm top (cut from flat_plane downward into plug)
    sk7 = sketches.add(flat_plane)
    sk7.name = '09_FloorScrews'
    for i in range(3):
        ang = math.radians(90 + 120 * i)
        cx, cy = mm(9) * math.cos(ang), mm(9) * math.sin(ang)
        fc = sk7.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx, cy, 0), mm(2.0)
        )
        dim_diameter(sk7, fc, 'floor_screw_d')
        rad = sk7.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0), fc.centerSketchPoint.geometry
        )
        rad.isConstruction = True
        dim_distance(sk7, rad.startSketchPoint, fc.centerSketchPoint, 'floor_screw_r')

    col2 = adsk.core.ObjectCollection.create()
    for i in range(sk7.profiles.count):
        col2.add(sk7.profiles.item(i))
    f_inp = extrudes.createInput(col2, adsk.fusion.FeatureOperations.CutFeatureOperation)
    # Negative = into the plug from the flat top
    f_inp.setDistanceExtent(False, adsk.core.ValueInput.createByString('-10 mm'))
    extrudes.add(f_inp)

    return comp


def build_hook(design, root):
    comp = new_component(root, 'PoleHook', 120)
    sketches = comp.sketches
    xy = comp.xYConstructionPlane
    extrudes = comp.features.extrudeFeatures

    # Sleeve OD
    sk = sketches.add(xy)
    sk.name = '01_SleeveOD'
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(20.35))
    dim_diameter(sk, c, 'sleeve_od')
    extrude_one(comp, largest_profile(sk), 'sleeve_length',
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    comp.bRepBodies.item(0).name = 'PoleHook'

    # Bore
    sk2 = sketches.add(xy)
    sk2.name = '02_SleeveID'
    c2 = sk2.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(14.35))
    dim_diameter(sk2, c2, 'sleeve_id')
    extrude_one(comp, largest_profile(sk2), 'sleeve_length + 1 mm',
                adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Hook: outer crook disk (join) + inner cut + mouth cut + tip/cap/neck joins
    sk3 = sketches.add(comp.xZConstructionPlane)
    sk3.name = '03_Hook'
    circles = sk3.sketchCurves.sketchCircles
    lines = sk3.sketchCurves.sketchLines

    seat_x, seat_z = mm(25.85), mm(65.0)
    throat, arm = mm(11.0), mm(7.0)
    outer = throat + 2 * arm

    outer_c = circles.addByCenterRadius(adsk.core.Point3D.create(seat_x, seat_z, 0), outer / 2)
    inner_c = circles.addByCenterRadius(adsk.core.Point3D.create(seat_x, seat_z, 0), throat / 2)
    dim_diameter(sk3, outer_c, 'hook_throat + 2*hook_arm_t')
    dim_diameter(sk3, inner_c, 'hook_throat')

    # Position dims
    clx = lines.addByTwoPoints(adsk.core.Point3D.create(0, seat_z, 0), outer_c.centerSketchPoint.geometry)
    clx.isConstruction = True
    dim_distance(sk3, clx.startSketchPoint, outer_c.centerSketchPoint, 'sleeve_od/2 + hook_throat/2')
    clz = lines.addByTwoPoints(adsk.core.Point3D.create(seat_x, 0, 0), outer_c.centerSketchPoint.geometry)
    clz.isConstruction = True
    dim_distance(sk3, clz.startSketchPoint, outer_c.centerSketchPoint, 'sleeve_length + hook_crook_rise')

    # Mouth block (cut)
    lines.addCenterPointRectangle(
        adsk.core.Point3D.create(seat_x + throat * 0.75, seat_z, 0),
        adsk.core.Point3D.create(seat_x + throat * 0.75 + arm + mm(6), seat_z + throat / 2, 0),
    )
    # Neck
    lines.addCenterPointRectangle(
        adsk.core.Point3D.create(mm(24.0), mm(58.0), 0),
        adsk.core.Point3D.create(mm(30.0), mm(66.0), 0),
    )
    # Tip lip
    lines.addCenterPointRectangle(
        adsk.core.Point3D.create(seat_x + throat / 2 + arm / 2, seat_z - throat / 2 - mm(5), 0),
        adsk.core.Point3D.create(seat_x + throat / 2 + arm, seat_z - throat / 2 - mm(11), 0),
    )
    # Top cap
    lines.addCenterPointRectangle(
        adsk.core.Point3D.create(seat_x, seat_z + throat / 2 + arm / 2, 0),
        adsk.core.Point3D.create(seat_x + outer / 2 - mm(1), seat_z + throat / 2 + arm, 0),
    )

    # Extrude the ring profile (largest profile that isn't the whole outer disk alone)
    # With concentric circles, profiles are: inner disk, ring. Largest after mouth/rects vary.
    # First extrude OUTER disk as join, then cut INNER + mouth.
    # Isolate: temporarily use only the two circles for first features by
    # extruding largest (outer disk area includes ring+hole as separate profiles).

    # Join: pick profile with area closest to ring
    ring_target = math.pi * ((outer / 2) ** 2 - (throat / 2) ** 2)
    ring_prof, best_err = None, 1e100
    for i in range(sk3.profiles.count):
        p = sk3.profiles.item(i)
        err = abs(abs(p.areaProperties().area) - ring_target)
        if err < best_err:
            best_err, ring_prof = err, p

    if ring_prof is None:
        ring_prof = largest_profile(sk3)

    extrude_symmetric(comp, ring_prof, 'hook_width/2',
                      adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # Cut inner hole
    inner_target = math.pi * (throat / 2) ** 2
    inner_prof, best_err = None, 1e100
    for i in range(sk3.profiles.count):
        p = sk3.profiles.item(i)
        err = abs(abs(p.areaProperties().area) - inner_target)
        if err < best_err:
            best_err, inner_prof = err, p
    if inner_prof is not None and best_err < mm(15) ** 2:
        extrude_symmetric(comp, inner_prof, 'hook_width/2 + 0.2 mm',
                          adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Cut mouth: small profile to the +X of seat
    mouth_prof = None
    for i in range(sk3.profiles.count):
        p = sk3.profiles.item(i)
        bb = p.boundingBox
        cx = 0.5 * (bb.minPoint.x + bb.maxPoint.x)
        if cx > seat_x + throat / 4:
            area = abs(p.areaProperties().area)
            if mm(5) ** 2 < area < mm(25) ** 2:
                mouth_prof = p
                break
    if mouth_prof:
        extrude_symmetric(comp, mouth_prof, 'hook_width/2 + 0.5 mm',
                          adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Join neck / tip / cap rectangles (remaining medium profiles near those regions)
    for target_x, target_z in (
        (mm(26), mm(60)),
        (seat_x + throat / 2 + arm / 2, seat_z - throat / 2 - mm(7)),
        (seat_x, seat_z + throat / 2 + arm / 2),
    ):
        cand = None
        best = 1e100
        for i in range(sk3.profiles.count):
            p = sk3.profiles.item(i)
            bb = p.boundingBox
            cx = 0.5 * (bb.minPoint.x + bb.maxPoint.x)
            cz = 0.5 * (bb.minPoint.y + bb.maxPoint.y)
            d = (cx - target_x) ** 2 + (cz - target_z) ** 2
            if d < best:
                best, cand = d, p
        if cand and best < mm(20) ** 2:
            try:
                extrude_symmetric(comp, cand, 'hook_width/2',
                                  adsk.fusion.FeatureOperations.JoinFeatureOperation)
            except Exception:
                pass

    # Spine rib
    sk4 = sketches.add(comp.xZConstructionPlane)
    sk4.name = '04_Spine'
    sk4.sketchCurves.sketchLines.addCenterPointRectangle(
        adsk.core.Point3D.create(mm(24.1), mm(41), 0),
        adsk.core.Point3D.create(mm(28.1), mm(55), 0),
    )
    extrude_symmetric(comp, largest_profile(sk4), '5 mm',
                      adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # Re-bore
    sk5 = sketches.add(xy)
    sk5.name = '05_Rebore'
    c5 = sk5.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), mm(14.35))
    dim_diameter(sk5, c5, 'sleeve_id')
    extrude_one(comp, largest_profile(sk5), 'sleeve_length + 1 mm',
                adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Cross screws
    for idx, (z_mm, z_expr) in enumerate(((14.0, 'hook_screw_z1'), (36.0, 'hook_screw_z2')), start=1):
        sks = sketches.add(comp.yZConstructionPlane)
        sks.name = f'06_Screw{idx}'
        sc = sks.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, mm(z_mm), 0), mm(2.25)
        )
        dim_diameter(sks, sc, 'hook_screw_d')
        cl = sks.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0), sc.centerSketchPoint.geometry
        )
        cl.isConstruction = True
        dim_distance(sks, cl.startSketchPoint, sc.centerSketchPoint, z_expr)
        s_inp = extrudes.createInput(largest_profile(sks), adsk.fusion.FeatureOperations.CutFeatureOperation)
        half = adsk.core.ValueInput.createByString('sleeve_od/2 + 1 mm')
        s_inp.setTwoSidesDistanceExtent(half, half)
        extrudes.add(s_inp)

    return comp


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        root.name = 'AtticStaircase'

        create_parameters(design)
        build_catch(design, root)
        build_hook(design, root)

        ui.messageBox(
            'Built native parametric components:\n'
            '  • CatchingPiece\n'
            '  • PoleHook\n\n'
            'Edit: Modify → Change Parameters\n'
            '(hole_d, pole_d, flange_od, sleeve_wall, …)\n\n'
            'Or double-click any sketch/feature in the Timeline.\n\n'
            'Print: right-click body → Save as Mesh (3MF/STL).',
            'Attic staircase — editable Fusion model'
        )
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
