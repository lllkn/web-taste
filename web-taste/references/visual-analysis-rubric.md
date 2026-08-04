# Visual Analysis Rubric

Use this rubric to produce observations that are specific enough to guide implementation. Inspect representative elements rather than exhaustively inventorying every CSS declaration.

## Evidence levels

- **Observed**: visible in a captured viewport or confirmed through DOM/computed-style inspection.
- **Measured**: a concrete browser-derived value such as width, gap, color, font size, radius, or duration.
- **Interpreted**: a reasoned explanation of intent or effect. Keep it visibly separate from observed facts.
- **Unknown**: inaccessible or ambiguous. State the gap rather than guessing.

## Composition and hierarchy

Inspect:

- viewport framing, content max-width, outer gutters, and full-bleed regions;
- grid columns, alignment anchors, overlap, asymmetry, and intentional breaks;
- first-viewport priorities and whether the next section is visible;
- density changes between sections and the rhythm of text, media, and empty space;
- layer ownership for navigation, overlays, sticky elements, and background media.

Ask: what does the eye notice first, second, and third, and which measurable choices cause that order?

## Typography

Inspect:

- actual font family or fallback stack, weight, size, line height, and letter spacing;
- display, heading, body, label, caption, numeric, and control roles;
- maximum line length, wrapping behavior, alignment, casing, and emphasis;
- type ratios and whether scale or weight carries hierarchy;
- font loading and mobile substitutions.

Avoid recording only the largest heading. The body and control typography often reveal more about the system.

## Color, imagery, and surfaces

Inspect:

- page, section, surface, text, muted text, accent, border, focus, and state colors;
- contrast relationships and where saturation is reserved;
- photography or illustration framing, crop, aspect ratio, treatment, and subject visibility;
- solid versus translucent surfaces, border strength, shadows, blur, noise, and texture;
- whether color communicates hierarchy, brand, state, or decoration.

Record representative computed colors. Explain their roles rather than making a flat palette list.

## Spacing and geometry

Inspect:

- recurring spacing units and exceptions;
- section padding, component gaps, internal control padding, and text-to-media distance;
- border width, corner radius, icon size, control height, and target size;
- stable dimensions, aspect ratios, min/max constraints, and overflow behavior.

Look for rhythm and ratios. A page can use generous whitespace while keeping controls dense.

## Components and interaction

Inspect:

- navigation, buttons, links, fields, menus, tabs, cards, lists, tables, dialogs, and feedback;
- default, hover, focus-visible, active, selected, loading, disabled, empty, and error states;
- icon semantics, labels, affordances, target sizes, and keyboard behavior;
- repeated component grammar and deliberately exceptional calls to action.

Do not infer an interaction from a static appearance when it can be exercised in the browser.

## Responsive behavior

Compare at least desktop and mobile when applicable:

- reflow versus simple scaling;
- column collapse, order changes, visibility changes, and navigation adaptation;
- type, padding, gap, media crop, and control changes;
- sticky/fixed behavior, safe areas, overflow, and long-word handling;
- whether the mobile layout preserves the same hierarchy or establishes a new one.

Record viewport sizes used. Do not treat a narrow desktop screenshot as proof of a deliberate mobile design.

## Motion

Inspect:

- trigger, property, distance, duration, easing, delay, and choreography;
- hover feedback, page entrance, scroll reveal, transition, loading, and modal behavior;
- whether movement explains causality, preserves spatial continuity, directs attention, or merely decorates;
- reduced-motion behavior when observable.

Prefer transform and opacity observations only when the page actually uses them; do not prescribe motion by default.

## Synthesis test

A useful source record should let another agent answer all of these:

1. Which 3-6 relationships make this design recognizable?
2. Which choices are reusable beyond the source brand?
3. Which choices depend on this page's content or business context?
4. How would those ideas translate into layout, tokens, components, and motion?
5. What must not be copied?
6. Which evidence is missing or uncertain?

If the record could describe dozens of unrelated websites unchanged, it is too generic.
