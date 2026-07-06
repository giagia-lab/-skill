# 理财 App 埋点规范参考（轻量）

> 详细存量数据由团队本地 `tracking-registry.xlsx` 构建至 `registry/`，运行时通过脚本检索。

## 知识库检索

```bash
python3 scripts/lookup_registry.py --page "页面中文或英文"
python3 scripts/lookup_registry.py --sheet "业务线"
python3 scripts/lookup_registry.py --list-exposure-sheets
python3 scripts/lookup_element_names.py --suggest "按钮文案"
```

重建索引：将存量 Excel 存为 `tracking-registry.xlsx` 后执行 `python3 scripts/build_registry.py`

## 事件类型

| 类型 | 埋点分类 | 说明 |
|------|----------|------|
| 浏览 | `浏览事件` | 默认每页 1 条 |
| 点击 | `点击事件` | 默认必埋 |
| 曝光 | `曝光事件` | 少数业务线；须用户确认 |

## 命名约定

- `page_name`：前缀 `wealth_`，snake_case（团队可自定前缀，确认单锁定）
- `event_name`：按业务线 event 族
- `module_name`：`page_top`、`page_bottom`、`page_popup`、`asset_card` 等
- `element_name`：先查本地 `element_name.txt`；后缀 `_click` / `_tab` / `_notice`

## 业务线示例

| 业务线 | 浏览 | 点击 | sheet 名 |
|--------|------|------|----------|
| 理财首页 | `wealth_home_view` | `wealth_home_click` | 理财首页 |
| 组合产品 | `wealth_portfolio_view` | `wealth_portfolio_click` | 组合产品 |
| 组合持仓 | `wealth_portfolio_position_view` | `wealth_portfolio_position_click` | 组合产品 |
| AI 助手 | `wealth_ai_assistant_view` | `wealth_ai_assistant_click` | AI助手 |

## 确认单 vs 生成阶段

| 阶段 | 用户确认 | Agent 自动 |
|------|----------|------------|
| 确认单 | 业务线、各页 page/event（中英）、是否新增 | — |
| 生成 | — | 模块、元素命名 |

## 暂不自动填写

- 前导页面、解释说明（除非用户要求）
- 曝光事件（除非确认单已确认）
