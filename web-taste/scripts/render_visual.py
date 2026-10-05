#!/usr/bin/env python3
"""Render self-contained Web Taste evidence boards and component choices."""

import argparse
import base64
import html
import json
import mimetypes
import re
import hashlib
import datetime as dt
from urllib.parse import urlparse
from pathlib import Path


def fail(message):
    raise SystemExit("ERROR: " + message)


def load_data(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("input file does not exist: {}".format(path))
    except json.JSONDecodeError as error:
        fail("invalid JSON at line {}: {}".format(error.lineno, error.msg))
    if not isinstance(data, dict):
        fail("input JSON must be an object")
    return data


def require(data, keys, context="document"):
    if not isinstance(data, dict):
        fail("{} must be an object".format(context))
    for key in keys:
        if key not in data or data[key] in (None, "", []):
            fail("{} is missing required field '{}'".format(context, key))


def esc(value):
    return html.escape(str(value), quote=True)


def as_list(value):
    if value is None:
        return []
    if not isinstance(value, list):
        fail("expected a list, got {}".format(type(value).__name__))
    return value


def local_image_data(path_value, input_dir):
    if re.match(r"^https?://", str(path_value), re.IGNORECASE):
        fail("remote images are not allowed: {}".format(path_value))
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = input_dir / path
    path = path.resolve()
    if not path.is_file():
        fail("image does not exist: {}".format(path))
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if not mime.startswith("image/"):
        fail("preview asset is not an image: {}".format(path))
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return "data:{};base64,{}".format(mime, encoded)


def render_tags(items):
    return "".join('<span class="tag">{}</span>'.format(esc(item)) for item in items)


def render_text_list(items, empty="None recorded"):
    if not items:
        return '<p class="empty">{}</p>'.format(esc(empty))
    return "<ul>{}</ul>".format("".join("<li>{}</li>".format(esc(item)) for item in items))


def render_image(item, input_dir, anchor=True):
    require(item, ("label", "path"), "screenshot")
    source = local_image_data(item["path"], input_dir)
    viewport = item.get("viewport", "viewport not recorded")
    return """<figure class="shot" {anchor}>
      <img src="{source}" alt="{label}">
      <figcaption><strong>{label}</strong><span>{viewport}</span></figcaption>
    </figure>""".format(
        anchor='id="{}"'.format(esc(item.get("id", ""))) if anchor else "",
        source=source,
        label=esc(item["label"]),
        viewport=esc(viewport),
    )


def safe_color(value):
    value = str(value).strip()
    patterns = (
        r"#[0-9a-fA-F]{3,8}",
        r"rgba?\([0-9.,%\s]+\)",
        r"hsla?\([0-9.,%\s]+\)",
    )
    return value if any(re.fullmatch(pattern, value) for pattern in patterns) else "transparent"


def render_palette(items):
    cards = []
    for item in items:
        require(item, ("name", "value", "role"), "palette item")
        cards.append(
            """<div class="swatch-card">
              <div class="swatch" style="background:{color}"></div>
              <strong>{name}</strong><code>{value}</code><p>{role}</p>
            </div>""".format(
                color=safe_color(item["value"]),
                name=esc(item["name"]),
                value=esc(item["value"]),
                role=esc(item["role"]),
            )
        )
    return "".join(cards) or '<p class="empty">No measured palette evidence.</p>'


def positive_number(value, name, maximum=512):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= maximum:
        fail("{} must be a positive number no greater than {}".format(name, maximum))
    return value


def render_type_scale(items):
    rows = []
    for item in items:
        require(item, ("role", "sample"), "type scale item")
        size, height, weight = item.get("size_px"), item.get("line_height_px"), item.get("weight", 400)
        # Retain legacy size/line-height, weight specs while supporting explicit values.
        match = re.fullmatch(r"([0-9.]+)/([0-9.]+),\s*([0-9]+)", str(item.get("spec", "")))
        if size is None and match:
            size, height, weight = float(match[1]), float(match[2]), int(match[3])
        style = ""
        if size is not None:
            positive_number(size, "size_px")
            height = size * 1.2 if height is None else positive_number(height, "line_height_px", 1024)
            positive_number(weight, "weight", 1000)
            style = "font-size:{}px;line-height:{}px;font-weight:{};".format(size, height, weight)
        family = str(item.get("font_family", "system-ui"))
        available = item.get("font_available", False)
        if available:
            if not re.fullmatch(r"[\w ,.-]+", family):
                fail("font_family contains unsupported CSS characters")
            style += "font-family:" + family + ";"
        spec = item.get("spec") or "{}/{} px, {}".format(size, height, weight)
        note = "Declared local family: " + family if available else "Source family: " + family + "; system substitute"
        if not style:
            note += "; size not measured"
        rows.append('<div class="type-row"><span>{}</span><div class="type-sample"><strong style="{}">{}</strong><small>{}</small></div><code>{}</code></div>'.format(
            esc(item["role"]), esc(style), esc(item["sample"]), esc(note), esc(spec)))
    return "".join(rows) or '<p class="empty">No measured typography evidence.</p>'


def render_geometry(items):
    rows = []
    lengths = []
    for item in items:
        match = re.fullmatch(r"([0-9.]+)\s*px", str(item.get("value", "")))
        lengths.append(float(match[1]) if match else None)
    maximum = max((value for value in lengths if value is not None), default=1) or 1
    for item, length in zip(items, lengths):
        require(item, ("name", "value", "role"), "geometry item")
        bar = '<div class="spacing-track"><span style="width:{}%"></span></div>'.format(max(0, min(100, length / maximum * 100))) if length is not None else ""
        rows.append('<div class="metric"><span>{}</span><strong>{}</strong>{}<p>{}</p></div>'.format(esc(item["name"]), esc(item["value"]), bar, esc(item["role"])))
    return "".join(rows) or '<p class="empty">No measured geometry evidence.</p>'


def render_layouts(items):
    rendered = []
    for item in items:
        require(item, ("label", "columns", "blocks"), "layout skeleton")
        columns = item["columns"]
        if type(columns) is not int or not 1 <= columns <= 12:
            fail("layout columns must be an integer from 1 to 12")
        blocks = []
        for block in as_list(item["blocks"]):
            require(block, ("label", "span"), "layout block")
            if type(block["span"]) is not int or not 1 <= block["span"] <= columns:
                fail("layout block span exceeds its grid")
            blocks.append('<div style="grid-column:span {}">{}</div>'.format(block["span"], esc(block["label"])))
        rendered.append('<article class="layout"><h3>{}</h3><div class="skeleton" style="grid-template-columns:repeat({},minmax(0,1fr))">{}</div></article>'.format(esc(item["label"]), columns, "".join(blocks)))
    return "".join(rendered) or '<p class="empty">Layout skeleton not captured.</p>'


def render_comparisons(items, screenshots, input_dir):
    shots = {item["id"]: item for item in screenshots}
    rendered = []
    for item in items:
        require(item, ("title", "desktop", "mobile", "summary"), "responsive comparison")
        if item["desktop"] not in shots or item["mobile"] not in shots:
            fail("responsive comparison references an unknown screenshot")
        rendered.append('<article><h3>{}</h3><p>{}</p><div class="grid">{}{}</div></article>'.format(esc(item["title"]), esc(item["summary"]), render_image(shots[item["desktop"]], input_dir, anchor=False), render_image(shots[item["mobile"]], input_dir, anchor=False)))
    return "".join(rendered) or '<p class="empty">Responsive comparison not captured or out of scope.</p>'


def render_sequences(items, screenshots, input_dir, motion=False):
    shots = {item["id"]: item for item in screenshots}
    rendered = []
    for item in items:
        require(item, ("title", "frames"), "state or motion sequence")
        frames = []
        for frame in as_list(item["frames"]):
            require(frame, ("label", "screenshot_ref"), "sequence frame")
            if frame["screenshot_ref"] not in shots:
                fail("sequence references an unknown screenshot")
            if motion:
                if type(frame.get("at_ms")) is not int or frame["at_ms"] < 0:
                    fail("motion frames require non-negative integer at_ms")
                label = "{} · {} ms".format(frame["label"], frame["at_ms"])
            else:
                label = frame["label"]
            shot = dict(shots[frame["screenshot_ref"]], label=label)
            frames.append(render_image(shot, input_dir, anchor=False))
        rendered.append('<article><h3>{}</h3><p>{}</p><div class="grid">{}</div></article>'.format(
            esc(item["title"]), esc(item.get("summary", "")), "".join(frames)))
    return "".join(rendered) or '<p class="empty">Not captured or out of scope; see confidence gaps.</p>'


def stable_id(prefix, label):
    return prefix + "-" + hashlib.sha256(str(label).encode("utf-8")).hexdigest()[:10]


def validate_board(data):
    require(data, ("title", "source_url", "captured_at", "summary", "learning_focus", "scope"))
    try:
        parsed = urlparse(data["source_url"])
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or any(char.isspace() for char in data["source_url"]):
            fail("source_url must be an absolute HTTP(S) URL")
        if dt.date.fromisoformat(data["captured_at"]).isoformat() != data["captured_at"]:
            fail("captured_at must be YYYY-MM-DD")
    except (TypeError, ValueError):
        fail("invalid source URL or capture date")
    data.setdefault("status", "reviewable")
    if data["status"] not in {"draft", "incomplete", "reviewable"}:
        fail("board status must be draft, incomplete or reviewable")
    ids, evidence_ids = set(), set()
    def register(item, prefix, label):
        item.setdefault("id", stable_id(prefix, label))
        identity = item["id"]
        if not isinstance(identity, str) or not re.fullmatch(r"[\w-]+", identity) or identity in ids:
            fail("evidence, screenshot and principle IDs must be valid and unique")
        ids.add(identity)
        return identity
    shots = as_list(data.get("screenshots"))
    for shot in shots:
        require(shot, ("label", "viewport"), "screenshot")
        register(shot, "shot", shot["label"])
    for section in as_list(data.get("sections")):
        require(section, ("title", "summary"), "section")
        for item in as_list(section.get("evidence")):
            require(item, ("type", "label", "value", "confidence"), "evidence")
            identity = register(item, "evidence", section["title"] + ":" + item["label"])
            if item["type"] not in {"observed", "measured", "interpreted", "unknown"}:
                fail("invalid evidence type")
            if item["confidence"] not in {"high", "medium", "low"}:
                fail("invalid evidence confidence")
            if item.get("screenshot_ref") and item["screenshot_ref"] not in {shot["id"] for shot in shots}:
                fail("evidence references an unknown screenshot")
            if item["type"] in {"observed", "measured"}:
                evidence_ids.add(identity)
    principles = as_list(data.get("principles"))
    for item in principles:
        require(item, ("title", "evidence", "use_when", "avoid_when", "implementation_cue", "confidence"), "principle")
        register(item, "principle", item["title"])
        if item["confidence"] not in {"high", "medium", "low"}:
            fail("invalid principle confidence")
        references = as_list(item.get("evidence_refs"))
        if any(not isinstance(ref, str) or ref not in evidence_ids for ref in references):
            fail("principle evidence_refs must reference observed or measured evidence IDs")
        if data["status"] == "reviewable" and not references:
            fail("reviewable principles require evidence_refs")
    if data["status"] == "reviewable":
        if not shots or not evidence_ids or not principles:
            fail("reviewable board requires screenshots, observed/measured evidence and principles")
    elif not as_list(data.get("gaps")):
        fail("draft or incomplete board requires explicit gaps")
    return data


def render_sections(items):
    blocks = []
    for section in items:
        require(section, ("title", "summary"), "evidence section")
        evidence_rows = []
        for evidence in as_list(section.get("evidence")):
            require(evidence, ("type", "label", "value", "confidence"), "evidence item")
            evidence_rows.append(
                """<div class="evidence-row" id="{id}">
                  <span class="evidence-type">{kind}</span>
                  <strong>{label}</strong><p>{value} {shot_link}</p>
                  <span class="confidence">{confidence} confidence</span>
                </div>""".format(
                    id=esc(evidence["id"]),
                    shot_link='<a href="#{}">Capture</a>'.format(esc(evidence["screenshot_ref"])) if evidence.get("screenshot_ref") else "",
                    kind=esc(evidence["type"]),
                    label=esc(evidence["label"]),
                    value=esc(evidence["value"]),
                    confidence=esc(evidence["confidence"]),
                )
            )
        blocks.append(
            """<article class="evidence-block"><h3>{title}</h3><p>{summary}</p>{rows}</article>""".format(
                title=esc(section["title"]),
                summary=esc(section["summary"]),
                rows="".join(evidence_rows) or '<p class="empty">Evidence unavailable.</p>',
            )
        )
    return "".join(blocks)


def render_principles(items):
    cards = []
    for item in items:
        require(
            item,
            ("title", "evidence", "use_when", "avoid_when", "implementation_cue", "confidence"),
            "principle",
        )
        cards.append(
            """<article class="principle" id="{id}">
              <header><h3>{title}</h3><span>{confidence} confidence</span></header>
              <dl>
                <dt>Evidence</dt><dd>{evidence} {refs}</dd>
                <dt>Use when</dt><dd>{use_when}</dd>
                <dt>Avoid when</dt><dd>{avoid_when}</dd>
                <dt>Implementation cue</dt><dd>{cue}</dd>
              </dl>
            </article>""".format(
                id=esc(item["id"]),
                refs=" ".join('<a href="#{}">{}</a>'.format(esc(ref), esc(ref)) for ref in as_list(item.get("evidence_refs"))),
                title=esc(item["title"]),
                confidence=esc(item["confidence"]),
                evidence=esc(item["evidence"]),
                use_when=esc(item["use_when"]),
                avoid_when=esc(item["avoid_when"]),
                cue=esc(item["implementation_cue"]),
            )
        )
    return "".join(cards)


BASE_CSS = """
:root { color-scheme: light; --ink:#161616; --muted:#666; --line:#d9d9d4; --paper:#f7f7f4; --accent:#0b6b4f; --signal:#1d5fd1; }
* { box-sizing:border-box; }
body { overflow-wrap:anywhere; margin:0; color:var(--ink); background:#fff; font:15px/1.55 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing:0; }
main { width:min(1180px,calc(100% - 32px)); margin:0 auto; padding:40px 0 80px; }
h1,h2,h3,p { margin-top:0; }
h1 { max-width:900px; font-size:76px; line-height:1; margin-bottom:20px; }
h2 { font-size:24px; margin-bottom:18px; }
h3 { font-size:17px; }
.hero { border-bottom:1px solid var(--line); padding-bottom:32px; }
.hero p { max-width:760px; color:var(--muted); font-size:18px; }
.meta { display:flex; gap:12px 24px; flex-wrap:wrap; margin:20px 0; color:var(--muted); }
.tag { display:inline-block; border:1px solid var(--line); border-radius:999px; padding:5px 10px; margin:0 6px 6px 0; background:var(--paper); }
section { padding:34px 0; border-bottom:1px solid var(--line); }
.grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:16px; align-items:start; }
.shot { grid-column:span 6; margin:0; border:1px solid var(--line); background:var(--paper); }
.shot img { width:100%; display:block; max-height:680px; object-fit:contain; background:#ecece7; }
.shot figcaption { display:flex; justify-content:space-between; gap:12px; padding:12px; }
.shot figcaption span,.empty { color:var(--muted); }
.swatches { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }
.swatch-card,.metric,.evidence-block,.principle,.choice { border:1px solid var(--line); border-radius:6px; background:#fff; }
.swatch-card { padding:10px; }
.swatch { aspect-ratio:16/8; border:1px solid rgba(0,0,0,.15); margin-bottom:10px; }
.swatch-card code { display:block; margin:4px 0; }
.swatch-card p,.metric p { color:var(--muted); margin:0; }
.type-row { display:grid; grid-template-columns:120px 1fr auto; gap:16px; align-items:baseline; padding:15px 0; border-top:1px solid var(--line); }
.type-row:first-child { border-top:0; }
.type-row > * { min-width:0; }
.type-sample { overflow:auto; }
.type-sample small { display:block; color:var(--muted); margin-top:8px; }
.type-row strong { font-size:20px; overflow-wrap:anywhere; }
.spacing-track { height:12px; background:var(--paper); margin:8px 0; }
.spacing-track span { display:block; height:100%; background:var(--accent); }
.skeleton { display:grid; gap:8px; margin:16px 0; }
.skeleton div { min-height:64px; padding:14px; border:1px solid var(--line); background:var(--paper); }
.preview iframe { width:100%; height:320px; border:0; }
.metrics { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; }
.metric { padding:16px; }
.metric strong { display:block; font-size:24px; margin:4px 0; }
.evidence-grid,.principle-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }
.evidence-block,.principle { padding:18px; }
.evidence-row { display:grid; grid-template-columns:auto 1fr auto; gap:6px 10px; padding:12px 0; border-top:1px solid var(--line); }
.evidence-row p { grid-column:2/-1; margin:0; }
.evidence-type,.confidence { color:var(--accent); font-size:12px; text-transform:uppercase; }
.principle header { display:flex; justify-content:space-between; gap:16px; }
.principle header span { color:var(--accent); white-space:nowrap; }
dl { display:grid; grid-template-columns:130px 1fr; gap:9px 14px; }
dt { color:var(--muted); } dd { margin:0; }
.boundary-grid { display:grid; grid-template-columns:1fr 1fr; gap:24px; }
code { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:13px; }
a { color:var(--signal); }
@media (max-width:720px) {
  main { width:min(100% - 24px,1180px); padding-top:24px; }
  h1 { font-size:40px; }
  .shot,.evidence-block,.principle { grid-column:1/-1; }
  .evidence-grid,.principle-grid,.boundary-grid { grid-template-columns:1fr; }
  .type-row { grid-template-columns:1fr; gap:4px; }
  .shot figcaption,.principle header { flex-direction:column; }
  dl { grid-template-columns:1fr; }
}
"""


def document(title, body, extra_css="", script="", metadata=None):
    if metadata is not None:
        encoded = json.dumps(metadata, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        script += '<script type="application/json" id="web-taste-data">' + encoded + '</script>'
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3' fill='%230b6b4f'/%3E%3C/svg%3E">
<title>{title}</title><style>{css}{extra_css}</style></head><body>{body}{script}</body></html>
""".format(title=esc(title), css=BASE_CSS, extra_css=extra_css, body=body, script=script)


def render_taste_board(data, input_path):
    validate_board(data)
    screenshots = as_list(data.get("screenshots"))
    sections = as_list(data.get("sections"))
    principles = as_list(data.get("principles"))
    screenshot_html = "".join(render_image(item, input_path.parent) for item in screenshots)
    if not screenshot_html:
        screenshot_html = '<p class="empty">No screenshot evidence available; see gaps.</p>'
    body = """<main>
      <header class="hero">
        <p>VISUAL TASTE BOARD · {status}</p><h1>{title}</h1><p>{summary}</p>
        <div class="meta"><span>{captured}</span><span>{scope}</span><a href="{url}">{url}</a></div>
        <div>{focus}</div>
      </header>
      <section><h2>Rendered evidence</h2><div class="grid">{screenshots}</div></section>
      <section><h2>Layout skeletons</h2>{layouts}</section>
      <section><h2>Responsive reflow</h2>{comparisons}</section>
      <section><h2>Component states</h2>{states}</section>
      <section><h2>Motion sequence</h2>{motion}</section>
      <section><h2>Color roles</h2><div class="swatches">{palette}</div></section>
      <section><h2>Typography ladder</h2>{type_scale}</section>
      <section><h2>Spacing and geometry</h2><div class="metrics">{geometry}</div></section>
      <section><h2>Classified evidence</h2><div class="evidence-grid">{sections}</div></section>
      <section><h2>Transferable principles</h2><div class="principle-grid">{principles}</div></section>
      <section><div class="boundary-grid"><div><h2>Do not copy</h2>{do_not_copy}</div><div><h2>Confidence gaps</h2>{gaps}</div></div></section>
    </main>""".format(
        status=esc(data["status"]),
        layouts=render_layouts(as_list(data.get("layout_skeletons"))),
        comparisons=render_comparisons(as_list(data.get("comparisons")), screenshots, input_path.parent),
        states=render_sequences(as_list(data.get("state_groups")), screenshots, input_path.parent),
        motion=render_sequences(as_list(data.get("motion_sequences")), screenshots, input_path.parent, motion=True),
        title=esc(data["title"]),
        summary=esc(data["summary"]),
        captured=esc(data["captured_at"]),
        scope=esc(data["scope"]),
        url=esc(data["source_url"]),
        focus=render_tags(as_list(data["learning_focus"])),
        screenshots=screenshot_html,
        palette=render_palette(as_list(data.get("palette"))),
        type_scale=render_type_scale(as_list(data.get("type_scale"))),
        geometry=render_geometry(as_list(data.get("geometry"))),
        sections=render_sections(sections),
        principles=render_principles(principles),
        do_not_copy=render_text_list(as_list(data.get("do_not_copy"))),
        gaps=render_text_list(as_list(data.get("gaps"))),
    )
    metadata = dict(data)
    metadata["screenshots"] = [{key: value for key, value in item.items() if key != "path"} for item in screenshots]
    return document(data["title"], body, metadata=metadata)


CHOICE_CSS = """
.choice-intro { max-width:760px; color:var(--muted); }
.choice-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; align-items:start; }
.choice { overflow:hidden; }
.choice.selected { outline:3px solid var(--accent); outline-offset:2px; }
.preview { min-height:240px; padding:18px; display:grid; place-items:center; background:var(--paper); border-bottom:1px solid var(--line); overflow:auto; }
.choice-copy { padding:18px; }
.choice-id { color:var(--accent); font-size:13px; font-weight:700; }
.choice dl { grid-template-columns:90px 1fr; }
.select { width:44px; height:44px; border-radius:50%; border:0; background:var(--ink); color:#fff; font-weight:700; cursor:pointer; }
.select:focus-visible { outline:3px solid var(--signal); outline-offset:3px; }
#selection { margin-top:24px; padding:14px 18px; border:1px solid var(--line); background:#fff; }
"""


def render_choice_preview(option, input_dir):
    if option.get("preview_html"):
        viewport = option.get("viewport", {"width": 390, "height": 320})
        require(viewport, ("width", "height"), "preview viewport")
        width = positive_number(viewport["width"], "viewport width", 2560)
        height = positive_number(viewport["height"], "viewport height", 2560)
        markup = '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + str(option["preview_html"]) + '</body></html>'
        return '<iframe sandbox="" title="{} preview" srcdoc="{}" style="width:{}px;height:{}px;max-width:none"></iframe>'.format(esc(option["name"]), esc(markup), width, height)
    if option.get("preview_image"):
        source = local_image_data(option["preview_image"], input_dir)
        return '<img src="{}" alt="{} preview" style="max-width:100%;height:auto">'.format(
            source, esc(option["name"])
        )
    fail("option '{}' needs preview_html or preview_image".format(option.get("id", "unknown")))


def render_component_choice(data, input_path):
    require(data, ("title", "context", "decision_question", "options"))
    options = as_list(data["options"])
    if len(options) < 2 or len(options) > 3:
        fail("component choice requires 2 or 3 options")
    cards = []
    seen = set()
    viewports = [option.get("viewport", {"width": 390, "height": 320}) for option in options]
    if any(viewport != viewports[0] for viewport in viewports):
        fail("component options must use identical viewport dimensions")
    for option in options:
        require(option, ("id", "name", "difference", "tradeoff", "states"), "component option")
        option_id = str(option["id"])
        if option_id in seen:
            fail("component option ids must be unique")
        seen.add(option_id)
        cards.append(
            """<article class="choice" data-choice="{id}">
              <div class="preview">{preview}</div>
              <div class="choice-copy"><span class="choice-id">OPTION {id}</span><h2>{name}</h2>
                <dl><dt>Difference</dt><dd>{difference}</dd><dt>Tradeoff</dt><dd>{tradeoff}</dd><dt>States</dt><dd>{states}</dd></dl>
                <button class="select" type="button" data-select="{id}" aria-label="Select option {id}">{id}</button>
              </div>
            </article>""".format(
                id=esc(option_id),
                preview=render_choice_preview(option, input_path.parent),
                name=esc(option["name"]),
                difference=esc(option["difference"]),
                tradeoff=esc(option["tradeoff"]),
                states=esc(option["states"]),
            )
        )
    body = """<main><header class="hero"><p>COMPONENT CHOICE</p><h1>{title}</h1>
      <p class="choice-intro">{context}</p><h2>{question}</h2></header>
      <section><div class="choice-grid">{cards}</div><div id="selection" role="status">No option selected.</div></section>
    </main>""".format(
        title=esc(data["title"]),
        context=esc(data["context"]),
        question=esc(data["decision_question"]),
        cards="".join(cards),
    )
    script = """<script>
document.querySelectorAll('[data-select]').forEach((button) => {
  button.addEventListener('click', () => {
    const id = button.dataset.select;
    document.querySelectorAll('[data-choice]').forEach((card) => card.classList.toggle('selected', card.dataset.choice === id));
    document.getElementById('selection').textContent = `Selected option ${id}. Copy this choice into the conversation; this page does not save approval.`;
  });
});
</script>"""
    return document(data["title"], body, CHOICE_CSS, script)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("taste-board", "component-choice"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("input", type=Path)
        subparser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = load_data(args.input)
    if args.command == "taste-board":
        output = render_taste_board(data, args.input)
    else:
        output = render_component_choice(data, args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
