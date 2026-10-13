// Attic staircase catching piece
// Seats in the hatch recess: Ø50 mm opening, 31 mm deep, curving in to a
// flat Ø30 mm top (dome sides, flat floor).
// Units: millimetres
//
// Strength strategy:
//   - Wide flange covers torn laminate; screws land in solid wood
//   - Tapered plug fills the cavity and seats on the flat Ø30 mm top
//   - Catch bar is an M8 bolt (steel). Set use_printed_bar=true only for a
//     no-hardware trial fit.
//
// Print on Bambu Lab P1S: flange flat on the bed, plug pointing up.
// Material: PETG / ASA / PA-CF. ≥5 walls, 40–60% gyroid. No supports.

// --- Hatch cavity (measured) ---
hole_d            = 50.0;    // opening diameter
hole_depth        = 31.0;    // opening depth
flat_top_d        = 30.0;    // flat floor at the top of the dome

// --- Plug / flange ---
plug_clearance    = 0.5;     // radial clearance vs cavity
plug_od           = hole_d - 2 * plug_clearance;       // 49.0 at mouth
flat_top_od       = flat_top_d - 2 * plug_clearance;   // 29.0 at floor
flange_od         = 80.0;
flange_thickness  = 5.0;
plug_h            = hole_depth - 0.5;  // leave a tiny gap at the floor
// How much of the plug stays near full Ø before the taper (rest is frustum)
cyl_fraction      = 0.35;    // 35% cylinder, then taper to flat top

// --- Catch pocket + M8 steel bar ---
pocket_w          = 34.0;
pocket_h          = 26.0;
pocket_len        = 38.0;
bar_z             = 10.0;
m8_clearance_d    = 8.4;
printed_bar_d     = 10.0;
use_printed_bar   = false;

// --- Flange wood screws (#8 / ~4.0 mm) ---
screw_d           = 4.5;
screw_head_d      = 9.0;
screw_head_h      = 3.0;
screw_circle_r    = 33.0;
screw_count       = 4;

// --- Floor screws into the flat Ø30 mm top ---
floor_screw_d     = 4.0;
floor_screw_r     = 9.0;     // stays inside the flat top
floor_screw_count = 3;

$fn = 96;

module solid_body() {
    cyl_h = plug_h * cyl_fraction;
    tap_h = plug_h - cyl_h;

    // Flange (room / hook side)
    cylinder(h = flange_thickness, d = flange_od);

    // Near-mouth cylinder
    translate([0, 0, flange_thickness - 0.01])
        cylinder(h = cyl_h + 0.01, d = plug_od);

    // Tapered “dome” frustum → flat top Ø ~29 mm
    translate([0, 0, flange_thickness + cyl_h - 0.01])
        cylinder(h = tap_h + 0.01, d1 = plug_od, d2 = flat_top_od);
}

module printed_bar() {
    translate([-pocket_w / 2 - 2, 0, bar_z])
        rotate([0, 90, 0])
            cylinder(h = pocket_w + 4, d = printed_bar_d);
}

module catching_piece() {
    union() {
        difference() {
            solid_body();

            // Hook entry pocket
            translate([-pocket_w / 2, -pocket_len / 2, -0.02])
                cube([pocket_w, pocket_len, pocket_h + 0.02]);

            if (!use_printed_bar) {
                translate([0, 0, bar_z])
                    rotate([0, 90, 0])
                        cylinder(h = flange_od + 4, d = m8_clearance_d, center = true);

                for (sx = [-1, 1]) {
                    translate([sx * (pocket_w / 2 + 4.0), 0, bar_z])
                        rotate([0, 90, 0])
                            cylinder(h = 8.5, d = 15.2, center = true, $fn = 6);
                }
            }

            // Flange wood screws
            for (i = [0 : screw_count - 1]) {
                ang = i * 360 / screw_count + 45;
                rotate([0, 0, ang])
                    translate([screw_circle_r, 0, 0]) {
                        translate([0, 0, -0.01])
                            cylinder(h = flange_thickness + plug_h + 1, d = screw_d);
                        translate([0, 0, flange_thickness - screw_head_h])
                            cylinder(
                                h = screw_head_h + 0.05,
                                d1 = screw_d,
                                d2 = screw_head_d
                            );
                    }
            }

            // Screws into the flat Ø30 mm floor
            for (i = [0 : floor_screw_count - 1]) {
                ang = i * 360 / floor_screw_count + 90;
                rotate([0, 0, ang])
                    translate([floor_screw_r, 0, flange_thickness + plug_h - 8])
                        cylinder(h = 10, d = floor_screw_d);
            }
        }

        if (use_printed_bar)
            printed_bar();
    }
}

catching_piece();
