#!/usr/bin/env python3
"""Search element_name.txt registry for existing element_name mappings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_REGISTRY = Path(__file__).resolve().parent.parent / "element_name.txt"


def load_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "," not in line:
                continue
            element_en, element_cn = line.split(",", 1)
            element_en = element_en.strip()
            element_cn = element_cn.strip()
            if not element_en:
                continue
            entries.append({
                "element_en": element_en,
                "element_cn": element_cn,
                "line": lineno,
            })
    return entries


def score_match(entry: dict[str, str], query: str, field: str) -> int:
    value = entry[field]
    q = query.lower()
    v = value.lower()
    if v == q:
        return 100
    if field == "element_cn" and q in value:
        return 80 - min(len(value) - len(query), 40)
    if field == "element_en" and v.startswith(q):
        return 70
    if field == "element_en" and q in v:
        return 50
    return 0


def search(
    entries: list[dict[str, str]],
    *,
    query: str | None = None,
    element_en: str | None = None,
    element_cn: str | None = None,
    limit: int = 20,
) -> list[dict[str, str]]:
    results: list[tuple[int, dict[str, str]]] = []

    if element_en:
        q = element_en.lower()
        for entry in entries:
            if entry["element_en"].lower() == q:
                results.append((100, entry))
            elif q in entry["element_en"].lower():
                results.append((60, entry))

    if element_cn:
        q = element_cn
        for entry in entries:
            score = score_match(entry, q, "element_cn")
            if score:
                results.append((score, entry))

    if query:
        q = query
        for entry in entries:
            cn_score = score_match(entry, q, "element_cn")
            en_score = score_match(entry, q, "element_en")
            score = max(cn_score, en_score)
            if score:
                results.append((score, entry))

    results.sort(key=lambda item: (-item[0], item[1]["element_en"]))
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for score, entry in results:
        if entry["element_en"] in seen:
            continue
        seen.add(entry["element_en"])
        deduped.append({**entry, "score": score})
        if len(deduped) >= limit:
            break
    return deduped


def suggest_for_interaction(entries: list[dict[str, str]], hint_cn: str, hint_html: str = "") -> list[dict[str, str]]:
    """Heuristic lookup for common HTML interaction patterns."""
    hints: list[str] = [hint_cn]
    html = hint_html.lower()
    combined = f"{hint_cn} {hint_html}"

    rules: list[tuple[str, list[str]]] = [
        (r"返回|back", ["返回上一页", "返回"]),
        (r"消息|message", ["消息", "消息提醒"]),
        (r"关闭|蒙层|遮罩|scrim|mask", ["关闭", "蒙层"]),
        (r"取消|稍后", ["取消", "稍后"]),
        (r"提交|确认", ["提交", "确认"]),
        (r"投顾|advisor|顾问", ["投顾", "问投顾"]),
        (r"报告|report|诊断", ["报告"]),
        (r"查看更多|more", ["查看更多"]),
        (r"tab|标签|分页|指示", ["tab"]),
        (r"企微|wechat", ["企微"]),
    ]

    for pattern, extra in rules:
        if re.search(pattern, combined, re.I):
            hints.extend(extra)

    merged: list[dict[str, str]] = []
    seen: set[str] = set()
    for hint in hints:
        for hit in search(entries, query=hint, limit=8):
            if hit["element_en"] in seen:
                continue
            seen.add(hit["element_en"])
            merged.append(hit)
    merged.sort(key=lambda item: (-item["score"], item["element_en"]))
    return merged[:15]


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup element_name mappings")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Path to element_name.txt")
    parser.add_argument("--query", "-q", help="Search CN or EN (fuzzy)")
    parser.add_argument("--en", help="Search element_en (exact or substring)")
    parser.add_argument("--cn", help="Search element_cn (fuzzy)")
    parser.add_argument("--suggest", help="Suggest names for a Chinese interaction label")
    parser.add_argument("--html-hint", default="", help="Optional HTML id/class/aria-label hint for --suggest")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--stats", action="store_true", help="Print registry stats")
    args = parser.parse_args()

    registry_path = Path(args.registry).resolve()
    if not registry_path.exists():
        print(f"Registry not found: {registry_path}", file=sys.stderr)
        sys.exit(1)

    entries = load_registry(registry_path)

    if args.stats:
        print(json.dumps({
            "path": str(registry_path),
            "count": len(entries),
            "sample": entries[:5],
        }, ensure_ascii=False, indent=2))
        return

    if args.suggest:
        hits = suggest_for_interaction(entries, args.suggest, args.html_hint)
    else:
        hits = search(
            entries,
            query=args.query,
            element_en=args.en,
            element_cn=args.cn,
            limit=args.limit,
        )

    print(json.dumps({
        "registry": str(registry_path),
        "query": args.suggest or args.query or args.en or args.cn,
        "count": len(hits),
        "hits": hits,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
