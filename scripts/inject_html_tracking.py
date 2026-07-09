#!/usr/bin/env python3
"""Inject data-track-* attributes into prototype HTML from tracking-spec.json."""

from __future__ import annotations

import re


def selector_to_pattern(selector: str) -> re.Pattern | None:
    selector = selector.strip()
    if not selector:
        return None

    attr_eq = re.match(r'^\[([\w-]+)=(["\'])(.+?)\2\]$', selector)
    if attr_eq:
        attr, _, val = attr_eq.groups()
        return re.compile(
            rf'<\w+\b([^>]*\b{re.escape(attr)}="{re.escape(val)}"[^>]*)>',
            re.I,
        )

    attr_flag = re.match(r'^\[([\w-]+)\]$', selector)
    if attr_flag:
        attr = attr_flag.group(1)
        return re.compile(rf'<\w+\b([^>]*\b{re.escape(attr)}\b[^>]*)>', re.I)

    if selector.startswith("a[href="):
        href = selector.split("=", 1)[1].rstrip("]").strip("\"'")
        return re.compile(rf'<a\b([^>]*\bhref="{re.escape(href)}"[^>]*)>', re.I)

    if selector.startswith("#"):
        id_val = selector[1:]
        return re.compile(rf'<\w+\b([^>]*\bid="{re.escape(id_val)}"[^>]*)>', re.I)

    tag_class = re.match(r'^(\w+)((?:\.[\w-]+)+)$', selector)
    if tag_class:
        tag, classes = tag_class.groups()
        cls = classes.split(".")[1]
        return re.compile(
            rf'<{re.escape(tag)}\b([^>]*\bclass="[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*)>',
            re.I,
        )

    return None


def inject_html(html: str, spec: dict, filename: str) -> str:
    for page_spec in spec["pages"]:
        if page_spec["page"].get("source_html") != filename:
            continue
        events = page_spec.get("events", {})
        targets: list[tuple[str, dict]] = []

        for item in page_spec.get("view_events", []):
            sel = (item.get("anchor") or {}).get("selector", "")
            if not sel:
                continue
            targets.append((sel, {
                "data-track-id": item["track_id"],
                "data-track-type": "view",
                "data-track-event": events["view"]["name_en"],
                "data-track-ix": item["interaction_id"],
            }))

        for item in page_spec.get("click_events", []):
            sel = (item.get("anchor") or {}).get("selector", "")
            if not sel:
                continue
            targets.append((sel, {
                "data-track-id": item["track_id"],
                "data-track-type": "click",
                "data-track-event": events["click"]["name_en"],
                "data-track-ix": item["interaction_id"],
            }))

        for sel, attrs in targets:
            pat = selector_to_pattern(sel)
            if not pat:
                continue
            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())

            def repl(m, a=attr_str):
                tag = m.group(0)
                if "data-track-id=" in tag:
                    return tag
                return tag[:-1] + f" {a}>"

            html = pat.sub(repl, html, count=1)

    if "tracking-debug-stub" not in html and "</body>" in html:
        html = html.replace(
            "</body>",
            """
  <script id="tracking-debug-stub">
    document.addEventListener('click', (e) => {
      const el = e.target.closest('[data-track-id]');
      if (!el || el.dataset.trackType === 'view') return;
      console.log('[track]', { ix: el.dataset.trackIx, id: el.dataset.trackId, type: el.dataset.trackType, event: el.dataset.trackEvent });
    });
  </script>
</body>""",
            1,
        )
    return html
