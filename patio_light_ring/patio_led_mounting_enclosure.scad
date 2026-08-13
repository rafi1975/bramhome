// Patio mounting enclosure for stepped LED spotlight
// Units: millimetres — MEASURED dimensions
//
// Print on Bambu Lab P1S: flange already oriented on the bed in the STL.
// Prefer PETG / ASA outdoors. PLA is fine for a fit check.

// --- Light (measured) ---
light_bezel_od = 79.0;
light_bezel_thickness = 2.5;
light_upper_od = 72.3;
light_upper_length = 15.3;
light_lower_od = 59.3;       // cleared by straight bore (not a stepped cavity)
light_lower_length = 53.3;

// --- Patio hole / cover (measured intent) ---
pavement_hole_id = 82.0;
cover_lip = 13.0;
cover_flange_od = pavement_hole_id + 2 * cover_lip; // 108
sleeve_od = 81.0; // fits Ø82 hole

// --- Fit ---
radial_clearance = 0.8;
bezel_seat_clearance = 0.5;
seat_depth_extra = 0.3;
cover_flange_thickness = 3.0;
edge_chamfer = 2.0; // anti-trip bevel on outer top edge
bottom_extra = 5.0;

$fn = 160;

seat_id = light_bezel_od + 2 * bezel_seat_clearance;
cavity_id = light_upper_od + 2 * radial_clearance; // straight bore
seat_depth = light_bezel_thickness + seat_depth_extra;
total_h = seat_depth + light_upper_length + light_lower_length + bottom_extra;

z_ledge = total_h - seat_depth;
z_flange_under = total_h - cover_flange_thickness;

module enclosure() {
    difference() {
        union() {
            // Cover flange with outer-top chamfer
            rotate_extrude(convexity = 4)
                polygon([
                    [0, z_flange_under],
                    [cover_flange_od / 2, z_flange_under],
                    [cover_flange_od / 2, total_h - edge_chamfer],
                    [cover_flange_od / 2 - edge_chamfer, total_h],
                    [0, total_h],
                ]);
            cylinder(h = z_flange_under + 0.01, d = sleeve_od);
        }

        // Flush bezel recess
        translate([0, 0, z_ledge])
            cylinder(h = seat_depth + 0.1, d = seat_id);

        // Straight sleeve bore (no internal step — printable flange-down)
        translate([0, 0, -0.1])
            cylinder(h = z_ledge + 0.2, d = cavity_id);
    }
}

// Print orientation: flange on the bed (matches STL)
translate([0, 0, total_h]) rotate([180, 0, 0])
    enclosure();
