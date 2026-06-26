# 示例：目标盈止盈T日持仓详情

源文件：`examples/sample-portfolio-detail.html`（示例 HTML，需自备）

## 锚点确认单（Step 0 示例）

| 字段 | 推断值 | 置信度 | 依据 |
|------|--------|--------|------|
| 业务线 / sheet | 目标盈 | 中 | 标题含「目标盈」「止盈T日」 |
| 页面中文名 | 目标盈止盈T日持仓详情 | 高 | nav-title |
| page_name | `finance_portfolio_target_profit_tp_t_asset_detail` | 中 | 新页面 |
| view / show / click | 目标盈族（见下方 spec） | 中 | 复用目标盈 event_name |

→ 输出确认单，**等用户回复「确认」**后再生成 Excel（即使业务线已在指令中写明）。

## JSON 规格（对齐存量命名）

```json
{
  "page": {
    "name_cn": "目标盈止盈T日持仓详情",
    "name_en": "finance_portfolio_target_profit_tp_t_asset_detail",
    "sheet_name": "目标盈",
    "product_line": "目标盈",
    "product_code": "",
    "remarks": "",
    "change_date": "2026-06-26"
  },
  "events": {
    "view": {
      "name_cn": "目标盈持仓详情浏览事件",
      "name_en": "finance_portfolio_target_profit_asset_view"
    },
    "exposure": {
      "name_cn": "目标盈曝光事件",
      "name_en": "finance_portfolio_target_profit_show"
    },
    "click": {
      "name_cn": "目标盈持仓详情点击事件",
      "name_en": "finance_portfolio_target_profit_asset_click"
    }
  }
}
```

## 点击元素命名对照（旧 → 新）

| 旧 element | 新 element（存量规范） |
|-----------|----------------------|
| `back` | `back_to` |
| `portfolio_detail` | `product_detail_click` |
| `position_asset_tip` | `position_asset_notice` |
| `daily_pnl_tip` | `dayincome_notice` |
| `holding_pnl_tip` | `holding_income_notice` |
| `trade_record` | `transaction_click` |
| `cumulative_pnl_tab` | `cumulative_pnl_tab` |
| `asset_decrease` | `asset_decrease_click` |
| `asset_increase` | `asset_increase_click` |

## 模块对照

| 旧 module | 新 module |
|-----------|-----------|
| `top` | `page_top` |
| `asset` | `asset_card` + `portfolio_income` |
| `status` | `product_card` |
| `function` | `asset_card` |
| `chart` | `portfolio_performance` |
| `bottom` | `page_bottom` |

## 预期产出

| 类型 | 条数 |
|------|------|
| 浏览 | 3 |
| 曝光 | 6 |
| 点击 | 11 |
| 合计 | 20 |

**交付文件**：`sample-portfolio-detail-埋点.xlsx`（仅此一份，不输出 JSON）

> JSON 块仅为 spec 结构说明，生成时写入临时文件后即删除。
