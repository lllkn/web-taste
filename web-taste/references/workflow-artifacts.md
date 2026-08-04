# Workflow Artifacts

Use these contracts at the confirmation gates. Keep the user-facing versions concise, but do not omit a field that could materially change the work.

## Learn Brief

Present this after a bounded quick scan and before deep inspection.

```markdown
## Quick scan

- Final URL and page identity:
- Content purpose and page type:
- Broad visual character:
- Access limitations:

## Proposed Learn Brief

- Learning focus:
- Page scope:
- Viewports:
- Interaction states:
- Exclusions:
- Persist to taste library: yes/no
- Open choice requiring confirmation:
```

A confirmed brief can be represented in source frontmatter with concise scalar values. Put detailed corrections and review notes in the record body.

## Visual Taste Board

The board is a visual evidence surface, not decorative documentation. It must include the categories that are in scope and visibly mark absent evidence as unknown.

Required blocks:

1. Source identity, confirmed focus, scope, viewports, and capture date.
2. Desktop/mobile overview screenshots or crops when applicable.
3. Layout skeleton and hierarchy order.
4. Typography ladder with roles, family, weight, size, and line height.
5. Role-labelled color swatches and surface treatment.
6. Spacing, radius, border, icon, and control geometry.
7. Representative component and interaction states.
8. Responsive reflow comparison.
9. Motion sequence or timing notes when motion is in scope.
10. Transferable principles, boundaries, do-not-copy items, confidence, and gaps.

Use `scripts/render_visual.py taste-board` with JSON shaped like this:

```json
{
  "title": "Reference page title",
  "source_url": "https://example.com/final-url",
  "captured_at": "YYYY-MM-DD",
  "summary": "One concrete sentence about the page system.",
  "learning_focus": ["layout", "typography", "components"],
  "scope": "Current landing page, desktop and mobile",
  "screenshots": [
    {"label": "Desktop hero", "path": "/absolute/path/desktop.png", "viewport": "1440 x 900"}
  ],
  "palette": [
    {"name": "Page", "value": "#FFFFFF", "role": "Primary page surface"}
  ],
  "type_scale": [
    {"role": "Display", "sample": "A short heading", "spec": "72/64, 700"}
  ],
  "geometry": [
    {"name": "Outer gutter", "value": "72 px", "role": "Desktop alignment anchor"}
  ],
  "sections": [
    {
      "title": "Composition and hierarchy",
      "summary": "What produces the hierarchy.",
      "evidence": [
        {"type": "measured", "label": "Content width", "value": "1296 px", "confidence": "high"}
      ]
    }
  ],
  "principles": [
    {
      "title": "Transferable principle",
      "evidence": "Observed support",
      "use_when": "Suitable context",
      "avoid_when": "Unsuitable context",
      "implementation_cue": "Practical direction",
      "confidence": "medium"
    }
  ],
  "do_not_copy": ["Brand identity"],
  "gaps": ["Reduced-motion behavior was unavailable"]
}
```

The renderer embeds local screenshot files into the HTML output. It rejects remote image URLs so the report remains self-contained and does not silently fetch third-party assets.

## Learning Review

Present these decisions with the board:

```markdown
- Proposed profile additions:
- Proposed conditional preferences:
- Proposed exclusions:
- Evidence gaps:
- User decision: approve / correct / reject / narrow
- User corrections:
```

Use `review_status: confirmed` only after the user reviews the findings. Use `corrected`, `rejected`, or `pending` honestly. Rejected findings remain in the source record for provenance but must not enter the positive profile.

## Application Brief

Present this after target inspection and before design implementation.

```markdown
- Product and goal:
- Target users:
- Page or component scope:
- Existing functionality to preserve:
- Content and asset constraints:
- Accessibility and responsive requirements:
- Desired character:
- Taste influence strength: light / balanced / strong
- Explicit exclusions:
- Deliverable:
- Validation target:
- Open choice requiring confirmation:
```

## Memory Fusion Note

Read the profile, index, and only the 2-4 closest records. Present:

| Source | Why it matches | Relationships to reuse | Exclusions | Conflict |
| --- | --- | --- | --- | --- |
| Source record | Product/density/content fit | Transferable system | Source-specific or harmful traits | None or named tension |

Then state one design thesis. Never average conflicts silently or list a source without explaining its contribution.

## Component Choice

Render a choice only when alternatives are consequential. Keep the same content, bounding dimensions, viewport context, and required states across options.

Use `scripts/render_visual.py component-choice` with JSON shaped like this:

```json
{
  "title": "Primary navigation direction",
  "context": "Desktop and mobile navigation for the confirmed target",
  "decision_question": "Which interaction grammar should guide the product?",
  "options": [
    {
      "id": "A",
      "name": "Compact utility",
      "preview_html": "<nav class='demo compact'>...</nav>",
      "difference": "Dense horizontal actions",
      "tradeoff": "Fast scanning, less editorial presence",
      "states": "default, hover, focus, mobile"
    }
  ]
}
```

`preview_html` is trusted local markup authored for the comparison and may contain inline styles. Never paste source-site HTML or untrusted third-party markup into it.

After the user chooses, record:

```markdown
- Component:
- Selected option:
- Accepted aspects:
- Rejected alternatives:
- Rationale in the user's words:
- Applies to:
- Source influences:
- Date:
```

## Verification Record

Finish an Apply task with evidence for:

- desktop and mobile rendering;
- hierarchy and design-thesis alignment;
- wrapping, overflow, and stable geometry;
- default, hover, focus, active, disabled, loading, empty, and error states as applicable;
- contrast and keyboard accessibility;
- motion purpose and reduced-motion fallback;
- preservation of existing functionality;
- remaining unverified platform or device behavior.
