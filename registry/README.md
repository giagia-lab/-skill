# registry/

团队本地存量埋点知识库索引目录（**不提交敏感 JSON**）。

## 使用

1. 将团队存量埋点 Excel 放到 skill 根目录，命名为 `tracking-registry.xlsx`（已 gitignore）
2. 构建索引：

```bash
python3 scripts/build_registry.py
```

3. 运行时检索：

```bash
python3 scripts/lookup_registry.py --page "组合详情"
python3 scripts/lookup_registry.py --sheet "组合产品"
python3 scripts/lookup_registry.py --list-exposure-sheets
```

## 文件（本地生成，不入库）

| 文件 | 说明 |
|------|------|
| `meta.json` | 构建元信息 |
| `sheets-index.json` | 业务线 → event 族 |
| `pages-index.json` | 页面 → 模块/元素存量 |

## 元素命名

另维护本地 `element_name.txt`（`element_en,中文` CSV），用 `lookup_element_names.py` 检索。
