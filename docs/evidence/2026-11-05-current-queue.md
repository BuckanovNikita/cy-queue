# Current-source single-GPU queue verification

Date: 2026-11-05. Result: passed for queued standalone training and pipeline
execution, publication, forced artifact/model downloads, CPU checkpoint inference
and exact-tag cleanup. This is scoped execution evidence, not release completion
or a substitute for the seven physical two-GPU scenarios.

## Tested source pair

The prepared installation used candidate CY **0.46.0** and cy-queue **0.1.9** with
Python 3.12.13. These are proposed release versions, not a claim that either version
was published. Source and installed metadata matched. Runtime identity was
`b0dc39faa82acb608adc53ce740af50d30394074746562da7eab95e2592ec3a3`
and remained identical before and after both jobs.

| Component | Base commit | Working diff SHA-256 |
| --- | --- | --- |
| CY | `8be76e4faaeeb20305f4b9e3be856d8855fc5609` | `5b04c07fbe1474ec205eb6383d801fc3937e74100ebc4388cf0c9af3b084b166` |
| cy-queue | `8a40f8e79d11b9134e0633f62eaa0ca142de81d3` | `83a7af39c6dfe347118b6a2c97fd42c2ba53e8dac3984fa1e3a5feeb339d4377` |

The previously recorded proposed-pair integration checks passed 583 tests with
seven physical tests deselected, normal dependency resolution and static/import
checks. This live run supplements those checks; it does not rerun or relabel them.

## Native execution and readback

Two real queue jobs ran sequentially: `train`, then `pipeline`. Each used six
existing images and ten original annotation rows, with one positive and one empty
image in each split. The recipe was random-initialized YOLOv8n, one epoch, image
size 64, batch two, zero data-loader workers and AMP disabled. Its purpose was
execution verification, not model-quality evaluation.

Both jobs observed a production guardian claim, the configured 12 GiB admission
threshold, actual CUDA execution and training loss output. They reached
`completed` with allocation release. The worker launcher exited zero; repeated
empty-cgroup observations and tracked process identities established cleanup.
No unresolved cleanup errors remained.

| Command | Queue job | ClearML task |
| --- | --- | --- |
| train | `aecf211f-f693-4290-861d-3b9d7225091c` | `f08e5d35002443158e99bff5815fc20b` |
| pipeline | `5eea4549-f0a2-4c28-b5c0-99ca9a79ca72` | `2938527b7c094c31befe3fc8af68823a` |

Authenticated SDK readback verified completed task identity, finite loss scalars,
ground-truth rows including empty images, pipeline prediction/ground-truth row
correspondence and one best output model per task. Required artifacts and models
were force-downloaded. Each downloaded checkpoint matched its unique archived
native checkpoint by SHA-256. Both checkpoints then passed CPU inference on two
held-out images; zero detections from this small verification run were permitted.

The readback subprocess and all observed descendants exited. Exact-tag cleanup
returned zero and removed the local run directory. A subsequent authenticated
query for both exact task IDs returned an empty list. Archived native outputs,
downloads, receipts and failed intermediate checks remain retained privately.

## Harness corrections and preserved failures

The first attempt failed during submission before creating any job: standalone
training does not expose pipeline's `run_dir` or `fiftyone` settings. The corrected
external harness uses `ultralytics.project` and `ultralytics.name` for training,
while the pipeline retains `run_dir`. Real configuration-composition regressions,
ownership/cleanup tests and independent review passed before the successful run.
No product source or scientific configuration was patched to pass this check.

After successful readback and deletion, the original absence check incorrectly
called `Task.get_tasks(task_ids=...)`, which constructs task objects and raises
when an ID has already been deleted. The one-line correction uses an exact-ID
listing filter. Tests exercised the installed SDK request construction, surviving
tasks and query failures. Parent verification and independent review passed before
rerunning only this absence query. Training, downloads and cleanup were not
repeated; their original receipts remained byte-identical.

The corrected harness suite passed 24 CPU tests. Ruff, documentation and
architecture preparation checks passed. Separate independent reviews accepted
the harness preparation and absence-only correction; actual native evidence is
retained independently of those preparation results.

## Acceptance boundary

Private evidence contains the immutable execution, readback, process-cleanup,
stand-cleanup, recovered absence and parent acceptance receipts. Key SHA-256 values:

- Execution: `f24b5da158a04026bd9a0c133d9c29a67dbd75e099eaa5ccac431ae8337d4ad9`.
- SDK/CPU readback: `ccf02fba149435dff4baf8be7cd811e156d16761ecaf48ac956388e1873d1609`.
- Exact task absence: `58ae4aef2579bf519cb7778e798142790fc1866e13f74edfc74eb2f2a6dd85d3`.

Physical two-GPU allocation/contraction, NCCL/DDP, compiled execution, nonowner
rank failure and multi-GPU recovery remain unverified. The estimator catalogue,
original campaign failures, SIGILL incident and final release pairing are separate
open gates. This run does not waive them or claim an instrumented handoff trace.

This document changes no runtime interfaces, dependencies or effect ownership;
the inspected no-impact record is
[2026-11-05-current-queue.architecture.json](2026-11-05-current-queue.architecture.json).
