// Attic staircase catching piece
// Seats in the hatch recess: Ø50 mm opening, 31 mm deep, curving in to a
// flat Ø30 mm top (dome sides, flat floor).
// Units: millimetres
//
// Screw recesses face the ROOM (visible flange face), not the door side.
// Floor holes are true through-holes opening on the flat Ø30 mm top.
//
// Print on Bambu Lab P1S: flange flat on the bed, plug pointing up.
// Material: PETG / ASA / PA-CF (PLA only for fit test).

// --- Hatch cavity (measured) ---
hole_d            = 50.0;
hole_depth        = 31.0;
flat_top_d        = 30.0;

// --- Plug / flange ---
plug_clearance    = 0.5;
plug_od           = hole_d - 2 * plug_clearance;       // 49.0
flat_top_od       = flat_top_d - 2 * plug_clearance;   // 29.0
flange_od         = 80.0;
flange_thickness  = 5.0;
plug_h            = hole_depth - 0.5;
cyl_fraction      = 0.35;

// --- Catch pocket + M8 steel bar ---
pocket_w          = 34.0;
pocket_h          = 26.0;
pocket_len        = 38.0;
bar_z             = 10.0;
m8_clearance_d    = 8.4;
printed_bar_d     = 10.0;
use_printed_bar   = false;

// --- Flange wood screws (#8 / ~4.0 mm) ---
// Recess is on the ROOM face (z = 0), so heads sit flush when screwing
// up into the hatch from below — not on the door-covered face.
screw_d           = 4.5;
screw_head_d      = 9.0;
screw_head_h      = 3.0;
screw_circle_r    = 33.0;
screw_count       = 4;

// --- Floor screws through the flat Ø30 mm top into the hatch wood ---
// Driven from inside the pocket UP into the wood. Clean through-hole on
// the flat top; head counterbore on the pocket-facing underside of the roof.
floor_screw_d     = 4.2;
floor_screw_head_d = 8.0;
floor_screw_head_h = 2.5;
floor_screw_r     = 9.0;
floor_screw_count = 3;

$fn = 96;

module solid_body() {
    cyl_h = plug_h * cyl_fraction;
    tap_h = plug_h - cyl_h;

    // Flange — room / hook face at z = 0
    cylinder(h = flange_thickness, d = flange_od);

    translate([0, 0, flange_thickness - 0.01])
        cylinder(h = cyl_h + 0.01, d = plug_od);

    translate([0, 0, flange_thickness + cyl_h - 0.01])
        cylinder(h = tap_h + 0.01, d1 = plug_od, d2 = flat_top_od);
}

module printed_bar() {
    translate([-pocket_w / 2 - 2, 0, bar_z])
        rotate([0, 90, 0])
            cylinder(h = pocket_w + 4, d = printed_bar_d);
}

module catching_piece() {
    top_z  = flange_thickness + plug_h;   // flat top against hatch wood
    roof_z = pocket_h;                    // underside of roof (inside pocket)

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

            // Flange wood screws — recess on ROOM face (z = 0)
            for (i = [0 : screw_count - 1]) {
                ang = i * 360 / screw_count + 45;
                rotate([0, 0, ang])
                    translate([screw_circle_r, 0, 0]) {
                        // Through hole
                        translate([0, 0, -0.01])
                            cylinder(h = flange_thickness + 2, d = screw_d);
                        // Counterbore on room face (wider at z = 0)
                        translate([0, 0, -0.01])
                            cylinder(h = screw_head_h + 0.01, d = screw_head_d);
                    }
            }

            // Floor screws — open cleanly on the flat top (door/wood side)
            for (i = [0 : floor_screw_count - 1]) {
                ang = i * 360 / floor_screw_count + 90;
                rotate([0, 0, ang])
                    translate([floor_screw_r, 0, 0]) {
                        // Full through-hole from below roof through past the top
                        translate([0, 0, roof_z - 0.5])
                            cylinder(h = top_z - roof_z + 1.5, d = floor_screw_d);
                        // Head seat on the pocket side of the roof (not on flat top)
                        translate([0, 0, roof_z - 0.01])
                            cylinder(h = floor_screw_head_h + 0.01, d = floor_screw_head_d);
                        // Guarantee a clean opening on the flat top face
                        translate([0, 0, top_z - 0.6])
                            cylinder(h = 1.2, d = floor_screw_d + 0.2);
                    }
            }
        }

        if (use_printed_bar)
            printed_bar();
    }
}

catching_piece();
