#!/usr/bin/env bash
# Install BramHome into the user FreeCAD Mod directory.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/Mod/BramHome"

if [[ "$(uname -s)" == "Darwin" ]]; then
  DEST="${HOME}/Library/Application Support/FreeCAD/Mod/BramHome"
else
  DEST="${HOME}/.local/share/FreeCAD/Mod/BramHome"
fi

mkdir -p "$(dirname "$DEST")"
if [[ -e "$DEST" || -L "$DEST" ]]; then
  echo "Removing existing install at: $DEST"
  rm -rf "$DEST"
fi

ln -s "$SRC" "$DEST"
echo "Installed BramHome → $DEST"
echo "Restart FreeCAD and select the BramHome workbench."
