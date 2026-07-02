# 示例：组合持仓详情页

源文件：`examples/sample-portfolio-detail.html`（示例 HTML，需自备）

## 锚点确认单（Step 0 示例）

| 字段 | 推断值 | 置信度 | 依据 |
|------|--------|--------|------|
| 业务线 / sheet | 组合产品 | 中 | 标题含「持仓」「组合」 |
| 页面中文名 | 组合持仓详情 | 高 | nav-title |
| page_name | `wealth_portfolio_position_detail` | 中 | 新页面 |
| view / click | 组合产品族 | 中 | 复用存量 event_name |

## spec 结构（内存组装，不交付 JSON）

```json
{
  "page": {
    "name_cn": "组合持仓详情",
    "name_en": "wealth_portfolio_position_detail",
    "sheet_name": "组合产品",
    "product_code": "",
    "remarks": "",
    "change_date": "2026-06-26"
  },
  "events": {
    "view": {
      "name_cn": "组合持仓详情浏览事件",
      "name_en": "wealth_portfolio_position_view"
    },
    "click": {
      "name_cn": "组合持仓详情点击事件",
      "name_en": "wealth_portfolio_position_click"
    }
  },
  "view_events": [{}],
  "click_events": [
    {"module_cn": "页面上方", "module_en": "page_top", "element_cn": "返回上一页", "element_en": "back_to"},
    {"module_cn": "页面上方", "module_en": "page_top", "element_cn": "详情", "element_en": "product_detail_click"}
  ]
}
```

> `view_events` 每页 1 条空对象即可。  
> `click_events` 不写 `explanation` 字段 → Excel 解释说明列为空。

## 预期产出

| 类型 | 条数 |
|------|------|
| 浏览 | 1 |
| 点击 | 11 |
| 合计 | 12 |

**交付文件**：`sample-portfolio-detail-埋点.xlsx`（仅此一份，不输出 JSON）
