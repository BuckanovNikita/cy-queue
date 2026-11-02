# Instruction migration checks — 2026-11-02

## Scope and preservation

The task standardizes agent instruction discovery only. Existing application,
service, generated workflow and unrelated source changes are preserved. No runtime
API, database, dependency or deployment changes are made. The implementation checks below preceded commit/release activity; release
outcomes are reported by the coordinating task separately. No deployment or
skill installation is part of this migration.

## Executed checks

- `uv run --frozen --no-sync --project ../clearml-yolo python ../clearml-yolo/scripts/check_docs.py --root . README.md AGENTS.md CLAUDE.md docs/development.md docs/interfaces.md docs/migration.md docs/plans/claude-codex-organization-20261102/plan.md` — PASS: seven Markdown files, zero issues.

Planning and acceptance record validation use the shared architecture validator
with this repository as the explicit root. All root adapter and changed-document
relative links were inspected separately; Git whitespace checks cover owned paths.

## Limits and remaining integration

File checks establish physical instruction discovery structure, not actual loaded
model context. Fresh Claude/Codex sessions, Windows discovery, settings parity,
parent integration, independent final review and authorized commit/release remain
with the coordinating task. Relevant application/runtime suites were not rerun
because no application behavior changed. Missing required release checks must
remain acceptance gaps rather than being inferred from these documentation checks.

## Independent review

The coordinating parent reported fresh `project_review` verdict **SHIP** with no
blocking defects on 2026-11-02. The reviewer validated all twelve project no-impact
records and inspected the documentation evidence across the integrated migration.
No runtime acceptance is inferred from that review. Authorized repository commit
and release gates remain in force; failed gates must be reported separately.

## Release gate outcome

A current origin fetch succeeded. The source checkout remains five commits
behind origin/main and CY remains 29 commits behind origin/master with unrelated
work. Queue source version 0.1.4 differs from installed queue metadata 0.1.3.
The required paired latest-source/normal-resolution/integration gate is unmet.
Task changes remain uncommitted; no shared environment upgrade, worker drain,
unrelated history merge, push or hook bypass is performed.

## Current-source pair reconciliation

The old stale-source/version blocker was reassessed on current published heads:
CY `7d3d258` version `0.44.8` and cy-queue `32bea01` version `0.1.7`
(`clearml-yolo>=0.38,<0.45`). Isolated checkouts and a task-owned environment
preserve the original dirty trees, indexes, active workers and operational environment.
Approved external dependencies were cloned at their existing exact source commits.

Normal editable installation of both source checkouts succeeded without `--no-deps`;
`uv pip check` verified all 285 installed packages compatible. Queue acceptance:
582 tests passed, seven opt-in physical DDP tests were deselected, 19 dependency
deprecation warnings. Ruff lint/format, strict mypy (70 source files), both import
contracts and actual `cy-queue --help` passed. No GPU/physical DDP outcome is claimed.
Changed-document checks and architecture acceptance passed. CY canonical verification
and final commit/release results remain separate evidence below.

## Canonical first-run result and stable retry

CY's ordinary suite completed with 4,703 passed, 30 skipped and 81 deselected
(182 warnings), but the canonical wrapper returned exit 1 because its dependency
input inventory changed during verification. The coordinating parent had appended
this queue checkout's release-evidence Markdown and source-pair JSON while CY
was checking the editable dependency tree. That tree includes documentation.
This is a coordination failure, not a passing acceptance receipt or a detected
application regression. Prior logs are retained; no receipt is forged or reused.

Both source checkouts and the installed environment are frozen for a fresh full
canonical retry. The coordinating task records its final wrapper exit and release
receipts separately; no queued worker or operational environment is changed.

## Final paired acceptance and queue handoff

CY's fresh frozen-input canonical retry passed with wrapper exit 0 and an
accepted receipt: Ruff, strict mypy, Vulture, import contracts and 4,703 passed,
30 skipped, 81 deselected (182 warnings). CY's instruction and receipt commits
were published through all installed hooks; final CY source is `84166d5`,
with source version `0.44.8` and its existing version tag unchanged. The
queue checkout stayed byte-frozen throughout those checks and CY publication.

Only after CY publication was this queue's documentation updated with the
observed result and final source identity. Queue version `0.1.7`, dependency
bounds and every runtime source file remain unchanged from the 582-test passing
pair. Final queue checks validate the changed documentation and installed/source
metadata without claiming that the earlier CY receipt includes these later
queue-documentation bytes. Native queue publication uses no invented version tag.

Final metadata compatibility regression passed after CY publication; all 286
packages in the isolated environment passed `uv pip check`. Initial setup had
285 packages; `pi-heif 1.4.0` was initialized during the first ordinary CY run
(metadata timestamp falls within that run), before the accepted stable retry.
The accepted retry therefore covers the initialized environment. The original
operational environment was never installed into or upgraded. Final changed
Markdown validation checked eight files with zero issues; architecture
acceptance and whitespace checks passed.
