# Agent Compatibility

Web Taste uses one standard `SKILL.md` with bundled Python helpers and references. It does not require a model provider API or a particular browser server. Host-specific discovery and invocation are separate from the capabilities needed to complete a workflow.

## Install and invoke

The supported installation targets for this release are Codex, Claude Code, Cursor and GitHub Copilot. Install the complete `web-taste/` folder, including scripts and references. `agents/openai.yaml` adds Codex UI information; the core works without that file.

| Host | Project skill directory | Personal skill directory | Invocation |
| --- | --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills/web-taste/` | `~/.agents/skills/web-taste/` | Select the discovered skill or ask to use `web-taste`; `$web-taste` is also used by the current Codex desktop host. |
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/web-taste/` | `~/.claude/skills/web-taste/` | `/web-taste`, or ask to use the skill. |
| [Cursor](https://cursor.com/docs/skills) | `.cursor/skills/web-taste/` or `.agents/skills/web-taste/` | `~/.cursor/skills/web-taste/` or `~/.agents/skills/web-taste/` | Select `/web-taste` when listed, or ask to use the skill. |
| [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | `.github/skills/web-taste/` or `.agents/skills/web-taste/` | `~/.copilot/skills/web-taste/` or `~/.agents/skills/web-taste/` | Ask to use `web-taste`; Copilot CLI also supports `/web-taste`. |

These paths are based on official documentation checked on 2026-10-05. Older client versions may use other supported directories; rely on the actual client's discovery result. Avoid installing duplicate copies under several paths read by the same client.

Use the [Agent Skills CLI](https://github.com/vercel-labs/skills) to choose destinations and install from GitHub:

```bash
npx skills add lllkn/web-taste --skill web-taste -a codex -a claude-code -a cursor -a github-copilot -y
```

This is a project installation. Add `-g` for personal installation. For local development, replace `lllkn/web-taste` with `.` from the repository root. Use only the `-a` targets requested by the user; commands in this document are examples, not authorization to change host configuration.

The CLI may choose a common `.agents/skills/` directory rather than a host-native directory where the host supports it. Both discovery routes are valid. A symlink installation is optional; `--copy` creates independent copies. Keep source data out of the install package; migrate an older in-skill library before replacing that installation.

If native skill discovery is unavailable, a host with local file access can still be explicitly told to read `/absolute/web-taste/SKILL.md` and follow it. This is manual use, not proof of native integration.

## Match workflow to capabilities

Check session tools and permissions, not just the host name. Browser tools can come from the agent, a browser MCP, an approved browser automation runtime or supplied screenshots.

| Available capabilities | What can be completed | Required limits |
| --- | --- | --- |
| Files + Python + interactive rendered browser + captures + computed styles | Learn, evidence boards, approved persistence and Apply | Verify only states exercised and viewports captured. |
| Files + Python + screenshots, without browser control | Visual learning and persistence of explicitly approved visible principles; Apply | Label static observations; interactions, timing and inaccessible measurements remain unknown. |
| Files + Python, without rendered evidence | Read existing memory, prepare briefs/implementation, draft reports | A draft cannot authorize new durable principles. Render verification remains outstanding until evidence is available. |
| Readable files and visual inputs, without Python execution | Analysis, visual proposals, reuse of readable approved memory | Do not pretend helper validation or persistence ran. Return the decision proposal for a compatible runtime. |
| No accessible private library | Work from the current brief | Do not invent historical taste; do not treat inability to read a library as an empty verified library. |

Scripts use the Python standard library and are tested with Python 3.9 and 3.12. On POSIX systems, `python3` is typical; on Windows, use a working `python` or `py -3` command. POSIX shell-variable assignment examples must be translated to the actual shell, or replaced with absolute paths. Do not edit the user's shell profile or agent permissions merely to make an example run.

HTML comparison iframes intentionally disable JavaScript. Exercise JS-driven states in the real target browser and use captures in the comparison. No particular host's preview panel is required: attach the self-contained HTML when possible, or provide its path with a summary and available screenshot previews.

## Share memory across hosts

All installations use the same schema and helpers. On the same machine, point each session at one accessible data directory:

```bash
python3 /absolute/installed/web-taste/scripts/taste_library.py --library-root /absolute/private/web-taste-library root
python3 /absolute/installed/web-taste/scripts/taste_library.py --library-root /absolute/private/web-taste-library search --query "narrative editorial" --scope project:poems
```

An exported `WEB_TASTE_LIBRARY_ROOT` also works if inherited by the agent's process. Environment variables set in a terminal may not reach an already-running desktop app; use `--library-root` when unsure. The script's `root` output is the actual resolved location.

Use one writer at a time: concurrent decision-log/profile writes are not supported by a locking protocol. Cloud/remote agents do not automatically receive local private memory or screenshots. Configure an accessible library deliberately, preserve user/project scope, and do not upload or synchronize personal data without the user's instruction.

## Verification status

On 2026-10-05, Skills CLI 1.7.0 recognized all four requested target IDs and successfully installed the local skill in an isolated project using `--copy`. It chose `.agents/skills/web-taste/` for the shared route and `.claude/skills/web-taste/` for Claude Code. Its `list` output labels locally detected hosts, so that output alone is not a complete compatibility matrix.

All 34 Python regression tests pass, including helper execution from all four host-native directory layouts with `agents/openai.yaml` removed. The same test verifies that approval is visible across installations and revocation from another installed copy updates the shared library. Standard metadata, local reference links and the skill validator also pass. Browser report rendering has a separate desktop/mobile test.

An installation test is not a full Learn → human review → Apply run inside each agent. The actual host must expose and permit the needed browser, Python, file and preview capabilities. Additional agents supporting the [Agent Skills specification](https://agentskills.io/specification) may be usable, but are not included in this release's verified installation targets.
