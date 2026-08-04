---
name: web-taste
description: Learn, visualize, confirm, store, and apply reusable frontend visual taste from reference webpage URLs. Use when a user asks to study, learn, save, imitate, or apply a website's style, layout, UI, typography, components, art direction, motion, or responsive behavior; when prior taste cases should inform a frontend; or when several component directions should be rendered for user choice.
---

# Web Taste

Turn webpage references into an evidence-backed taste system and apply that system through explicit user decisions. Learn transferable relationships and constraints, never a site's identity or copied CSS values.

## Choose a mode

- **Learn**: inspect references, report the findings visually, obtain user review, and store the result.
- **Apply**: confirm the target need, retrieve relevant memories, resolve choices, implement, and verify.
- **Learn and apply**: complete every Learn gate before starting every Apply gate.

Read [workflow-artifacts.md](references/workflow-artifacts.md) for the required briefs, visual schemas, confirmation language, and decision records. For Learn mode also read [visual-analysis-rubric.md](references/visual-analysis-rubric.md) and [site-record-template.md](references/site-record-template.md). For Apply mode also read [taste-profile.md](references/taste-profile.md) and [site-index.md](references/site-index.md), then open only the 2-4 most relevant source records.

## Non-negotiable gates

1. Do not deeply inspect a submitted URL until the user confirms the Learn Brief.
2. Do not promote findings into the taste profile until the user reviews the Visual Taste Board.
3. Do not implement or restyle a target until the user confirms the Application Brief and proposed memory fusion.
4. When a consequential component has multiple coherent directions, render 2-3 comparable options and wait for the user's choice before propagating one through the design.

Treat a clear answer in the user's original request as confirmation; do not ask again for information already supplied. A gate pauses work only when a material choice remains unresolved.

## Learn workflow

### 1. Quick scan

Open the URL in a real rendered browser and perform only a bounded reconnaissance pass. Confirm the final URL, page identity, content purpose, probable page type, broad visual character, and whether authentication or overlays block inspection. Do not yet perform exhaustive DOM measurement, interaction traversal, full-page capture, or preference promotion.

Report the quick scan in 3-5 concrete sentences, then prepare a Learn Brief covering:

- learning focus: layout, hierarchy, typography, color, imagery, surfaces, components, interaction, responsive behavior, motion, or the whole system;
- page scope: current page, named sections, or a broader site journey;
- viewport and state scope: desktop, mobile, hover, focus, menus, dialogs, media, scroll, and transitions as applicable;
- exclusions and whether the result should enter the persistent library.

Ask the user to confirm or amend the brief. Wait when these choices are not already explicit.

### 2. Deep inspection

After confirmation, inspect the rendered page at desktop and mobile sizes when responsive. Capture first viewport and full-page evidence separately. Exercise meaningful hover, focus, menu, tab, modal, scroll, loading, and transition states within the confirmed scope.

Gather computed styles and geometry for representative elements. Classify evidence under composition and hierarchy, typography, color/imagery/surfaces, spacing and geometry, components and interaction, responsive behavior, and motion. Label every important statement as observed, measured, interpreted, or unknown. Never infer an interaction that can be exercised.

### 3. Visual report and review

Create a Visual Taste Board, not a text-only summary. Use screenshots or crops, a layout skeleton, role-labelled color swatches, a typography ladder, spacing/geometry samples, component states, desktop/mobile comparisons, and a motion sequence where evidence exists. Every reusable principle must include evidence, confidence, use conditions, avoid conditions, and an implementation cue.

Use `python3 scripts/render_visual.py taste-board INPUT.json OUTPUT.html` for a self-contained report when a file artifact is appropriate. Present the board to the user and summarize:

- what was observed;
- what was inferred;
- the 3-6 transferable relationships;
- source-specific elements that must not be copied;
- gaps or uncertainty;
- proposed additions, conditional preferences, and exclusions for the taste profile.

Ask the user to approve, correct, reject, or narrow the findings. Do not silently treat the submitted URL as endorsement.

### 4. Persist reviewed learning

Create or update a source record in `references/sites/` only with traceable provenance. Store the confirmed Learn Brief, report path, review state, user corrections, evidence, reusable principles, boundaries, and confidence. Use `python3 scripts/taste_library.py new ...` for a scaffold.

Promote a preference into [taste-profile.md](references/taste-profile.md) only when the user explicitly endorses it or multiple independent sources support it. Keep one-off findings conditional. Record contradictions as contextual alternatives, direct rejections as exclusions, and user corrections at higher confidence than inference.

Run:

```bash
python3 scripts/taste_library.py index
python3 scripts/taste_library.py validate
```

If access is blocked, do not fabricate. Report the missing evidence and request screenshots, exports, recordings, or an accessible equivalent.

## Apply workflow

### 1. Confirm the Application Brief

Inspect the target repository, product audience, content, assets, framework, functionality, and existing design system. Prepare an Application Brief with the product goal, target users, page/component scope, functional constraints, accessibility requirements, content shape, desired emotional character, taste influence strength, exclusions, deliverable, and validation target.

Ask the user to confirm or amend it before styling or implementation. Use `python3 scripts/taste_library.py new-application ...` when the application should be recorded persistently.

### 2. Retrieve and fuse memory

Read the concise taste profile and source index. Select only 2-4 relevant records by product type, information density, interaction model, content shape, and emotional goal. Do not combine every favorite trait.

Present a short Memory Fusion Note before implementation. Name each selected source, what relationship it contributes, why it fits, what is excluded, and any conflict. Resolve conflicts in favor of usability, the confirmed brief, and the target's established conventions. Ask for confirmation together with the Application Brief when possible.

After confirmation, write a design thesis covering product character, hierarchy, spatial rhythm, typography role, color behavior, surface treatment, component grammar, and motion behavior. Derive coherent tokens and relationships; adapt exact values to the target.

### 3. Resolve component choices

Trigger a choice when 2-3 materially different directions are all plausible and the decision affects hierarchy, repeated components, interaction grammar, or later implementation. Do not interrupt for trivial size or color variations.

Render the options with identical content, dimensions, state coverage, and viewport context. Label the differences and tradeoffs without presenting one as secretly complete. Use `python3 scripts/render_visual.py component-choice INPUT.json OUTPUT.html` for a lightweight comparison. Ask the user to choose or combine explicit aspects, then record the choice, rationale, rejected alternatives, scope, and source influences in the application record.

### 4. Implement and verify

Implement real states and responsive behavior while preserving functionality. Use assets that reveal the actual product or subject. Remove generic styling with no support in the confirmed brief or selected influences.

Compare the rendered result at desktop and mobile sizes. Verify hierarchy at a glance, wrapping, overflow, alignment, contrast, keyboard/focus behavior, interactive states, reduced-motion behavior, and consistency with the chosen component direction. Report verified evidence and remaining gaps.

Store explicit post-implementation corrections as decision evidence. Promote them to durable taste only when the same endorsement rules are met.

## Learning rules

- Prefer relationships over coordinates: ratios, rhythm, alignment logic, contrast hierarchy, and transition grammar transfer better than isolated values.
- Preserve source provenance and distinguish observed facts from interpretations.
- Keep durable taste separate from situational solutions.
- Never copy logos, trademarks, proprietary text, custom illustrations, photos, icons, font files, or source code.
- Keep [taste-profile.md](references/taste-profile.md) concise. Move detailed evidence into source records instead of bloating the profile.
