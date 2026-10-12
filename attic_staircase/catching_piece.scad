// Attic staircase catching piece
// Seats in the Ø50 × 31 mm domed recess in the hatch underside.
// Units: millimetres
//
// Strength strategy:
//   - Wide flange covers torn laminate and lands screws in solid wood
//   - Domed plug fills the cavity so the part cannot tip under pull
//   - Catch bar is an M8 bolt (steel) — printed body holds the bolt and
//     transfers load into wood screws. Set use_printed_bar=true only for a
//     no-hardware trial fit.
//
// Install: flange toward the room, plug into the hatch. Align the pocket
// so the M8 bar is easy to hook from below.
//
// Hardware: M8×50–60 bolt + nylock nut (and washers if you like).
// Wood screws: 4× ~4 mm / #8 into the flange, optional 3 into the dome floor.
//
// Print on Bambu Lab P1S: flange flat on the bed, plug pointing up.
// Material: PETG / ASA / PA-CF. ≥5 walls, 40–60% gyroid. No supports.

// --- Hatch cavity (measured) ---
hole_d            = 50.0;
hole_depth        = 31.0;

// --- Plug / flange ---
plug_clearance    = 0.5;     // radial clearance in the 50 mm hole
plug_od           = hole_d - 2 * plug_clearance;  // 49.0
flange_od         = 80.0;    // covers damage; screw landings outside hole
flange_thickness  = 5.0;
dome_bulge         = 8.0;     // spherical tip that seats in the dome floor
plug_cyl_h        = hole_depth - dome_bulge - 0.5; // tiny gap at the top

// --- Catch pocket + M8 steel bar ---
// Sized for pole_hook.scad head (outer crook ≈ 25 mm, width 16 mm)
pocket_w          = 34.0;    // X — hook enters here
pocket_h          = 26.0;    // Z depth from flange face into the plug
pocket_len        = 38.0;    // Y
bar_z             = 10.0;    // M8 centre from flange face (matches hook crook_rise)
m8_clearance_d    = 8.4;
printed_bar_d     = 10.0;
use_printed_bar   = false;   // false = rely on M8 bolt (recommended)

// --- Flange wood screws (#8 / ~4.0 mm) ---
screw_d           = 4.5;
screw_head_d      = 9.0;
screw_head_h      = 3.0;
screw_circle_r    = 33.0;    // outside the 50 mm hole
screw_count       = 4;

// --- Optional dome-floor screws (into old pilot holes) ---
floor_screw_d     = 4.0;
floor_screw_r     = 12.0;
floor_screw_count = 3;

$fn = 96;

module solid_body() {
    plug_r = plug_od / 2;
    // Flange (room / hook side)
    cylinder(h = flange_thickness, d = flange_od);
    // Plug cylinder into the hatch
    translate([0, 0, flange_thickness - 0.01])
        cylinder(h = plug_cyl_h + 0.01, d = plug_od);
    // Domed tip — sphere clipped to a bulge so it seats in the dome
    translate([0, 0, flange_thickness + plug_cyl_h])
        intersection() {
            translate([0, 0, -plug_r + dome_bulge])
                sphere(r = plug_r);
            translate([-plug_r - 1, -plug_r - 1, -0.01])
                cube([2 * plug_r + 2, 2 * plug_r + 2, dome_bulge + 0.2]);
        }
}

module printed_bar() {
    // Spans the pocket; added AFTER the pocket cut so it is not removed
    translate([-pocket_w / 2 - 2, 0, bar_z])
        rotate([0, 90, 0])
            cylinder(h = pocket_w + 4, d = printed_bar_d);
}

module catching_piece() {
    union() {
        difference() {
            solid_body();

            // Entry pocket for the hook (open on room-facing flange)
            translate([-pocket_w / 2, -pocket_len / 2, -0.02])
                cube([pocket_w, pocket_len, pocket_h + 0.02]);

            // M8 bolt bore + nut seats (skip when using a solid printed bar)
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

            // Flange wood-screw holes (outside the hatch opening)
            for (i = [0 : screw_count - 1]) {
                ang = i * 360 / screw_count + 45;
                rotate([0, 0, ang])
                    translate([screw_circle_r, 0, 0]) {
                        translate([0, 0, -0.01])
                            cylinder(
                                h = flange_thickness + plug_cyl_h + dome_bulge + 1,
                                d = screw_d
                            );
                        translate([0, 0, flange_thickness - screw_head_h])
                            cylinder(
                                h = screw_head_h + 0.05,
                                d1 = screw_d,
                                d2 = screw_head_d
                            );
                    }
            }

            // Dome-floor screws into the hatch core
            for (i = [0 : floor_screw_count - 1]) {
                ang = i * 360 / floor_screw_count + 90;
                rotate([0, 0, ang])
                    translate([floor_screw_r, 0, flange_thickness + plug_cyl_h - 1])
                        cylinder(h = dome_bulge + 3, d = floor_screw_d);
            }
        }

        if (use_printed_bar)
            printed_bar();
    }
}

catching_piece();
