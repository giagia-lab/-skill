#!/usr/bin/env python3
"""Format compact horizontal tracking tables for PRD inline embedding.

硬约束（写死，禁止手改）：
1. 表头列名必须是英文 field key：event_name / page_name / module_name / element_name / anchor
   ——禁止「事件名称 / 页面名称 / 模块名称 / 元素名称 / 锚点」等中文列头。
2. 输出行一律顶格（无前导空格）。列表内缩进表格会导致
   VS Code / Cursor Markdown Preview（GFM）不渲染——源码可见、预览消失。
3. 阶段 3：Agent 必须 import 本模块生成表，写出 PRD 后立刻调用
   validate_prd_tracking_tables() 或 CLI --check；失败则自行修复。
   **禁止**把 --check 当作用户操作步骤；使用者无需运行任何命令。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 表头写死（唯一合法列头；改此处即改全技能输出）
# ---------------------------------------------------------------------------
PRD_COL_EVENT = "event_name"
PRD_COL_PAGE = "page_name"
PRD_COL_MODULE = "module_name"
PRD_COL_ELEMENT = "element_name"
PRD_COL_ANCHOR = "anchor"

# 唯一合法表头行（与图示标准表一致，禁止替换为中文）
PRD_TABLE_HEADER = (
    f"| | {PRD_COL_EVENT} | {PRD_COL_PAGE} | {PRD_COL_MODULE} | "
    f"{PRD_COL_ELEMENT} | {PRD_COL_ANCHOR} |"
)
PRD_SUMMARY_HEADER = (
    f"| 编号 | {PRD_COL_EVENT} | {PRD_COL_PAGE} | {PRD_COL_MODULE} | "
    f"{PRD_COL_ELEMENT} | {PRD_COL_ANCHOR} |"
)

# 标准表骨架（占位符；Agent / build 禁止另造格式）
PRD_INLINE_TABLE_TEMPLATE = """\
<!-- TRACKING:{ix}:BEGIN -->
**埋点映射（{ix}）**

| | event_name | page_name | module_name | element_name | anchor |
| --- | --- | --- | --- | --- | --- |
| 中文 | {event_cn} | {page_cn} | {module_cn} | {element_cn} | — |
| 英文 | `{event_en}` | `{page_en}` | `{module_en}` | `{element_en}` | `{anchor}` |
<!-- TRACKING:{ix}:END -->
"""

# 禁止出现在「埋点映射」表头行的中文列名（命中即失败）
FORBIDDEN_HEADER_CN = (
    "事件名称",
    "页面名称",
    "模块名称",
    "元素名称",
    "锚点",
    "元素位置",
    "埋点分类",
)


def _cell(value: str | None, fallback: str = "—") -> str:
    text = (value or "").strip()
    return text if text else fallback


def _en_cell(value: str | None) -> str:
    text = (value or "").strip()
    return f"`{text}`" if text else "—"


def _anchor_selector(item: dict, _page_spec: dict) -> str:
    anchor = item.get("anchor", {})
    return (anchor.get("selector") or "").strip()


def _compact_table(
    ix: str,
    event_cn: str,
    event_en: str,
    page_cn: str,
    page_en: str,
    module_cn: str,
    module_en: str,
    element_cn: str,
    element_en: str,
    anchor: str,
    indent: str = "",
) -> list[str]:
    """Emit PRD tracking table — 格式写死，与 PRD_INLINE_TABLE_TEMPLATE 一致。

    表格必须顶格输出：GFM / VS Code / Cursor Preview 对「列表项下缩进的表格」
    解析不稳定（源码可见、预览消失）。紧跟交互 bullet 即可，忽略 indent 参数。
    """
    _ = indent  # 兼容旧调用签名；强制忽略，始终顶格
    anchor_cn = "—"
    anchor_en = f"`{anchor}`" if anchor else "—"
    lines = [
        f"<!-- TRACKING:{ix}:BEGIN -->",
        f"**埋点映射（{ix}）**",
        "",
        PRD_TABLE_HEADER,
        "| --- | --- | --- | --- | --- | --- |",
        f"| 中文 | {_cell(event_cn)} | {_cell(page_cn)} | {_cell(module_cn)} | {_cell(element_cn)} | {anchor_cn} |",
        f"| 英文 | {_en_cell(event_en)} | {_en_cell(page_en)} | {_en_cell(module_en)} | {_en_cell(element_en)} | {anchor_en} |",
        f"<!-- TRACKING:{ix}:END -->",
    ]
    # 自检：表头必须是英文 field key
    if lines[3] != PRD_TABLE_HEADER:
        raise ValueError(f"table header must be locked English keys, got: {lines[3]!r}")
    for ln in lines:
        if ln.startswith((" ", "\t")):
            raise ValueError(f"tracking table line must be flush-left, got: {ln!r}")
        for bad in FORBIDDEN_HEADER_CN:
            # 仅拦表头行；数据行中文值允许包含「页面名称」等业务文案
            if ln.startswith("| |") and bad in ln:
                raise ValueError(f"Chinese header column forbidden: {bad!r} in {ln!r}")
    return lines


def format_click_table(item: dict, page_spec: dict, event_cfg: dict) -> list[str]:
    page = page_spec["page"]
    return _compact_table(
        item["interaction_id"],
        event_cfg.get("name_cn", ""),
        event_cfg.get("name_en", ""),
        page.get("name_cn", ""),
        page.get("name_en", ""),
        item.get("module_cn", ""),
        item.get("module_en", ""),
        item.get("element_cn", ""),
        item.get("element_en", ""),
        _anchor_selector(item, page_spec),
    )


def format_view_table(item: dict, page_spec: dict, event_cfg: dict) -> list[str]:
    page = page_spec["page"]
    return _compact_table(
        item["interaction_id"],
        event_cfg.get("name_cn", ""),
        event_cfg.get("name_en", ""),
        page.get("name_cn", ""),
        page.get("name_en", ""),
        "",
        "",
        "",
        "",
        _anchor_selector(item, page_spec),
        indent="",
    )


def format_click_block(item: dict, page_spec: dict, event_cfg: dict) -> list[str]:
    return format_click_table(item, page_spec, event_cfg)


def format_view_block(item: dict, page_spec: dict, event_cfg: dict) -> list[str]:
    return format_view_table(item, page_spec, event_cfg)


def build_summary_table(spec: dict) -> str:
    lines = [
        "## 附录：埋点映射总表（自动生成）",
        "",
        PRD_SUMMARY_HEADER,
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for page_spec in spec.get("pages", []):
        page = page_spec["page"]
        events = page_spec.get("events", {})

        def row(ix: str, ev_cn: str, ev_en: str, m_cn: str, m_en: str, e_cn: str, e_en: str, anchor: str) -> str:
            if anchor:
                return (
                    f"| {ix} | {_cell(ev_cn)} / `{_cell(ev_en)}` | "
                    f"{_cell(page.get('name_cn'))} / `{_cell(page.get('name_en'))}` | "
                    f"{_cell(m_cn)} / `{_cell(m_en)}` | "
                    f"{_cell(e_cn)} / `{_cell(e_en)}` | `{anchor}` |"
                )
            return (
                f"| {ix} | {_cell(ev_cn)} / `{_cell(ev_en)}` | "
                f"{_cell(page.get('name_cn'))} / `{_cell(page.get('name_en'))}` | "
                f"{_cell(m_cn)} / `{_cell(m_en)}` | "
                f"{_cell(e_cn)} / `{_cell(e_en)}` | — |"
            )

        for item in page_spec.get("view_events", []):
            ev = events.get("view", {})
            lines.append(row(
                item["interaction_id"], ev.get("name_cn", ""), ev.get("name_en", ""),
                "", "", "", "", _anchor_selector(item, page_spec),
            ))
        for item in page_spec.get("click_events", []):
            ev = events.get("click", {})
            lines.append(row(
                item["interaction_id"], ev.get("name_cn", ""), ev.get("name_en", ""),
                item.get("module_cn", ""), item.get("module_en", ""),
                item.get("element_cn", ""), item.get("element_en", ""),
                _anchor_selector(item, page_spec),
            ))
    return "\n".join(lines) + "\n"


def validate_prd_tracking_tables(prd_text: str) -> list[str]:
    """校验 PRD 内所有埋点映射表：表头必须为英文 field key、必须顶格。

    返回错误列表；空列表表示通过。
    """
    errors: list[str] = []
    # 每个 TRACKING 块
    blocks = re.finditer(
        r"<!-- TRACKING:([^:]+):BEGIN -->(.*?)<!-- TRACKING:\1:END -->",
        prd_text,
        flags=re.S,
    )
    found = 0
    for m in blocks:
        found += 1
        ix = m.group(1)
        body = m.group(2)
        # 块内每一行不得以空白开头（相对整段；取块内行）
        for i, raw in enumerate(body.splitlines(), start=1):
            if raw.startswith((" ", "\t")) and raw.strip():
                errors.append(f"{ix}: line {i} is indented (must be flush-left): {raw[:60]!r}")
        # 必须含合法英文表头
        if PRD_TABLE_HEADER not in body and PRD_TABLE_HEADER.strip() not in body:
            # 宽松：找 | | event_name | ...
            header_lines = [
                ln for ln in body.splitlines()
                if ln.strip().startswith("| |") or ln.strip().startswith("| 编号 |")
            ]
            if not header_lines:
                errors.append(f"{ix}: missing table header row")
            else:
                hdr = header_lines[0].strip()
                if "event_name" not in hdr or "page_name" not in hdr:
                    errors.append(
                        f"{ix}: header must use English field keys "
                        f"(event_name/page_name/...), got: {hdr!r}"
                    )
                for bad in FORBIDDEN_HEADER_CN:
                    if bad in hdr:
                        errors.append(
                            f"{ix}: Chinese header column forbidden: {bad!r} in {hdr!r}"
                        )
        # 禁止中文列头出现在表头行（| | … | 形式）
        for ln in body.splitlines():
            s = ln.strip()
            if not (s.startswith("| |") or s.startswith("| 编号 |")):
                continue
            for bad in FORBIDDEN_HEADER_CN:
                if bad in s:
                    errors.append(f"{ix}: Chinese header column forbidden: {bad!r}")

    if found == 0 and "埋点映射" in prd_text:
        errors.append("found「埋点映射」but no <!-- TRACKING:…:BEGIN/END --> blocks")

    # 全文扫描：埋点映射附近出现中文表头
    for m in re.finditer(r"\*\*埋点映射[^*]*\*\*", prd_text):
        window = prd_text[m.end() : m.end() + 400]
        for bad in FORBIDDEN_HEADER_CN:
            # 仅当出现在表头语境：| … 事件名称 …
            if re.search(rf"\|\s*{re.escape(bad)}\s*\|", window):
                errors.append(
                    f"near {m.group(0)}: Chinese header `{bad}` — "
                    f"must use English keys: {PRD_TABLE_HEADER}"
                )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PRD inline tracking table helper (format locked to English field keys)"
    )
    parser.add_argument(
        "--check",
        metavar="PRD.md",
        help="Validate PRD tracking table headers / flush-left rules",
    )
    parser.add_argument(
        "--print-template",
        action="store_true",
        help="Print the locked inline table template and exit",
    )
    args = parser.parse_args()

    if args.print_template:
        print(PRD_INLINE_TABLE_TEMPLATE)
        print("# locked header:")
        print(PRD_TABLE_HEADER)
        return

    if args.check:
        path = Path(args.check)
        text = path.read_text(encoding="utf-8")
        errs = validate_prd_tracking_tables(text)
        if errs:
            print(f"FAIL {path}: {len(errs)} error(s)", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(1)
        print(f"OK {path}: tracking table headers valid")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
