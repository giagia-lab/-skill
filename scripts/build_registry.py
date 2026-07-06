#!/usr/bin/env python3
"""Build compact registry indexes from local tracking-registry.xlsx."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from _xlsx_read import read_workbook  # noqa: E402

DEFAULT_XLSX = SCRIPT_DIR.parent / "tracking-registry.xlsx"
DEFAULT_OUT = SCRIPT_DIR.parent / "registry"

SKIP_SHEETS = {"目录", "！埋点规范", "预置属性", "工作表1"}

HEADER_ALIASES = {
    "category": ("埋点分类",),
    "event_cn": ("事件名称",),
    "event_en": ("事件英文名称", "event_name"),
    "page_cn": ("页面名称",),
    "page_en": ("页面英文名称", "page_name"),
    "module_cn": ("模块名称",),
    "module_en": ("模块英文名称", "module_name"),
    "element_cn": ("元素名称",),
    "element_en": ("元素英文名称", "element_name"),
}

CATEGORY_KIND = {
    "view": ("浏览",),
    "click": ("点击",),
    "show": ("曝光",),
}


def norm_header(value: str) -> str:
    return re.sub(r"\s+", "", str(value).replace("*", "").replace("\n", ""))


def is_header_row(row: list[str]) -> bool:
    joined = " ".join(norm_header(c) for c in row)
    return "埋点分类" in joined and "事件名称" in joined


def map_header(row: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, cell in enumerate(row):
        n = norm_header(cell)
        if not n:
            continue
        for key, aliases in HEADER_ALIASES.items():
            for alias in aliases:
                if alias.replace("\n", "") in n or n in alias.replace("\n", ""):
                    mapping.setdefault(key, idx)
    return mapping


def pick_category(raw: str) -> str | None:
    text = raw.replace("埋点", "")
    for kind, keys in CATEGORY_KIND.items():
        if any(k in text for k in keys):
            return kind
    return None


def clean_sheet_name(name: str) -> str:
    return re.sub(r"^[👀✅❌!！\s]+", "", name).strip()


def get_cell(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return str(row[idx]).strip()


def parse_sheet(sheet_name: str, rows: list[list[str]]) -> tuple[list[dict], dict]:
    entries: list[dict] = []
    pages_meta: dict[str, dict] = {}
    header_map: dict[str, int] = {}
    state = {
        "category": "",
        "event_cn": "",
        "event_en": "",
        "page_cn": "",
        "page_en": "",
        "module_cn": "",
        "module_en": "",
    }

    for row in rows:
        if is_header_row(row):
            header_map = map_header(row)
            continue

        if not header_map:
            continue

        def g(key: str) -> str:
            return get_cell(row, header_map.get(key))

        cat_raw = g("category")
        if cat_raw:
            kind = pick_category(cat_raw)
            if kind:
                state["category"] = kind

        for key in ("event_cn", "event_en", "page_cn", "page_en", "module_cn", "module_en"):
            val = g(key)
            if val:
                state[key] = val

        page_en = state["page_en"]
        if not page_en:
            continue

        entry = {
            "sheet_name": sheet_name,
            "category": state["category"],
            "event_cn": state["event_cn"],
            "event_en": state["event_en"],
            "page_cn": state["page_cn"],
            "page_en": page_en,
            "module_cn": state["module_cn"],
            "module_en": state["module_en"],
            "element_cn": g("element_cn"),
            "element_en": g("element_en"),
        }
        entries.append(entry)

        meta = pages_meta.setdefault(page_en, {
            "page_cn": state["page_cn"],
            "page_en": page_en,
            "sheets": {sheet_name},
            "events": {},
            "modules": {},
            "has_exposure": False,
        })
        if state["page_cn"]:
            meta["page_cn"] = state["page_cn"]
        meta["sheets"].add(sheet_name)

        if state["category"] and state["event_en"]:
            meta["events"].setdefault(state["category"], {
                "name_cn": state["event_cn"],
                "name_en": state["event_en"],
            })
            if state["category"] == "show":
                meta["has_exposure"] = True

        if state["module_en"] or state["module_cn"]:
            mod_key = state["module_en"] or state["module_cn"]
            mod = meta["modules"].setdefault(mod_key, {
                "module_cn": state["module_cn"],
                "module_en": state["module_en"],
                "elements": [],
            })
            if state["module_cn"]:
                mod["module_cn"] = state["module_cn"]
            if state["module_en"]:
                mod["module_en"] = state["module_en"]
            if entry["element_en"] or entry["element_cn"]:
                el = {
                    "element_cn": entry["element_cn"],
                    "element_en": entry["element_en"],
                }
                if el not in mod["elements"]:
                    mod["elements"].append(el)

    return entries, pages_meta


def merge_pages(all_pages: dict[str, dict], sheet_pages: dict[str, dict]) -> None:
    for page_en, meta in sheet_pages.items():
        if page_en not in all_pages:
            all_pages[page_en] = meta
            continue
        dst = all_pages[page_en]
        dst["sheets"] |= meta["sheets"]
        dst["has_exposure"] = dst.get("has_exposure", False) or meta.get("has_exposure", False)
        if meta.get("page_cn"):
            dst["page_cn"] = meta["page_cn"]
        for kind, ev in meta.get("events", {}).items():
            dst.setdefault("events", {}).setdefault(kind, ev)
        for mod_key, mod in meta.get("modules", {}).items():
            dst_mod = dst.setdefault("modules", {}).setdefault(mod_key, {
                "module_cn": mod.get("module_cn", ""),
                "module_en": mod.get("module_en", ""),
                "elements": [],
            })
            seen = {(e.get("element_en"), e.get("element_cn")) for e in dst_mod["elements"]}
            for el in mod.get("elements", []):
                key = (el.get("element_en"), el.get("element_cn"))
                if key not in seen and (el.get("element_en") or el.get("element_cn")):
                    dst_mod["elements"].append(el)
                    seen.add(key)


def build_sheets_index(all_entries: list[dict], all_pages: dict[str, dict]) -> dict:
    sheets: dict[str, dict] = {}
    for entry in all_entries:
        sheet = entry["sheet_name"]
        s = sheets.setdefault(sheet, {
            "sheet_name": sheet,
            "display_name": clean_sheet_name(sheet),
            "has_exposure": False,
            "event_families": {},
            "pages": set(),
            "entry_count": 0,
        })
        s["entry_count"] += 1
        if entry.get("page_en"):
            s["pages"].add(entry["page_en"])
        if entry.get("category") == "show":
            s["has_exposure"] = True
        if entry.get("category") and entry.get("event_en"):
            s["event_families"].setdefault(entry["category"], {
                "name_cn": entry["event_cn"],
                "name_en": entry["event_en"],
            })

    for page_en, meta in all_pages.items():
        for sheet in meta["sheets"]:
            if sheet in sheets and meta.get("has_exposure"):
                sheets[sheet]["has_exposure"] = True

    result = {}
    for sheet, data in sorted(sheets.items(), key=lambda x: x[0]):
        result[sheet] = {
            **data,
            "pages": sorted(data["pages"]),
            "page_count": len(data["pages"]),
        }
    return result


def serialize_pages(all_pages: dict[str, dict]) -> dict:
    out = {}
    for page_en, meta in sorted(all_pages.items()):
        out[page_en] = {
            "page_cn": meta.get("page_cn", ""),
            "page_en": page_en,
            "sheets": sorted(meta.get("sheets", [])),
            "has_exposure": meta.get("has_exposure", False),
            "events": meta.get("events", {}),
            "modules": meta.get("modules", {}),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build tracking registry indexes")
    parser.add_argument("--input", "-i", default=str(DEFAULT_XLSX))
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    workbook = read_workbook(input_path)
    all_entries: list[dict] = []
    all_pages: dict[str, dict] = {}

    for sheet_name, rows in workbook.items():
        if sheet_name in SKIP_SHEETS or not rows:
            continue
        entries, pages = parse_sheet(sheet_name, rows)
        if not entries:
            continue
        all_entries.extend(entries)
        merge_pages(all_pages, pages)

    sheets_index = build_sheets_index(all_entries, all_pages)
    pages_index = serialize_pages(all_pages)

    exposure_sheets = [k for k, v in sheets_index.items() if v.get("has_exposure")]

    meta = {
        "source": input_path.name,
        "built_at": date.today().isoformat(),
        "sheet_count": len(sheets_index),
        "page_count": len(pages_index),
        "entry_count": len(all_entries),
        "exposure_sheet_count": len(exposure_sheets),
    }

    (output_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "sheets-index.json").write_text(
        json.dumps(sheets_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "pages-index.json").write_text(
        json.dumps(pages_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps({
        **meta,
        "exposure_sheets": exposure_sheets,
        "output_dir": str(output_dir),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
