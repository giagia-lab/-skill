---
name: html-tracking-spec
description: >-
  从 HTML 页面原型分析并生成理财 App 埋点提报 Excel。生成前须与用户确认业务线、
  各页面名称（中英）、埋点事件（浏览/点击/曝光，中英）及页面是否新增；模块与元素
  在确认后自动从 HTML + 本地 registry/element_name 推导。交付物仅 Excel。
---

# 理财 App HTML 埋点提报

从 HTML 原型提取交互元素，按团队埋点提报表格式输出 Excel，保存到 HTML 同目录。

**默认范围**：浏览 + 点击；部分业务线含曝光（须在确认单中明确）。

## 硬性门禁

1. **业务线 / sheet 名已与用户确认**
2. **《埋点确认单》已输出，且用户明确回复确认**
3. 确认单中**各页面**的页面名（中英）、事件（浏览/点击/曝光，中英）、是否新增已落定

> 确认单**不包含**模块、元素清单——这些在用户确认后由 Agent 自动推导。

---

## 工作流

```
Task Progress:
- [ ] 0. 读 HTML + 查 registry → 输出《埋点确认单》（仅页面级锚点）
- [ ] 1. 多轮对话完善页面/事件命名、曝光、存量页补充材料
- [ ] 2. 用户确认后 → 划分 module、逐元素命名（registry + element_name.txt）
- [ ] 3. 内存组装 spec → 运行脚本 → 仅输出 Excel
- [ ] 4. 自检
```

---

## 知识库（本地可选，勿整表塞进对话）

| 资源 | 用途 | 说明 |
|------|------|------|
| [registry/](registry/) | 存量页面 / 业务线 / event 族 | 由本地 `tracking-registry.xlsx` 构建，不入库 |
| `element_name.txt` | 元素英文 ↔ 中文 | 团队本地维护，不入库 |

```bash
python3 scripts/build_registry.py          # 首次：放置 tracking-registry.xlsx 后执行
python3 scripts/lookup_registry.py --page "组合详情"
python3 scripts/lookup_registry.py --sheet "组合产品"
python3 scripts/lookup_registry.py --list-exposure-sheets
python3 scripts/lookup_element_names.py --suggest "返回上一页"
```

---

## Step 0：《埋点确认单》（必做，仅页面级）

读 HTML 后**先**输出确认单，**不要**直接生成 Excel，**不要**在确认单中列出模块/元素。

### 确认单必含字段

| 层级 | 字段 | 说明 |
|------|------|------|
| 全局 | **业务线 / sheet** | 须用户确认 |
| 每页面 | **页面名称（中文）** | |
| 每页面 | **页面名称（英文）** `page_name` | registry 命中则复用，否则建议 |
| 每页面 | **是否新增** | `新增` / `存量` |
| 每页面 | **浏览/点击/曝光事件**（中 + 英） | 不适用填「—」 |

### 确认单模板

```markdown
## 埋点确认单

**业务线 / sheet**：{sheet}（须确认）

### 页面清单

| # | 页面名称（中文） | page_name | 是否新增 | 浏览事件 | view event | 点击事件 | click event | 曝光事件 | show event |
|---|-----------------|-----------|----------|----------|------------|----------|-------------|----------|------------|
| 1 | {page_cn} | `{page_en}` | 新增/存量 | {view_cn} | `{view_en}` | {click_cn} | `{click_en}` | — | — |

### 存量页补充（仅当存在「存量」行时提示）

可补充历史埋点 Excel/截图，用于生成阶段对齐命名（不在确认单中逐项列出）。

### 请你确认

全部无误后回复「确认」，我再生成 Excel（模块与元素由我自动补全）。
```

### 禁止出现在确认单中

- ❌ 模块名称清单
- ❌ 元素名称 / element_en 清单

---

## Step 1：确认门禁

- 用户可多轮修改确认单中的**业务线、页面名、事件名、是否新增、曝光**
- **仅当**用户明确回复「确认」→ 进入生成
- 曝光未经确认 → 不写入 Excel

---

## Step 2：生成阶段（用户确认后）

| 信息 | 来源 |
|------|------|
| 页面/事件中英名 | 确认单 |
| 模块名 | registry 存量页 + HTML 结构 |
| 元素名 | HTML 交互 + `element_name.txt`（存量优先） |

**不埋点**：状态栏、纯装饰、Mock 工具栏、无交互静态文案。

---

## Step 3：生成 Excel

```bash
python3 scripts/generate_tracking_excel.py \
  --input "/tmp/page-埋点.json" \
  --output "/path/to/page-埋点.xlsx" \
  --remove-input
```

多页面用 spec 的 `pages` 数组；含曝光时加 `show_events`（见 [examples.md](examples.md)）。

---

## Step 4：自检

- [ ] 确认单与 Excel 的 page_name、事件名、是否新增一致
- [ ] 曝光行仅含用户确认项
- [ ] 解释说明列默认为空；Excel 15 列、橙色表头

## 附加资源

- [reference.md](reference.md) · [examples.md](examples.md) · [registry/](registry/)
