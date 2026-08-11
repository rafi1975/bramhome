// Patio floor-light support / trim ring
// Matches patio_light_support_ring.stl (photo-estimated dimensions)
// Units: millimetres
//
// Print on Bambu Lab P1S: flange down on the bed, no supports.
// Prefer PETG / ASA for outdoor UV and weather.

// --- Primary dimensions (adjust to your hole / light) ---
flange_od = 98.0;        // cover flange outer diameter
sleeve_od = 82.0;        // sleeve OD — must fit the drilled pavement hole
bore_id = 76.0;          // through-hole for the light body
flange_thickness = 2.5;  // flange height above pavement
sleeve_length = 28.0;    // sleeve depth below flange underside

// --- Details ---
bottom_chamfer = 1.2;    // eases insertion into the hole
fillet_radius = 1.0;     // strength blend under the flange
$fn = 192;

module ring() {
    r_bore = bore_id / 2;
    r_sleeve = sleeve_od / 2;
    r_flange = flange_od / 2;
    z_under = sleeve_length;
    z_top = sleeve_length + flange_thickness;
    R = min(fillet_radius, (flange_od - sleeve_od) / 2 - 0.3, flange_thickness);
    C = min(bottom_chamfer, (sleeve_od - bore_id) / 2 - 0.3, sleeve_length / 3);

    // Build as flange disk + sleeve tube, minus bore, plus optional fillet torus sector
    difference() {
        union() {
            // Flange
            translate([0, 0, z_under])
                cylinder(h = flange_thickness, d = flange_od, center = false);

            // Sleeve (slightly into flange to guarantee manifold union)
            translate([0, 0, -0.01])
                cylinder(h = sleeve_length + 0.01, d = sleeve_od, center = false);

            // Exterior fillet under flange (rotate_extrude of a quarter-circle)
            if (R > 0.05) {
                translate([0, 0, z_under])
                    rotate_extrude(convexity = 4)
                        translate([r_sleeve + R, 0, 0])
                            difference() {
                                translate([-R, -R]) square([R, R]);
                                circle(r = R);
                            }
            }
        }

        // Through bore
        translate([0, 0, -0.5])
            cylinder(h = z_top + 1.0, d = bore_id, center = false);

        // Bottom insertion chamfer (cone cut)
        if (C > 0.05) {
            translate([0, 0, -0.01])
                cylinder(h = C + 0.01, d1 = sleeve_od + 0.02, d2 = sleeve_od - 2 * C, center = false);
        }
    }
}

ring();
