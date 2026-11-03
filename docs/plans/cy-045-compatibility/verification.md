# CY 0.45 compatibility verification, 2026-11-03

## Source and requested pair

The isolated queue branch `fix/cy-045-compatibility` starts at latest main
`0139152`; CY starts at latest master `84166d5` plus the saved batch-estimate
coverage implementation. Queue metadata moves from `0.1.7` to `0.1.8` and widens
only the tested CY upper bound from `<0.45` to `<0.46`, retaining the `>=0.38`
lower bound. Proposed CY delivery is `0.45.0`; the parent owns final source and
installed identities and normal-resolution checks after CY's release hook.

The parent normally installed the changed editable queue into its isolated CY
environment and reported `uv pip check` passing before these checks. Installed
versions at this checkpoint are CY `0.44.8` and queue `0.1.8`. This task did not
modify the environment, original source checkout, installed skills or shared
services. No queue lockfile exists, and no dependency lock update was introduced.

## Regression and static checks

The new package-boundary regression
`test_supported_cy_range_includes_saved_estimate_listing_minor` failed before the
metadata change because `<0.45` rejected `0.45.0`. It passed afterward and also
checks rejection of the still-untested `0.46.0` minor. Existing installed-source
identity, command composition, allocation-aware batch lookup and lifecycle tests
remain required; the bound assertion alone does not establish compatibility.

Executed from this queue checkout through
`uv run --frozen --no-sync --project ../clearml-yolo`:

- `ruff check .`: passed.
- `ruff format --check .`: all 101 files passed.
- `mypy .`: no issues in 70 source files.
- `lint-imports`: both contracts kept; no broken inward-layer or pure-policy rules.
- `cy-queue --help`: exit 0 with the existing command interface.
- CY `scripts/check_docs.py --root . --all` plus explicit new plan/evidence paths:
  Markdown structure and local links/anchors passed.
- `git diff --check`: passed.

The architecture record was validated in planning before edits. Runtime modules,
CY-consumed imports, shared records, snapshots, ownership and admission are unchanged;
only distribution compatibility metadata, its regression and documentation change.
README installation/usage and migration instructions were reviewed and retain their
existing compatible-pair and coordinated upgrade requirements; no edits were needed.

## Complete ordinary suite

`CUDA_VISIBLE_DEVICES= uv run --frozen --no-sync --project ../clearml-yolo pytest -q`
passed: **583 passed, 7 deselected**, exit 0. The deselected cases are explicit
physical GPU acceptance, not passes. The 19 warnings came from upstream Hydra-Zen
Pydantic deprecation. The run included installed-source identity, outside-checkout
console entrypoints, allocation-aware automatic batch lookup and architecture
negative cases. Its command output is retained in the parent host's task log.
This verifies the changed source with installed CY `0.44.8` / queue `0.1.8`, not
the final proposed CY version metadata.

## Remaining acceptance

The parent must verify the final installed CY `0.45.0` / queue `0.1.8` pair after version hooks,
and obtain fresh independent review before accepting the architecture record and
publishing either repository. No physical GPU, NFS or ClearML publication outcome
is claimed by these offline/source checks. Queue delivery is a Conventional Commit
and authorized `main` push; this repository has no version-tag release automation.


## Proposed-version pair verified by parent

Before release/tag creation, normal dependency-enabled installation of prospective
CY0.45.0 with queue0.1.8 and unchanged approved external sources passed, followed by
`uv pip check`. Source/installed versions agreed. The parent verified installed
queue module bytes against the source checkout; a noneditable queue source install
freezes the installed verification input while this evidence is maintained.
The complete queue suite passed **583 tests, 7 deselected**, 19 warnings, exit 0
(132.40s). Final committed metadata will be reinstalled and verified after hooks.


## Actual committed pair accepted (2026-11-04, Moscow)

CY native hooks created annotated v0.45.0 at 850557c after feature a89e486.
Normal dependency-enabled installation of that committed source and queue0.1.8
passed pip check. Both distribution versions matched source; CY imports resolved
to the released source worktree and all installed queue Python modules matched
this checkout byte-for-byte. The complete actual pair suite passed 583 tests,
seven physical opt-ins deselected, 19 warnings, exit 0 (137.91s). Queue help passed.

Fresh independent review is accepted and architecture acceptance validation passed.
Runtime modules remain unchanged. Package delivery is the reviewed source commit
and a verified main push only; no queue tag, registry or deployment is involved.
