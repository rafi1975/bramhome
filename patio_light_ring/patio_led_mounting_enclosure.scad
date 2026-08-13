// Patio mounting enclosure for stepped LED spotlight
// Units: millimetres
//
// PHOTO-ESTIMATED light dimensions — measure with calipers and update
// before the final print.
//
// Print on Bambu Lab P1S: flange down on the bed. No supports.
// Prefer PETG / ASA outdoors.

// --- Light (measure these) ---
light_flange_od = 72.0;
light_flange_thickness = 2.5;
light_upper_od = 58.0;
light_upper_length = 18.0;
light_lower_od = 48.0;
light_lower_length = 72.0;
light_cable_notch_w = 14.0;
light_cable_notch_h = 16.0;

// --- Fit / cover ---
radial_clearance = 0.8;
flange_seat_clearance = 0.5;
seat_depth_extra = 0.3;
cover_flange_od = 110.0;
cover_flange_thickness = 3.0;
wall_thickness = 3.0;
bottom_extra = 8.0;
cable_slot_extra_w = 4.0;
cable_slot_extra_h = 10.0;

$fn = 128;

seat_id = light_flange_od + 2 * flange_seat_clearance;
upper_id = light_upper_od + 2 * radial_clearance;
lower_id = light_lower_od + 2 * radial_clearance;
seat_depth = light_flange_thickness + seat_depth_extra;
sleeve_od = max(seat_id, upper_id) + 2 * wall_thickness;
total_h = seat_depth + light_upper_length + light_lower_length + bottom_extra;

z_ledge = total_h - seat_depth;
z_step = z_ledge - light_upper_length;
z_flange_under = total_h - cover_flange_thickness;

module enclosure() {
    difference() {
        union() {
            translate([0, 0, z_flange_under])
                cylinder(h = cover_flange_thickness, d = cover_flange_od);
            cylinder(h = z_flange_under + 0.01, d = sleeve_od);
        }

        // Bezel seat
        translate([0, 0, z_ledge])
            cylinder(h = seat_depth + 0.1, d = seat_id);

        // Upper body cavity
        translate([0, 0, z_step - 0.05])
            cylinder(h = light_upper_length + 0.1, d = upper_id);

        // Lower body cavity (open bottom)
        translate([0, 0, -0.1])
            cylinder(h = z_step + 0.2, d = lower_id);

        // Cable slot
        slot_w = light_cable_notch_w + cable_slot_extra_w;
        slot_h = light_cable_notch_h + cable_slot_extra_h;
        translate([sleeve_od / 2, 0, slot_h / 2 - 0.1])
            cube([sleeve_od, slot_w, slot_h + 0.2], center = true);
    }
}

enclosure();
