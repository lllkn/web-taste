# Site Record Schema

Use this schema for every file in `references/sites/`. The helper script creates the frontmatter and headings; replace all placeholder text with evidence.

## Required frontmatter

```yaml
---
title: "Human-readable page or product name"
source_url: "https://example.com/final-url"
captured_at: "YYYY-MM-DD"
page_type: "landing-page"
tags: ["editorial", "high-contrast", "motion-light"]
learning_focus: "layout, typography, motion"
learning_scope: "current page; desktop and mobile; primary interactions"
review_status: "pending"
visual_report: "pending"
---
```

Use the final navigated URL. Keep tags lowercase and concrete. Useful page types include `landing-page`, `editorial`, `portfolio`, `commerce`, `dashboard`, `tool`, `documentation`, and `mobile-web`.

Set `review_status` to `confirmed`, `corrected`, `rejected`, or `pending`. A confirmed or corrected record must link to its self-contained Visual Taste Board through `visual_report`. Use `not-created-legacy` only for records captured before the visual-review workflow existed.

## Required sections

### Confirmed learning brief

Record what the user asked the skill to learn, the inspected page and state scope, exclusions, persistence choice, and the confirmation that unlocked deep inspection.

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
