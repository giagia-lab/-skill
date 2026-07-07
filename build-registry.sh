#!/usr/bin/env bash
set -euo pipefail

# 定位 skill 根目录 = 本脚本所在目录(天然不挑 AI 编辑器)
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD="$SKILL_DIR/scripts/build_registry.py"
XLSX="$SKILL_DIR/tracking-registry.xlsx"

usage() {
  cat <<EOF
用法: bash build-registry.sh [存量埋点Excel路径]

  传入 Excel 路径 → 拷贝到 skill 根目录为 tracking-registry.xlsx 后构建索引
  不传参数        → 使用 skill 根目录已有的 tracking-registry.xlsx

可选:把元素中英映射表放到 $SKILL_DIR/element_name.txt
EOF
}

case "${1:-}" in -h|--help) usage; exit 0 ;; esac

# 1. 依赖检查
command -v python3 >/dev/null 2>&1 || { echo "❌ 未找到 python3,请先安装"; exit 1; }
if ! python3 -c "import openpyxl" >/dev/null 2>&1; then
  echo "📦 安装依赖 openpyxl ..."
  python3 -m pip install --user openpyxl \
    || python3 -m pip install --user --break-system-packages openpyxl
fi

# 2. 处理输入 Excel
if [ -n "${1:-}" ]; then
  [ -f "$1" ] || { echo "❌ Excel 不存在:$1"; exit 1; }
  cp "$1" "$XLSX"
  echo "📄 已载入:$1 → tracking-registry.xlsx"
fi
if [ ! -f "$XLSX" ]; then
  echo "❌ 未找到 tracking-registry.xlsx,请把存量埋点 Excel 作为参数传入"
  usage
  exit 1
fi

# 3. 构建索引
python3 "$BUILD"
echo "✅ 知识库已构建 → $SKILL_DIR/registry/"
