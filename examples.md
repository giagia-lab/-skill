# 示例：组合持仓详情页

源文件：`demo/portfolio-position-detail.html`（示例路径）

## 埋点确认单（阶段 1）

**业务线 / sheet**：组合产品  
**事件名策略**：`event_name` 来自**事件名称字典**（非 registry 细名）。

### 事件名称（重点核对）

| # | 逻辑页 | 事件归属 | 浏览事件 | view event | 点击事件 | click event | 曝光 |
|---|--------|----------|----------|------------|----------|-------------|------|
| 1 | 组合持仓详情 | 字典 `wealth_fund` | 理财基金浏览 | `wealth_fund_view` | 理财基金点击 | `wealth_fund_click` | — |

### 页面清单

| # | 页面名称（中文） | page_name | 是否新增（页） | view / click |
|---|-----------------|-----------|----------------|--------------|
| 1 | 组合持仓详情 | `wealth_portfolio_position_detail` | 新增 | `wealth_fund_*` |

用户回复 **「确认」** → Excel；再 **「Excel 确认」** → PRD/HTML。

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
      "view": { "name_cn": "理财基金浏览", "name_en": "wealth_fund_view" },
      "click": { "name_cn": "理财基金点击", "name_en": "wealth_fund_click" }
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
    "change_date": "2026-07-15"
  },
  "events": {
    "view": { "name_cn": "理财基金浏览", "name_en": "wealth_fund_view" },
    "click": { "name_cn": "理财基金点击", "name_en": "wealth_fund_click" }
  },
  "view_events": [{}],
  "click_events": [
    {"module_cn": "页面上方", "module_en": "page_top", "element_cn": "返回上一页", "element_en": "back_to"}
  ]
}
```

## 预期产出

- 阶段 2：浏览 1 · 点击 N → `demo/portfolio-position-detail-埋点.xlsx` + `tracking-spec.json`
- 阶段 3：PRD 内联表（顶格）+ 带 `data-track-*` 的原型 HTML
