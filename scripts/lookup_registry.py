#!/usr/bin/env python3
"""Lookup pages and sheets from registry indexes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REGISTRY_DIR = Path(__file__).resolve().parent.parent / "registry"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def score(text: str, query: str) -> int:
    t, q = text.lower(), query.lower()
    if t == q:
        return 100
    if q in t:
        return 70 - min(len(t) - len(q), 30)
    return 0


def search_pages(pages: dict, query: str, limit: int = 10) -> list[dict]:
    hits: list[tuple[int, dict]] = []
    for page_en, meta in pages.items():
        s = max(
            score(page_en, query),
            score(meta.get("page_cn", ""), query),
        )
        if s:
            hits.append((s, {"page_en": page_en, **meta}))
    hits.sort(key=lambda x: (-x[0], x[1]["page_en"]))
    return [{**m, "score": s} for s, m in hits[:limit]]


def search_sheets(sheets: dict, query: str, limit: int = 10) -> list[dict]:
    hits: list[tuple[int, dict]] = []
    for sheet_name, meta in sheets.items():
        s = max(
            score(sheet_name, query),
            score(meta.get("display_name", ""), query),
        )
        if s:
            hits.append((s, {"sheet_name": sheet_name, **meta}))
    hits.sort(key=lambda x: (-x[0], x[1]["sheet_name"]))
    return [{**m, "score": s} for s, m in hits[:limit]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup tracking registry")
    parser.add_argument("--registry", default=str(REGISTRY_DIR))
    parser.add_argument("--page", help="Lookup page by en/cn fuzzy match")
    parser.add_argument("--page-en", help="Exact page_en")
    parser.add_argument("--sheet", help="Lookup sheet by name fuzzy match")
    parser.add_argument("--list-exposure-sheets", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    reg = Path(args.registry)
    pages = load_json(reg / "pages-index.json")
    sheets = load_json(reg / "sheets-index.json")
    meta = load_json(reg / "meta.json")

    if not pages and not sheets:
        print(json.dumps({
            "error": "registry not built",
            "hint": "run scripts/build_registry.py first",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    result: dict = {"meta": meta}

    if args.list_exposure_sheets:
        result["exposure_sheets"] = [
            {"sheet_name": k, **v}
            for k, v in sheets.items() if v.get("has_exposure")
        ]
    elif args.page_en:
        hit = pages.get(args.page_en)
        result["page"] = hit or None
        result["found"] = bool(hit)
    elif args.page:
        result["pages"] = search_pages(pages, args.page, args.limit)
    elif args.sheet:
        result["sheets"] = search_sheets(sheets, args.sheet, args.limit)
    else:
        result["stats"] = meta
        result["sample_sheets"] = list(sheets.keys())[:8]

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
