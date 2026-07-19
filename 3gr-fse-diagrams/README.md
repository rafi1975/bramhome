# 3GR-FSE Engine Diagrams (2006 GS300 GRS190 — Ireland RHD)

**Only these files are current.** Older incorrect diagrams were removed.

## Use these

| File | What it shows |
|------|----------------|
| `3gr-fse-intake-ports-correct.png` | Full intake valley — twin oval ports per cylinder |
| `3gr-fse-one-cylinder-ports.png` | Close-up: one cylinder = two ovals + bridge |
| `3gr-fse-exploded-ports-correct.png` | Exploded view with correct ports |
| `valve-closed-vs-open.png` | Camera looking **down** into ports — CLOSED vs OPEN |
| `crank-rotation-clockwise.png` | Turn crank **clockwise** only (from front of car) |

## RHD reminder (Ireland)

Standing at the front of the car looking into the bay:

- **Right side of bay** = driver side = **Bank 1** (cylinders 1, 3, 5)
- **Left side of bay** = passenger side = **Bank 2** (cylinders 2, 4, 6)

## After pulling

```bash
git fetch origin
git checkout cursor/3gr-fse-diagrams-756c
git pull
cd 3gr-fse-diagrams
ls
open .
```

If you still see old files, delete the local folder and re-checkout:

```bash
rm -rf 3gr-fse-diagrams
git checkout -- 3gr-fse-diagrams
```
