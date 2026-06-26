---
name: html-tracking-spec
description: >-
  从 HTML 页面原型分析并生成理财线埋点提报 Excel（浏览/曝光/点击三类事件）。
  生成前须与用户确认业务线（sheet 名）及 page_name 等锚点。交付物仅 Excel，
  不向用户输出 JSON。当用户提供 HTML 页面并要求生成埋点、埋点提报、
  浏览/曝光/点击事件、埋点 Excel 时使用。
---

# 理财线 HTML 埋点提报

从 HTML 原型提取交互元素，按团队理财线埋点提报表格式输出 Excel，保存到 HTML 同目录。

## 硬性门禁（两条，全部满足才允许写 JSON / 跑脚本 / 出 Excel）

1. **业务线 / sheet 名已与用户确认**（见 Step 0）
2. **锚点确认单已输出，且用户明确回复确认**（见 Step 1）

> 即使用户在首条指令里写了业务线，也**必须先出确认单并等用户回复**，不得跳过。

---

## 工作流

```
Task Progress:
- [ ] 0. 读 HTML + 推断业务线 → 输出《埋点锚点确认单》
- [ ] 1. 等用户确认业务线与锚点（必须显式回复）
- [ ] 2. 通读 HTML 划分 module
- [ ] 3. 逐元素命名（按 reference 规范与后缀规则）
- [ ] 4. 内存组装 spec → 运行脚本 → **仅输出 Excel**
- [ ] 5. 对照 reference 自检
```

---

## Step 0：埋点锚点确认（必做，优先生成）

读 HTML 后**先**输出《埋点锚点确认单》，**不要**直接生成 Excel。

### 最小输入

| 输入 | 必填 | 说明 |
|------|:----:|------|
| HTML 路径 | ✅ | 用户 @ 或提供路径 |
| **业务线 / sheet 名** | ✅ **须用户确认** | 可推断，但推断值须写入确认单等用户点头 |
| 页面中文名 | 推断 | `<title>`、导航标题；用户可覆盖 |
| page_name | 建议待确认 | 查 reference 存量；新页按命名模式给建议值 |
| event_name 族 | 建议待确认 | 按业务线查 reference；新业务线给建议值 |

### 确认单模板

```markdown
## 埋点锚点确认单

| 字段 | 推断值 | 置信度 | 依据 |
|------|--------|--------|------|
| 业务线 / sheet | 目标盈 | 中 | 标题含业务线关键词 |
| 页面中文名 | 目标盈止盈T日持仓详情 | 高 | nav-title |
| page_name | finance_portfolio_target_profit_tp_t_asset_detail | 中 | 新页面，按命名模式生成 |
| view event | finance_portfolio_target_profit_asset_view | 中 | 目标盈族 |
| show event | finance_portfolio_target_profit_show | 中 | 目标盈族 |
| click event | finance_portfolio_target_profit_asset_click | 中 | 目标盈族 |
| 备注标签 | （空） | — | 默认留空，用户确认时可指定 |

**请确认业务线（sheet 名）及上表命名；回复「确认」或指出需修改字段后，我再生成 Excel。**
```

---

## Step 1：业务线确认（必须等待用户）

### 业务线不明 → AskQuestion

用 AskQuestion，选项来自 [reference.md](reference.md)「业务线清单」：

- 理财首页基金投顾tab
- 管理型组合
- 基金投顾满意度回访
- 目标盈
- 高端理财
- AI投顾（示例业务线）
- 其他（用户补充）

### 确认话术（统一使用）

```
我已读完 HTML，锚点推断如下。
请确认：
1. 业务线 / sheet 名是否为「{sheet}」？
2. page_name / event 族是否有需修改？

确认后我生成 Excel。
```

**仅当用户回复「确认」「可以」「OK」或等价明确同意** → 进入 Step 2。
用户修正任意字段 → 更新确认单 → 再次请用户确认。

### 禁止行为

- ❌ 用户仅 @ HTML 未回复确认 → 不出 Excel
- ❌ 推断置信度「高」自动跳过确认

---

## Step 2：业务线 → event_name 族

**不要**全站套用 `finance_home_view/click`。按**已确认**业务线选族：

| 业务线 | 浏览 | 曝光 | 点击 | sheet 名 |
|--------|------|------|------|----------|
| 理财首页/商城 | `finance_home_view` | `finance_home_show` | `finance_home_click` | 理财首页基金投顾tab |
| 管理型组合 | `finance_portfolio_managed_view` | `finance_portfolio_managed_show` | `finance_portfolio_managed_click` | 管理型组合 |
| 管理型组合持仓 | `…_asset_detail_view` 或共用 view | `finance_portfolio_managed_show` | `finance_portfolio_managed_asset_click` | 管理型组合 |
| 基金投顾满意度 | `…questionnaire_detail_view` | — | `…questionnaire_detail_click` | 基金投顾满意度回访 |
| 目标盈 | `finance_portfolio_target_profit_asset_view` | `finance_portfolio_target_profit_show` | `finance_portfolio_target_profit_asset_click` | 目标盈 |

完整映射见 [reference.md](reference.md)。

---

## Step 3：解析 HTML

| 信息 | 来源 |
|------|------|
| 页面中文名 | 确认单（优先）或 HTML 推断 |
| page_name | 确认单（优先）；存量页查 reference |
| 产品代码 | 默认留空；确认单中用户指定时才填 |
| 备注 | 默认留空；确认单中用户指定时才填 |

**不埋点**：状态栏、纯装饰、Mock 工具栏、无交互静态文案。

---

## Step 4：三类事件

| 类型 | 埋点分类 | 触发时机 |
|------|----------|----------|
| 浏览 | `浏览事件` | 页面渲染完成 |
| 曝光 | `曝光事件` | 模块进可视区，单次去重 |
| 点击 | `点击事件` | 用户点击 |

- 浏览：`from_page` 独立列，不写备注
- 曝光：`*_show`
- 点击：元素带 `_click` / `_tab` / `_notice` / `_touchandhold` / `_popup`

---

## Step 5：模块与元素

复用 reference 中 module_name：`page_top`、`asset_card`、`portfolio_income`、`portfolio_nav`、`portfolio_performance`、`product_card`、`page_bottom`、`page_popup`。

元素规则见 [reference.md](reference.md)。

---

## Step 6：生成 Excel（仅用户确认后）

**交付物**：仅 `{html文件名}-埋点.xlsx`（与 HTML 同目录）。**不要**向用户交付或持久化 JSON 文件。

生成流程：

1. 在内存中组装 spec（单页 `page` 或多页 `pages` 结构，格式见 [examples.md](examples.md)）
2. 写入**临时** JSON（如 `/tmp/{html名}-埋点.json`），运行脚本后立即删除：

```bash
python3 scripts/generate_tracking_excel.py \
  --input "/tmp/page-埋点.json" \
  --output "/path/to/page-埋点.xlsx" \
  --remove-input
```

3. 向用户汇报：**仅 Excel 路径** + 三类事件条数 + 锚点摘要

> Agent 回复中**不要**列出 JSON 路径；JSON 仅为脚本输入的中间格式。

---

## Step 7：自检

- [ ] 业务线与 sheet 名**已由用户明确确认**
- [ ] 用户已回复确认后再出 Excel
- [ ] **仅交付 Excel**，未向 HTML 同目录写入 `-埋点.json`
- [ ] page_name / event_name 来自确认单，非临时编造
- [ ] 曝光 `*_show`；点击元素有动作后缀
- [ ] `from_page` 独立列；`*产品代码` / `*备注` 默认为空（首行列标题保留）
- [ ] 埋点分类列：`浏览事件` / `曝光事件` / `点击事件`（勿填业务线名）
- [ ] Excel 15 列、橙色表头、event 列合并

## 附加资源

- 业务线清单与命名词表：[reference.md](reference.md)
- 完整示例：[examples.md](examples.md)
