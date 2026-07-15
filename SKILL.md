---
name: html-tracking-spec
description: >-
  理财 App 埋点三阶段交付：HTML + PRD → 埋点确认单（事件名前置）→
  Excel + tracking-spec.json → PRD 内联埋点表 + HTML data-track-*。
  event_name 默认来自事件名称字典（wealth_home / wealth_fund 等），
  与页面同单确认；registry 只用于 page/module/element。Agent 不主动新增事件名。
---

# 理财 App HTML 埋点交付

从 HTML 原型 + PRD 提取交互，按团队埋点提报表格式输出 Excel，并在 Excel 确认后将埋点映射写入 PRD 内联表与 HTML 锚点。

**默认范围**：浏览 + 点击；部分业务线含曝光（须在确认单中明确）。

## 三阶段门禁

```
阶段1：埋点确认单（页面级；事件归属/中英名前置强调） → 用户「确认」
阶段2：tracking-spec.json + Excel                    → 用户「Excel 确认」
阶段3：新 PRD（内联埋点表）+ 新 HTML（data-track-*）
```

| 阶段 | 交付物 | 禁止 |
|------|--------|------|
| 1 | 《埋点确认单》 | 不出 Excel / 不改 PRD / 不改 HTML；不含模块/元素清单 |
| 2 | `tracking-spec.json` + Excel | 不出 PRD / 不改 HTML；**不得改写已确认 event 前缀** |
| 3 | 新 PRD + 原型 HTML | 仅在 Excel 确认后执行 |

> 事件命名管控严格，但**不另开独立确认门禁**：与页面字段同单确认；确认单内**事件名称优先**，歧义页用 AskQuestion。  
> 模块/元素不在确认单中列出——整单「确认」后由 Agent 自动推导。

---

## 工作流

```
Task Progress:
- [ ] 0. 读 HTML + PRD + 查 registry / 事件字典 → 输出《埋点确认单》（事件名前置）
- [ ] 1. 歧义处 AskQuestion；多轮完善后用户「确认」
- [ ] 2. 划分 module、逐元素命名 → tracking-spec.json + Excel
- [ ] 3. 用户「Excel 确认」→ PRD 内联表 + HTML data-track-*
- [ ] 4. 自检
```

---

## 知识库（运行时检索，勿整表塞进对话）

| 资源 | 用途 | 说明 |
|------|------|------|
| [references/event-name-dictionary.md](references/event-name-dictionary.md) | **`event_name` 默认标准来源**（示例字典，可替换） | 开确认单前必读 |
| [registry/](registry/) | 存量 **page** / sheet / module·element（**非** event 提案源） | 由本地 `tracking-registry.xlsx` 构建，不入库 |
| `element_name.txt` | 元素英文 ↔ 中文 | 团队本地维护，不入库 |
| [scripts/event_name_cn.py](scripts/event_name_cn.py) | 事件中文动作词校验 / 补齐 | `--check` / `--normalize` |
| [scripts/lookup_event_names.py](scripts/lookup_event_names.py) | **按字典**建议前缀 | `--suggest` / `--list-dict` |

```bash
python3 scripts/lookup_event_names.py --suggest "基金详情"
python3 scripts/lookup_event_names.py --list-dict
python3 scripts/lookup_registry.py --page "组合详情"
python3 scripts/lookup_element_names.py --suggest "返回上一页"
```

---

## 阶段 1：《埋点确认单》（必做，仅页面级）

读 HTML + PRD 并完成 registry / 字典检索后，**先**输出本单，**不要**直接生成 Excel，**不要**列出模块/元素。

### 事件名称在确认单中的位置（写死）

**与页面字段同单确认，不另开「事件名称确认」门禁。** 确认单必须：

1. **开头先放**「事件名称（重点核对）」专节  
2. 每行标明 **事件归属** + 浏览/点击/曝光中英文  
3. 有歧义（如 `wealth_home` vs `wealth_fund`）→ **AskQuestion**，不得暗含选定  
4. 用户一次回复 **「确认」** 同时锁定页面与事件名；阶段 2 **不得改写**已确认 event 前缀  

### event_name 归属硬约束（写死 · 字典默认来源）

**`event_name`（英）默认来源**：[references/event-name-dictionary.md](references/event-name-dictionary.md)。  
理财线示例默认只有：

| 业务 | 前缀 | 三件套 |
|------|------|--------|
| 理财 | `wealth_home` | `wealth_home_view` / `_click` / `_show` |
| 理财基金 | `wealth_fund` | `wealth_fund_view` / `_click` / `_show` |

同一前缀可服务多页面——靠 `page_name` / `module_name` / `element_name` 区分。  
`page_name` 可以新；**禁止**为每个新页面拆一套字典外默认 event 前缀。

**提案规则：**

| 步骤 | 动作 |
|------|------|
| 1 | 读字典 + `lookup_event_names.py --suggest`（**仅返回字典前缀**） |
| 2 | 公募/基金详情、购买、基金 H5 → 默认 `wealth_fund_*`；商城首页/专区 → `wealth_home_*` |
| 3 | `wealth_home` vs `wealth_fund` 不清 → AskQuestion |
| 4 | registry 细粒度历史名**可在备注中提示**，但确认单默认栏仍填**字典**名；仅用户明示「用户指定（非字典）」才改写 |

**禁止（Agent 默认行为）：**

- ❌ 用 registry 页级/sheet 级 `events.*` 当作确认单默认 `event_name`
- ❌ 自造或沿用字典外细名作默认
- ❌ 为每个新页面拆一套新 event 前缀

### 事件中文名硬约束（写死）

`event_name` **中文必须体现动作**，与英文 `_view` / `_click` / `_show` 对齐。

| 前缀 | 浏览中文 | 点击中文 | 曝光中文 |
|------|----------|----------|----------|
| `wealth_fund` | 理财基金浏览 | 理财基金点击 | 理财基金曝光 |
| `wealth_home` | 理财浏览 | 理财点击 | 理财曝光 |

```bash
python3 scripts/event_name_cn.py --check tracking-spec.json
python3 scripts/event_name_cn.py --normalize tracking-spec.json --write-in-place
```

### 确认单必含字段

| 层级 | 字段 | 说明 |
|------|------|------|
| 全局 | **业务线 / sheet** | 须用户确认 |
| 每页面 | **页面名称（中文）** | |
| 每页面 | **页面名称（英文）** `page_name` | registry 命中则复用，否则建议（页面可新增） |
| 每页面 | **是否新增** | 指**页面**：`新增` / `存量` |
| 每页面 | **事件归属** | 字典档或 `用户指定新增`（**重点**） |
| 每页面 | **浏览/点击/曝光事件**（中 + 英） | 中文须含动作词（**重点**） |

### 确认单模板

```markdown
## 埋点确认单

**业务线 / sheet**：{sheet}（须确认）

**事件名策略**：默认归属已有前缀（见「事件归属」）；Agent 未提议新前缀。改英文字段即「用户指定新增」。

### 事件名称（重点核对）

| # | 逻辑页 | 事件归属 | 浏览事件 | view event | 点击事件 | click event | 曝光 | show | 归属依据 |
|---|--------|----------|----------|------------|----------|-------------|------|------|----------|
| 1 | {page_cn} | 字典 `wealth_fund` | 理财基金浏览 | `wealth_fund_view` | 理财基金点击 | `wealth_fund_click` | — | — | 事件字典·理财基金 |

有歧义时列出候选并 AskQuestion（勿擅自选定）。

### 页面清单

| # | 页面名称（中文） | page_name | 是否新增（页） | 事件归属（同上） | 浏览 / view | 点击 / click | 曝光 / show |
|---|-----------------|-----------|----------------|------------------|-------------|--------------|-------------|
| 1 | {page_cn} | `{page_en}` | 新增/存量 | … | … / `{…}` | … / `{…}` | — |

### 存量页补充（仅当存在「存量」行时提示）

如有存量页面需增量埋点，可补充历史埋点 Excel/截图，用于生成阶段对齐 module/元素（**不在确认单逐项列出**）。

### 请你确认

请重点核对**事件归属与事件中英文**，并确认业务线、页面名、是否新增页、曝光。  
全部无误后回复「确认」，我再生成 Excel（模块与元素由我自动补全）。
```

### 多页面 HTML

一个 HTML 含多个逻辑屏 → 确认单按**逻辑页面**分行，每行独立 page_name 与事件。

### 存量页判定（页面）与事件判定（事件）

| 对象 | 判定 |
|------|------|
| **页面** | `--page` 命中 → 存量页；未命中 → 新增页（仍可复用已有 event） |
| **事件** | **仅字典前缀**；**新增页 ≠ 新事件名**（多页可共用 `wealth_fund_*`） |

### 曝光事件

- 业务线 `has_exposure=true` 或页面存量含曝光 → 确认单列出，须用户确认/手改  
- 用户未确认曝光 → 生成时不写曝光行  

### 禁止出现在确认单中

- ❌ 模块 / 元素清单、逐条点击预览表  
- ❌ 默认自造新前缀，或默认填 registry 细粒度非字典名  
- ❌ 另建《事件名称确认单》作为必经门禁（已并入本单）  

### 阶段 1 门禁

- **仅当**用户明确回复「确认」→ 进入阶段 2  
- 业务线不明或事件前缀歧义 → AskQuestion  

---

## 阶段 2：Excel + tracking-spec.json（用户确认后）

| 信息 | 来源 |
|------|------|
| 页面/事件中英名 | 埋点确认单（含已确认事件名） |
| 模块名 | registry 存量页 + HTML 结构 |
| 元素名 | HTML 交互 + `element_name.txt`（存量优先） |
| track_id / anchor / interaction_id | Agent 组装进 `tracking-spec.json` |
| 产品代码 / 备注 / 解释说明 | 默认空 |

**不埋点**：状态栏、纯装饰、Mock 工具栏、无交互静态文案。

元素命名优先级：完全命中 → 近义命中 → 同族风格 → 新增。  
（**元素**可新增；**事件前缀**仍受确认单约束，阶段 2 不得偷偷改成新前缀。）

### 生成 Excel

```bash
python3 scripts/generate_tracking_excel.py \
  --input "/tmp/page-埋点.json" \
  --output "/path/to/page-埋点.xlsx" \
  --remove-input
```

多页面用 spec 的 `pages` 数组；含曝光时加 `show_events`（见 [examples.md](examples.md)）。

向用户汇报：**Excel 路径** + 浏览/点击/曝光条数 + 页面数摘要；同时交付 `tracking-spec.json`（机器契约，含 track_id、anchor、interaction_id）。

**仅当**用户明确回复「Excel 确认」→ 进入阶段 3。

### 阶段 2 禁止

- ❌ 未获埋点确认单「确认」→ 不出 Excel
- ❌ 在确认单中要求用户确认每个模块/元素
- ❌ 曝光未经确认就写入 Excel
- ❌ Excel 未确认 → 不出 PRD / 不改 HTML
- ❌ 阶段 2 偷偷把确认单已确认 event 前缀改成 Agent 自造新前缀

---

## 阶段 3：PRD 内联埋点 + HTML 锚点

读取已确认的 `tracking-spec.json`，生成新 PRD 与新 HTML（**勿改原稿**，输出到交付目录）。

### PRD 内联表规则

**一一对应（硬约束）**

| 类型 | 挂载位置 | 格式 | 禁止 |
|------|----------|------|------|
| **点击** | 「交互描述」下**每一条可埋点 bullet** 之后 | `一句功能描述` → 紧跟一张 `埋点映射（Fxx-IXxx）` 表 | 多句共用一张、堆到文末、挂在状态结果句下 |
| **浏览** | **仅对逻辑页面有效**：功能节标题下、`#### 业务描述` **之前**（每逻辑页至多 1 条 view） | 模块/元素填 `—` | 挂在某条点击交互下、或按按钮拆浏览 |

**表格顶格（硬约束 · 写死）**

| 规则 | 说明 |
|------|------|
| 强制 | `<!-- TRACKING:… -->`、`**埋点映射**`、表头行、分隔行、数据行 **全部行首无空格/Tab** |
| 禁止 | 为「看起来缩在列表下」给表格加缩进；禁止用手写缩进覆盖 `prd_tracking_table.py` |
| 原因 | GFM / VS Code / Cursor Markdown Preview：列表内缩进表格常解析失败 → **源码看得见、Preview 表消失** |
| 实现 | 一律调用 `scripts/prd_tracking_table.py`（内部强制顶格）；build 脚本**禁止**再包一层缩进 |

正例（表顶格，紧跟 bullet）：

```markdown
- 用户点击“了解详情”后,当前页面蒙层展示弹窗。
<!-- TRACKING:F02-IX01:BEGIN -->
**埋点映射（F02-IX01）**

| | event_name | page_name | module_name | element_name | anchor |
| --- | --- | --- | --- | --- | --- |
| 中文 | 理财基金点击 | 净值型公募基金详情页 | 交易规则 | 了解详情 | — |
| 英文 | `wealth_fund_click` | `wealth_fund_product_detail` | `fund_information` | `learn_detail_click` | `[data-ann="detail-learn-more"]` |
<!-- TRACKING:F02-IX01:END -->
```

细则：

1. **点击埋点**：紧跟可埋点交互 bullet；**表必须顶格**。
2. **浏览埋点**：放在功能节标题与 `#### 业务描述` 之间（同样顶格）。
3. **状态类 bullet**：**不插表**。
4. 原稿缺可埋点交互句、但 Excel/spec 已有对应点击时：先补一句交互描述，再挂表。
5. 表格列头为 **event_name / page_name / module_name / element_name / anchor**；数据行纵向 **中文 / 英文**。
6. **不展示**：埋点分类、元素位置、track_id（仅保留在 JSON / HTML）。
7. 文末 `## 附录：埋点映射总表` 仅作索引，**不能代替**正文内联一一对应。

### HTML 锚点

向原型 HTML 写入（与 `data-ann` 并存）：

- `data-track-id`
- `data-track-type`（view / click）
- `data-track-event`（event_name_en）
- `data-track-ix`（与 PRD 编号一致）

可选注入 debug stub（控制台 `[track]` 日志）。

### 脚本

```bash
python3 scripts/prd_tracking_table.py
python3 scripts/inject_html_tracking.py
```

项目内阶段 3 应 import 本 skill 的 `scripts/`，**禁止**手写简化版埋点行。

---

## 自检（三阶段）

**阶段 1**
- [ ] 确认单含「事件名称（重点核对）」专节；与页面字段同单
- [ ] **每个 view/click/show 英前缀均在事件名称字典内**（或用户明示「用户指定（非字典）」）
- [ ] 默认提案**无** registry 细名
- [ ] `wealth_home` vs `wealth_fund` 歧义已 AskQuestion
- [ ] 中文事件名含动作词；确认单无模块/元素清单
- [ ] 用户已回复「确认」

**阶段 2**
- [ ] 确认单中的业务线、各页 page_name、事件名、是否新增与 Excel 一致
- [ ] **事件中文名均含动作词**；`event_name_cn.py --check` 通过
- [ ] **事件英文前缀均在字典内**（或确认单已标「用户指定（非字典）」）
- [ ] 存量页 module/element 已参考 registry；元素已查 element_name.txt
- [ ] 曝光行仅含用户确认项
- [ ] Excel 15 列、橙色表头、英文 field 副标题、event 列合并
- [ ] `tracking-spec.json` 与 Excel 条数、字段一致

**阶段 3**
- [ ] 点击：一句可埋点交互描述 + 一张埋点表（一一对应）；状态句无表
- [ ] **所有 TRACKING 表相关行顶格**（行首无空格）
- [ ] 浏览：仅挂在页面级；每逻辑页至多 1 条 view
- [ ] PRD 内联表列头完整；锚点值在英文行
- [ ] `<!-- TRACKING:{IX}:BEGIN/END -->` 可 idempotent 重生成
- [ ] HTML `data-track-*` selector 可命中对应元素
- [ ] `data-track-ix` 与 PRD 编号一致
- [ ] 附录总表仅作索引，正文以内联为准

## 附加资源

- [reference.md](reference.md) · [examples.md](examples.md) · [registry/](registry/)
