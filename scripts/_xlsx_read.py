#!/usr/bin/env python3
"""Minimal xlsx reader (no styles) for department tracking workbooks."""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _col_row(ref: str) -> tuple[int, int]:
    m = re.match(r"([A-Z]+)(\d+)", ref)
    if not m:
        return 0, 0
    col_s, row_s = m.groups()
    col = 0
    for ch in col_s:
        col = col * 26 + (ord(ch) - 64)
    return int(row_s), col


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    t = cell.attrib.get("t")
    v = cell.find("m:v", NS)
    if t == "s" and v is not None and v.text is not None:
        idx = int(v.text)
        return shared[idx] if 0 <= idx < len(shared) else ""
    if t == "inlineStr":
        is_el = cell.find("m:is/m:t", NS)
        return (is_el.text or "") if is_el is not None else ""
    if v is not None and v.text is not None:
        return v.text
    return ""


def read_workbook(path: Path) -> dict[str, list[list[str]]]:
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                parts = [t.text or "" for t in si.findall(".//m:t", NS)]
                shared.append("".join(parts))

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {
            r.attrib["Id"]: r.attrib["Target"]
            for r in rels
            if r.attrib.get("Type", "").endswith("/worksheet")
        }

        out: dict[str, list[list[str]]] = {}
        for sheet in wb.findall(".//m:sheet", NS):
            name = sheet.attrib["name"]
            rid = sheet.attrib[f"{{{REL_NS}}}id"]
            target = rid_to_target.get(rid, "")
            if target.startswith("/"):
                target = target[1:]
            if not target.startswith("xl/"):
                target = "xl/" + target.lstrip("/")
            if target not in z.namelist():
                continue
            root = ET.fromstring(z.read(target))
            rows_map: dict[int, dict[int, str]] = {}
            max_col = 0
            for row in root.findall(".//m:sheetData/m:row", NS):
                r_idx = int(row.attrib.get("r", 0))
                for cell in row.findall("m:c", NS):
                    ref = cell.attrib.get("r", "")
                    rr, cc = _col_row(ref)
                    if rr == 0:
                        continue
                    rows_map.setdefault(rr, {})[cc] = _cell_value(cell, shared)
                    max_col = max(max_col, cc)
            if not rows_map:
                out[name] = []
                continue
            max_row = max(rows_map)
            table: list[list[str]] = []
            for r in range(1, max_row + 1):
                line = [rows_map.get(r, {}).get(c, "") for c in range(1, max_col + 1)]
                while line and line[-1] == "":
                    line.pop()
                table.append(line)
            out[name] = table
        return out


if __name__ == "__main__":
    import json
    import sys

    p = Path(sys.argv[1])
    data = read_workbook(p)
    print(json.dumps({"sheets": list(data.keys()), "count": len(data)}, ensure_ascii=False, indent=2))
