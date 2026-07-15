# 理财 App 埋点规范参考（轻量）

> 详细存量数据由团队本地 `tracking-registry.xlsx` 构建至 `registry/`，运行时通过脚本检索，**勿将整表写入对话**。

## 知识库检索

```bash
python3 scripts/lookup_registry.py --page "页面中文或英文"
python3 scripts/lookup_registry.py --sheet "业务线"
python3 scripts/lookup_registry.py --list-exposure-sheets
python3 scripts/lookup_event_names.py --suggest "基金详情"
python3 scripts/lookup_event_names.py --list-dict
python3 scripts/lookup_element_names.py --suggest "按钮文案"
```

重建索引：将存量 Excel 存为 `tracking-registry.xlsx` 后执行 `python3 scripts/build_registry.py`

事件名归属示例字典：[references/event-name-dictionary.md](references/event-name-dictionary.md)

## 事件类型

| 类型 | 埋点分类 | 说明 |
|------|----------|------|
| 浏览 | `浏览事件` | 默认每页 1 条 |
| 点击 | `点击事件` | 默认必埋 |
| 曝光 | `曝光事件` | 少数业务线；须用户确认场景与事件名 |

## 命名约定

- `page_name`：前缀 `wealth_`，snake_case；**页面可新增**（查 registry 复用存量页）；团队可自定前缀，确认单锁定
- `event_name`（英）：**默认来源 = 事件名称字典** + `_view` / `_click` / `_show`
  - 理财线示例：`wealth_home_*` 或 `wealth_fund_*`
  - **禁止**默认使用 registry 细名
  - 多页共用同一前缀，靠 page / module / element 区分
- `event_name`（中）：须含动作词；字典默认如「理财基金浏览 / 理财基金点击」
- `module_name` / `element_name`：registry + `element_name.txt`（元素允许新增）

## 字段默认

| 字段 | 默认 |
|------|------|
| *产品代码 / *备注 / 解释说明 | 空 |
| 老埋点关联 eventId | 空 |
| 新增或修改日期 | 当天 |

## Excel 列（15 列，无「前导页面」）

表头为中文主标题 + 英文 field key 副标题（换行）：

| 列 | 表头（单元格内换行） |
|----|---------------------|
| A | 埋点分类 |
| B | 事件名称 |
| C | *事件英文名称<br>event_name |
| D | 页面名称 |
| E | *页面英文名称<br>page_name |
| F | 模块名称 |
| G | *模块英文名称<br>module_name |
| H | 元素名称 |
| I | *元素英文名称<br>element_name |
| J | *元素位置<br>location |
| K | *产品代码<br>product_code |
| L | *备注<br>remarks |
| M | 解释说明 |
| N | 老埋点关联<br>eventId |
| O | 新增或修改日期 |

格式：橙色表头 `#ED7D31`；同 event 的 B/C 列合并；先浏览、后点击、再曝光。

## HTML → 埋点

| HTML 特征 | 处理 |
|-----------|------|
| 页面加载 | 浏览 1 条 |
| `<button>`、可点击列表行 | 点击，`{语义}_click` |
| Tab | `{名}_tab` |
| 说明 i 图标 | `{字段}_notice` |
| 返回 | 优先 `back_to` |

## 确认单 vs 生成阶段

| 阶段 | 用户确认 | Agent 自动 |
|------|----------|------------|
| **埋点确认单** | 业务线、page_name、是否新增页；**事件归属与浏览/点击/曝光中英**（专节前置）；歧义 AskQuestion；回复「确认」 | 检索 registry / 字典并建议已有前缀（不自造） |
| 生成（阶段 2） | — | 模块/元素命名；**不得改写确认单已确认事件前缀** |

不另开《事件名称确认单》门禁；事件名与页面同单确认。

## 暂不自动填写

- 前导页面（`from_page`）
- 解释说明（除非用户明确要求）
- 曝光事件（除非确认单已确认）

---

## PRD 内联埋点表格

横向 5 列：**event_name · page_name · module_name · element_name · anchor**；纵向 2 行：**中文 / 英文**。

不展示：埋点分类、元素位置、track_id、埋点编号表内重复字段（编号仅保留在标题 `埋点映射（F02-IX01）`）。

**排版硬约束（写死）**：TRACKING 注释、`**埋点映射**`、表的每一行必须**顶格**（行首无空格/Tab）。由 `prd_tracking_table.py` 强制；禁止 build 脚本再缩进。否则 GFM Preview 表格会消失。

### 点击事件

**格式硬约束：一句功能描述 + 一张埋点表（一一对应）；表顶格。**

```markdown
- 用户点击「了解详情」后，当前页面蒙层展示弹窗。
<!-- TRACKING:F02-IX01:BEGIN -->
**埋点映射（F02-IX01）**

| | event_name | page_name | module_name | element_name | anchor |
| --- | --- | --- | --- | --- | --- |
| 中文 | 理财基金点击 | 组合产品详情页 | 产品信息 | 了解详情 | — |
| 英文 | `wealth_fund_click` | `wealth_portfolio_detail` | `product_info` | `learn_detail_click` | `[data-ann="learn-more"]` |
<!-- TRACKING:F02-IX01:END -->
```

- **表格必须顶格**：勿给表加缩进。
- **锚点**：写在英文行；中文行填 `—`。
- **状态结果句**：不插表。
- **浏览事件**：只对逻辑页面有效；放在功能节标题下、`#### 业务描述` 之前；模块、元素填 `—`。

### 浏览事件

```markdown
### 6.2 功能 F02:…

<!-- TRACKING:F02-V01:BEGIN -->
**埋点映射（F02-V01）**

| | event_name | page_name | module_name | element_name | anchor |
| --- | --- | --- | --- | --- | --- |
| 中文 | 理财基金浏览 | 组合产品详情页 | — | — | — |
| 英文 | `wealth_fund_view` | `wealth_portfolio_detail` | — | — | `section.screen` |
<!-- TRACKING:F02-V01:END -->

#### 业务描述
```

每逻辑页至多 1 条 view。

### 字段来源（tracking-spec.json）

| 列 | 中文行 field | 英文行 field |
|----|--------------|--------------|
| event_name | `events.*.name_cn` | `events.*.name_en` |
| page_name | `page.name_cn` | `page.name_en` |
| module_name | `click_events[].module_cn` | `click_events[].module_en` |
| element_name | `click_events[].element_cn` | `click_events[].element_en` |
| anchor | — | `anchor.selector` |

### 附录总表

单行 per IX，单元格内 `中文 / \`英文\``；锚点仅一列。由 `scripts/prd_tracking_table.py` 的 `build_summary_table()` 生成。

### HTML 锚点属性

| 属性 | 说明 |
|------|------|
| `data-track-id` | track_id（不进 PRD 表） |
| `data-track-type` | `view` / `click` |
| `data-track-event` | event_name_en |
| `data-track-ix` | 与 PRD interaction_id 一致 |

由 `scripts/inject_html_tracking.py` 根据 `anchor.selector` 注入。
