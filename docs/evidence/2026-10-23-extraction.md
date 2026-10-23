# Queue extraction verification — 2026-10-23

## Scope

Moved queue policy, records, storage, locks, guardians, inventory/probe and CLI/TUI
from CY into `cy_queue`. Shared process/lifecycle, filesystem, observability and
Hydra command contracts remain in CY. Existing protocol names and storage/config
locations are unchanged. Added standalone train composition/exec and two-package
installation identity. CY's direct physical GPU harness remains queue-independent;
queue keeps the cross-package physical comparison harness and queued cases.

An editable source installation used the existing prepared CY environment with
`uv pip install --python <prepared-environment-python> --no-deps --editable ../cy-queue`.
No dependencies were resolved/replaced, registry published, remote created or live
GPU reservation acquired. Readback found the prepared environment still had CY distribution metadata 0.34.0,
while the current source declares 0.37.0; queue targets >=0.38,<0.39. Parent acceptance must verify the final
compatible-version installation after the CY release/reinstall.

## Executed checks

Commands below used the prepared CY interpreter/development tools. Paths are relative
to the stated working repository rather than machine-specific executable locations.

| Check | Executed command / working directory | Result |
| --- | --- | --- |
| Queue complete routine suite | `uv run --frozen --no-sync pytest ../cy-queue/tests -q` from CY | 490 passed, 7 opt-in physical tests deselected; exit 0 |
| Final queue command/train/import regressions after diagnostic wording | `uv run --frozen --no-sync pytest ../cy-queue/tests/test_queue_commands.py ../cy-queue/tests/test_standalone_training.py ../cy-queue/tests/test_architecture.py -q` from CY | 59 passed; exit 0 |
| Queue strict typing | `mypy .` from queue | 67 source files checked; exit 0 |
| Queue lint and formatting | `ruff check .`, `ruff format --check .` from queue | exit 0 |
| Transitive import contracts | `lint-imports` from queue | 2 kept, 0 broken; exit 0 |
| Architecture negatives | Included in test_architecture.py | Static, type-only, dynamic and worker forbidden edges rejected; initializers inert |
| CY remaining test discovery | `uv run --frozen --no-sync pytest tests --collect-only -q` from CY | 3027 selected, 2 opt-in physical tests deselected; exit 0 |
| CY mixed-test migration | Focused pytest on ddp_gpu_harness, Hydra sweeps/tags, tracing, ground truth, quality properties, Git warning and ClearML cache | 384 passed; exit 0 |
| CY changed test/helper typing | Strict mypy on the 13 changed test/helper files | exit 0 |
| Documentation | CY `scripts/check_docs.py --root .` on README, AGENTS and migration/interfaces/development from queue | 5 Markdown files, 0 issues; exit 0 |
| Architecture planning record | Shared validator, `--phase plan` | exit 0 |

The suite verifies real owned subprocess cleanup and local lock lifecycle with controlled
NVML data. An initial CLI test called the host NVML library and segfaulted during ctypes
loading; faulthandler identified that boundary. The offline fixture now explicitly uses
its existing file-backed NVML double. This makes routine CLI tests independent of real
hardware. No production telemetry behavior or admission threshold was changed.

The physical queue harness now reads JSON submit identities, uses the configured host
coordination root for reservation readback and checks acknowledged contraction to the
first GPU after training. Its seven physical cases were not executed in this stream.
Live multiuser provisioning, physical queue execution, GPU training, Agent execution and
ClearML publication require parent integration evidence. Artifactory connectivity is not
part of the queue stream and remains outside these local claims.

## Acceptance status

Implementation and local checks above are complete for this stream. Fresh independent
cross-repository review, final version-compatible installation, live acceptance and the
parent's release decision are pending. No commit has been made. The architecture review
field remains pending rather than representing these checks as final acceptance.

## Follow-up source installation and real admission preflight

A fresh isolated environment successfully installed both local source checkouts with
`uv pip install --offline --python <isolated-python> --no-deps --editable . --editable ../cy-queue`.
Only the two requested packages were installed; external dependencies were deliberately
not installed. An isolated interpreter outside either checkout imported the inert package
initializers, read CY 0.37.0 / queue 0.1.0 metadata and confirmed the `cy-train` / `cy-queue`
entrypoint ownership and one-way dependency. This establishes source packaging/metadata,
not a complete isolated runtime installation. The temporary environment was removed after
retaining its machine-specific audit in the task's untracked workspace.

The existing prepared environment successfully executed queue and submit help outside the
checkouts, including `--command {pipeline,train}`. Read-only `uv pip check` reported one
incompatibility: installed CY 0.34.0 does not satisfy queue >=0.38,<0.39. The source checkout
version 0.37.0 also precedes that declared release range. Neither CY version nor the shared
installation was modified. Refreshing CY metadata at the final compatible release and
rerunning the package compatibility check remains a parent acceptance requirement.

Additional identity tests confirm both packages' Python source and packaged manifest data
change the snapshot identity, while generated bytecode does not. The standalone/installation
module now has 13 passing tests; its Ruff, formatting and strict mypy checks also pass.

Real NVML and the production `GPUInventory.snapshot()` both succeeded. At the observed
preflight, every physical GPU exceeded the unchanged strictly-below-2-GiB admission limit.
The task-owned untracked preflight JSON retains exact timestamps/bytes. No eligible GPU
was available, and explicit CPU training still requires a positive queue GPU allocation.
No worker, queued native execution, ClearML task or model publication was started. No
threshold, telemetry provider, existing workload, process or shared coordination was
changed. Physical extracted-queue training/publication remains an acceptance gap.

## Final integrated review checks

The final optional-argument validation correction and five regressions are described
in [independent review](2026-10-23-review.md). The complete corrected suite passed
500 tests with seven physical cases deselected. Ruff, formatting, strict mypy for
67 files and both import contracts passed. The parent also verified compatible
candidate source installation using CY 0.38.0 metadata and queue 0.1.0 with externally
prepared dependencies: dependency consistency, entrypoint ownership and packaged
DEIM manifest checks passed. This does not publish that CY version or refresh the
active environment. Physical queue execution remains unavailable.

## Final delivery acceptance

The resumed [live queue acceptance](2026-10-23-live-queue.md) supersedes the earlier
unavailable-physical-execution status above. Real standalone training and pipeline
execution, publication downloads, native checkpoint reload, single-GPU acknowledged
retention and complete owned-resource cleanup passed under the explicitly scoped
16 GiB test ceiling. Production 2 GiB busy rejection remained unchanged and was
verified separately. Ordinary idle-GPU admission and multi-GPU behavior are not
claimed by that run.

Fresh [independent review](2026-10-23-review.md) accepted both the final code and live
evidence. The parent reconciled the architecture record against the final package
and checks; its acceptance validator and all package Markdown/link checks passed.
No production source changed after the complete 500-test suite and static/import
checks. The repository is accepted for its established delivery stopping point:
a Conventional Commit, with no remote creation, tag, push or package publication.
