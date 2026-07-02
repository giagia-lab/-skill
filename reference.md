# 理财 App 埋点规范参考

> 通用模板，可按团队内部存量表覆盖。**当前 skill 仅输出浏览 + 点击，暂不记录曝光。**

## 业务线清单（AskQuestion 选项源）

| sheet 名 | 业务线 key | HTML 推断线索 |
|----------|-----------|--------------|
| 理财首页 | `wealth_home` | 首页、Tab、产品列表 |
| 组合产品 | `portfolio` | 组合详情、持仓、净值 |
| 问卷回访 | `questionnaire` | 问卷、满意度、回访 |
| 高端产品 | `high_end` | 高端、私募、信托 |
| 产品推荐 | `product_feed` | 推荐、榜单、发车 |
| AI助手 | `ai_assistant` | AI、智能助手、对话 |

**置信度推断规则：**

| 线索 | 置信度 |
|------|--------|
| 用户指令写明业务线 | 高 |
| 标题/文案仅命中一条业务线关键词 | 中 |
| 命中多条业务线，或无任何特征 | 低 → 必须 AskQuestion |
| page_name 在下方存量表有完全匹配 | 高 |

## event_name 族（核心）

| 后缀 | 类型 | 示例 |
|------|------|------|
| `_view` | 浏览 | `wealth_portfolio_view` |
| `_click` | 点击 | `wealth_portfolio_position_click` |

### 示例 event_name

| 事件名称（中文） | event_name | 适用范围 |
|-----------------|------------|----------|
| 组合产品浏览事件 | `wealth_portfolio_view` | 组合相关页面 |
| 组合产品点击事件 | `wealth_portfolio_click` | 组合详情等 |
| 持仓详情点击事件 | `wealth_portfolio_position_click` | 持仓详情页 |
| 理财首页浏览 | `wealth_home_view` | 理财首页 |
| 理财首页点击 | `wealth_home_click` | 理财首页 |
| 问卷详情浏览 | `wealth_questionnaire_detail_view` | 问卷页 |
| 问卷详情点击 | `wealth_questionnaire_detail_click` | 问卷页 |
| AI 助手浏览 | `wealth_ai_assistant_view` | AI 助手多页面 |
| AI 助手点击 | `wealth_ai_assistant_click` | AI 助手多页面 |

> 曝光 event（`*_show`）在部分存量文档中存在，**当前 skill 暂不写入 Excel**。

### 新页面如何定 event_name

1. 找到团队文档中**同业务线 sheet**
2. 若已有 view/click 族 → **复用**，不新建
3. 全新业务线 → `{domain}_{业务域}_{子域}_{view|click}`
4. 特殊单页 → 可用 `{page_name}_view` 作为 event_name

## page_name

- 前缀建议 `wealth_`（或团队统一前缀），snake_case

| 页面 | page_name |
|------|-----------|
| 组合详情页 | `wealth_portfolio_detail` |
| 组合持仓详情页 | `wealth_portfolio_position_detail` |
| 问卷详情 | `wealth_questionnaire_detail` |
| 理财首页 Tab | `wealth_home_tab` |
| AI 助手入口 | `wealth_ai_assistant_entry` |

## module_name 词表

| module_name | 中文 |
|-------------|------|
| `page_top` / `top` | 页面上方 |
| `asset_card` | 资产卡片 |
| `portfolio_income` | 组合收益 |
| `portfolio_nav` | 组合净值表现 |
| `portfolio_performance` | 组合业绩表现 |
| `product_card` | 产品卡片 |
| `page_bottom` | 页面底部 |
| `page_popup` | 页面弹窗 |

## element_name 命名规则

| 后缀 | 场景 | 示例 |
|------|------|------|
| `_click` | 按钮、列表行 | `product_detail_click`, `transaction_click` |
| `_tab` | Tab 切换 | `cumulative_pnl_tab` |
| `_notice` | 说明图标 i | `dayincome_notice` |
| `_touchandhold` | 图表长按 | `nav_touchandhold` |

### 元素对照

| element_name | 中文 | module |
|--------------|------|--------|
| `back_to` | 返回上一页 | page_top |
| `product_detail_click` | 进入产品详情 | page_top |
| `transaction_click` | 交易记录 | asset_card |
| `dayincome_notice` | 日收益说明 | portfolio_income |
| `asset_increase_click` | 转入 | page_bottom |
| `asset_decrease_click` | 转出 | page_bottom |
| `submit` | 提交 | page_bottom |
| `confirm_to_submit` | 确认提交 | page_popup |
| `cancel` | 取消 | page_popup |

## 字段默认值

| 字段 | 默认 |
|------|------|
| *产品代码 | 空 |
| *备注 | 空 |
| **解释说明** | **空（不自动填写）** |
| 老埋点关联 eventId | 空 |
| 新增或修改日期 | 当天日期 |

## 事件名称（中文）列

填业务线级名称，如 `组合产品点击事件`，非「点击{页面名}」。

## Excel 列定义（15 列，无「前导页面」）

| 列 | 字段 | 浏览 | 点击 |
|----|------|:----:|:----:|
| A | 埋点分类 | ✓ | ✓ |
| B | 事件名称 | ✓ | ✓ |
| C | *事件英文名称 | ✓ | ✓ |
| D | 页面名称 | ✓ | ✓ |
| E | *页面英文名称 | ✓ | ✓ |
| F | 模块名称 | | ✓ |
| G | *模块英文名称 | | ✓ |
| H | 元素名称 | | ✓ |
| I | *元素英文名称 | | ✓ |
| J | *元素位置 | 可选 | 可选 |
| K | *产品代码 | ✓ | ✓ |
| L | *备注 | ✓ | ✓ |
| M | 解释说明 | ✓（默认空） | ✓（默认空） |
| N | 老埋点关联 eventId | 可选 | 可选 |
| O | 新增或修改日期 | 可选 | 可选 |

## Excel 格式

- 表头：橙色 `#ED7D31`，白字
- 同 event 的 B/C 列合并
- 排列：先浏览，后点击
- **不含曝光行、不含前导页面列**

## HTML → 埋点映射

| HTML 特征 | 类型 | 处理 |
|-----------|------|------|
| 页面加载 | 浏览 | 每页 1 条 |
| `<button>`、`.btn` | 点击 | `{语义}_click` |
| `.chart-tab` | 点击 | `{tab名}_tab` |
| `.info-icon` | 点击 | `{字段}_notice` |
| `.list-row` 带箭头 | 点击 | `{功能}_click` |
| `.nav-back` | 点击 | `back_to` |

## 暂不记录

- 曝光事件（`*_show`）
- 前导页面（`from_page`）
- 解释说明自动文案（除非用户明确要求填写）
