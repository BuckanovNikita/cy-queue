# Queued batch alignment fixture — 2026-11-02

## Scope and architecture

CY automatic batch search now uses multiples of eight images per GPU. The queue
integration fixture previously requested a global ceiling of eight on two GPUs,
which can supply only four images per GPU. It therefore fails before constructing
its saved estimate. Change only that synthetic ceiling and expected resolved batch
to global sixteen/per-GPU eight. Preserve the single-GPU source at thirty-two,
exact allocation preference, assigned-device mapping and canonical requested null.

The [architecture record](architecture.json) records inspected no-impact ownership.
No queue runtime behavior or package version changes. The existing
[interfaces](../../interfaces.md) remain authoritative.

## Plan and acceptance

- Record the original failing path and architecture before editing.
- Correct only the fixture ceiling and corresponding batch assertions.
- Run full queue pytest, Ruff, format, strict mypy, import contracts and installed help.
- Validate Markdown/local links and the architecture record.
- Commit the task-owned test and evidence after verification; coordinate paired
  proposed/final CY version evidence with the parent release workflow.

## Original observation

Against latest CY source with the alignment change, the unmodified queue suite
reported one failure and 581 passes, with seven physical cases deselected.
`test_worker_resolves_the_allocated_gpu_count_without_replacing_requested_null`
failed in `BatchSearch.start`: the search ceiling must cover at least eight images
per rank. This is fixture drift caused by the intentional CY policy change.

## Verification

The four fixture/assertion edits preserve the original regression's exact-allocation
preference and requested-null checks. Both normal dependency-enabled resolutions
used prepared packages offline; no dependency was skipped or upgraded. CY and queue
source versions, installed metadata and editable import origins agreed in each
selected environment; `uv pip check` reported all 286 installed packages compatible.

| Check | Current CY 0.44.6 plus alignment patch | Proposed CY 0.44.7 snapshot |
| --- | --- | --- |
| Full `python -m pytest -q` | 582 passed, 7 deselected, 19 warnings; 134.69 s | 582 passed, 7 deselected, 19 warnings; 131.81 s |
| `python -m ruff check .` | passed | passed |
| `python -m ruff format --check .` | 97 files formatted | 97 files formatted |
| `python -m mypy .` | 70 source files passed | 70 source files passed |
| `lint-imports` | 2 contracts kept | 2 contracts kept |
| `cy-queue --help` | passed | passed |

The architecture suite, including forbidden-edge negative cases, ran as part of each
full pytest invocation. Markdown/local-link checking and architecture record planning
validation passed. Acceptance validation is performed after this evidence update.
Seven physical opt-ins were deselected; these runs establish offline integration,
not GPU throughput, physical queue execution or ClearML publication.

## Source and release boundaries

Queue source baseline is `4e539f227f06e600d95753e27049baf6df517398`
(version 0.1.7), with this test-only amendment. CY source baseline is
`6cccd55` (version 0.44.6), with the parent's alignment change. The proposed
snapshot differs in root version tokens only from that tested application behavior.
Its estimator implementation SHA-256 is
`5eccce1a28501edc7ed7411d8a9997b1f4c910e85a7f0f1ca2e05bf7c5af4af8`,
matching the parent implementation at this checkpoint.

The source remains compatible with the queue's existing `>=0.38,<0.45` CY bound.
No queue runtime change or package-version bump is needed. The parent release
workflow owns consolidated final review, commits, final committed-pair verification
and delivery. Proposed-version success alone is not evidence that a release was
created or pushed. Original workspaces, installed environments and running workloads
were preserved; all checks used isolated task-owned sources and environments.
