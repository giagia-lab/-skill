# html-tracking-spec

Cursor Agent Skill：从 HTML 页面原型生成理财线埋点提报 Excel（浏览 / 曝光 / 点击）。

## 安装

```bash
git clone https://github.com/wangsijia/html-tracking-spec.git
cd html-tracking-spec
bash install.sh
```

或一行（已克隆到本地后）：

```bash
bash install.sh
```

安装位置：`~/.cursor/skills/html-tracking-spec/`

## 依赖

```bash
pip3 install openpyxl
```

## 使用

在 Cursor 中 `@你的页面.html`，并说：

> 生成该 HTML 的页面埋点

Agent 会先输出《埋点锚点确认单》，确认业务线后生成 `{页面名}-埋点.xlsx`。

## 目录

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Agent 主流程 |
| `reference.md` | 命名词表与 Excel 列定义 |
| `examples.md` | 示例 spec |
| `scripts/generate_tracking_excel.py` | JSON → Excel |
| `scripts/parse_tracking_registry.py` | 存量表解析（可选） |

## 生成 Excel（手动）

```bash
python3 scripts/generate_tracking_excel.py \
  --input /tmp/spec.json \
  --output ./page-埋点.xlsx \
  --remove-input
```

## License

MIT
