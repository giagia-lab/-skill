#!/usr/bin/env bash
set -euo pipefail

SKILL="html-tracking-spec"
DEST="${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}"
SRC="$(cd "$(dirname "$0")" && pwd)"

# 1. 安装 skill 文件到 Cursor skills 目录
mkdir -p "$DEST"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude '.git' "$SRC/" "$DEST/$SKILL/"
else
  rm -rf "$DEST/$SKILL"
  mkdir -p "$DEST/$SKILL"
  cp -R "$SRC/." "$DEST/$SKILL/"
  rm -rf "$DEST/$SKILL/.git"
fi
echo "✅ Skill installed: $DEST/$SKILL"

# 2. 安装 Python 依赖 (openpyxl)
if python3 -c "import openpyxl" >/dev/null 2>&1; then
  echo "✅ openpyxl already installed"
else
  echo "📦 Installing openpyxl ..."
  python3 -m pip install --user openpyxl \
    || python3 -m pip install --user --break-system-packages openpyxl
  echo "✅ openpyxl installed"
fi

echo "🎉 Done. Restart Cursor to load the '$SKILL' skill."
