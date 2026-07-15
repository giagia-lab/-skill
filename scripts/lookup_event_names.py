#!/usr/bin/env python3
"""按事件名称字典建议 event_name 前缀（唯一提案源）。

registry 细粒度前缀不再作为 --suggest 默认结果。
默认附带示例字典；团队可替换 references/event-name-dictionary.md 与本表。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 示例字典（与 references/event-name-dictionary.md 表一致；可被团队本地替换）
COMPANY_DICT: dict[str, dict] = {
    "home": {"biz": "首页", "line": "综合", "cn": ("首页浏览", "首页点击", "首页曝光")},
    "trade": {"biz": "交易", "line": "交易", "cn": ("交易浏览", "交易点击", "交易曝光")},
    "market": {"biz": "行情", "line": "行情", "cn": ("行情浏览", "行情点击", "行情曝光")},
    "info": {"biz": "资讯", "line": "资讯", "cn": ("资讯浏览", "资讯点击", "资讯曝光")},
    "watchlist": {"biz": "自选", "line": "交易", "cn": ("自选浏览", "自选点击", "自选曝光")},
    "system": {"biz": "系统基础", "line": "基础", "cn": ("系统浏览", "系统点击", "系统曝光")},
    "wealth_home": {
        "biz": "理财",
        "line": "理财",
        "cn": ("理财浏览", "理财点击", "理财曝光"),
    },
    "wealth_fund": {
        "biz": "理财基金",
        "line": "理财",
        "cn": ("理财基金浏览", "理财基金点击", "理财基金曝光"),
    },
    "account": {"biz": "开户", "line": "账户", "cn": ("开户浏览", "开户点击", "开户曝光")},
    "activity_page": {
        "biz": "营销活动",
        "line": "活动",
        "cn": ("活动页浏览", "活动页点击", "活动页曝光"),
    },
    "adsense": {"biz": "广告组件", "line": "通用", "cn": ("广告浏览", "广告点击", "广告曝光")},
}

KEYWORD_HINTS: list[tuple[tuple[str, ...], str, int]] = [
    (("商城首页", "理财首页", "专区", "泛理财"), "wealth_home", 95),
    (("公募", "基金详情", "净值", "申购", "购买产品", "份额", "faq", "常见问题", "基金"), "wealth_fund", 95),
    (("理财",), "wealth_home", 60),
    (("开户", "实名"), "account", 90),
    (("行情", "k线", "盘口"), "market", 90),
    (("委托", "买卖", "交易"), "trade", 80),
    (("自选",), "watchlist", 85),
    (("资讯", "早报", "新闻"), "info", 85),
    (("活动", "抽奖", "邀请", "营销"), "activity_page", 85),
    (("广告", "banner", "adsense"), "adsense", 90),
]


def trio(prefix: str) -> dict[str, str]:
    return {
        "view": f"{prefix}_view",
        "click": f"{prefix}_click",
        "show": f"{prefix}_show",
    }


def cn_names(prefix: str) -> dict[str, str]:
    meta = COMPANY_DICT.get(prefix) or {}
    c = meta.get("cn") or ("浏览", "点击", "曝光")
    return {"view": c[0], "click": c[1], "show": c[2]}


def is_company_prefix(prefix: str) -> bool:
    return prefix in COMPANY_DICT


def suggest(query: str, limit: int = 5, finance_only: bool = False) -> list[dict]:
    q = (query or "").lower()
    scored: dict[str, int] = {}
    for kws, pref, base in KEYWORD_HINTS:
        if any(k.lower() in q for k in kws):
            scored[pref] = max(scored.get(pref, 0), base)
    for pref, meta in COMPANY_DICT.items():
        if finance_only and pref not in ("wealth_home", "wealth_fund"):
            continue
        s = 0
        if q and (q in pref or pref.replace("_", "") in q.replace("_", "").replace(" ", "")):
            s = 50
        if q and q in meta["biz"].lower():
            s = max(s, 70)
        if s:
            scored[pref] = max(scored.get(pref, 0), s)
    if not scored:
        if any(x in q for x in ("基金", "公募", "申购", "购买", "份额", "详情")):
            scored["wealth_fund"] = 50
        elif "理财" in q or "商城" in q:
            scored["wealth_home"] = 50
    ranked = sorted(scored.items(), key=lambda x: (-x[1], x[0]))
    out = []
    for pref, score in ranked[:limit]:
        meta = COMPANY_DICT[pref]
        out.append(
            {
                "prefix": pref,
                "score": score,
                "source": "event_name_dictionary",
                "biz": meta["biz"],
                "line": meta["line"],
                "events": trio(pref),
                "name_cn": cn_names(pref),
                "note": "确认单默认须用字典前缀；勿改用 registry 细粒度名",
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Event-name dictionary lookup")
    ap.add_argument("--suggest", help="按页面/需求关键词建议字典前缀")
    ap.add_argument("--prefix", help="查询某字典前缀详情")
    ap.add_argument("--list-dict", action="store_true", help="列出字典全部前缀")
    ap.add_argument("--finance-only", action="store_true", help="仅理财线 wealth_home/fund")
    ap.add_argument("--check-prefix", help="检查前缀是否在字典内（exit 1 if not）")
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()

    if args.check_prefix:
        p = args.check_prefix
        for suf in ("_view", "_click", "_show"):
            if p.endswith(suf):
                p = p[: -len(suf)]
                break
        ok = is_company_prefix(p)
        print(json.dumps({"prefix": p, "in_dictionary": ok}, ensure_ascii=False, indent=2))
        return 0 if ok else 1

    if args.prefix:
        if args.prefix not in COMPANY_DICT:
            print(
                json.dumps(
                    {
                        "error": "not_in_dictionary",
                        "query": args.prefix,
                        "hint": "默认提案禁止使用字典外前缀；见 --list-dict",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 1
        meta = COMPANY_DICT[args.prefix]
        print(
            json.dumps(
                {
                    "prefix": args.prefix,
                    "biz": meta["biz"],
                    "line": meta["line"],
                    "events": trio(args.prefix),
                    "name_cn": cn_names(args.prefix),
                    "source": "event_name_dictionary",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.suggest:
        hits = suggest(args.suggest, limit=args.limit, finance_only=args.finance_only)
        print(
            json.dumps(
                {
                    "query": args.suggest,
                    "policy": "dictionary_only",
                    "suggestions": hits,
                    "ambiguous_finance": ["wealth_home", "wealth_fund"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.list_dict:
        rows = []
        for pref, meta in COMPANY_DICT.items():
            if args.finance_only and pref not in ("wealth_home", "wealth_fund"):
                continue
            rows.append(
                {
                    "prefix": pref,
                    "biz": meta["biz"],
                    "line": meta["line"],
                    "view": f"{pref}_view",
                    "click": f"{pref}_click",
                    "view_cn": cn_names(pref)["view"],
                    "click_cn": cn_names(pref)["click"],
                }
            )
        print(
            json.dumps(
                {"source": "event_name_dictionary", "count": len(rows), "prefixes": rows},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
