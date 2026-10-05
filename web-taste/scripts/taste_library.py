#!/usr/bin/env python3
"""Create, index, and validate Web Taste records and application decisions."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "references"


def default_library_root():
    override = os.environ.get("WEB_TASTE_LIBRARY_ROOT")
    if override:
        return Path(override).expanduser()
    data_home = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    return data_home / "web-taste"


def configure_library(root):
    global LIBRARY_ROOT, SITES, APPLICATIONS, REPORTS, INDEX, PROFILE, DECISIONS
    LIBRARY_ROOT = Path(root).expanduser().resolve()
    SITES = LIBRARY_ROOT / "sites"
    APPLICATIONS = LIBRARY_ROOT / "applications"
    REPORTS = LIBRARY_ROOT / "reports"
    INDEX = LIBRARY_ROOT / "site-index.md"
    PROFILE = LIBRARY_ROOT / "taste-profile.md"
    DECISIONS = LIBRARY_ROOT / "decisions.jsonl"


configure_library(default_library_root())


def require_private_root():
    if LIBRARY_ROOT == SKILL_ROOT or SKILL_ROOT in LIBRARY_ROOT.parents:
        raise SystemExit("Personal memory must be stored outside the skill installation")


def initialize_library(_args=None):
    require_private_root()
    for folder in (LIBRARY_ROOT, SITES, APPLICATIONS, REPORTS):
        folder.mkdir(parents=True, exist_ok=True)
    for name in ("taste-profile.md", "site-index.md"):
        path = LIBRARY_ROOT / name
        if not path.exists():
            path.write_text((TEMPLATES / name).read_text(encoding="utf-8"), encoding="utf-8")
    if not DECISIONS.exists():
        DECISIONS.write_text("", encoding="utf-8")
    if _args is not None:
        print(LIBRARY_ROOT)


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
    return json.dumps(value, ensure_ascii=False)


def slugify(value):
    value = re.sub(r"^https?://", "", value.lower().strip())
    value = re.sub(r"[^\w-]+", "-", value, flags=re.UNICODE).strip("-_")
    return value[:64] or "record"


def default_slug(url):
    parsed = urlparse(url)
    identity = parsed._replace(fragment="").geturl()
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:10]
    return slugify(parsed.netloc + parsed.path.rstrip("/")) + "-" + digest


def valid_url(value):
    if not isinstance(value, str) or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and parsed.port != 0
    except ValueError:
        return False


def valid_date(value):
    try:
        return isinstance(value, str) and dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def ensure_new_path(directory, slug):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (slug + ".md")
    if path.exists():
        raise SystemExit("Record already exists: {}".format(path))
    return path


def new_record(args):
    if any(not getattr(args, field).strip() for field in ("title", "learning_focus", "learning_scope", "page_type")):
        raise SystemExit("Title, learning focus, scope and page type must be non-empty")
    if not valid_url(args.url):
        raise SystemExit("Source URL must be an absolute HTTP(S) URL")
    if args.date and not valid_date(args.date):
        raise SystemExit("Date must be YYYY-MM-DD")
    initialize_library()
    slug = slugify(args.slug) if args.slug else default_slug(args.url)
    path = ensure_new_path(SITES, slug)
    captured_at = args.date or dt.date.today().isoformat()
    content = """---
schema_version: 2
title: {title}
source_url: {url}
captured_at: {captured_at}
page_type: {page_type}
tags: []
information_density: "unknown"
content_shape: "unknown"
interaction_model: "unknown"
emotional_goal: "unknown"
learning_focus: {learning_focus}
learning_scope: {learning_scope}
review_status: "pending"
visual_report: "pending"
---

# {heading}

## Confirmed learning brief

TODO: Record the confirmed focus, scope, states, exclusions, persistence choice, and user confirmation.

## Why it matters

TODO: Explain why this source is useful and where it may apply.

## Observed evidence

### Composition and hierarchy

TODO: Observed and measured evidence.

### Typography

TODO: Observed and measured evidence.

### Color, imagery, and surfaces

TODO: Observed and measured evidence.

### Spacing and geometry

TODO: Observed and measured evidence.

### Components and interaction

TODO: Observed and measured evidence.

### Responsive behavior

TODO: Desktop/mobile comparison and viewport sizes.

### Motion

TODO: Triggers, properties, timing, easing, and purpose.

## Visual signature

TODO: Name the 3-6 distinctive relationships.

## Reusable principles

### Principle 1

- **ID**: TODO: Stable principle ID matching the visual report.
- **Evidence refs**: TODO: Evidence IDs from the visual report.
- **Observation confidence**: low
- **User decision**: pending
- **Scope**: unapproved until the user specifies global or project:name.

- **Principle**: TODO: Transferable rule.
- **Evidence**: TODO: Supporting observations.
- **Use when**: TODO: Suitable context.
- **Avoid when**: TODO: Unsuitable context.
- **Implementation cue**: TODO: Practical direction without copied code.

## Context boundaries

TODO: Separate durable taste from source-specific constraints.

## Do not copy

TODO: List identity-bearing or protected elements.

## Application cues

TODO: List suitable targets, pairings, and conflicts.

## Confidence and gaps

**Confidence**: low

TODO: List missing or uncertain evidence.

## User review

- **Decision**: pending
- **Corrections**: TODO: Record corrections or none.
- **Approved profile additions**: TODO: Record approved additions or none.
- **Conditional preferences**: TODO: Record conditional preferences or none.
- **Exclusions**: TODO: Record rejected traits or none.
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
    if args.date and not valid_date(args.date):
        raise SystemExit("Date must be YYYY-MM-DD")
    if not args.title.strip() or not args.target.strip():
        raise SystemExit("Title and target must be non-empty")
    initialize_library()
    slug = slugify(args.slug) if args.slug else slugify(args.title) + "-" + uuid.uuid4().hex[:10]
    path = ensure_new_path(APPLICATIONS, slug)
    created_at = args.date or dt.date.today().isoformat()
    content = """---
schema_version: 2
title: {title}
target: {target}
created_at: {created_at}
status: "pending"
---

# {heading}

## Application brief

- **Product and goal**: TODO: Confirmed goal.
- **Target users**: TODO: Audience.
- **Scope**: TODO: Pages or components.
- **Functionality to preserve**: TODO: Existing behavior.
- **Constraints**: TODO: Content, assets, accessibility, and responsive needs.
- **Desired character**: TODO: Emotional and visual goal.
- **Influence strength**: TODO: Light, balanced, or strong.
- **Exclusions**: TODO: Explicit exclusions.
- **Deliverable and validation target**: TODO: Expected output and evidence.
- **Confirmation**: pending

## Memory fusion

| Source | Why it matches | Relationships to reuse | Exclusions | Conflict |
| --- | --- | --- | --- | --- |
| TODO: Source record | TODO: Fit | TODO: Transferable relationships | TODO: Excluded traits | TODO: Conflict or none |

## Design thesis

TODO: Product character, hierarchy, rhythm, typography, color, surfaces, components, and motion.

## Component decisions

TODO: For each consequential choice, record selected option, accepted aspects, rejected alternatives, rationale, scope, and source influences.

## Verification

TODO: Record desktop/mobile evidence, states, accessibility, preserved behavior, and remaining gaps.
""".format(
        title=quote_yaml(args.title),
        target=quote_yaml(args.target),
        created_at=quote_yaml(created_at),
        heading=args.title,
    )
    path.write_text(content, encoding="utf-8")
    print(path)


def parse_value(value):
    """Parse the documented flat YAML subset, not arbitrary nested YAML."""
    value = value.strip()
    if value.startswith('"'):
        decoded = json.loads(value)
        if not isinstance(decoded, str):
            raise ValueError("expected a quoted string")
        return decoded
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ValueError("unterminated single-quoted string")
        inner = value[1:-1]
        if "'" in inner.replace("''", ""):
            raise ValueError("single quotes must be doubled")
        return inner.replace("''", "'")
    if value.startswith("["):
        if not value.endswith("]"):
            raise ValueError("unterminated list")
        inner = value[1:-1].strip()
        if not inner:
            return []
        tokens, start, quote = [], 0, None
        index = 0
        while index < len(inner):
            char = inner[index]
            if quote:
                if quote == '"' and char == "\\":
                    index += 2
                    continue
                if char == quote:
                    if quote == "'" and index + 1 < len(inner) and inner[index + 1] == "'":
                        index += 2
                        continue
                    quote = None
            elif char in "\"'":
                quote = char
            elif char == ",":
                tokens.append(inner[start:index])
                start = index + 1
            index += 1
        if quote:
            raise ValueError("unterminated list string")
        tokens.append(inner[start:])
        result = [parse_value(token) for token in tokens]
        if any(not isinstance(item, str) or not item for item in result):
            raise ValueError("lists must contain non-empty strings")
        return result
    if not value or value in {"null", "~"}:
        return ""
    if value.startswith(("{", "|", ">", "&", "*", "!")):
        raise ValueError("nested YAML, block scalars and aliases are unsupported")
    return value.split(" #", 1)[0].strip()


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unclosed frontmatter")
    data = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line != line.lstrip() or ":" not in line:
            raise ValueError("metadata must use flat key: value lines")
        key, value = line.split(":", 1)
        if not re.fullmatch(r"[a-z_]+", key) or key in data:
            raise ValueError("invalid or duplicate metadata key: " + key)
        data[key] = parse_value(value)
    return data, text[end + 5:]


def display_tags(raw):
    return ", ".join(raw) if isinstance(raw, list) and raw else "-"


def markdown_paths(directory):
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.md") if path.name != "index.md")


def record_paths():
    return markdown_paths(SITES)


def application_paths():
    return markdown_paths(APPLICATIONS)


def build_index(_args=None):
    require_private_root()
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
        escaped = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
        rows.append(
            "| {} | {} | {} | {} | {} | {} | [Open](sites/{}) |".format(
                *escaped, path.name
            )
        )

    body = [
        "# Site Index",
        "",
        "Generated by `taste_library.py index` in the private library. Do not edit the table manually.",
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


# Only these old scaffold markers are placeholders; Markdown links remain valid.
LEGACY_MARKERS = {
    'Audience.',
    'Confirmed goal.',
    'Conflict or none',
    'Content, assets, accessibility, and responsive needs.',
    'Desktop/mobile comparison and viewport sizes.',
    'Emotional and visual goal.',
    'Excluded traits',
    'Existing behavior.',
    'Expected output and evidence.',
    'Explain why this source is useful and where it may apply.',
    'Explicit exclusions.',
    'Fit',
    'For each consequential choice, record selected option, accepted aspects, rejected alternatives, rationale, scope, and source influences.',
    'Light, balanced, or strong.',
    'List identity-bearing or protected elements.',
    'List missing or uncertain evidence.',
    'List suitable targets, pairings, and conflicts.',
    'Name the 3-6 distinctive relationships.',
    'Observed and measured evidence.',
    'Pages or components.',
    'Practical direction without copied code.',
    'Product character, hierarchy, rhythm, typography, color, surfaces, components, and motion.',
    'Record approved additions or none.',
    'Record conditional preferences or none.',
    'Record corrections or none.',
    'Record desktop/mobile evidence, states, accessibility, preserved behavior, and remaining gaps.',
    'Record rejected traits or none.',
    'Record the confirmed focus, scope, states, exclusions, persistence choice, and user confirmation.',
    'Separate durable taste from source-specific constraints.',
    'Source record',
    'Suitable context.',
    'Supporting observations.',
    'Transferable relationships',
    'Transferable rule.',
    'Triggers, properties, timing, easing, and purpose.',
    'Unsuitable context.',
}


def has_placeholder(body):
    return bool(re.search(r"\bTODO:", body) or any(
        token in LEGACY_MARKERS for token in re.findall(r"\[([^\]\n]+)\](?!\()", body)
    ))


def validate_meta(path, meta, required, errors):
    for key in required:
        value = meta.get(key)
        if key == "tags":
            if not isinstance(value, list) or any(not isinstance(tag, str) or not tag.strip() for tag in value):
                errors.append("{}: tags must be a string list".format(path))
        elif not isinstance(value, str) or not value.strip():
            errors.append("{}: missing or empty metadata '{}'".format(path, key))


class BoardMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.inside = tag == "script" and dict(attrs).get("id") == "web-taste-data"

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False


def report_path(meta):
    path = Path(meta["visual_report"]).expanduser()
    return path if path.is_absolute() else LIBRARY_ROOT / path


def read_board(meta):
    parser = BoardMetadataParser()
    parser.feed(report_path(meta).read_text(encoding="utf-8"))
    if not parser.parts:
        raise ValueError("report has no structured evidence; regenerate before approving principles")
    data = json.loads("".join(parser.parts))
    if not isinstance(data, dict) or data.get("status") != "reviewable":
        raise ValueError("report must be reviewable before approving principles")
    # Revalidate the embedded contract independently of the visible status label.
    from render_visual import validate_board
    validate_board(data)
    if data.get("source_url") != meta.get("source_url"):
        raise ValueError("report source URL does not match the source record")
    if meta.get("captured_at") and data.get("captured_at") != meta["captured_at"]:
        raise ValueError("report capture date does not match the source record")
    return data


def site_errors(path):
    errors = []
    try:
        meta, body = parse_frontmatter(path)
    except (ValueError, OSError) as error:
        return ["{}: {}".format(path, error)]
    required = ("title", "source_url", "captured_at", "page_type", "tags", "learning_focus",
                "learning_scope", "review_status", "visual_report")
    if meta.get("schema_version") not in {None, "2"}:
        errors.append("{}: unsupported schema_version".format(path))
    if meta.get("schema_version") == "2":
        required += ("information_density", "content_shape", "interaction_model", "emotional_goal")
    validate_meta(path, meta, required, errors)
    if not valid_url(meta.get("source_url")):
        errors.append("{}: invalid source_url".format(path))
    if not valid_date(meta.get("captured_at")):
        errors.append("{}: invalid captured_at".format(path))
    for heading in REQUIRED_SITE_SECTIONS:
        if not has_section(body, heading):
            errors.append("{}: missing section '## {}'".format(path, heading))
    status = meta.get("review_status")
    if status not in REVIEW_STATUSES:
        errors.append("{}: invalid review_status".format(path))
    if status in {"confirmed", "corrected"}:
        report = meta.get("visual_report")
        if not report or report == "pending":
            errors.append("{}: reviewed record has no visual report".format(path))
        elif report == "not-created-legacy":
            if meta.get("schema_version") == "2":
                errors.append("{}: new records cannot bypass visual review".format(path))
        elif not report_path(meta).is_file():
            errors.append("{}: visual report does not exist".format(path))
        elif meta.get("schema_version") == "2":
            try:
                read_board(meta)
            except (ValueError, OSError, SystemExit) as error:
                errors.append("{}: {}".format(path, error))
        if has_placeholder(body):
            errors.append("{}: reviewed record contains placeholder text".format(path))
    return errors


def load_decisions(path=None):
    path = path or DECISIONS
    if not path.exists():
        return []
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = json.loads(line)
            required = ("source", "principle_id", "scope", "decision", "user_words", "recorded_at")
            if not isinstance(event, dict) or any(not isinstance(event.get(key), str) or not event[key].strip() for key in required):
                raise ValueError("missing decision fields")
            if event["decision"] not in {"approved", "rejected", "revoked"}:
                raise ValueError("invalid decision")
            if not re.fullmatch(r"[\w-]+", event["source"]) or not re.fullmatch(r"[\w-]+", event["principle_id"]):
                raise ValueError("invalid source or principle ID")
            if event["scope"] != "global" and not re.fullmatch(r"project:[^\n]+", event["scope"]):
                raise ValueError("scope must be global or project:name")
            dt.datetime.fromisoformat(event["recorded_at"])
            if event["decision"] != "revoked":
                principle = event.get("principle")
                fields = ("title", "evidence", "use_when", "avoid_when", "implementation_cue", "confidence")
                if (not isinstance(principle, dict)
                        or any(not isinstance(principle.get(key), str) or not principle[key].strip() for key in fields)
                        or principle.get("id") != event["principle_id"]
                        or principle["confidence"] not in {"high", "medium", "low"}
                        or not isinstance(principle.get("evidence_refs"), list)
                        or not principle["evidence_refs"]
                        or any(not isinstance(ref, str) or not ref.strip() for ref in principle["evidence_refs"])
                        or not re.fullmatch(r"[a-f0-9]{64}", str(event.get("report_sha256", "")))):
                    raise ValueError("missing principle snapshot")
            events.append(event)
        except (ValueError, TypeError) as error:
            raise ValueError("decisions.jsonl line {}: {}".format(number, error))
    return events


def latest_decisions():
    latest = {}
    for event in load_decisions():
        latest[(event["source"], event["principle_id"], event["scope"])] = event
    return list(latest.values())


def eligible_decisions(scope="global"):
    return [event for event in latest_decisions()
            if event["scope"] in {"global", scope} and event["decision"] != "revoked"]


def rebuild_profile(_args=None):
    require_private_root()
    lines = ["# Taste Profile", "", "Generated from explicit, scoped user decisions. Do not edit manually.", ""]
    if (LIBRARY_ROOT / "legacy-profile.md").exists():
        lines += ["[Archived legacy profile](legacy-profile.md): retained for review, not automatically promoted.", ""]
    for decision, heading in (("approved", "Approved principles"), ("rejected", "Explicit exclusions")):
        lines += ["## " + heading, ""]
        matches = [event for event in latest_decisions() if event["decision"] == decision]
        if not matches:
            lines += ["No explicit decisions yet.", ""]
        for event in matches:
            source = SITES / (event["source"] + ".md")
            if not source.is_file():
                continue
            meta, _ = parse_frontmatter(source)
            if meta.get("review_status") not in {"confirmed", "corrected"} and decision == "approved":
                continue
            principle = event["principle"]
            lines += ["### " + str(principle["title"]), "",
                      "- ID: `{} / {}`".format(event["source"], event["principle_id"]),
                      "- Scope: " + event["scope"],
                      "- User decision: " + event["user_words"],
                      "- Observation confidence: " + str(principle.get("confidence", "unknown")),
                      "- Use when: " + str(principle.get("use_when", "")),
                      "- Avoid when: " + str(principle.get("avoid_when", "")),
                      "- Implementation cue: " + str(principle.get("implementation_cue", "")),
                      "- Evidence: " + ", ".join(principle["evidence_refs"]),
                      "- Source: [Open](sites/{}.md)".format(event["source"]), ""]
    PROFILE.write_text("\n".join(lines), encoding="utf-8")


def record_decision(args):
    if not re.fullmatch(r"[\w-]+", args.source) or not re.fullmatch(r"[\w-]+", args.principle_id):
        raise SystemExit("Source and principle IDs must contain only letters, digits, underscores or hyphens")
    if not args.user_words.strip():
        raise SystemExit("Record the user's explicit decision in --user-words")
    if args.scope != "global" and not re.fullmatch(r"project:[^\n]+", args.scope):
        raise SystemExit("Scope must be global or project:name")
    initialize_library()
    source = SITES / (args.source + ".md")
    key = (args.source, args.principle_id, args.scope)
    previous = next((event for event in latest_decisions() if (event["source"], event["principle_id"], event["scope"]) == key), None)
    event = dict(source=args.source, principle_id=args.principle_id, scope=args.scope,
                 decision=args.decision, user_words=args.user_words,
                 recorded_at=dt.datetime.now(dt.timezone.utc).isoformat())
    if args.decision == "revoked":
        if not previous or previous["decision"] == "revoked":
            raise SystemExit("No active decision to revoke for this principle and scope")
    else:
        errors = site_errors(source)
        if errors:
            raise SystemExit("\n".join(errors))
        meta, _ = parse_frontmatter(source)
        allowed = {"confirmed", "corrected", "rejected"} if args.decision == "rejected" else {"confirmed", "corrected"}
        if meta.get("review_status") not in allowed:
            raise SystemExit("Review the source record before recording a principle decision")
        try:
            board = read_board(meta)
        except (ValueError, OSError) as error:
            raise SystemExit(str(error))
        principle = next((item for item in board["principles"] if item["id"] == args.principle_id), None)
        if principle is None:
            raise SystemExit("Principle ID is absent from the visual report")
        event["principle"] = principle
        event["report_sha256"] = hashlib.sha256(report_path(meta).read_bytes()).hexdigest()
    with DECISIONS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    rebuild_profile()
    print("{}: {} ({})".format(args.principle_id, args.decision, args.scope))


def search(args):
    if args.scope != "global" and not re.fullmatch(r"project:[^\n]+", args.scope):
        raise SystemExit("Scope must be global or project:name")
    query = args.query.lower().strip()
    approved = {}
    excluded = {}
    # Project-specific choices override global choices for the same principle.
    applicable = sorted(eligible_decisions(args.scope), key=lambda event: event["scope"] != "global")
    effective = {}
    for event in applicable:
        effective[(event["source"], event["principle_id"])] = event
    for event in effective.values():
        target = approved if event["decision"] == "approved" else excluded
        target.setdefault(event["source"], []).append(event["principle"])
    rows = []
    for path in record_paths():
        if site_errors(path):
            continue
        meta, _ = parse_frontmatter(path)
        if meta.get("review_status") not in {"confirmed", "corrected"}:
            continue
        principles = approved.get(path.stem, [])
        if not principles:
            continue
        fields = [meta.get(key, "") for key in ("title", "page_type", "learning_focus", "information_density", "content_shape", "interaction_model", "emotional_goal")]
        fields += meta.get("tags", [])
        fields += [item.get(key, "") for item in principles for key in ("title", "use_when", "implementation_cue")]
        text = " ".join(str(value).lower() for value in fields)
        terms = query.split()
        score = sum(text.count(term) for term in terms)
        if query and score == 0:
            continue
        rows.append(dict(source=path.stem, title=meta["title"], record=str(path), score=score,
                         principles=principles, exclusions=excluded.get(path.stem, [])))
    rows.sort(key=lambda row: (-row["score"], row["source"]))
    exclusions = [dict(source=event["source"], scope=event["scope"], principle=event["principle"])
                  for event in effective.values() if event["decision"] == "rejected"
                  and not site_errors(SITES / (event["source"] + ".md"))]
    print(json.dumps(dict(matches=rows[:args.limit], exclusions=exclusions,
                         message="" if rows else "No approved matching memory. Proceed from the current brief; do not invent or pad sources."), ensure_ascii=False, indent=2))


def validate(_args=None):
    errors = []
    for path in (PROFILE, INDEX):
        if not path.is_file():
            errors.append("Missing {}; run init or migrate first".format(path))
    for path in record_paths():
        errors += site_errors(path)
    for path in application_paths():
        try:
            meta, body = parse_frontmatter(path)
        except (ValueError, OSError) as error:
            errors.append("{}: {}".format(path, error))
            continue
        validate_meta(path, meta, ("title", "target", "created_at", "status"), errors)
        if not valid_date(meta.get("created_at")):
            errors.append("{}: invalid created_at".format(path))
        for heading in REQUIRED_APPLICATION_SECTIONS:
            if not has_section(body, heading):
                errors.append("{}: missing section '{}'".format(path, heading))
        if meta.get("status") not in APPLICATION_STATUSES:
            errors.append("{}: invalid application status".format(path))
        if meta.get("status") == "implemented" and has_placeholder(body):
            errors.append("{}: implemented application contains placeholder text".format(path))
        if meta.get("status") == "confirmed":
            brief = body.split("## Application brief", 1)[-1].split("## Design thesis", 1)[0]
            if has_placeholder(brief) or "**Confirmation**: pending" in brief:
                errors.append("{}: confirmed application has an unfinished brief or fusion".format(path))
    try:
        for event in load_decisions():
            if not (SITES / (event["source"] + ".md")).is_file():
                errors.append("Decision references missing source: " + event["source"])
    except ValueError as error:
        errors.append(str(error))
    if errors:
        raise SystemExit("\n".join("ERROR: " + error for error in errors))
    print("Validated {} source record(s), {} application record(s) and decision log.".format(len(record_paths()), len(application_paths())))


def migrate(args):
    require_private_root()
    source = args.from_root.expanduser().resolve()
    if source == LIBRARY_ROOT or source in LIBRARY_ROOT.parents or LIBRARY_ROOT in source.parents:
        raise SystemExit("Migration source and destination must be separate, non-nested directories")
    if not source.is_dir():
        raise SystemExit("Legacy library does not exist: " + str(source))
    files = []
    for folder in ("sites", "reports", "applications"):
        if (source / folder).exists():
            files += [(path, path.relative_to(source)) for path in (source / folder).rglob("*") if path.is_file() and path.name != ".gitkeep"]
    if (source / "taste-profile.md").is_file():
        files.append((source / "taste-profile.md", Path("legacy-profile.md")))
    if (source / "decisions.jsonl").is_file():
        files.append((source / "decisions.jsonl", Path("decisions.jsonl")))
    if not files:
        raise SystemExit("No legacy memory files found")
    marker = LIBRARY_ROOT / "migrations" / (hashlib.sha256(str(source).encode()).hexdigest()[:12] + ".json")
    fingerprints = {str(relative): hashlib.sha256(path.read_bytes()).hexdigest() for path, relative in files}
    if marker.exists():
        previous = json.loads(marker.read_text(encoding="utf-8"))
        if previous["files"] != fingerprints:
            raise SystemExit("Legacy source changed since migration; use a separate destination to review changes")
        missing = [str(relative) for _, relative in files if not (LIBRARY_ROOT / relative).is_file()]
        if missing:
            raise SystemExit("Migrated files are missing: " + ", ".join(missing))
        print("Already migrated; existing memory preserved")
        return
    conflicts = [str(relative) for _, relative in files if (LIBRARY_ROOT / relative).exists() and (relative != Path("decisions.jsonl") or (LIBRARY_ROOT / relative).stat().st_size)]
    if conflicts:
        raise SystemExit("Migration would overwrite existing data: " + ", ".join(conflicts))
    # Parse and prepare all metadata before writing, so a malformed record cannot
    # strand a partial import. Preserve exact source bytes in the backup.
    if (source / "decisions.jsonl").is_file():
        imported_decisions = load_decisions(source / "decisions.jsonl")
        if any(not (source / "sites" / (event["source"] + ".md")).is_file() for event in imported_decisions):
            raise SystemExit("Legacy decision log references missing source records")
    for existing in record_paths():
        parse_frontmatter(existing)
    rewrites = {}
    for path, relative in files:
        if relative.parts[0] in {"sites", "applications"} and path.suffix == ".md":
            meta, _ = parse_frontmatter(path)
            old_report = meta.get("visual_report", "")
            if old_report and Path(old_report).is_absolute():
                try:
                    new_report = str(Path(old_report).resolve().relative_to(source))
                except ValueError:
                    continue
                rewrites[relative] = re.sub(r"^visual_report:.*$", lambda _: "visual_report: " + quote_yaml(new_report), path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    # Snapshot everything being imported before writing runtime data; leave source intact.
    backup = LIBRARY_ROOT / "backups" / uuid.uuid4().hex
    for path, relative in files:
        target = backup / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    initialize_library()
    for path, relative in files:
        target = LIBRARY_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        if relative in rewrites:
            target.write_text(rewrites[relative], encoding="utf-8")
    build_index()
    rebuild_profile()
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(dict(source=str(source), backup=str(backup), files=fingerprints), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Migrated {} files; backup: {}".format(len(files), backup))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library-root", type=Path, default=default_library_root(), help="User data directory, independent of skill installation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="Initialize without overwriting existing memory")
    init_parser.set_defaults(func=initialize_library)
    root_parser = subparsers.add_parser("root", help="Print the resolved data directory without creating it")
    root_parser.set_defaults(func=lambda _args: print(LIBRARY_ROOT))
    migration_parser = subparsers.add_parser("migrate", help="Back up and copy an old library without deleting it")
    migration_parser.add_argument("--from", dest="from_root", type=Path, required=True)
    migration_parser.set_defaults(func=migrate)
    search_parser = subparsers.add_parser("search", help="Find explicitly approved, applicable principles")
    search_parser.add_argument("--query", default="")
    search_parser.add_argument("--scope", default="global")
    search_parser.add_argument("--limit", type=int, choices=range(1, 5), default=4)
    search_parser.set_defaults(func=search)
    review_parser = subparsers.add_parser("review", help="Record an explicit user decision for one principle and scope")
    review_parser.add_argument("--source", required=True)
    review_parser.add_argument("--principle-id", required=True)
    review_parser.add_argument("--scope", required=True)
    review_parser.add_argument("--decision", choices=("approved", "rejected", "revoked"), required=True)
    review_parser.add_argument("--user-words", required=True)
    review_parser.set_defaults(func=record_decision)
    profile_parser = subparsers.add_parser("profile", help="Rebuild the profile from recorded user decisions")
    profile_parser.set_defaults(func=rebuild_profile)

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
    configure_library(args.library_root)
    if args.command in {"init", "new", "new-application"} and not INDEX.exists():
        legacy_files = list((TEMPLATES / "sites").glob("*.md")) + list((TEMPLATES / "applications").glob("*.md"))
        if legacy_files:
            raise SystemExit("Legacy memory detected. Run migrate --from {} before creating a new library".format(TEMPLATES))
    try:
        args.func(args)
    except (ValueError, OSError) as error:
        raise SystemExit("ERROR: " + str(error))


if __name__ == "__main__":
    main()
