// Patio mounting enclosure for stepped LED spotlight
// Units: millimetres — MEASURED dimensions
//
// Sleeve is 30 mm (sandstone depth only).
// Slice: flange on the build plate + supports for the bezel recess.

// --- Light (measured) ---
light_bezel_od = 79.0;
light_bezel_thickness = 2.5;
light_upper_od = 72.3; // widest body — sets bore

// --- Patio hole / cover ---
pavement_hole_id = 82.0;
cover_lip = 13.0;
cover_flange_od = pavement_hole_id + 2 * cover_lip; // 108
sleeve_od = 81.0;
sleeve_length = 30.0; // sandstone slab depth

// --- Fit ---
radial_clearance = 0.8;
bezel_seat_clearance = 0.5;
seat_depth_extra = 0.3;
cover_flange_thickness = 3.0;
edge_chamfer = 2.0;

$fn = 160;

seat_id = light_bezel_od + 2 * bezel_seat_clearance;
cavity_id = light_upper_od + 2 * radial_clearance;
seat_depth = light_bezel_thickness + seat_depth_extra;
total_h = cover_flange_thickness + sleeve_length;

z_ledge = total_h - seat_depth;
z_flange_under = sleeve_length;

module enclosure() {
    difference() {
        union() {
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

        translate([0, 0, z_ledge])
            cylinder(h = seat_depth + 0.1, d = seat_id);

        translate([0, 0, -0.1])
            cylinder(h = z_ledge + 0.2, d = cavity_id);
    }
}

enclosure();
