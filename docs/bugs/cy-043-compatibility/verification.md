# CY 0.43 proposed-pair verification

Date: 2026-10-29. Companion task: [compatibility plan](plan.md).

## Inspected sources and scope

Both SSH remotes were fetched successfully. CY's latest default branch is
`f8eb8a3c198806c08c0a41161aa4e8034dec0273`, after the existing `v0.42.0` release
at `335370d`. Queue's latest default branch and clean initial checkout match
`4205b9ba58f70cd69ffd9d8380ef0dd5556a3937` (version 0.1.3).

The paired CY snapshot contains that latest released feature 007 source plus the
integrated feature 008 changes. It does not use the stale pre-007 working-tree
baseline or the earlier 007-only environment. Approved external source revisions
were clean and captured unchanged:

- digital-metrics: `6e801be1564dce458294eb23592cc1aa0939c4d9`.
- report-generator: `d10aa395d08f738e92e04e076cee93b3a993bf8f`.

Before copying each source, an inventory of tracked and nonignored untracked files
was hashed; a second inventory rejected races. Snapshot-only normalization changed
CY's project/root lock version from 0.42.0 to 0.43.0, queue version from 0.1.3 to
0.1.4, and the queue upper bound from `<0.43` to `<0.44`. Parsed CY metadata was
compared before/after with the version restored, proving root-version-only edits.
No dependency revision, runtime source or test was changed in those snapshots.

The previous queue requirement excludes 0.43.0. The candidate requirement contains
0.43.0 and excludes 0.44.0. After the proposed pair passed, only these two real
queue metadata lines were updated. Existing exact CY interface/import contracts,
negative architecture cases and ordinary integration tests cover this bounded fix;
no runtime or test changes were required.

## Commands and results

An isolated Python 3.12.13 environment used the integrated CY lockfile's frozen
export and the four captured editable sources. Installation used normal dependency
resolution with copy mode, without `--no-deps` or shared-environment writes.
The commands used explicit private paths; `CY_SNAPSHOT`, `QUEUE_SNAPSHOT`,
`PAIR_ROOT` and `PAIR_PYTHON` below name those retained task-owned resources.

```bash
uv export --frozen --no-hashes --no-emit-project --format requirements-txt --output-file "$PAIR_ROOT/requirements.txt"
uv venv --python 3.12.13 "$PAIR_ROOT/venv"
UV_LINK_MODE=copy uv pip install --python "$PAIR_PYTHON" -r "$PAIR_ROOT/requirements.txt" -e "$CY_SNAPSHOT" -e "$QUEUE_SNAPSHOT"
uv pip check --python "$PAIR_PYTHON"
```

From the captured queue directory, with CUDA devices hidden and no `PYTEST_ADDOPTS`:

```bash
"$PAIR_PYTHON" -m pytest -q
"$PAIR_ROOT/venv/bin/ruff" check .
"$PAIR_ROOT/venv/bin/ruff" format --check .
"$PAIR_ROOT/venv/bin/mypy" .
"$PAIR_ROOT/venv/bin/lint-imports"
"$PAIR_ROOT/venv/bin/cy-queue" --help
```

All commands passed. Normal resolution installed 285 packages and `uv pip check`
reported all compatible. A separate isolated-mode metadata probe ran outside both
source checkouts and asserted exact source/installed versions and normalized direct
requirements for CY, queue, digital-metrics and report-generator. Module origins
and editable `direct_url.json` locations point to the four captured sources. CY is
0.43.0, queue is 0.1.4, and installed queue requires `clearml-yolo<0.44,>=0.38`.

The complete ordinary suite reported **518 passed, 7 deselected, 19 warnings** in
127.69 seconds. The warnings are upstream hydra-zen/Pydantic deprecations. Ruff
and formatting passed; strict mypy found no issues in 69 source files. Import-linter
kept both contracts (67 files, 205 dependencies). Installed CLI help passed.
Physical opt-in tests were deselected and are not claimed as passed.

An additional isolated process installed an import finder that raises for every
CY documentation module. It successfully composed and validated both pipeline and
train queue snapshots, checked ground-truth/epoch values and command-specific schema
fields, and confirmed no documentation module loaded. The first probe fixture put
its temporary project outside inherited `CY_HOME`, correctly triggering existing
filesystem confinement. Setting `CY_HOME` to that fixture directory fixed only the
probe; the identical deny-documentation scenario then passed. Both logs are retained.

## Identity and drift

Task-owned private evidence `cy008-release-pair-nk8xx0ix` retains exact argument
vectors, working directories, exit codes, durations and log SHA-256 values in
`results.json`, plus `source-manifests.json`, `tested-manifests.json`,
`normalization.json`, `identity.json` and individual `proposed-*.log` files.
The manifest hashes below identify sorted path-to-SHA-256 mappings after proposed
metadata normalization:

| Captured package | Tested manifest SHA-256 |
| --- | --- |
| clearml-yolo | `fac1c8f348c9743ee87542f4d0c01fa2197f930a42235a6bfef1f54eea52141e` |
| cy-queue | `ae19dcf2619141849b5957ba847019324e33f2d87ce635d8a3955ccdd4e46090` |
| digital-metrics | `88f5b0d13224e04104e0d63bcb65c8aa23ae2e7084c507fd4293159b0b009272` |
| report-generator | `f9b58fddd7a33dea362c72fdc1ddda92baaf78bcca8522340a0107584498fdd0` |

The post-check audit found only concurrent CY task prose changes in feature 008's
specification, tasks and delivery evidence. CY runtime, tests, package/configuration
inputs, queue sources and approved externals stayed unchanged during verification.

## Acceptance limits and remaining delivery work

Existing development, interface and migration guides were reviewed. Their bounded
compatibility, source-first installation, explicit integration ownership and coordinated
upgrade procedures remain accurate; no evergreen guidance change is needed.
Task Markdown and local links are checked with CY's `scripts/check_docs.py` against
the queue root. The architecture plan passed structural validation before metadata
changes. Final acceptance still requires parent integrated review and architecture
acceptance after review, plus refresh of the actual committed pair before pushing.

This evidence establishes offline ordinary queue compatibility with the candidate
CY source. It does not claim physical GPU/NCCL, multiuser/NFS, remote ClearML
publication or a shared operational installation upgrade. CY canonical/native evidence
is owned by its feature acceptance. No shared workers, reservations, services or
remote tasks were changed, and this bounded verification made no commit or push.

## Fresh independent acceptance review

After integrated verification and parent inspection, fresh native agent
`release_companion_review` reviewed the complete two-line package change, task
artifacts, retained command-log hashes, tested source manifests and compatibility
interfaces without write ownership or further delegation. Verdict: **ship for the
companion candidate**, with no blocking findings. It confirmed unchanged runtime
and dependency direction, exact tested metadata, normal-resolution evidence and
truthful opt-in limitations. Parent acceptance reconciles these results with the
actual diff and the adjacent architecture record.

Final committed CY/queue metadata refresh and remote delivery are still pending;
this review does not substitute for main CY acceptance or physical execution.


## Final committed-pair refresh

Date: 2026-10-29. Final integration checks passed for actual committed CY
`dbde23565a9938cfb7556819ab6a5beee24d5423` (0.43.0) and queue
`114b97272ab5bb406a90c146ea62d8fdd19d75b1` (0.1.4). CY's annotated `v0.43.0`
tag object `877480264094557b82ae1166b1ebbbecbbd27011` peels to the tested release
commit. Its feature parent is `60091649dd71087e5dac2a9a712098eaa5be5de6`.

Clean source captures were verified file-by-file against Git blob identities.
Both committed package metadata files and CY's lockfile exactly match the tested
proposal. All runtime, tests, scripts, browser tests and check configuration are
also identical. Differences from the proposal are restricted to changelog and
acceptance prose. Approved digital-metrics and report-generator source trees and
revisions remain identical to the earlier captured pins.

A fresh frozen requirements export and normal dependency resolution reinstalled
the four committed editable source origins in the retained private environment.
All 285 installed packages were compatible. The source/installed metadata probe
again checked versions, normalized direct requirements, origins and editable URLs
for all four distributions; queue still admits 0.43.0 and excludes 0.44.0.
The canonical CY verification environment and original proposal snapshots were
preserved throughout.

All final commands passed: the ordinary queue suite reported **518 passed,
7 deselected, 19 upstream warnings** in 120.44 seconds; Ruff, formatting, strict
mypy (69 files), both import contracts, installed help and train/pipeline composition
with documentation imports blocked also passed. Installed `cy-docs --check` passed
with 467 fields, 156 configurations and 8 tutorials. A separate isolated catalog
probe asserted that installed CY and catalog versions both equal **0.43.0**.

Committed manifest hashes are CY
`6045f9c9eecbbbffd0c331c1e7615ecc59d8abc29aeeef55438bd6d4a9aebe8d` and queue
`b6e7975e6c5606ff4c4151e8c56722deef8e17ffe6558fbb23036d34a6449f71`; external
manifest hashes remain unchanged. A post-check source inventory found no drift in
any captured repository before this evidence-only appendix. Both appended Markdown
records passed local-link validation.

The retained private task evidence adds `committed-source-manifests.json`,
`committed-proposal-comparison.json`, `committed-source-drift.json`,
`committed-identities.json`, `committed-evidence-hashes.json` and `committed-*.log`.
Exact arguments, exit codes and log hashes are recorded in `results.json`; every
recorded final-command log hash was independently recomputed successfully.

Final committed pairing closes the remaining integration refresh gate after the
accepted independent review. The parent owns evidence commits and remote delivery.
No operational installation, shared worker or physical acceptance claim is added.
