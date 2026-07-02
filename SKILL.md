---
name: html-tracking-spec
description: >-
  从 HTML 页面原型分析并生成理财 App 埋点提报 Excel（浏览事件、点击事件）。
  生成前须与用户确认业务线（sheet 名）及 page_name 等锚点。交付物仅 Excel，
  不向用户输出 JSON。当用户提供 HTML 页面并要求生成埋点、埋点提报、浏览/点击事件、埋点 Excel 时使用。
---

# 理财 App HTML 埋点提报

从 HTML 原型提取交互元素，按团队埋点提报表格式输出 Excel，保存到 HTML 同目录。

**当前范围**：仅 **浏览事件**、**点击事件**；**暂不记录曝光事件**。

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
| 业务线 / sheet | 组合产品 | 中 | 标题含业务线关键词 |
| 页面中文名 | 组合持仓详情 | 高 | nav-title |
| page_name | wealth_portfolio_position_detail | 中 | 新页面 |
| view event | wealth_portfolio_position_view | 中 | 组合产品族 |
| click event | wealth_portfolio_position_click | 中 | 组合产品族 |
| 备注标签 | （空） | — | 默认留空，用户确认时可指定 |

**请确认业务线（sheet 名）及上表命名；回复「确认」或指出需修改字段后，我再生成 Excel。**
```

---

## Step 1：业务线确认（必须等待用户）

### 业务线不明 → AskQuestion

用 AskQuestion，选项来自 [reference.md](reference.md)「业务线清单」。

### 确认话术（统一使用）

```
我已读完 HTML，锚点推断如下。
请确认：
1. 业务线 / sheet 名是否为「{sheet}」？
2. page_name / event 族是否有需修改？

确认后我生成 Excel。
```

**仅当用户回复「确认」「可以」「OK」或等价明确同意** → 进入 Step 2。

### 禁止行为

- ❌ 用户仅 @ HTML 未回复确认 → 不出 Excel
- ❌ 推断置信度「高」自动跳过确认

---

## Step 2：业务线 → event_name 族

**不要**全站套用同一套 view/click。按**已确认**业务线选族：

| 业务线 | 浏览 | 点击 | sheet 名 |
|--------|------|------|----------|
| 理财首页 | `wealth_home_view` | `wealth_home_click` | 理财首页 |
| 组合产品 | `wealth_portfolio_view` | `wealth_portfolio_click` | 组合产品 |
| 组合持仓 | `wealth_portfolio_position_view` | `wealth_portfolio_position_click` | 组合产品 |
| 问卷回访 | `wealth_questionnaire_detail_view` | `wealth_questionnaire_detail_click` | 问卷回访 |
| AI 助手 | `wealth_ai_assistant_view` | `wealth_ai_assistant_click` | AI助手 |

完整映射见 [reference.md](reference.md)。团队若有内部存量表，以存量 event_name 为准。

---

## Step 3：解析 HTML

| 信息 | 来源 |
|------|------|
| 页面中文名 | 确认单（优先）或 HTML 推断 |
| page_name | 确认单（优先）；存量页查 reference |
| 产品代码 | 默认留空 |
| 备注 | 默认留空 |
| 解释说明 | **默认留空，不自动填写** |

**不埋点**：状态栏、纯装饰、Mock 工具栏、无交互静态文案。

---

## Step 4：两类事件

| 类型 | 埋点分类 | 触发时机 |
|------|----------|----------|
| 浏览 | `浏览事件` | 页面渲染完成（每页 1 条） |
| 点击 | `点击事件` | 用户点击 |

- 点击：元素带 `_click` / `_tab` / `_notice` / `_touchandhold` / `_popup`
- **不生成曝光事件**（`*_show` 等暂不写入 Excel）

---

## Step 5：模块与元素

复用 reference 中 module_name：`page_top`、`asset_card`、`portfolio_income`、`portfolio_nav`、`portfolio_performance`、`product_card`、`page_bottom`、`page_popup`。

元素规则见 [reference.md](reference.md)。

---

## Step 6：生成 Excel（仅用户确认后）

**交付物**：仅 `{html文件名}-埋点.xlsx`（与 HTML 同目录）。**不要**向用户交付或持久化 JSON 文件。

```bash
python3 scripts/generate_tracking_excel.py \
  --input "/tmp/page-埋点.json" \
  --output "/path/to/page-埋点.xlsx" \
  --remove-input
```

向用户汇报：**仅 Excel 路径** + 浏览/点击条数 + 锚点摘要。

---

## Step 7：自检

- [ ] 业务线与 sheet 名**已由用户明确确认**
- [ ] **仅交付 Excel**，未持久化 JSON
- [ ] 仅含浏览 + 点击，**无曝光行**
- [ ] **无「前导页面」列**
- [ ] **解释说明列默认为空**
- [ ] page_name / event_name 来自确认单
- [ ] 点击元素有动作后缀
- [ ] `*产品代码` / `*备注` 默认为空
- [ ] 埋点分类列：`浏览事件` / `点击事件`
- [ ] Excel 15 列、橙色表头、event 列合并

## 附加资源

- 业务线清单与命名词表：[reference.md](reference.md)
- 完整示例：[examples.md](examples.md)
