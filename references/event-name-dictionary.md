# 事件名称字典（示例 · 可替换）

> **本 skill 中 `event_name`（英）的默认提案来源。**  
> 开源包内为**示例字典**。接入真实项目时，请用团队自有字典替换本文件，并同步更新 `scripts/lookup_event_names.py` 中的 `COMPANY_DICT`。  
>
> 用途：阶段 1 确认单确定归属业务 → 得到 `{前缀}` → 固定三件套  
> `{前缀}_view` / `{前缀}_click` / `{前缀}_show`。

## 硬约束（写死）

1. **确认单默认提案的 `event_name` 英文前缀，必须来自字典某一行**，不得用 registry 细粒度历史名作默认。  
2. 同一业务的 view/click/show **三件套复用**；具体页/按钮靠 `page_name` / `module_name` / `element_name` 区分。  
3. `page_name` 可以新；**`event_name` 不随新页面造词**。  
4. registry 仅用于：页面是否存量、`page_name` 复用、module/element 词表；**不作为 `event_name` 提案源**。  
5. 仅当用户在确认单中**明示改写**且标注「用户指定（非字典）」时，才允许字典外前缀。  
6. `wealth_home` vs `wealth_fund` 等歧义 → AskQuestion。

## 示例字典

| 业务 | event_name 前缀 | view / click / show | 条线（示例） |
|---|---|---|---|
| 首页 | `home` | home_view / home_click / home_show | 综合 |
| 交易 | `trade` | trade_view / trade_click / trade_show | 交易 |
| 行情 | `market` | market_view / market_click / market_show | 行情 |
| 资讯 | `info` | info_view / info_click / info_show | 资讯 |
| 自选 | `watchlist` | watchlist_view / watchlist_click / watchlist_show | 交易 |
| 系统基础 | `system` | system_view / system_click / system_show | 基础 |
| **理财** | `wealth_home` | wealth_home_view / wealth_home_click / wealth_home_show | **理财** |
| **理财基金** | `wealth_fund` | wealth_fund_view / wealth_fund_click / wealth_fund_show | **理财** |
| 开户 | `account` | account_view / account_click / account_show | 账户 |
| 营销活动 | `activity_page` | activity_page_view / activity_page_click / activity_page_show | 活动 |
| 广告组件 | `adsense` | adsense_view / adsense_click / adsense_show | 通用 |

## 本 skill（理财）默认映射

| 场景关键词 | 字典前缀 | 默认中文事件名（须含动作） |
|------------|----------|----------------------------|
| 理财商城首页、专区、泛理财入口 | `wealth_home` | 理财浏览 / 理财点击 / 理财曝光 |
| 公募/基金详情、购买申购、基金 FAQ/说明 H5 | `wealth_fund` | 理财基金浏览 / 理财基金点击 / 理财基金曝光 |

> 反例（**禁止作为默认提案**）：为每个页面拆 `*_detail_*` / `*_buy_*` / `*_faq_*` 细粒度前缀。  
> （历史 Excel 细名若需沿用，须用户在确认单明示「用户指定（非字典）」。）
