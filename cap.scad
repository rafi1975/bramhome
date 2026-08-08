// Cap with counterbored bolt holes
// Bolt head recess: 5.5 mm diameter, 3 mm deep (per measured bolt)

// --- Cap dimensions (adjust to match your part) ---
cap_diameter = 40;
cap_height = 8;

// --- Bolt hole layout (adjust positions/count for your cap) ---
bolt_positions = [
    [12, 0],
    [-12, 0],
];

// --- Bolt / counterbore dimensions ---
counterbore_diameter = 5.5;   // bolt head OD
counterbore_depth = 3;        // bolt head height
through_hole_diameter = 3.2;  // M3 clearance (adjust if not M3)

// Small clearance so the head seats without binding
head_clearance = 0.05;

module counterbored_bolt_hole() {
    // Recess on top face for bolt head
    translate([0, 0, cap_height - counterbore_depth])
        cylinder(
            h = counterbore_depth + 0.01,
            d = counterbore_diameter + head_clearance,
            center = false,
            $fn = 48
        );

    // Through-hole for shank
    translate([0, 0, -0.01])
        cylinder(
            h = cap_height + 0.02,
            d = through_hole_diameter,
            center = false,
            $fn = 32
        );
}

module cap_body() {
    difference() {
        cylinder(h = cap_height, d = cap_diameter, $fn = 80);

        for (pos = bolt_positions) {
            translate([pos[0], pos[1], 0])
                counterbored_bolt_hole();
        }
    }
}

cap_body();
