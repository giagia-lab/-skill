# html-tracking-spec

从 HTML 页面原型生成理财 App 埋点提报 Excel（浏览 / 点击 / 曝光）的 Cursor Agent Skill。

## 功能

- 页面级《埋点确认单》→ 用户确认后自动生成 Excel
- 支持多页面 HTML、曝光事件、本地存量知识库检索
- 敏感数据（存量 Excel、element 映射表、registry 索引）**仅本地维护，不入库**

## 安装

一键安装（自动安装 skill 文件 + Python 依赖 `openpyxl`，装完重启编辑器生效）：

```bash
rm -rf /tmp/html-tracking-spec && \
git clone --depth 1 https://github.com/giagia-lab/-skill.git /tmp/html-tracking-spec && \
bash /tmp/html-tracking-spec/install.sh
```

默认装到 `~/.cursor/skills/html-tracking-spec`；Claude Code 等其他编辑器可先设环境变量再执行：

```bash
CURSOR_SKILLS_DIR="$HOME/.claude/skills" bash /tmp/html-tracking-spec/install.sh
```

## 本地知识库（可选）

把团队存量埋点 Excel 作为参数传入即可，脚本自动定位 skill 目录（不区分 AI 编辑器）：

```bash
bash ~/.cursor/skills/html-tracking-spec/build-registry.sh ~/Downloads/tracking-registry.xlsx
```

> Claude Code 用户把路径中的 `.cursor` 换成 `.claude` 即可。
> 可选：把元素中英映射表放到 skill 根目录 `element_name.txt`。

也可手动分步（等价）：

```bash
# 1. 放置团队存量埋点 Excel 为 tracking-registry.xlsx
# 2. 放置 element_name.txt（可选）
python3 scripts/build_registry.py
```

## 生成 Excel

```bash
python3 scripts/generate_tracking_excel.py \
  -i /tmp/spec.json \
  -o ./output-埋点.xlsx \
  --remove-input
```

## 文档

- [SKILL.md](SKILL.md) — Agent 工作流
- [reference.md](reference.md) — 命名约定
- [examples.md](examples.md) — 示例

## License

MIT — 见 [LICENSE](LICENSE)
