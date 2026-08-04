#!/usr/bin/env python3
"""Render self-contained Web Taste evidence boards and component choices."""

import argparse
import base64
import html
import json
import mimetypes
import re
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


def render_image(item, input_dir):
    require(item, ("label", "path"), "screenshot")
    source = local_image_data(item["path"], input_dir)
    viewport = item.get("viewport", "viewport not recorded")
    return """<figure class="shot">
      <img src="{source}" alt="{label}">
      <figcaption><strong>{label}</strong><span>{viewport}</span></figcaption>
    </figure>""".format(
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


def render_type_scale(items):
    rows = []
    for item in items:
        require(item, ("role", "sample", "spec"), "type scale item")
        rows.append(
            """<div class="type-row"><span>{role}</span><strong>{sample}</strong><code>{spec}</code></div>""".format(
                role=esc(item["role"]), sample=esc(item["sample"]), spec=esc(item["spec"])
            )
        )
    return "".join(rows) or '<p class="empty">No measured typography evidence.</p>'


def render_geometry(items):
    rows = []
    for item in items:
        require(item, ("name", "value", "role"), "geometry item")
        rows.append(
            """<div class="metric"><span>{name}</span><strong>{value}</strong><p>{role}</p></div>""".format(
                name=esc(item["name"]), value=esc(item["value"]), role=esc(item["role"])
            )
        )
    return "".join(rows) or '<p class="empty">No measured geometry evidence.</p>'


def render_sections(items):
    blocks = []
    for section in items:
        require(section, ("title", "summary"), "evidence section")
        evidence_rows = []
        for evidence in as_list(section.get("evidence")):
            require(evidence, ("type", "label", "value", "confidence"), "evidence item")
            evidence_rows.append(
                """<div class="evidence-row">
                  <span class="evidence-type">{kind}</span>
                  <strong>{label}</strong><p>{value}</p>
                  <span class="confidence">{confidence} confidence</span>
                </div>""".format(
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
            """<article class="principle">
              <header><h3>{title}</h3><span>{confidence} confidence</span></header>
              <dl>
                <dt>Evidence</dt><dd>{evidence}</dd>
                <dt>Use when</dt><dd>{use_when}</dd>
                <dt>Avoid when</dt><dd>{avoid_when}</dd>
                <dt>Implementation cue</dt><dd>{cue}</dd>
              </dl>
            </article>""".format(
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
body { margin:0; color:var(--ink); background:#fff; font:15px/1.55 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing:0; }
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
.grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:16px; }
.shot { grid-column:span 6; margin:0; border:1px solid var(--line); background:var(--paper); }
.shot img { width:100%; display:block; max-height:680px; object-fit:contain; background:#ecece7; }
.shot figcaption { display:flex; justify-content:space-between; gap:12px; padding:12px; }
.shot figcaption span,.empty { color:var(--muted); }
.swatches { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }
.swatch-card,.metric,.evidence-block,.principle,.choice { border:1px solid var(--line); border-radius:6px; background:#fff; }
.swatch-card { padding:10px; }
.swatch { aspect-ratio:16/8; border:1px solid rgba(0,0,0,.15); margin-bottom:10px; }
.swatch-card code { display:block; margin:4px 0; }
.swatch-card p,.metric p { color:var(--muted); margin:0; }
.type-row { display:grid; grid-template-columns:120px 1fr auto; gap:16px; align-items:baseline; padding:15px 0; border-top:1px solid var(--line); }
.type-row:first-child { border-top:0; }
.type-row strong { font-size:20px; overflow-wrap:anywhere; }
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


def document(title, body, extra_css="", script=""):
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3' fill='%230b6b4f'/%3E%3C/svg%3E">
<title>{title}</title><style>{css}{extra_css}</style></head><body>{body}{script}</body></html>
""".format(title=esc(title), css=BASE_CSS, extra_css=extra_css, body=body, script=script)


def render_taste_board(data, input_path):
    require(data, ("title", "source_url", "captured_at", "summary", "learning_focus", "scope", "sections", "principles"))
    screenshots = as_list(data.get("screenshots"))
    sections = as_list(data["sections"])
    principles = as_list(data["principles"])
    if not sections:
        fail("taste board requires at least one evidence section")
    if not principles:
        fail("taste board requires at least one reusable principle")
    screenshot_html = "".join(render_image(item, input_path.parent) for item in screenshots)
    if not screenshot_html:
        screenshot_html = '<p class="empty">No screenshot evidence available; see gaps.</p>'
    body = """<main>
      <header class="hero">
        <p>VISUAL TASTE BOARD</p><h1>{title}</h1><p>{summary}</p>
        <div class="meta"><span>{captured}</span><span>{scope}</span><a href="{url}">{url}</a></div>
        <div>{focus}</div>
      </header>
      <section><h2>Rendered evidence</h2><div class="grid">{screenshots}</div></section>
      <section><h2>Color roles</h2><div class="swatches">{palette}</div></section>
      <section><h2>Typography ladder</h2>{type_scale}</section>
      <section><h2>Spacing and geometry</h2><div class="metrics">{geometry}</div></section>
      <section><h2>Classified evidence</h2><div class="evidence-grid">{sections}</div></section>
      <section><h2>Transferable principles</h2><div class="principle-grid">{principles}</div></section>
      <section><div class="boundary-grid"><div><h2>Do not copy</h2>{do_not_copy}</div><div><h2>Confidence gaps</h2>{gaps}</div></div></section>
    </main>""".format(
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
    return document(data["title"], body)


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
        return str(option["preview_html"])
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
    document.getElementById('selection').textContent = `Selected option ${id}. Report this option to continue the workflow.`;
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
