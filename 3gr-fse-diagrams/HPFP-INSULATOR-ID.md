# Identified: High-Pressure Fuel Pump Insulator

**Vehicle:** Lexus GS 300 (GRS190)  
**Engine:** 3GR-FSE (D-4 direct injection)  
**Photo:** `hpfp-insulator-oriented.jpg` (crop: `hpfp-insulator-crop.jpg`)

## Verdict

The black oval / diamond flange sitting on the two studs is the **high-pressure fuel pump (HPFP) insulator** — OEM name **Insulator, Fuel Pump**.

It is the heat / vibration insulator that seals between the cam-driven HPFP and the **right-bank cylinder head cover** (valve cover). The pump has been removed; the insulator was left on the mounting studs.

## Why this matches the photo

| Clue in photo | Match |
|---|---|
| Black flat oval / diamond flange with large centre bore | HPFP insulator shape |
| Two threaded studs through opposite ears | HPFP mounts with **2 nuts on studs** |
| Looking into the bore: oily chamber + spring / cam hardware | Pump is **cam-driven** off the right-bank exhaust cam |
| Sitting on cast cover next to an ignition coil | Pump mounts **on the head cover**, beside the coils |
| Unplugged multi-wire connector nearby | HPFP electrical connector |

This is **not** a VVT oil-control-valve (OCV) gasket. On 3GR-FSE the OCVs seal with an **O-ring** (`90099-14137` → `90068-14030`) and one bolt each.

## OEM part numbers (GRS190 / 3GR-FSE)

| Part | OEM No. | Notes |
|---|---|---|
| **Fuel pump insulator (this gasket)** | **`23915-46011`** | Replace when pump or valve cover is off |
| High-pressure fuel pump assy | `23100-39615` → **`23100-39646`** | Engine-room / head-cover pump |
| Mounting stud (hex lobular / E-Torx) | `90126-08048` → **`90126-A0023`** | Typically 2 |
| Pump mounting nuts | see EPC (e.g. `90179-08153` / `90179-08175` family) | 2 nuts |
| Related O-ring (fuel system) | `90301-11029` | Confirm on EPC for your VIN |

Aftermarket cross (same insulator family): AJUSA **`00973900`** (“Gasket, fuel pump”) — listed as ~76 × 50 × 4 mm.

## Reassembly notes

1. Depressurise the high-pressure fuel system before disconnecting pipes.
2. Fit a **new** insulator `23915-46011` — do not reuse a crushed / oil-soaked one.
3. Seat the insulator on the two head-cover studs, then install the pump and nuts.
4. Reconnect the pump connector and fuel lines; check for fuel and oil leaks after first start.

## Related project files

- Valve-cleaning / leak work: see PR branch `cursor/3gr-fse-diagrams-756c` (`GS300-VALVE-CLEANING-CHECKLIST.md`).
- Replace this insulator whenever the right-bank valve cover or HPFP is disturbed.
