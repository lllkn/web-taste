# Site Record Schema

Use this schema for every file in the private library’s `sites/`. The helper script creates the frontmatter and headings; replace every `TODO:` marker with evidence or an explicit out-of-scope note.

## Required frontmatter

```yaml
---
schema_version: 2
title: "Human-readable page or product name"
source_url: "https://example.com/final-url"
captured_at: "YYYY-MM-DD"
page_type: "landing-page"
tags: ["editorial", "high-contrast", "motion-light"]
information_density: "low"
content_shape: "narrative"
interaction_model: "scroll"
emotional_goal: "restrained"
learning_focus: "layout, typography, motion"
learning_scope: "current page; desktop and mobile; primary interactions"
review_status: "pending"
visual_report: "pending"
---
```

Use the final navigated URL. Keep tags lowercase and concrete. Useful page types include `landing-page`, `editorial`, `portfolio`, `commerce`, `dashboard`, `tool`, `documentation`, and `mobile-web`.

Set `review_status` to `confirmed`, `corrected`, `rejected`, or `pending`. A confirmed or corrected record must link to its self-contained Visual Taste Board through `visual_report`. Use `not-created-legacy` only for historical records without `schema_version: 2`. New reviewed records require a structured `reviewable` Board matching the source URL and capture date. `visual_report` is relative to the private library root, e.g. `reports/reference.html`, or an absolute local file path.

## Metadata format

The standard-library helper supports flat YAML-style `key: value` lines, double-quoted JSON strings, single-quoted strings with doubled apostrophes, bare scalar strings, and inline string lists (quoted or bare items). Metadata is not arbitrary YAML: nested mappings, multiline/block values, aliases and duplicate keys are rejected. Use the Markdown body for long descriptions. URL, ISO date, status, tag-list type and required non-empty fields are checked.

Scaffolds use `TODO:` markers. Ordinary Markdown links, image links and bracketed prose are not placeholders. Legacy scaffold markers are still recognized. Schema v2 records also carry retrieval dimensions; leave an unmeasured dimension `unknown`, not an invented value.

## Required sections

### Confirmed learning brief

Record what the user asked the skill to learn, the inspected page and state scope, exclusions, persistence choice, and the original request or clarification that resolved the scope.

### Why it matters

State why this source is worth retaining and which product contexts it may inform. Do not claim user preference unless the user explicitly said so.

### Observed evidence

Cover these subsections:

- `Composition and hierarchy`
- `Typography`
- `Color, imagery, and surfaces`
- `Spacing and geometry`
- `Components and interaction`
- `Responsive behavior`
- `Motion`

Include representative computed values and viewport dimensions where available. Write facts, not praise.

### Visual signature

Name the 3-6 relationships that make the page distinctive. Describe combinations, such as a narrow editorial measure paired with oversized media and restrained controls.

### Reusable principles

For each principle include:

- **ID**: a stable principle ID matching the report.
- **Evidence refs**: observed/measured evidence IDs in the report.
- **Observation confidence**: high, medium or low; separate from approval.
- **User decision and scope**: pending until explicitly endorsed; global or project:name.
- **Principle**: a transferable design rule.
- **Evidence**: the observations supporting it.
- **Use when**: suitable products, content, or states.
- **Avoid when**: contexts where it becomes harmful or incoherent.
- **Implementation cue**: a practical CSS, layout, component, or motion direction without copying source code.

### Context boundaries

Separate durable ideas from choices caused by the source's brand, audience, content volume, technology, campaign, or business model.

### Do not copy

List protected or identity-bearing elements: logos, wordmarks, brand copy, proprietary images, illustrations, icons, distinctive branded motifs, and source code.

### Application cues

List target page types and features that could benefit from this source. Note sensible pairings or conflicts with existing source records.

### Confidence and gaps

Label confidence as `high`, `medium`, or `low` and explain missing states, breakpoints, inaccessible content, uncertain font identification, or other evidence gaps.

### User review

Record the review decision, corrections, rejected interpretations, approved profile additions, conditional preferences, exclusions, and any unresolved question. A submitted URL alone is not user approval.

Review status applies to the analysis, not every principle. The decision log is the source of truth for positive preferences and exclusions; record partial approval/rejection with `taste_library.py review`. Multiple independent sources cannot substitute for explicit approval.
