// Attic staircase pole hook — reinforced replacement for the broken tip
// Slides onto the existing Ø28 mm wooden pole.
// Units: millimetres
//
// Strength strategy:
//   - ~6 mm sleeve walls + solid spine into the hook crook
//   - Hook throat sized for the M8 steel catch bar (+ clearance)
//   - Two cross-screws so the sleeve cannot spin or pull off
//   - Flat Y-faces so you can print on the SIDE: layer lines run WITH
//     the pull force (the old vertical print delaminated at the neck)
//
// Engagement: raise the pole past the catch bar, shift sideways so the
// bar enters the side-opening J, then pull down — bar seats in the crook.
// Hook head is sized to fit the catching_piece pocket (34 × 38 × 26 mm).
//
// Print on Bambu Lab P1S:
//   Lay the part on its flat Y face (pole axis horizontal on the bed,
//   hook opening facing up). Enable supports for the hook arch.
// Material: PETG / ASA / PA-CF / PETG-CF. ≥6 walls, 50–80% gyroid.

// --- Pole interface ---
pole_d            = 28.0;
sleeve_clearance  = 0.35;    // snug slip-fit; sand lightly if tight
sleeve_id         = pole_d + 2 * sleeve_clearance;  // 28.7
wall              = 6.0;
sleeve_od         = sleeve_id + 2 * wall;           // 40.7
sleeve_length     = 55.0;

// Cross screws into the pole (wood screws ~4 mm / #8)
screw_d           = 4.5;
screw_z1          = 14.0;    // from open end
screw_z2          = 36.0;
countersink_d     = 9.0;
countersink_h     = 2.5;

// --- Hook (grabs M8 catch bar) — kept compact for the catch pocket ---
bar_d             = 8.0;
throat            = 11.0;    // opening the bar must pass through
hook_width        = 16.0;    // Y thickness (pocket is 38 mm)
arm_t             = 7.0;     // hook wall thickness (outer crook ≈ 25 mm)
crook_rise        = 10.0;    // bar seat above sleeve end (matches catch bar_z)
tip_back          = 11.0;    // tip curls back toward handle past the seat
spine_drop        = 28.0;    // reinforcement rib down the sleeve
spine_w           = 10.0;    // Y width of lower spine

$fn = 80;

module pole_bore() {
    translate([0, 0, -1])
        cylinder(h = sleeve_length + 2, d = sleeve_id);
}

module sleeve_body() {
    difference() {
        cylinder(h = sleeve_length, d = sleeve_od);
        pole_bore();
    }
}

module screw_holes() {
    for (z = [screw_z1, screw_z2]) {
        translate([0, 0, z])
            rotate([0, 90, 0]) {
                cylinder(h = sleeve_od + 2, d = screw_d, center = true);
                translate([0, 0, sleeve_od / 2 - countersink_h])
                    cylinder(h = countersink_h + 0.05, d1 = screw_d, d2 = countersink_d);
            }
    }
}

// Cylinder extruded along Y (hook thickness axis)
module cyl_y(d, x, z) {
    translate([x, 0, z])
        rotate([90, 0, 0])
            cylinder(h = hook_width, d = d, center = true);
}

// Side-opening J at the closed end of the sleeve.
//
//              tip curls back (−Z)
//           +--------+
//           |        |
//           |  seat  |  ← throat opens to +X
//           |        |
//      =====+--------+====  z = sleeve_length
//      ||              ||
//
module hook_body() {
    r_out  = sleeve_od / 2;
    seat_x = r_out + throat / 2;          // ~25.9
    seat_z = sleeve_length + crook_rise;  // bar centre when engaged
    outer  = throat + 2 * arm_t;          // ~25

    difference() {
        union() {
            // Main crook body
            cyl_y(outer, seat_x, seat_z);

            // Neck: blend crook into sleeve end (primary tension path)
            hull() {
                translate([r_out - 1, -hook_width / 2, sleeve_length - 10])
                    cube([arm_t + 2, hook_width, 10]);
                cyl_y(arm_t + 2, r_out + arm_t / 2, seat_z - 1);
            }

            // Closed top cap of the J
            hull() {
                cyl_y(arm_t, seat_x - throat / 2 - arm_t / 2 + 0.5,
                      seat_z + throat / 2 + arm_t / 2 - 0.5);
                cyl_y(arm_t, seat_x + throat / 2 + arm_t / 2 - 0.5,
                      seat_z + throat / 2 + arm_t / 2 - 0.5);
            }

            // Tip lip (curls past seat toward the handle)
            hull() {
                cyl_y(arm_t, seat_x + throat / 2 + arm_t / 2 - 0.5, seat_z);
                cyl_y(arm_t, seat_x + throat / 2 + arm_t / 2 - 0.5,
                      seat_z - throat / 2 - tip_back + arm_t / 2);
            }

            // Spine rib down +X face of the sleeve
            hull() {
                translate([r_out - 0.5, -spine_w / 2, sleeve_length - spine_drop])
                    cube([wall + 1.5, spine_w, 2]);
                translate([r_out - 0.5, -hook_width / 2, sleeve_length - 3])
                    cube([wall + 1.5, hook_width, 3]);
            }
        }

        // Inner seat
        cyl_y(throat, seat_x, seat_z);

        // Open mouth to +X (sideways bar entry)
        translate([seat_x - 1, -hook_width / 2 - 0.5, seat_z - throat / 2])
            cube([throat / 2 + arm_t + 8, hook_width + 1, throat]);

        // Soft lead-in: trim only the tip's inner corner (keeps tip attached)
        translate([seat_x + throat / 2 + 0.5, -hook_width / 2 - 0.5,
                   seat_z - throat / 2 - tip_back])
            rotate([0, -35, 0])
                cube([6, hook_width + 1, 8]);
    }
}

module reinforced_hook() {
    difference() {
        union() {
            sleeve_body();
            hook_body();
        }
        pole_bore();
        screw_holes();
    }
}

reinforced_hook();
