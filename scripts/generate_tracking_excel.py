#!/usr/bin/env python3
"""Generate finance tracking spec Excel from JSON."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    print("Missing dependency: openpyxl. Install with: pip3 install openpyxl", file=sys.stderr)
    sys.exit(1)

COLUMNS = [
    "埋点分类",
    "事件名称",
    "*事件英文名称",
    "页面名称",
    "*页面英文名称",
    "*前导页面",
    "模块名称",
    "*模块英文名称",
    "元素名称",
    "*元素英文名称",
    "*元素位置",
    "*产品代码",
    "*备注",
    "解释说明",
    "老埋点关联 eventId",
    "新增或修改日期",
]

HEADER_FILL = PatternFill("solid", fgColor="ED7D31")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
BODY_ALIGN = Alignment(vertical="top", wrap_text=True)

COL_WIDTHS = [10, 26, 36, 26, 36, 28, 14, 20, 20, 28, 12, 14, 22, 40, 18, 16]

CATEGORY = {"view": "浏览事件", "exposure": "曝光事件", "click": "点击事件"}


def load_spec(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_events_config(spec: dict) -> dict:
    """Support both new `events` block and legacy flat page fields."""
    page = spec["page"]
    events = spec.get("events", {})
    return {
        "view": events.get("view", {
            "name_cn": page.get("view_event_cn", f"{page.get('product_line', '')}浏览事件".strip()),
            "name_en": page.get("view_event_en", "finance_home_view"),
        }),
        "exposure": events.get("exposure", {
            "name_cn": page.get("exposure_event_cn", f"{page.get('product_line', '')}曝光事件".strip()),
            "name_en": page.get("exposure_event_en", "finance_home_show"),
        }),
        "click": events.get("click", {
            "name_cn": page.get("click_event_cn", f"{page.get('product_line', '')}点击事件".strip()),
            "name_en": page.get("click_event_en", "finance_home_click"),
        }),
    }


def build_rows(spec: dict) -> list[list]:
    page = spec["page"]
    page_cn = page["name_cn"]
    page_en = page["name_en"]
    product_code = page.get("product_code", "")
    page_remarks = page.get("remarks", "")
    default_date = page.get("change_date", date.today().isoformat())
    events_cfg = get_events_config(spec)

    rows: list[list] = []

    def remarks(*parts: str) -> str:
        return " | ".join(p for p in parts if p)

    for item in spec.get("view_events", []):
        rows.append([
            CATEGORY["view"],
            item.get("event_name_cn") or events_cfg["view"]["name_cn"],
            item.get("event_name_en") or events_cfg["view"]["name_en"],
            page_cn,
            page_en,
            item.get("from_page", ""),
            "", "", "", "",
            item.get("location", ""),
            product_code,
            remarks(page_remarks, item.get("remarks", "")),
            item.get("explanation", ""),
            item.get("legacy_event_id", ""),
            item.get("change_date", default_date),
        ])

    for item in spec.get("exposure_events", []):
        rows.append([
            CATEGORY["exposure"],
            item.get("event_name_cn") or events_cfg["exposure"]["name_cn"],
            item.get("event_name_en") or events_cfg["exposure"]["name_en"],
            page_cn,
            page_en,
            "",
            item.get("module_cn", ""),
            item.get("module_en", ""),
            item.get("element_cn", ""),
            item.get("element_en", ""),
            item.get("location", ""),
            product_code,
            remarks(page_remarks, item.get("remarks", "")),
            item.get("explanation", ""),
            item.get("legacy_event_id", ""),
            item.get("change_date", default_date),
        ])

    for item in spec.get("click_events", []):
        rows.append([
            CATEGORY["click"],
            item.get("event_name_cn") or events_cfg["click"]["name_cn"],
            item.get("event_name_en") or events_cfg["click"]["name_en"],
            page_cn,
            page_en,
            "",
            item.get("module_cn", ""),
            item.get("module_en", ""),
            item.get("element_cn", ""),
            item.get("element_en", ""),
            item.get("location", ""),
            product_code,
            remarks(page_remarks, item.get("remarks", "")),
            item.get("explanation", ""),
            item.get("legacy_event_id", ""),
            item.get("change_date", default_date),
        ])

    return rows


def merge_event_columns(ws, rows: list[list]) -> None:
    """Merge 事件名称 & *事件英文名称 when consecutive rows share same values."""
    merge_cols = (2, 3)  # B, C
    n = len(rows)
    if n == 0:
        return
    start = 2
    for i in range(1, n):
        curr_row = 2 + i
        prev_vals = tuple(rows[i - 1][c - 1] for c in merge_cols)
        curr_vals = tuple(rows[i][c - 1] for c in merge_cols)
        if curr_vals != prev_vals:
            end = 2 + i - 1
            for col in merge_cols:
                if end > start:
                    ws.merge_cells(start_row=start, start_column=col, end_row=end, end_column=col)
            start = curr_row
    end = 2 + n - 1
    for col in merge_cols:
        if end > start:
            ws.merge_cells(start_row=start, start_column=col, end_row=end, end_column=col)


def write_excel(rows: list[list], output: Path, sheet_name: str = "埋点提报") -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]

    ws.append(COLUMNS)
    for col_idx in range(1, len(COLUMNS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN

    for row in rows:
        ws.append(row)

    merge_event_columns(ws, rows)

    for idx, width in enumerate(COL_WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = width

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(COLUMNS)):
        for cell in row:
            cell.alignment = BODY_ALIGN

    ws.freeze_panes = "A2"
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)


def collect_rows_from_document(document: dict) -> tuple[list[list], str]:
    """Build Excel rows from single-page or multi-page (`pages` array) spec."""
    if "pages" in document:
        sheet_name = document.get("sheet_name", "埋点提报")
        default_date = document.get("change_date", date.today().isoformat())
        product_line = document.get("product_line", "")
        all_rows: list[list] = []
        for page_spec in document["pages"]:
            page = page_spec["page"]
            spec = {
                "page": {
                    **page,
                    "sheet_name": sheet_name,
                    "product_line": product_line,
                    "change_date": page.get("change_date", default_date),
                },
                "events": page_spec.get("events", {}),
                "view_events": page_spec.get("view_events", []),
                "exposure_events": page_spec.get("exposure_events", []),
                "click_events": page_spec.get("click_events", []),
            }
            all_rows.extend(build_rows(spec))
        return all_rows, sheet_name

    rows = build_rows(document)
    sheet_name = document.get("page", {}).get("sheet_name", "埋点提报")
    return rows, sheet_name


def summarize_document(document: dict, rows: list[list]) -> str:
    if "pages" in document:
        view_n = sum(len(p.get("view_events", [])) for p in document["pages"])
        exp_n = sum(len(p.get("exposure_events", [])) for p in document["pages"])
        click_n = sum(len(p.get("click_events", [])) for p in document["pages"])
        return (
            f"页面数: {len(document['pages'])} | "
            f"浏览 {view_n} | 曝光 {exp_n} | 点击 {click_n} | 合计 {len(rows)}"
        )

    view_n = len(document.get("view_events", []))
    exp_n = len(document.get("exposure_events", []))
    click_n = len(document.get("click_events", []))
    page = document.get("page", {})
    return (
        f"页面: {page.get('name_cn', '')} ({page.get('name_en', '')})\n"
        f"浏览 {view_n} | 曝光 {exp_n} | 点击 {click_n} | 合计 {len(rows)}"
    )


def summarize(spec: dict, rows: list[list]) -> str:
    return summarize_document(spec, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate tracking spec Excel")
    parser.add_argument("--input", "-i", required=True, help="JSON spec file path (single or multi-page)")
    parser.add_argument("--output", "-o", help="Output xlsx path (default: same name as input)")
    parser.add_argument("--sheet", help="Worksheet name (default: from JSON sheet_name / page.sheet_name)")
    parser.add_argument(
        "--remove-input",
        action="store_true",
        help="Delete input JSON after successful Excel generation (excel-only deliverable)",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else input_path.with_suffix(".xlsx")

    document = load_spec(input_path)
    rows, default_sheet = collect_rows_from_document(document)
    if not rows:
        print("No tracking events found in spec.", file=sys.stderr)
        sys.exit(1)

    sheet_name = args.sheet or default_sheet
    write_excel(rows, output_path, sheet_name=sheet_name)
    print(summarize_document(document, rows))
    print(f"Saved: {output_path}")

    if args.remove_input:
        input_path.unlink(missing_ok=True)
        print(f"Removed intermediate JSON: {input_path}")


if __name__ == "__main__":
    main()
