#!/usr/bin/env python3
"""Format compact horizontal tracking tables for PRD inline embedding."""

from __future__ import annotations


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
    indent: str = "  ",
) -> list[str]:
    anchor_cn = "—"
    anchor_en = f"`{anchor}`" if anchor else "—"
    p = indent
    return [
        f"{p}<!-- TRACKING:{ix}:BEGIN -->",
        f"{p}**埋点映射（{ix}）**",
        f"{p}",
        f"{p}| | 事件 | 页面 | 模块 | 元素 | 锚点 |",
        f"{p}| --- | --- | --- | --- | --- | --- |",
        f"{p}| 中文 | {_cell(event_cn)} | {_cell(page_cn)} | {_cell(module_cn)} | {_cell(element_cn)} | {anchor_cn} |",
        f"{p}| 英文 | {_en_cell(event_en)} | {_en_cell(page_en)} | {_en_cell(module_en)} | {_en_cell(element_en)} | {anchor_en} |",
        f"{p}<!-- TRACKING:{ix}:END -->",
    ]


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
        "| 编号 | 事件 | 页面 | 模块 | 元素 | 锚点 |",
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
