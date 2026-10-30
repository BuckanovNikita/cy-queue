# GPU memory threshold verification — 2026-10-30

## Scope and behavior

The isolated queue checkout starts at `397753c` (0.1.5), with proposed source version
**0.1.6** and unchanged `clearml-yolo>=0.38,<0.45` requirement. Task-owned runtime
changes are the six modules in [architecture.json](architecture.json): configuration,
inventory, guardian records, process runtime, guardian startup and CLI composition.
Four existing test files gain behavioral regressions; README, interfaces and
migration document the optional setting. No public job/snapshot/lock protocol,
model dependency, operational environment or existing worker is changed.

`queue.max_used_memory_gib` defaults to 2.0 and accepts positive finite TOML
integers/floats. It rejects zero, negative, boolean, string and nonfinite input
before creating queue resources. Both admission and the fresh guardian check use
strictly less than `threshold * 1024**3` bytes; unavailable telemetry still blocks
that GPU. Private payloads freeze the selected value; historical payloads without
it default to 2.0. Shared public protocol remains `shared-cy-queue-v1`.

## Executed implementation checks

Architecture plan validation passed before any runtime edits. The test-first run
reproduced the missing configuration field (4 failures), then missing adapter and
process constructor parameters/private payload support (16 failures, 6 existing
cases passed). The CLI-composed service regression also failed on the previously
unknown configuration option before implementation.

Tools were read from an existing prepared environment without installing into it.
`QUEUE_SRC` is this isolated checkout; `TOOL_ENV` denotes that borrowed environment.
The final focused run used an absolute source path, so subprocess imports select
this checkout even after a working-directory change:

```bash
PYTHONPATH="$QUEUE_SRC/src" "$TOOL_ENV/bin/python" -m pytest -q tests/test_architecture.py tests/test_queue_settings.py tests/test_queue_admission.py tests/test_gpu_resources.py tests/test_queue_logging.py --tb=short
"$TOOL_ENV/bin/ruff" check .
"$TOOL_ENV/bin/ruff" format --check .
PYTHONPATH="$QUEUE_SRC/src" "$TOOL_ENV/bin/mypy" .
PYTHONPATH="$QUEUE_SRC/src" "$TOOL_ENV/bin/lint-imports"
```

- Focused behavior and architecture: **212 passed in 12.42 seconds**.
- Ruff check and format: passed; 91 files formatted.
- Strict mypy: passed for 69 source files.
- Import-linter: both contracts kept, 67 files and 209 dependencies analyzed.
- `git diff --check`: passed.

The tests cover default/configured thresholds, exact boundary and one byte on
both sides, missing telemetry, bad configuration, effective CLI JSON/text and
worker diagnostics, rejection of the removed worker flag, historical/private
payload semantics and a real owned subprocess. The CLI-composed service admits
controlled 8 GiB usage under a 12 GiB threshold and executes the owned child,
proving both constructor injections. Actual NVML is replaced with controlled
telemetry; no physical training/GPU or ClearML publication result is claimed.

The full source suite also ran before paired installation:

```bash
PYTHONPATH=src "$TOOL_ENV/bin/python" -m pytest -q --tb=short
```

Result: **543 passed, 1 failed, 7 deselected, 19 warnings in 134.12 seconds**.
The sole failure is
`test_standalone_training.py::test_current_source_and_installed_versions_are_compatible`:
borrowed installed queue metadata is 0.1.3 while this source is 0.1.6. This was a
failed pre-installation check, not a passing full-suite result. The later paired
run below resolves the metadata gap without altering the borrowed environment. The deselected tests
require opt-in physical execution; warnings are upstream hydra-zen/Pydantic
deprecations. No installation into the borrowed environment was attempted.

Initial formatting and one strict-mypy error in test kwargs were corrected. The
final focused/static checks above cover those changes; runtime and test sources
were frozen before the companion's normally resolved CY 0.44.4/queue 0.1.6 pair.

## Documentation

Russian README, English interfaces/migration and the plan passed markdownlint-cli2.
The task check uses 100-column prose with existing code blocks and tables exempt;
the repository has no configured Markdown lint profile. The initial default
80-column check reported existing long prose/tables as well as new plan lines.
Eight local links across these four documents resolved, including target anchors
where present, and the README TOML example parsed with `max_used_memory_gib = 2.0`.
The settings regressions validate that same optional default through its real loader.

## Paired verification and independent review

The companion normally installed the frozen proposed CY 0.44.4 and queue 0.1.6
sources in its isolated environment. Candidate CY is based on source HEAD
`02e2d50ad9f3dd6ea619f69adfe5ffc45c32f361`; the queue patch is based on
`397753c123f379ade50f06a2babf5e4b1476b9d2`. Source HEAD alone does not identify the
uncommitted candidate: the queue's 73 runtime/test/check/metadata files were frozen
with aggregate inventory SHA-256
`144e304da02e2b14fc2e9b25f38c7742a89b72c7eaf35bdae732be622c203af6`.
The companion and fresh reviewer each verified this inventory remained unchanged.
Only task documentation and acceptance bookkeeping changed after the freeze.

The approved editable dependencies remained at digital-metrics
`6e801be1564dce458294eb23592cc1aa0939c4d9` and report-generator
`d10aa395d08f738e92e04e076cee93b3a993bf8f`. The companion's identity helper checked
source and installed versions, editable import origins and these approved pins.
The dependency bound remains `clearml-yolo>=0.38,<0.45`.

The actual normal-resolution installation command, from the task base, was:

```bash
UV_LINK_MODE=copy uv pip install --python paired-env/bin/python -e paired-cy-proposed -e cy-queue-memory -e repo/external/digital-metrics -e repo/external/report-generator
```

From the queue checkout, the companion ran:

```bash
CUDA_VISIBLE_DEVICES= UV_PROJECT_ENVIRONMENT=../paired-env uv run --frozen --no-sync --project ../paired-cy-proposed python -m pytest -q
UV_PROJECT_ENVIRONMENT=../paired-env uv run --frozen --no-sync --project ../paired-cy-proposed python -m ruff check .
UV_PROJECT_ENVIRONMENT=../paired-env uv run --frozen --no-sync --project ../paired-cy-proposed python -m ruff format --check .
UV_PROJECT_ENVIRONMENT=../paired-env uv run --frozen --no-sync --project ../paired-cy-proposed python -m mypy .
UV_PROJECT_ENVIRONMENT=../paired-env uv run --frozen --no-sync --project ../paired-cy-proposed lint-imports
uv pip check --python ../paired-env/bin/python
CUDA_VISIBLE_DEVICES= UV_PROJECT_ENVIRONMENT=../paired-env uv run --frozen --no-sync --project ../paired-cy-proposed cy-queue --help
```

Results: **544 passed, 7 physical-GPU tests deselected, 19 existing upstream
warnings in 133.74 seconds**. Ruff and format passed for 91 files; strict mypy
passed for 69 source files; both import contracts passed. Normal installation
resolved 243 packages and refreshed the four editable distributions. Dependency
checking passed for the prepared environment's 286 packages. CLI help and exact
source/installed metadata and origins passed. The retained companion logs are
`proposed-queue016-install.log`, `proposed-queue016-pytest.log` and
`proposed-queue016-identities.json`; source identity is retained in
`queue016-source-inventory.json` alongside `verify_queue_source.py`.

Parent integration verification reran the four focused behavior files against the
normally installed pair: **199 passed in 12.47 seconds**. Fresh independent reviewer
`review_queue_memory` returned **SHIP**, with no findings, after reviewing the queue
implementation and portable guidance. It independently verified 88 focused tests,
the 73-file inventory, dependency check, local links and architecture plan. See
[review](review.md) for scope and reconciliation.

Final architecture acceptance validation passed with the installed architecture
validator (`--phase acceptance --repo-root .`). The source inventory checker again
reported 73 checked files and no differences after the evidence update. No runtime
or test changes followed the paired checks or fresh review.

## Completion boundary

Implementation, candidate-pair verification and independent review are accepted.
The task-scoped Conventional Commit is authorized after final documentation and
architecture validation. Parent retains the final refresh against the actual CY
release commit before pushing. No tag, publication, deployment, operational
installation or worker restart is performed by this bounded agent.
