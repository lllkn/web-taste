# Changelog

## 2026-10-05 — Reliable taste memory and multi-agent support

This update makes personal memory independent of skill updates, records exactly which principles the user approves, and documents installation and capability fallbacks for Codex, Claude Code, Cursor and GitHub Copilot.

### Changed

- **Portable agent workflow:** one standard `SKILL.md`, absolute helper paths, optional Codex UI metadata, and fallbacks for sessions without browser control, computed styles or Python. Agents on the same machine can use one explicitly configured private library, with sequential writes.
- **Private data lifecycle:** runtime data defaults to `${XDG_DATA_HOME:-~/.local/share}/web-taste`, with `WEB_TASTE_LIBRARY_ROOT` and `--library-root` overrides. Helpers reject writing personal data into the skill installation. Profile/index files shipped with the skill are initialization templates.
- **Backed-up migration:** `migrate --from` preserves the old library, backs up imported data, repairs internal absolute report paths and refuses conflicting overwrites. Repeated migration leaves existing imported records intact. Old summaries are preserved as `legacy-profile.md` for review.
- **Explicit preference decisions:** approval, rejection and revocation are recorded per principle and global/project scope, including user words, evidence snapshots and report hashes. Reviewing a source or seeing the same pattern on multiple websites no longer implies approval.
- **Scoped retrieval:** search returns relevant approved principles and separate exclusions, respects project overrides, and supports empty libraries. A task can proceed without a fixed number of historical sources.
- **Record validation:** corrected Markdown placeholder detection and checks for dates, URLs, statuses, tags and damaged decision logs. Chinese names are preserved in IDs; page identity hashes distinguish URL/query variants, and repeated application titles get unique IDs. Metadata uses a documented flat YAML subset.
- **Visual evidence:** boards show actual type sizes, line heights and weights, proportional spacing, layout skeletons, responsive comparisons, state captures and timestamped motion sequences. Principles link to identifiable evidence and screenshots. Draft/incomplete reports state their gaps and cannot authorize durable principles.
- **Comparable components:** static HTML options use separate sandboxed iframes with matching viewports. Styles cannot contaminate another option, and the selection UI does not persist approval. JS-driven states are represented by actual browser captures.
- **Documentation and CI:** updated bilingual README, installation instructions, artifact schemas, privacy/migration guidance and ignored runtime directories. CI runs regression tests and initializes/validates an isolated library.

### Upgrade

If an older installation keeps personal data in `web-taste/references/`, keep that installation until migration finishes. Run the new helper from a separate checkout, targeting the old directory:

```bash
python3 /absolute/new-checkout/web-taste/scripts/taste_library.py \
  --library-root /absolute/private/library \
  migrate --from /absolute/old-install/web-taste/references
```

Use the same library root in subsequent sessions. Migration preserves old evidence and summaries; new approvals require a structured, reviewable board. See the [README upgrade instructions](README.md#个人数据与升级) and [artifact reference](web-taste/references/workflow-artifacts.md).

### Validation and limits

- 34 regression tests pass on Python 3.9 and 3.12, including migration, decision semantics, retrieval, validation and shared memory across four host-native installation layouts without Codex metadata.
- Skills CLI 1.7.0 installs all four requested targets in an isolated project. Skill metadata and local reference links validate.
- Chrome rendering checks at 1440 px and 390 px confirm report layout, evidence links, image loading, typography, component isolation and mouse/keyboard selection.
- A complete Learn → human review → Apply workflow inside every agent has not been verified. Actual session capabilities and permissions determine what can run. Cloud agents do not automatically share local memory; concurrent library writes are not supported.
- Structured validation checks consistency; the agent must still inspect real browser evidence and obtain actual user decisions. Search is a lightweight keyword candidate search.

Details: [修复与验证记录](docs/fix-verification.zh-CN.md) · [Agent compatibility](web-taste/references/agent-compatibility.md).

## Previous release

The earlier release established the Learn/Apply workflow, visual reports, bilingual README and public result demos. The [optimization review](docs/optimization-review.zh-CN.md) describes the baseline examined before the changes above.
