# 示例：组合持仓详情页

源文件：`demo/portfolio-position-detail.html`（示例路径）

## 埋点确认单（Step 0 示例）

**业务线 / sheet**：组合产品

| # | 页面名称（中文） | page_name | 是否新增 | 浏览事件 | view event | 点击事件 | click event | 曝光事件 | show event |
|---|-----------------|-----------|----------|----------|------------|----------|-------------|----------|------------|
| 1 | 组合持仓详情 | `wealth_portfolio_position_detail` | 新增 | 组合持仓浏览事件 | `wealth_portfolio_position_view` | 组合持仓点击事件 | `wealth_portfolio_position_click` | — | — |

> 用户回复「确认」后，Agent 再从 HTML 推导 module/element 并生成 Excel。

## spec 结构（内存组装，不交付 JSON）

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

浏览 1 · 点击 N → `demo/portfolio-position-detail-埋点.xlsx`
