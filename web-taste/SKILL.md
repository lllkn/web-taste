---
name: web-taste
description: Learn transferable design relationships from reference webpages, visualize evidence, remember explicitly approved preferences, and apply relevant taste memory to interfaces. Use for learning a reference site's visual system or designing with previously saved taste. Ordinary frontend implementation or component comparison without reference learning or taste memory does not require this skill.
---

# Web Taste

Turn reference webpages into traceable design evidence and scoped user preferences. Transfer hierarchy, rhythm and interaction relationships while preserving the target's content, functionality and established conventions.

## Runtime portability

This is a portable Agent Skill. Use the host's file, terminal and browser capabilities; do not assume Codex-specific tool names or invocation syntax. `agents/openai.yaml` is optional Codex UI metadata, not a runtime dependency. For installation, host invocation or access troubleshooting, read [agent-compatibility.md](references/agent-compatibility.md).

Before starting, check the capabilities actually available in this session:

- Bundled scripts require Python 3.9+ and filesystem access. Resolve a working interpreter (`python3`, `python`, or `py -3`) and substitute it in the examples. Python and browser tools are separate capabilities.
- Interactive browser plus local captures enables state/responsive inspection; computed-style access enables measurements. Use the available browser/MCP integration only within the host's permissions.
- Screenshot inputs without browser control support visible observations; mark interactions and unavailable measurements unknown. Do not infer interactive behavior from static captures.
- Without rendered evidence, deliver a draft with explicit gaps. Without Python execution, provide analysis and a review proposal; defer helper-based persistence until a compatible runtime is available. Applying readable existing memory can still proceed.
- Use the host's attachment/preview mechanism to present HTML when available; otherwise provide the local artifact path and a concise summary or accessible screenshots. Do not publish a report just to display it.

The same local library can be used from different agents by choosing the same absolute `WEB_TASTE_LIBRARY_ROOT`. A remote or cloud session needs its own accessible data location; local installation does not imply cloud availability. Use one writer at a time for a shared library.

## Route the task

- **Learn**: inspect the requested reference and present visual evidence. Save preferences only when explicitly approved.
- **Apply**: inspect the target and retrieve relevant approved memory, then implement and verify.
- **Learn and apply**: share one scope brief; inspect references, propose the relevant relationships, and proceed with implementation when the user has authorized the direction. Review durable memory changes separately.

For Learn read [visual-analysis-rubric.md](references/visual-analysis-rubric.md) and the relevant Board/review sections of [workflow-artifacts.md](references/workflow-artifacts.md). For Apply read its brief, fusion, comparison and verification sections. Read [site-record-template.md](references/site-record-template.md) only when saving a source record. Do not load all resources for every task.

## Scope and user decisions

Treat scope and choices already clear in the user's request as authorization; do not ask the user to repeat them. Prepare a short brief stating the meaningful assumptions and proceed when the task is clear. Ask only about missing decisions that materially affect the result. Combine related questions and do independent work while awaiting answers.

Keep three decisions distinct: permission to inspect or implement, a consequential visual choice, and approval to save a durable preference. A submitted URL, approval of an analysis, or a one-project component choice does not automatically endorse every observed trait for future projects. Multiple independent sources increase observation confidence, never user approval.

When the user wants to choose a consequential direction, render 2–3 comparable options and wait for that choice. When the user delegates design decisions, recommend and implement a coherent direction without manufacturing another gate. State the resulting decisions with the reviewable output.

## Locate tools and private data

Resolve this `SKILL.md` directory to an absolute path, represented below by `WEB_TASTE_SKILL`. Call scripts using that path even when working in a different project. Do not assume the target's `scripts/` belongs to this skill.

```bash
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" root
python3 "${WEB_TASTE_SKILL}/scripts/taste_library.py" --library-root /absolute/user/library init
```

The default library is `$WEB_TASTE_LIBRARY_ROOT` when set, otherwise `${XDG_DATA_HOME:-~/.local/share}/web-taste`. `--library-root` overrides it and must appear before the subcommand. Read the resolved library's `taste-profile.md` and `site-index.md`; files of those names shipped in `references/` are empty initialization templates, not user memory. Scripts reject writes inside the skill installation.

For an older library inside a skill's `references/`, use `migrate --from /absolute/old/references` with the chosen data root. It backs up and copies records, preserves the source, repairs internal absolute report paths, and refuses conflicts. Imported summaries remain `legacy-profile.md` until explicit principles are reviewed; they are not silently promoted. See [workflow-artifacts.md](references/workflow-artifacts.md#library-commands) for commands.

## Learn

1. Open the reference in a rendered browser. Check page identity, final URL, content purpose and access limits. State a concise Learn Brief with focus, page/state scope, viewports, exclusions and persistence choice. Clarify only material gaps.
2. Inspect representative elements and meaningful states within that scope. Compare desktop/mobile when applicable; capture first viewport and full-page evidence separately when useful. Collect computed styles and geometry only when the browser exposes them. If it does not, mark visual estimates as interpreted, not measured. Do not fabricate inaccessible states.
3. Render a Visual Taste Board with `render_visual.py taste-board INPUT.json OUTPUT.html`. Include the in-scope screenshots, hierarchy/layout, typography, color roles, geometry, responsive comparisons, states and motion. Use stable evidence and principle IDs. Link each reusable principle to observed/measured evidence and state confidence, use/avoid conditions and an implementation cue.
4. Mark a board `draft` or `incomplete` with explicit gaps when evidence is insufficient. Such reports cannot authorize durable principles. Show the report and distinguish observations, interpretations, transferable relationships and source-specific boundaries.
5. Save source observations to the private library when the user requested persistence. Complete `TODO:` fields or mark the dimension explicitly out of scope. Set source review status honestly after review; report approval alone does not create positive taste memory.
6. For each explicit approval or rejection, run `taste_library.py review` with its source ID, principle ID, `global` or `project:name` scope and the user's actual words. `review` retains the evidence snapshot and regenerates the profile. Use `revoked` when the user withdraws a recorded decision. Never invent approval wording or generalize a project choice into global taste.

If access is blocked, produce a limited report with gaps, or request an accessible reference, screenshots or recordings when needed. A screenshot supports visible facts, not unexercised interactions.

## Apply

1. Inspect the repository, audience, content, assets, functionality, framework and existing design system. State a short Application Brief with goal, scope, constraints, intended character, influence strength, deliverable and verification target. Proceed when the request already resolves these choices.
2. Read the private profile and run `taste_library.py search --query "task keywords" --scope project:name`. Search returns explicitly approved, scoped principles and exclusions; pending/rejected sources are not positive memory. Project-specific decisions take precedence over global decisions for the same principle. Read only the best-fitting source records, up to four; never fill a quota.
3. If the library is empty or no memory fits, work from the current brief and established design system. State that no historical memory supports the direction. Do not invent preferences or block implementation merely to collect more references. One relevant source is sufficient.
4. Present a concise Memory Fusion Note: which relationship fits the target, what is excluded and how conflicts are resolved. Prioritize the user's current requirements, usability and existing conventions. Ask only about unresolved consequential choices; otherwise state a design thesis and derive coherent tokens and components.
5. When comparison is requested or needed for a user's choice, use identical content, states and viewport dimensions. Prefer screenshots of actual components; HTML previews are isolated in sandboxed iframes and support static/CSS states only. A click in the comparison page changes display state, not persistent approval; record a choice after the user communicates it.
6. Implement and verify the rendered desktop/mobile result, hierarchy, wrapping, overflow, contrast, keyboard/focus behavior, relevant states, reduced motion and existing functionality. State verified evidence and remaining gaps. Record project decisions in `applications/`; save new durable preferences only with explicit scoped endorsement.

## Invariants

- Separate observed, measured, interpreted and unknown evidence. Confidence describes evidence quality, not strength of user preference.
- Keep provenance and contextual boundaries; record partial approval and rejection at principle level.
- Preserve the user's chosen framework, design system and authorized assets. Do not copy third-party identity, proprietary assets or source code without authorization; use user-owned or otherwise authorized resources within the request.
- Keep runtime data outside the distributed skill. Rebuild the index and run `taste_library.py validate` after changing library records. Validation checks structure and evidence links, not actual browser fidelity or human approval.
