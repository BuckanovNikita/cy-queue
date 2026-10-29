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
