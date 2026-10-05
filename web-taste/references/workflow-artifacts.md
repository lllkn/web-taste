# Workflow Artifacts

Use only the fields that materially affect the current task. State resolved assumptions and proceed; ask about significant missing choices. Scope authorization, visual choice and durable memory approval are separate decisions.

## Learn Brief

After a bounded rendered-page scan, state the final URL and page identity, learning focus, page/state scope, viewports, exclusions, access limitations and persistence choice. If these are already supplied or reasonably resolved, continue inspection. A narrow typography task does not require a complete site inventory.

## Visual Taste Board

For in-scope dimensions, provide rendered evidence, a hierarchy/layout skeleton, real typography samples, color roles, relative geometry, responsive comparison, component states and motion captures. Label unknown or out-of-scope dimensions. Do not manufacture evidence to fill a template.

Use `python3 "${WEB_TASTE_SKILL}/scripts/render_visual.py" taste-board INPUT.json OUTPUT.html`. A complete example:

```json
{
  "title": "Reference page",
  "source_url": "https://example.com/final-url",
  "captured_at": "2026-10-05",
  "status": "reviewable",
  "summary": "A large editorial measure establishes hierarchy above compact controls.",
  "learning_focus": ["layout", "typography"],
  "scope": "Current page, desktop and mobile",
  "screenshots": [
    {"id": "desktop", "label": "Desktop hero", "path": "desktop.png", "viewport": "1440 x 900"},
    {"id": "mobile", "label": "Mobile hero", "path": "mobile.png", "viewport": "390 x 844"}
  ],
  "layout_skeletons": [
    {"label": "Desktop", "columns": 12, "blocks": [{"label": "Copy", "span": 5}, {"label": "Media", "span": 7}]},
    {"label": "Mobile", "columns": 1, "blocks": [{"label": "Copy", "span": 1}, {"label": "Media", "span": 1}]}
  ],
  "comparisons": [
    {"title": "Hero reflow", "desktop": "desktop", "mobile": "mobile", "summary": "The two-column layout stacks with copy first."}
  ],
  "palette": [{"name": "Ink", "value": "#161616", "role": "Primary text"}],
  "type_scale": [
    {"role": "Display", "sample": "A short heading", "size_px": 72, "line_height_px": 64, "weight": 700, "font_family": "Reference Serif", "font_available": false},
    {"role": "Body", "sample": "A readable content sample", "size_px": 16, "line_height_px": 24, "weight": 400}
  ],
  "geometry": [
    {"name": "Outer gutter", "value": "72 px", "role": "Desktop alignment"},
    {"name": "Content gap", "value": "24 px", "role": "Internal grouping"}
  ],
  "sections": [
    {"title": "Composition", "summary": "One dominant message precedes supporting controls.", "evidence": [
      {"id": "content-width", "type": "measured", "label": "Content width", "value": "1296 px", "confidence": "high", "screenshot_ref": "desktop"}
    ]}
  ],
  "principles": [
    {"id": "editorial-hierarchy", "title": "Editorial hierarchy", "evidence": "Wide framing supports a dominant headline.", "evidence_refs": ["content-width"], "use_when": "Narrative landing pages", "avoid_when": "Dense utility screens", "implementation_cue": "Reserve a larger display role while keeping controls compact.", "confidence": "medium"}
  ],
  "do_not_copy": ["Reference brand identity"],
  "gaps": ["Motion and interaction states are outside this learning scope."]
}
```

Screenshot paths are local, relative to the JSON file or absolute. The renderer embeds images; it never fetches remote assets. Report metadata omits original image paths. IDs use letters, digits, underscores or hyphens and must be unique. Omitted IDs are generated from labels/titles, but explicit stable IDs are preferable for future corrections.

A `reviewable` board requires screenshots, observed/measured evidence and principles referencing that evidence. `draft` and `incomplete` boards may lack these, but must explain gaps and cannot be used to approve principles. This is a structural check, not proof that a browser was actually inspected. A `high` confidence label does not mean user endorsement.

`size_px`, `line_height_px` and `weight` drive sample appearance. Legacy `spec: "72/64, 700"` still works. Unless `font_available` explicitly indicates an available local family, samples use a labelled system substitute. Do not download source font files merely to complete a report. Pixel geometry bars show relative proportions across the displayed measurements.

For component states and motion, optionally add:

```json
{
  "state_groups": [
    {"title": "Menu states", "summary": "Default and open captures", "frames": [
      {"label": "Default", "screenshot_ref": "menu-default"},
      {"label": "Open", "screenshot_ref": "menu-open"}
    ]}
  ],
  "motion_sequences": [
    {"title": "Menu entrance", "summary": "Observed transition after activation", "frames": [
      {"label": "Before", "screenshot_ref": "menu-default", "at_ms": 0},
      {"label": "After", "screenshot_ref": "menu-open", "at_ms": 200}
    ]}
  ]
}
```

Add those IDs to `screenshots` with actual capture files. A timeline is a set of captured states; do not present two stills as proof of easing or smoothness without separate observation.

## Learning Review

Present proposed preferences, contextual limits, exclusions and evidence gaps. Record partial acceptance explicitly: principle ID, user's words, `global` or `project:name` scope, and approval/rejection/revocation.

Source `review_status` (`pending`, `confirmed`, `corrected`, `rejected`) describes review of the analysis. It does not approve all principles. A URL, a reviewed source, repeated source traits or an implementation decision alone is insufficient to create positive memory.

Use `review` only after an explicit user decision. It preserves a principle snapshot, evidence references, report hash and timestamp in `decisions.jsonl`, then regenerates the profile. `rejected` records a scoped exclusion; `revoked` removes a prior decision from active use while retaining its history. Revocation applies to the named scope. To prohibit a globally approved principle in one project, record a project-scoped rejection rather than merely withdrawing a project choice.

## Application Brief and Memory Fusion

State goal, audience, scope, functionality to preserve, content/assets, framework/design system, accessibility/responsive constraints, desired character, influence strength, exclusions, deliverable and verification target. Confirm only material unresolved choices.

Use `search` and read zero to four best-fitting source records. Present:

| Source | Fit to task | Approved relationships to reuse | Exclusions | Conflict resolution |
| --- | --- | --- | --- | --- |
| Source record | Product/content/interaction fit | Specific scoped principles | Identity or unsuitable traits | Concrete decision |

Search is lexical candidate retrieval; the agent must check use/avoid conditions against the actual brief. Pending and rejected sources cannot contribute positive preferences. Project-specific decisions override global decisions for the same source/principle. Exclusions are also returned when no positive source matches.

An empty library or no relevant match means work from the current brief and established conventions. One related source is enough. State the resulting design thesis; do not invent historical taste or force collection of additional references.

## Component Choice

Only render a comparison when requested or when the user must settle a consequential open choice. Keep content, dimensions, viewport and states comparable. Use `render_visual.py component-choice`:

```json
{
  "title": "Primary navigation direction",
  "context": "The same content at 390 x 320",
  "decision_question": "Which navigation direction should guide the page?",
  "options": [
    {"id": "A", "name": "Compact", "preview_html": "<nav style='padding:12px'>Home · Work · About</nav>", "viewport": {"width": 390, "height": 320}, "difference": "Compact actions", "tradeoff": "Less room between items", "states": "default"},
    {"id": "B", "name": "Spacious", "preview_html": "<nav style='padding:32px'>Home · Work · About</nav>", "viewport": {"width": 390, "height": 320}, "difference": "More room", "tradeoff": "More vertical space", "states": "default"}
  ]
}
```

Options accept `preview_image` instead of `preview_html`; actual component screenshots are preferred. HTML is locally authored markup isolated in sandboxed iframes. Scripts are disabled, so capture JS-driven states separately rather than claiming they work in this preview. Identical viewport dimensions are required; previews scroll horizontally when the report column is narrower, preserving their declared viewport.

The selection button changes only the comparison display. The user communicates the choice in conversation; no approval is saved by the page. Record selected option, accepted aspects, rejected alternatives, rationale, project scope and influences in the application record. Durable preference storage requires a separate explicit scoped endorsement.

## Verification Record

Verify rendered desktop/mobile hierarchy, wrapping, overflow, geometry, contrast, keyboard/focus behavior, relevant interaction states, reduced motion and preserved functionality. Record actual evidence and remaining device/platform gaps. Source checks alone are not rendered verification.

## Library Commands

Resolve `WEB_TASTE_SKILL` to the installed skill's absolute directory. All examples work from a target project's working directory. Runtime data defaults to `$WEB_TASTE_LIBRARY_ROOT`, otherwise `${XDG_DATA_HOME:-~/.local/share}/web-taste`. Pass `--library-root` before the subcommand to override the default.

```bash
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" root
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" init
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" new --title "Reference" --url "https://example.com/final-url" --learning-focus "layout, typography" --learning-scope "current page; desktop and mobile"
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" new-application --title "Poetry reader" --target /absolute/project
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" index
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" validate
```

Complete source scaffolds and render the board before a principle decision. Replace `SOURCE_ID` with the generated record filename without `.md`, and use an ID present in the report:

```bash
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" review --source SOURCE_ID --principle-id editorial-hierarchy --decision approved --scope global --user-words "Use this hierarchy for narrative landing pages in future."
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" search --query "narrative landing" --scope project:poems
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" review --source SOURCE_ID --principle-id editorial-hierarchy --decision revoked --scope global --user-words "Remove this preference from future use."
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" profile
```

Substitute the user's actual words; examples do not authorize storing those preferences. If review evidence changes, retain stable principle IDs and record the new explicit decision to replace the earlier snapshot. `profile` rebuilds summaries from the decision log without adding decisions. `init` never overwrites existing memory.

Upgrade from an old in-skill library before deleting or replacing its installation:

```bash
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" --library-root /absolute/user/library migrate --from /absolute/old/skill/references
```

Migration preserves the old directory, saves a backup, converts internal absolute report paths to library-relative paths and refuses collisions. Repeating a completed migration is harmless; changed source files require a separate destination for review. Old profile text becomes `legacy-profile.md`; review its principles before rebuilding positive preferences. Source observations and legacy reports remain available, but fresh approvals require a structured reviewable Board.
