// Attic staircase pole hook — clean reinforced J for the Ø28 mm pole
// Units: millimetres
//
// Single 2D profile (no hull scraps) extruded once, then unioned with the
// sleeve. Mouth opens to +X for sideways catch on the M8 bar.
//
// Print on Bambu Lab P1S: lay on a flat Y face (pole axis horizontal,
// hook opening facing up). Supports for the arch. PETG / ASA / PA-CF.
// ≥6 walls, 50–80% gyroid.

// --- Pole interface ---
pole_d            = 28.0;
sleeve_clearance  = 0.35;
sleeve_id         = pole_d + 2 * sleeve_clearance;  // 28.7
wall              = 6.0;
sleeve_od         = sleeve_id + 2 * wall;           // 40.7
sleeve_length     = 55.0;

// Cross screws
screw_d           = 4.5;
screw_z1          = 14.0;
screw_z2          = 36.0;
countersink_d     = 9.0;
countersink_h     = 2.5;

// --- Hook (fits catch pocket 34 × 38 × 26; grabs M8 bar) ---
throat            = 11.0;
hook_width        = 16.0;
arm_t             = 7.0;
crook_rise        = 10.0;    // seat above sleeve end (= catch bar_z)
tip_drop          = 10.0;    // tip length below seat centre
spine_drop        = 26.0;

$fn = 96;

module reinforced_hook() {
    r_out  = sleeve_od / 2;
    seat_x = r_out + throat / 2 + 0.2;
    outer_r = throat / 2 + arm_t;

    difference() {
        union() {
            cylinder(h = sleeve_length, d = sleeve_od);

            // Hook head — single 2D profile in XZ, extruded in Y
            translate([0, hook_width / 2, 0])
                rotate([90, 0, 0])
                    linear_extrude(height = hook_width, convexity = 6)
                        clean_hook_2d(r_out, seat_x, outer_r);
        }

        // Pole bore
        translate([0, 0, -0.5])
            cylinder(h = sleeve_length + 1, d = sleeve_id);

        // Cross screws
        for (z = [screw_z1, screw_z2]) {
            translate([0, 0, z])
                rotate([0, 90, 0]) {
                    cylinder(h = sleeve_od + 2, d = screw_d, center = true);
                    translate([0, 0, sleeve_od / 2 - countersink_h])
                        cylinder(
                            h = countersink_h + 0.05,
                            d1 = screw_d,
                            d2 = countersink_d
                        );
                }
        }
    }
}

// 2D profile: x = radial (+X), y = along pole (world Z)
// Origin at world origin; sleeve end at y = sleeve_length.
module clean_hook_2d(r_out, seat_x, outer_r) {
    seat_y = sleeve_length + crook_rise;
    tip_y  = seat_y - tip_drop;
    r_in   = throat / 2;

    difference() {
        union() {
            // Outer crook
            translate([seat_x, seat_y])
                circle(r = outer_r);

            // Back wall / neck: from sleeve OD up into the crook
            translate([r_out - 0.2, sleeve_length - 8])
                square([seat_x - r_out + arm_t * 0.5, crook_rise + outer_r + 8]);

            // Tip (outer lip curling back toward the handle)
            translate([seat_x + r_in, tip_y])
                square([arm_t, seat_y - tip_y + r_in]);

            // Crown above the seat
            translate([seat_x - r_in - arm_t, seat_y + r_in])
                square([throat + 2 * arm_t, arm_t]);

            // Spine on +X face of the sleeve
            translate([r_out - 0.2, sleeve_length - spine_drop])
                square([wall * 0.75, spine_drop + 0.2]);
        }

        // Throat
        translate([seat_x, seat_y])
            circle(d = throat);

        // Mouth open to +X
        translate([seat_x, seat_y - r_in])
            square([outer_r + 8, throat]);

        // Never invade the sleeve interior (x < r_out)
        translate([-sleeve_od, -2])
            square([sleeve_od + r_out - 0.05, sleeve_length + crook_rise + outer_r + 20]);
    }
}

reinforced_hook();
