#!/usr/bin/env python3
"""事件中文名必须体现动作：浏览 / 点击 / 曝光。

存量 registry 偶有缺动作（如 finance_buy_click →「购买产品页面」）。
确认单与 Excel / tracking-spec 写入前须 normalize。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ACTION_BY_TYPE = {
    "view": "浏览",
    "click": "点击",
    "show": "曝光",
}

# 任意一个即视为已含动作（兼容「浏览xxx」「xxx浏览」「xxx点击事件」）
ACTION_WORDS = ("浏览", "点击", "曝光")
ACTION_RE = re.compile("|".join(ACTION_WORDS))


def has_action(name_cn: str) -> bool:
    return bool(name_cn and ACTION_RE.search(name_cn))


def _short_base(name_cn: str) -> str:
    """页面语义短名：购买产品页面 → 购买产品页。"""
    s = (name_cn or "").strip()
    if not s:
        return s
    if s.endswith("页面"):
        return s[:-2] + "页"
    return s


def normalize_event_cn(name_cn: str, event_type: str) -> str:
    """缺动作词时补齐为「{短名}{动作}」；已含动作则原样返回。"""
    if not name_cn or name_cn in ("—", "-", "不适用"):
        return name_cn
    if event_type not in ACTION_BY_TYPE:
        raise ValueError(f"unknown event_type: {event_type}")
    if has_action(name_cn):
        return name_cn
    return f"{_short_base(name_cn)}{ACTION_BY_TYPE[event_type]}"


def suggest_from_page(page_cn: str, event_type: str) -> str:
    """新增页默认：{页面短名}浏览|点击|曝光。"""
    return f"{_short_base(page_cn)}{ACTION_BY_TYPE[event_type]}"


def validate_name(name_cn: str, event_type: str, name_en: str = "") -> list[str]:
    errs: list[str] = []
    if not name_cn or name_cn in ("—", "-"):
        return errs
    if not has_action(name_cn):
        errs.append(
            f"事件中文名缺少动作词（须含 浏览/点击/曝光）: 「{name_cn}」"
            f" → 建议「{normalize_event_cn(name_cn, event_type)}」"
        )
    expected = ACTION_BY_TYPE[event_type]
    # 中文动作与类型不一致（如 click 写成浏览）
    others = [a for a in ACTION_WORDS if a != expected]
    if expected not in name_cn and any(a in name_cn for a in others):
        errs.append(
            f"事件中文动作与类型不符: type={event_type} name_cn=「{name_cn}」（应含「{expected}」）"
        )
    if name_en:
        suffix = {"view": "_view", "click": "_click", "show": "_show"}[event_type]
        if suffix not in name_en.split("\n")[0]:
            errs.append(
                f"事件英文后缀与类型不符: type={event_type} name_en=`{name_en}`（应含 {suffix}）"
            )
    return errs


def normalize_events_dict(events: dict) -> tuple[dict, list[str]]:
    """Normalize events.view/click/show name_cn in place-like copy; return (new, changes)."""
    out = dict(events or {})
    changes: list[str] = []
    for et in ("view", "click", "show"):
        cfg = out.get(et)
        if not isinstance(cfg, dict):
            continue
        old = cfg.get("name_cn", "")
        new = normalize_event_cn(old, et)
        if new != old:
            changes.append(f"{et}: 「{old}」→「{new}」")
            cfg = dict(cfg)
            cfg["name_cn"] = new
            out[et] = cfg
    return out, changes


def check_spec(spec: dict) -> list[str]:
    errs: list[str] = []
    pages = spec.get("pages") or ([spec] if "page" in spec or "events" in spec else [])
    if "page" in spec and "pages" not in spec:
        pages = [spec]
    for page_spec in pages:
        events = page_spec.get("events") or {}
        page = page_spec.get("page") or {}
        label = page.get("name_en") or page.get("name_cn") or "?"
        for et in ("view", "click", "show"):
            cfg = events.get(et) or {}
            cn = cfg.get("name_cn", "")
            en = cfg.get("name_en", "")
            if not cn:
                continue
            for e in validate_name(cn, et, en):
                errs.append(f"[{label}] {e}")
        for key, et in (("view_events", "view"), ("click_events", "click"), ("show_events", "show")):
            for item in page_spec.get(key) or []:
                cn = item.get("event_name_cn") or ""
                en = item.get("event_name_en") or ""
                if not cn:
                    continue
                for e in validate_name(cn, et, en):
                    errs.append(f"[{label}/{item.get('interaction_id', '')}] {e}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description="校验/规范化事件中文名（须含浏览|点击|曝光）")
    ap.add_argument("--check", type=Path, help="检查 tracking-spec.json")
    ap.add_argument("--normalize", type=Path, help="规范化后写回 JSON")
    ap.add_argument("--fix-in-place", action="store_true", help="与 --normalize 联用，原地写回")
    args = ap.parse_args()
    if not args.check and not args.normalize:
        ap.print_help()
        return 2

    path = args.normalize or args.check
    spec = json.loads(path.read_text(encoding="utf-8"))

    if args.normalize:
        if "pages" in spec:
            all_changes = []
            for p in spec["pages"]:
                ev, ch = normalize_events_dict(p.get("events") or {})
                p["events"] = ev
                all_changes.extend(ch)
        else:
            ev, all_changes = normalize_events_dict(spec.get("events") or {})
            spec["events"] = ev
        out = path if args.fix_in_place else Path(str(path) + ".normalized.json")
        out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for c in all_changes:
            print(c)
        print(f"wrote {out}")

    errs = check_spec(json.loads(path.read_text(encoding="utf-8")) if args.check and not args.normalize else spec)
    if args.normalize and args.fix_in_place:
        errs = check_spec(spec)
    for e in errs:
        print(e, file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
