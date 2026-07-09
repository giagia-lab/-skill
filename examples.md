# 示例：组合持仓详情页

源文件：`demo/portfolio-position-detail.html`（示例路径）

## 埋点确认单（阶段 1 示例）

**业务线 / sheet**：组合产品

| # | 页面名称（中文） | page_name | 是否新增 | 浏览事件 | view event | 点击事件 | click event | 曝光事件 | show event |
|---|-----------------|-----------|----------|----------|------------|----------|-------------|----------|------------|
| 1 | 组合持仓详情 | `wealth_portfolio_position_detail` | 新增 | 组合持仓浏览事件 | `wealth_portfolio_position_view` | 组合持仓点击事件 | `wealth_portfolio_position_click` | — | — |

> 用户回复「确认」后，Agent 再从 HTML 推导 module/element，生成 Excel 与 `tracking-spec.json`。

## tracking-spec.json（阶段 2 机器契约，节选）

```json
{
  "pages": [{
    "page": {
      "name_cn": "组合持仓详情",
      "name_en": "wealth_portfolio_position_detail",
      "source_html": "portfolio-position-detail.html"
    },
    "events": {
      "view": { "name_cn": "组合持仓浏览事件", "name_en": "wealth_portfolio_position_view" },
      "click": { "name_cn": "组合持仓点击事件", "name_en": "wealth_portfolio_position_click" }
    },
    "view_events": [{
      "interaction_id": "F01-IX01",
      "track_id": "T001",
      "anchor": { "selector": "section.screen" }
    }],
    "click_events": [{
      "interaction_id": "F01-IX02",
      "track_id": "T002",
      "module_cn": "页面上方",
      "module_en": "page_top",
      "element_cn": "返回上一页",
      "element_en": "back_to",
      "anchor": { "selector": "[data-ann=\"back\"]" }
    }]
  }]
}
```

## Excel spec（generate_tracking_excel 输入，节选）

```json
{
  "page": {
    "name_cn": "组合持仓详情",
    "name_en": "wealth_portfolio_position_detail",
    "sheet_name": "组合产品",
    "change_date": "2026-07-06"
  },
  "events": {
    "view": { "name_cn": "组合持仓浏览事件", "name_en": "wealth_portfolio_position_view" },
    "click": { "name_cn": "组合持仓点击事件", "name_en": "wealth_portfolio_position_click" }
  },
  "view_events": [{}],
  "click_events": [
    {"module_cn": "页面上方", "module_en": "page_top", "element_cn": "返回上一页", "element_en": "back_to"}
  ]
}
```

## 预期产出

- 阶段 2：浏览 1 · 点击 N → `demo/portfolio-position-detail-埋点.xlsx` + `tracking-spec.json`
- 阶段 3：PRD 内联表 + 带 `data-track-*` 的原型 HTML
