#!/usr/bin/env bash
set -euo pipefail
DEST="${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}"
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DEST"
rsync -a --delete "$SRC/" "$DEST/html-tracking-spec/"
echo "Installed: $DEST/html-tracking-spec"
