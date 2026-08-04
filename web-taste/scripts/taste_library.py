#!/usr/bin/env python3
"""Create, index, and validate Web Taste records and application decisions."""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES = SKILL_ROOT / "references"
SITES = REFERENCES / "sites"
APPLICATIONS = REFERENCES / "applications"
REPORTS = REFERENCES / "reports"
INDEX = REFERENCES / "site-index.md"
PROFILE = REFERENCES / "taste-profile.md"

REQUIRED_SITE_SECTIONS = (
    "Confirmed learning brief",
    "Why it matters",
    "Observed evidence",
    "Visual signature",
    "Reusable principles",
    "Context boundaries",
    "Do not copy",
    "Application cues",
    "Confidence and gaps",
    "User review",
)

REQUIRED_APPLICATION_SECTIONS = (
    "Application brief",
    "Memory fusion",
    "Design thesis",
    "Component decisions",
    "Verification",
)

REVIEW_STATUSES = {"pending", "confirmed", "corrected", "rejected"}
APPLICATION_STATUSES = {"pending", "confirmed", "implemented"}


def quote_yaml(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80] or "record"


def default_slug(url):
    parsed = urlparse(url)
    raw = parsed.netloc + parsed.path.rstrip("/")
    return slugify(raw)


def ensure_new_path(directory, slug):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (slug + ".md")
    if path.exists():
        raise SystemExit("Record already exists: {}".format(path))
    return path


def new_record(args):
    slug = slugify(args.slug) if args.slug else default_slug(args.url)
    path = ensure_new_path(SITES, slug)
    captured_at = args.date or dt.date.today().isoformat()
    content = """---
title: {title}
source_url: {url}
captured_at: {captured_at}
page_type: {page_type}
tags: []
learning_focus: {learning_focus}
learning_scope: {learning_scope}
review_status: "pending"
visual_report: "pending"
---

# {heading}

## Confirmed learning brief

[Record the confirmed focus, scope, states, exclusions, persistence choice, and user confirmation.]

## Why it matters

[Explain why this source is useful and where it may apply.]

## Observed evidence

### Composition and hierarchy

[Observed and measured evidence.]

### Typography

[Observed and measured evidence.]

### Color, imagery, and surfaces

[Observed and measured evidence.]

### Spacing and geometry

[Observed and measured evidence.]

### Components and interaction

[Observed and measured evidence.]

### Responsive behavior

[Desktop/mobile comparison and viewport sizes.]

### Motion

[Triggers, properties, timing, easing, and purpose.]

## Visual signature

[Name the 3-6 distinctive relationships.]

## Reusable principles

### Principle 1

- **Principle**: [Transferable rule.]
- **Evidence**: [Supporting observations.]
- **Use when**: [Suitable context.]
- **Avoid when**: [Unsuitable context.]
- **Implementation cue**: [Practical direction without copied code.]

## Context boundaries

[Separate durable taste from source-specific constraints.]

## Do not copy

[List identity-bearing or protected elements.]

## Application cues

[List suitable targets, pairings, and conflicts.]

## Confidence and gaps

**Confidence**: low

[List missing or uncertain evidence.]

## User review

- **Decision**: pending
- **Corrections**: [Record corrections or none.]
- **Approved profile additions**: [Record approved additions or none.]
- **Conditional preferences**: [Record conditional preferences or none.]
- **Exclusions**: [Record rejected traits or none.]
""".format(
        title=quote_yaml(args.title),
        url=quote_yaml(args.url),
        captured_at=quote_yaml(captured_at),
        page_type=quote_yaml(args.page_type),
        learning_focus=quote_yaml(args.learning_focus),
        learning_scope=quote_yaml(args.learning_scope),
        heading=args.title,
    )
    path.write_text(content, encoding="utf-8")
    print(path)


def new_application(args):
    slug = slugify(args.slug or args.title)
    path = ensure_new_path(APPLICATIONS, slug)
    created_at = args.date or dt.date.today().isoformat()
    content = """---
title: {title}
target: {target}
created_at: {created_at}
status: "pending"
---

# {heading}

## Application brief

- **Product and goal**: [Confirmed goal.]
- **Target users**: [Audience.]
- **Scope**: [Pages or components.]
- **Functionality to preserve**: [Existing behavior.]
- **Constraints**: [Content, assets, accessibility, and responsive needs.]
- **Desired character**: [Emotional and visual goal.]
- **Influence strength**: [Light, balanced, or strong.]
- **Exclusions**: [Explicit exclusions.]
- **Deliverable and validation target**: [Expected output and evidence.]
- **Confirmation**: pending

## Memory fusion

| Source | Why it matches | Relationships to reuse | Exclusions | Conflict |
| --- | --- | --- | --- | --- |
| [Source record] | [Fit] | [Transferable relationships] | [Excluded traits] | [Conflict or none] |

## Design thesis

[Product character, hierarchy, rhythm, typography, color, surfaces, components, and motion.]

## Component decisions

[For each consequential choice, record selected option, accepted aspects, rejected alternatives, rationale, scope, and source influences.]

## Verification

[Record desktop/mobile evidence, states, accessibility, preserved behavior, and remaining gaps.]
""".format(
        title=quote_yaml(args.title),
        target=quote_yaml(args.target),
        created_at=quote_yaml(created_at),
        heading=args.title,
    )
    path.write_text(content, encoding="utf-8")
    print(path)


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    data = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        data[key.strip()] = value
    return data, text[end + 5 :]


def display_tags(raw):
    if not raw or raw == "[]":
        return "-"
    return raw.strip("[]").replace('"', "").replace("'", "") or "-"


def markdown_paths(directory):
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.md") if path.name != "index.md")


def record_paths():
    return markdown_paths(SITES)


def application_paths():
    return markdown_paths(APPLICATIONS)


def build_index(_args=None):
    rows = []
    for path in record_paths():
        meta, _ = parse_frontmatter(path)
        values = (
            meta.get("title", path.stem),
            meta.get("page_type", "unknown"),
            meta.get("captured_at", "unknown"),
            display_tags(meta.get("tags", "[]")),
            meta.get("learning_focus", "unknown"),
            meta.get("review_status", "unknown"),
        )
        escaped = [value.replace("|", "\\|") for value in values]
        rows.append(
            "| {} | {} | {} | {} | {} | {} | [Open](sites/{}) |".format(
                *escaped, path.name
            )
        )

    body = [
        "# Site Index",
        "",
        "Generated by `python3 scripts/taste_library.py index`. Do not edit the table manually.",
        "",
        "| Source | Page type | Captured | Tags | Learning focus | Review | Record |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    body.extend(rows)
    body.append("")
    INDEX.write_text("\n".join(body), encoding="utf-8")
    print("Indexed {} record(s) in {}".format(len(rows), INDEX))


def has_section(body, heading):
    return re.search(r"^## {}\s*$".format(re.escape(heading)), body, re.MULTILINE)


def validate_meta(path, meta, required, errors):
    for key in required:
        if key not in meta:
            errors.append("{}: missing frontmatter key '{}'".format(path, key))


def validate(_args=None):
    errors = []
    if not PROFILE.exists():
        errors.append("Missing {}".format(PROFILE))
    if not INDEX.exists():
        errors.append("Missing {}".format(INDEX))

    placeholder = re.compile(r"\[[^\]\n]+\]")
    site_meta = (
        "title",
        "source_url",
        "captured_at",
        "page_type",
        "tags",
        "learning_focus",
        "learning_scope",
        "review_status",
        "visual_report",
    )
    for path in record_paths():
        meta, body = parse_frontmatter(path)
        validate_meta(path, meta, site_meta, errors)
        for heading in REQUIRED_SITE_SECTIONS:
            if not has_section(body, heading):
                errors.append("{}: missing section '## {}'".format(path, heading))

        review_status = meta.get("review_status")
        if review_status and review_status not in REVIEW_STATUSES:
            errors.append("{}: invalid review_status '{}'".format(path, review_status))
        if review_status in {"confirmed", "corrected"}:
            report = meta.get("visual_report")
            if report == "pending" or not report:
                errors.append("{}: reviewed record has no visual report".format(path))
            elif report != "not-created-legacy":
                report_path = Path(report)
                if not report_path.is_absolute():
                    report_path = REFERENCES / report_path
                if not report_path.exists():
                    errors.append("{}: visual report does not exist: {}".format(path, report))
            if placeholder.search(body):
                errors.append("{}: reviewed record contains placeholder text".format(path))

    application_meta = ("title", "target", "created_at", "status")
    for path in application_paths():
        meta, body = parse_frontmatter(path)
        validate_meta(path, meta, application_meta, errors)
        for heading in REQUIRED_APPLICATION_SECTIONS:
            if not has_section(body, heading):
                errors.append("{}: missing section '## {}'".format(path, heading))
        status = meta.get("status")
        if status and status not in APPLICATION_STATUSES:
            errors.append("{}: invalid application status '{}'".format(path, status))
        if status == "implemented" and placeholder.search(body):
            errors.append("{}: implemented application contains placeholder text".format(path))

    if errors:
        for error in errors:
            print("ERROR: " + error, file=sys.stderr)
        raise SystemExit(1)
    print(
        "Validated {} source record(s) and {} application record(s).".format(
            len(record_paths()), len(application_paths())
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="Create a confirmed-learning source scaffold")
    new_parser.add_argument("--title", required=True)
    new_parser.add_argument("--url", required=True)
    new_parser.add_argument("--learning-focus", required=True)
    new_parser.add_argument("--learning-scope", required=True)
    new_parser.add_argument("--slug")
    new_parser.add_argument("--date")
    new_parser.add_argument("--page-type", default="unknown")
    new_parser.set_defaults(func=new_record)

    app_parser = subparsers.add_parser(
        "new-application", help="Create an application brief and decision scaffold"
    )
    app_parser.add_argument("--title", required=True)
    app_parser.add_argument("--target", required=True)
    app_parser.add_argument("--slug")
    app_parser.add_argument("--date")
    app_parser.set_defaults(func=new_application)

    index_parser = subparsers.add_parser("index", help="Rebuild the Markdown source index")
    index_parser.set_defaults(func=build_index)

    validate_parser = subparsers.add_parser("validate", help="Validate the taste library")
    validate_parser.set_defaults(func=validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
