// Attic staircase catching piece — SOLID walls (no side openings)
// Units: millimetres
//
// What went wrong before: the hook pocket was wider than the plug could
// support, and M8 nut recesses were cut from the OUTSIDE, carving the
// Ø44 shell into thin struts that snapped.
//
// This revision:
//   - Continuous solid outer wall (Ø44 → flat Ø29 top)
//   - Smaller pocket open ONLY on the room face
//   - Thick integral catch bar (no holes through the outer shell)
//   - Optional M8 mode that only recesses INTO the pocket walls from inside
//
// Print: flange on bed, plug up. PETG/ASA for real use; PLA for fit only.

// --- Hatch / plug ---
hole_depth        = 31.0;
flat_top_d        = 30.0;
plug_od           = 44.0;    // sits in the door
plug_clearance    = 0.5;
flat_top_od       = flat_top_d - 2 * plug_clearance; // 29
flange_od         = 80.0;
flange_thickness  = 5.0;
plug_h            = hole_depth - 0.5;
cyl_fraction      = 0.40;

// --- Hook pocket (open on room face only) ---
// Sized so side walls stay ≥10 mm in the Ø44 plug.
pocket_w          = 20.0;    // X — hook enters here (was 34 — too wide)
pocket_len        = 24.0;    // Y — fits hook_width 16 + clearance
pocket_h          = 20.0;    // depth — thicker solid roof above
bar_z             = 10.0;    // catch-bar centre from room face

// --- Catch bar ---
// Default: thick printed bar fused into the side walls (no outer openings).
// Set use_m8_bar=true for a steel M8 with recesses cut from INSIDE only.
use_m8_bar        = false;
printed_bar_d     = 9.0;     // fits hook throat 11 mm; strength is in the thick walls
m8_clearance_d    = 8.4;
m8_embed          = 7.0;     // how far M8/nut sits into each pocket wall
m8_nut_d          = 15.0;    // hex-ish clearance, from inside only
m8_nut_h          = 5.0;

// --- Flange screws (ROOM-face counterbore) ---
screw_d           = 4.5;
screw_head_d      = 9.0;
screw_head_h      = 3.0;
screw_circle_r    = 33.0;
screw_count       = 4;

// --- Floor screws through flat top ---
floor_screw_d     = 4.2;
floor_screw_head_d = 8.0;
floor_screw_head_h = 2.5;
floor_screw_r     = 8.0;
floor_screw_count = 3;

$fn = 96;

module solid_body() {
    cyl_h = plug_h * cyl_fraction;
    tap_h = plug_h - cyl_h;

    cylinder(h = flange_thickness, d = flange_od);

    translate([0, 0, flange_thickness - 0.01])
        cylinder(h = cyl_h + 0.01, d = plug_od);

    translate([0, 0, flange_thickness + cyl_h - 0.01])
        cylinder(h = tap_h + 0.01, d1 = plug_od, d2 = flat_top_od);
}

module catching_piece() {
    top_z  = flange_thickness + plug_h;
    roof_z = pocket_h;

    difference() {
        union() {
            solid_body();

            // Integral catch bar — spans the pocket and keys into both walls
            if (!use_m8_bar) {
                translate([0, 0, bar_z])
                    rotate([0, 90, 0])
                        cylinder(h = pocket_w + 2 * 6, d = printed_bar_d, center = true);
            }
        }

        // Pocket — ONLY opens on the room face (z=0). Does not pierce sides.
        translate([-pocket_w / 2, -pocket_len / 2, -0.02])
            cube([pocket_w, pocket_len, pocket_h + 0.02]);

        if (use_m8_bar) {
            // M8 bore: only long enough to sit in the pocket walls, NOT
            // through the outer Ø44 shell.
            translate([0, 0, bar_z])
                rotate([0, 90, 0])
                    cylinder(
                        h = pocket_w + 2 * m8_embed,
                        d = m8_clearance_d,
                        center = true
                    );

            // Nut / head seats cut from the POCKET interior into the wall
            for (sx = [-1, 1]) {
                translate([
                    sx * (pocket_w / 2 + m8_nut_h / 2 - 0.01),
                    0,
                    bar_z
                ])
                    rotate([0, 90, 0])
                        cylinder(h = m8_nut_h, d = m8_nut_d, center = true, $fn = 6);
            }
        }

        // Flange screws — counterbore on ROOM face
        for (i = [0 : screw_count - 1]) {
            ang = i * 360 / screw_count + 45;
            rotate([0, 0, ang])
                translate([screw_circle_r, 0, 0]) {
                    translate([0, 0, -0.01])
                        cylinder(h = flange_thickness + 2, d = screw_d);
                    translate([0, 0, -0.01])
                        cylinder(h = screw_head_h + 0.01, d = screw_head_d);
                }
        }

        // Floor screws — through flat top; head seat on roof underside
        for (i = [0 : floor_screw_count - 1]) {
            ang = i * 360 / floor_screw_count + 90;
            rotate([0, 0, ang])
                translate([floor_screw_r, 0, 0]) {
                    translate([0, 0, roof_z - 0.5])
                        cylinder(h = top_z - roof_z + 1.5, d = floor_screw_d);
                    translate([0, 0, roof_z - 0.01])
                        cylinder(h = floor_screw_head_h + 0.01, d = floor_screw_head_d);
                    translate([0, 0, top_z - 0.6])
                        cylinder(h = 1.2, d = floor_screw_d + 0.2);
                }
        }
    }
}

catching_piece();
