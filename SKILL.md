---
name: html-tracking-spec
description: >-
  理财 App 埋点三阶段交付：HTML + PRD → 埋点确认单 → Excel + tracking-spec.json →
  PRD 内联埋点表 + HTML data-track-* 锚点。生成前须确认业务线、各页面名称（中英）、
  埋点事件（浏览/点击/曝光，中英）及页面是否新增；模块与元素在确认后自动从 HTML +
  本地 registry/element_name 推导。
---

# 理财 App HTML 埋点交付

从 HTML 原型 + PRD 提取交互，按团队埋点提报表格式输出 Excel，并在 Excel 确认后将埋点映射写入 PRD 内联表与 HTML 锚点。

**默认范围**：浏览 + 点击；部分业务线含曝光（须在确认单中明确）。

## 三阶段门禁

```
阶段1：埋点确认单（仅页面级）     → 用户「确认」
阶段2：tracking-spec.json + Excel → 用户「Excel 确认」
阶段3：新 PRD（内联埋点表）+ 新 HTML（data-track-*）
```

| 阶段 | 交付物 | 禁止 |
|------|--------|------|
| 1 | 《埋点确认单》 | 不出 Excel / 不改 PRD / 不改 HTML |
| 2 | `tracking-spec.json` + Excel | 不出 PRD / 不改 HTML |
| 3 | 新 PRD + 原型 HTML | 仅在 Excel 确认后执行 |

> 确认单**不包含**模块、元素清单——这些在用户确认后由 Agent 自动推导。

---

## 工作流

```
Task Progress:
- [ ] 0. 读 HTML + PRD + 查 registry → 输出《埋点确认单》（仅页面级锚点）
- [ ] 1. 多轮对话完善页面/事件命名、曝光、存量页补充材料
- [ ] 2. 用户「确认」→ 划分 module、逐元素命名 → tracking-spec.json + Excel
- [ ] 3. 用户「Excel 确认」→ PRD 内联表 + HTML data-track-*
- [ ] 4. 自检（三阶段）
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

## 阶段 1：《埋点确认单》（必做，仅页面级）

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
| 1 | {page_cn} | `{page_en}` | 新增/存量 | {view_cn} | `{view_en}` | {click_cn} | `{click_en}` | — 或 {show_cn} | — 或 `{show_en}` |

### 存量页补充（仅当存在「存量」行时提示）

可补充历史埋点 Excel/截图，用于生成阶段对齐命名（不在确认单中逐项列出）。

### 请你确认

全部无误后回复「确认」，我再生成 Excel（模块与元素由我自动补全）。
```

### 多页面 HTML

一个 HTML 含多个逻辑屏 → 确认单按**逻辑页面**分行，每行独立 page_name 与事件。

### 禁止出现在确认单中

- ❌ 模块名称清单
- ❌ 元素名称 / element_en 清单
- ❌ 逐条点击事件预览表

### 阶段 1 门禁

- 用户可多轮修改确认单中的**业务线、页面名、事件名、是否新增、曝光**
- **仅当**用户明确回复「确认」→ 进入阶段 2
- 曝光未经确认 → 不写入 Excel

---

## 阶段 2：Excel + tracking-spec.json（用户确认后）

| 信息 | 来源 |
|------|------|
| 页面/事件中英名 | 确认单 |
| 模块名 | registry 存量页 + HTML 结构 |
| 元素名 | HTML 交互 + `element_name.txt`（存量优先） |
| track_id / anchor / interaction_id | Agent 组装进 `tracking-spec.json` |
| 产品代码 / 备注 / 解释说明 | 默认空 |

**不埋点**：状态栏、纯装饰、Mock 工具栏、无交互静态文案。

### 生成 Excel

```bash
python3 scripts/generate_tracking_excel.py \
  --input "/tmp/page-埋点.json" \
  --output "/path/to/page-埋点.xlsx" \
  --remove-input
```

多页面用 spec 的 `pages` 数组；含曝光时加 `show_events`（见 [examples.md](examples.md)）。

向用户汇报：**Excel 路径** + 浏览/点击/曝光条数；同时交付 `tracking-spec.json`（机器契约，含 track_id、anchor、interaction_id）。

**仅当**用户明确回复「Excel 确认」→ 进入阶段 3。

### 阶段 2 禁止

- ❌ 未出确认单 → 不出 Excel
- ❌ Excel 未确认 → 不出 PRD / 不改 HTML

---

## 阶段 3：PRD 内联埋点 + HTML 锚点

读取已确认的 `tracking-spec.json`，生成新 PRD 与新 HTML（**勿改原稿**，输出到交付目录）。

### PRD 内联表规则

1. **点击埋点**：紧跟「交互描述」中可埋点 bullet，插入 `<!-- TRACKING:{IX}:BEGIN/END -->` 包裹的**完整映射表**。
2. **浏览埋点**：放在功能节标题下、`#### 业务描述` 之前。
3. **状态类 bullet**：不插表。
4. 表格列头为 **event_name / page_name / module_name / element_name / anchor**；数据行纵向 **中文 / 英文** 两行。
5. **不展示**：埋点分类、元素位置、track_id（track_id 仅保留在 JSON / HTML）。

### 点击事件标准表

| | event_name | page_name | module_name | element_name | anchor |
| --- | --- | --- | --- | --- | --- |
| 中文 | 组合详情页点击 | 组合产品详情页 | 产品信息 | 了解详情 | — |
| 英文 | `wealth_portfolio_detail_click` | `wealth_portfolio_detail` | `product_info` | `learn_detail_click` | `[data-ann="learn-more"]` |

浏览事件：模块、元素两行均填 `—`；锚点写在英文行。

阶段 3 自动追加 `## 附录：埋点映射总表`。详见 [reference.md](reference.md#prd-内联埋点表格)。

### HTML 锚点

向原型 HTML 写入（与 `data-ann` 等标注并存）：

- `data-track-id`
- `data-track-type`（view / click）
- `data-track-event`（event_name_en）
- `data-track-ix`（与 PRD 编号一致）

可选注入 debug stub（控制台 `[track]` 日志）。

### 脚本

```bash
# 表格生成（由项目 build 脚本 import）
python3 scripts/prd_tracking_table.py

# HTML 注入（由项目 build 脚本 import）
python3 scripts/inject_html_tracking.py
```

项目内阶段 3 应 import 本 skill 的 `scripts/`，**禁止**手写简化版埋点行。

---

## 自检（三阶段）

**阶段 1**
- [ ] 确认单仅含页面级字段，无模块/元素清单

**阶段 2**
- [ ] 确认单与 Excel 的 page_name、事件名、是否新增一致
- [ ] 曝光行仅含用户确认项
- [ ] Excel 15 列、橙色表头
- [ ] `tracking-spec.json` 与 Excel 条数、字段一致

**阶段 3**
- [ ] PRD 内联表五列完整，锚点在英文行；无 track_id / 埋点分类 / 元素位置
- [ ] `<!-- TRACKING:{IX}:BEGIN/END -->` 可 idempotent 重生成
- [ ] HTML `data-track-*` selector 可命中对应元素
- [ ] `data-track-ix` 与 PRD 编号一致

## 附加资源

- [reference.md](reference.md) · [examples.md](examples.md) · [registry/](registry/)
