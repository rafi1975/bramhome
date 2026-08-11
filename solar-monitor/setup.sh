#!/usr/bin/env bash
# Quick helper for Raspberry Pi installs.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
if [[ ! -f config.yaml ]]; then
  cp config.example.yaml config.yaml
  echo "Created config.yaml — edit serial.port and optional MQTT/PVOutput settings."
fi
mkdir -p data
# Default local DB path if user prefers not to use /var/lib
python - <<'PY'
from pathlib import Path
import yaml
p = Path("config.yaml")
cfg = yaml.safe_load(p.read_text())
cfg.setdefault("storage", {})["sqlite_path"] = str(Path("data/readings.db").resolve())
p.write_text(yaml.safe_dump(cfg, sort_keys=False))
print("storage.sqlite_path ->", cfg["storage"]["sqlite_path"])
PY
echo "Done. Test with:  source .venv/bin/activate && python monitor.py --once -v"
