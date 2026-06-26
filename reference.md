# 理财线埋点规范参考

> 基于团队理财线埋点存量表提炼。冲突时以最新线上下线表为准。

## 业务线清单（AskQuestion 选项源）

| sheet 名 | 业务线 key | 默认备注标签 | HTML 推断线索 |
|----------|-----------|-------------|--------------|
| 理财首页基金投顾tab | `finance_home` | — | 首页、Tab、推荐组合列表 |
| 管理型组合 | `portfolio_managed` | — | 管理型组合、组合详情、持仓详情 |
| 基金投顾满意度回访 | `satisfaction` | — | 问卷、满意度、回访 |
| 目标盈 | `target_profit` | — | 目标盈、止盈、运作周期 |
| 高端理财 | `high_end` | — | 高端、私募、信托 |
| 组合发车 | `portfolio_departure` | — | 发车、跟车 |
| AI投顾 | `ai_advisory` | — | AI 投顾、智能持仓分析 |

**置信度推断规则：**

| 线索 | 置信度 |
|------|--------|
| 用户指令写明业务线 | 高 |
| 标题/文案仅命中一条业务线关键词 | 中 |
| 命中多条业务线，或无任何特征 | 低 → 必须 AskQuestion |
| page_name 在下方存量表有完全匹配 | 高 |

## event_name 族（核心）

**同一业务线内**，浏览/曝光/点击各有独立 event_name，靠 `page_name` + `module_name` + `element_name` 区分页面与元素。

| 后缀 | 类型 | 示例 |
|------|------|------|
| `_view` | 浏览 | `finance_portfolio_managed_view` |
| `_show` | 曝光 | `finance_home_show` |
| `_click` | 点击 | `finance_portfolio_managed_asset_click` |

### 存量 event_name 示例

| 事件名称（中文） | event_name | 适用范围 |
|-----------------|------------|----------|
| 管理型组合浏览事件 | `finance_portfolio_managed_view` | 管理型组合多页面共用 |
| 管理型组合点击事件 | `finance_portfolio_managed_click` | 组合详情等 |
| 管理型组合资产总览点击事件 | `finance_portfolio_managed_asset_click` | 持仓详情页 |
| 理财底端页曝光 | `finance_home_show` | 底部转入等曝光 |
| 理财商城浏览 | `finance_home_view` | 理财首页 |
| 理财商城点击 | `finance_home_click` | 理财首页 |
| 问卷详情浏览 | `finance_portfolio_satisfaction_questionnaire_detail_view` | 页面级独立 view |
| 问卷详情点击 | `finance_portfolio_satisfaction_questionnaire_detail_click` | 问卷页点击 |
| 目标盈持仓浏览 | `finance_portfolio_target_profit_asset_view` | 目标盈持仓页 |
| 目标盈曝光 | `finance_portfolio_target_profit_show` | 目标盈模块曝光 |
| 目标盈持仓点击 | `finance_portfolio_target_profit_asset_click` | 目标盈持仓页点击 |

### 新页面如何定 event_name

1. 找到存量文档中**同业务线 sheet**（如「管理型组合」「目标盈」）
2. 若该 sheet 已有 view/click/show 族 → **复用**，不新建
3. 若是全新业务线 → `{finance_}{业务域}_{子域}_{view|show|click}`
4. 特殊单页（如问卷）→ 可用 `page_name_view` 作为 event_name

## page_name

- 前缀 `finance_`，snake_case
- 模式：`finance_{产品域}_{页面特征}_{detail|list|tab}`

| 页面 | page_name |
|------|-----------|
| 管理型组合详情页 | `finance_portfolio_managed_detail` |
| 管理型组合持仓详情页 | `finance_portfolio_managed_asset_detail` |
| 组合替换基金 | `components_substitution` |
| 问卷详情 | `finance_portfolio_satisfaction_questionnaire_detail` |
| 理财首页基金投顾 Tab | `home_portfolio_tab` |
| 目标盈止盈T日持仓详情 | `finance_portfolio_target_profit_tp_t_asset_detail` |

## from_page（前导页面，独立列）

| from_page | 含义 |
|-----------|------|
| `home_portfolio_tab` | 理财首页基金投顾 Tab |
| `finance_portfolio_managed_detail` | 管理型组合详情 |
| `finance_portfolio_managed_asset_detail` | 持仓详情（子页互跳） |
| `finance_portfolio_position_list` | 持仓列表 |

## module_name 存量词表

| module_name | 中文 | 典型元素 |
|-------------|------|----------|
| `page_top` | 页面上方 | 返回、分享 |
| `top` | 页面上方 | 同上（管理型组合用法） |
| `asset_card` | 资产卡片 | 持仓资产、说明 |
| `portfolio_income` | 组合收益 | 日收益、持有收益 |
| `portfolio_nav` | 组合净值表现 | 净值图、长按、阶段 |
| `portfolio_performance` | 组合业绩表现 | 业绩 Tab、基准公式 |
| `product_card` | 产品卡片 | 运作状态、时间轴 |
| `page_bottom` | 页面底部 | 转入转出 |
| `bottom` | 页面底部 | 曝光场景 |
| `page_popup` | 页面弹窗 | 确认/取消 |

## element_name 命名规则

### 后缀（强制）

| 后缀 | 场景 | 示例 |
|------|------|------|
| `_click` | 按钮、列表行、可点区域 | `product_detail_click`, `transaction_click` |
| `_tab` | Tab 切换 | `income_tab`, `cumulative_pnl_tab` |
| `_notice` | 说明图标 i | `yield_notice`, `dayincome_notice` |
| `_touchandhold` | 图表长按 | `nav_touchandhold`, `income_touchandhold` |
| `_popup` | 弹窗内按钮 | `confirm_popup` |

### 存量元素对照

| element_name | 中文 | module |
|--------------|------|--------|
| `back_to` | 返回上一页 | page_top |
| `product_detail_click` | 进入产品详情 | top / asset_card |
| `portfolio_share` | 组合分享 | top |
| `transaction_click` | 交易记录 | asset_card / function |
| `dayincome_click` | 查看日收益 | portfolio_income |
| `dayincome_notice` | 日收益说明 | portfolio_income |
| `asset_increase_click` | 转入 | page_bottom |
| `asset_decrease_click` | 转出 | page_bottom |
| `bottom_asset_increase` | 底部转入曝光 | bottom |
| `benchmark_formula_click` | 业绩基准公式 | portfolio_performance |
| `more_period` | 更多阶段 | portfolio_nav |
| `nav_touchandhold` | 长按净值走势图 | portfolio_nav |
| `submit` | 提交 | page_bottom |
| `confirm_to_submit` | 确认提交 | page_popup |
| `cancel` | 取消/再看看 | page_popup |

## 曝光事件

- event_name 用 `*_show`，不用 `*_exposure`
- 曝光行也填 module + element（元素可为底部按钮、卡片等）
- 示例：`finance_home_show` + `bottom` + `bottom_asset_increase`

## 产品代码与备注

| 字段 | 默认 | 说明 |
|------|------|------|
| 产品代码 | **空** | Excel 首行仍保留「*产品代码」列标题；仅在用户确认单中指定时填写 |
| 备注 | **空** | Excel 首行仍保留「*备注」列标题；仅在用户确认单中指定时填写 |
| 元素位置 | 空或序号 | `(1)`, `(2)`, `{0}/{1}/{2}/{3}` |

## 事件名称（中文）列

填**业务线级名称**，非「浏览{页面名}」：

- ✅ `管理型组合点击事件`
- ✅ `管理型组合资产总览点击事件`
- ❌ `点击管理型组合持仓详情页`

## Excel 列定义（16 列）

| 列 | 字段 | 浏览 | 曝光 | 点击 |
|----|------|:----:|:----:|:----:|
| A | 埋点分类 | ✓ | ✓ | ✓ |
| B | 事件名称 | ✓ | ✓ | ✓ |
| C | *事件英文名称 | ✓ | ✓ | ✓ |
| D | 页面名称 | ✓ | ✓ | ✓ |
| E | *页面英文名称 | ✓ | ✓ | ✓ |
| F | *前导页面 | ✓ | | |
| G | 模块名称 | | ✓ | ✓ |
| H | *模块英文名称 | | ✓ | ✓ |
| I | 元素名称 | | ✓ | ✓ |
| J | *元素英文名称 | | ✓ | ✓ |
| K | *元素位置 | | 可选 | 可选 |
| L | *产品代码 | ✓ | ✓ | ✓ |
| M | *备注 | ✓ | ✓ | ✓ |
| N | 解释说明 | ✓ | ✓ | ✓ |
| O | 老埋点关联 eventId | 可选 | 可选 | 可选 |
| P | 新增或修改日期 | 可选 | 可选 | 可选 |

## Excel 格式

- 表头：橙色底 `#ED7D31`，白字
- 同 section 的「事件名称」「*事件英文名称」合并单元格
- 浏览 / 曝光 / 点击 分块排列（先浏览、再曝光、再点击）
- 含「新增或修改日期」列，新埋点填当天日期

## HTML → 埋点映射

| HTML 特征 | 类型 | 处理 |
|-----------|------|------|
| 页面加载 | 浏览 | 按入口列 from_page |
| `.card` 首屏以下 | 曝光 | module + `_show` 元素 |
| `.bottom-bar` | 曝光+点击 | 曝光整条；按钮各 `_click` |
| `<button>` | 点击 | `{文案语义}_click` |
| `.chart-tab` | 点击 | `{tab名}_tab` + location |
| `.info-icon` | 点击 | `{字段}_notice` |
| `.list-row` 带箭头 | 点击 | `{功能}_click` |
| `.nav-back` | 点击 | `back_to` 或 `back_click` |
| 图表长按（若有） | 点击 | `{图类型}_touchandhold` |

## 与旧版 skill 差异（校正项）

| 旧（错误） | 新（存量规范） |
|-----------|---------------|
| `finance_home_exposure` | `finance_home_show` |
| 全站 `finance_home_view/click` | 按业务线分族 |
| `from_page` 写备注 | 独立列 |
| 默认填产品代码/备注 | 产品代码、备注列**默认为空** |
| `back`, `trade_record` | `back_to`, `transaction_click` |
| `_tip` 后缀 | `_notice` 后缀 |
| 点击元素无后缀 | 必须 `_click`/`_tab` 等 |
