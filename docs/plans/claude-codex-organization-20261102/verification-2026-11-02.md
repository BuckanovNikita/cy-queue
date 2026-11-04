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

## Queue publication

Fresh independent review returned SHIP for the five-path documentation candidate.
Commit `2392b90` was pushed to `origin/main` after changed-document validation,
architecture acceptance, installed/source compatibility and whitespace checks
passed. The source tree was clean after that push. This final receipt closure
changes documentation only. Queue version `0.1.7` and all runtime/dependency files
remain unchanged; no version tag, registry package or deployment is created.

## Preserved draft reconciliation, 2026-11-04

A fresh origin fetch resolves `main` to `4cf32f0cd84730aebd3cf930829f80ba47d5af24`
(queue 0.1.8). Its history includes the published instruction migration `2392b90`
and receipt completion `0139152`. The preserved draft checkout is based on
`4e18ec622121c228474dd454b0b46d4af902cf92`; its earlier uncommitted/stale-pair
statements describe that older checkpoint, not the current published outcome.

Byte comparison confirms that the preserved `AGENTS.md`, regular `CLAUDE.md`
containing `@AGENTS.md`, and no-impact architecture record already match the
published versions. Its draft plan and verification document are superseded by
the completed publication records above. The draft checkout, index and unrelated
changes were preserved without reset, stash, duplicate migration or environment
upgrade. Only this dated reconciliation and its plan amendment change in the
isolated review candidate. Runtime modules, dependency bounds and executable
architecture contracts remain unchanged; the existing no-impact record applies.

Fresh isolated source pairing used CY `8be76e4faaeeb20305f4b9e3be856d8855fc5609`
(0.45.0) and queue `4cf32f0` (0.1.8). Normal editable resolution used the CY
lockfile's registry versions and unchanged approved external source revisions:
digital-metrics `6e801be1564dce458294eb23592cc1aa0939c4d9` and report-generator
`d10aa395d08f738e92e04e076cee93b3a993bf8f`. No `--no-deps` shortcut or shared
environment mutation was used. Source and installed distribution versions match;
queue's `clearml-yolo>=0.38,<0.46` bound includes this CY version.

The ordinary queue suite passed: **583 passed, seven physical cases deselected**,
19 dependency deprecation warnings, 147.55 seconds. Ruff lint and formatting passed,
both import contracts passed, and actual `cy-queue --help` succeeded. The first
strict mypy attempt reported missing YAML and pandas stubs in the newly prepared
environment. Their locked development packages were then installed with copy mode;
this setup correction changes no repository dependency requirement or source.
Strict mypy then passed all 70 source files. Final `uv pip check` passed with
all 256 installed packages compatible. All four inspected/changed Markdown files
passed structure and local-link validation; architecture planning and acceptance
validation and `git diff --check` passed. These checks establish file structure
and source compatibility, not a fresh Claude/Codex session's loaded context.

Physical CUDA/NCCL acceptance remains open. The seven opt-in scenarios require at
least two distinct physical devices: direct/queued eager and compiled pipelines,
queued rank failure, cancellation and guardian death. No physical suite was launched
or relabeled successful. Valid queue configuration must preserve the host coordination
root, while explicit project/evidence arguments own the test outputs. The coordinating
task must establish suitable hardware, run those scenarios and verify owned cleanup.

These results reconcile the preserved instruction draft and verify the stated source
pair only. They are not final acceptance of later integrated CY changes, proposed
release metadata or physical execution. The coordinating parent retains final-source
pairing, fresh review and Git delivery ownership.

Fresh independent review accepted the final two-file documentation reconciliation.
The parent inspected the diff, confirmed that the no-impact architecture scope
matches it, and re-fetched both origins: the source identities above remain current.
The review excludes physical execution and the separately proposed CY 0.46 pair.
This documentation-only delivery does not change package versions or runtime files.
