# Physical two-GPU queue acceptance waiver

Date: 2026-11-07. Result: **waived by user decision (2026-11-06)**, not passed.

## Decision

On 2026-11-06 the user decided that physical multi-GPU (DDP) verification will not
be done for CY and cy-queue. The decision is recorded in CY
`docs/plans/remaining-work-20261106/plan.md` ("Dropped: physical multi-GPU
acceptance") and covers CY 006 T022, the 16 CY T026 DDP scenarios, the CY 006
`ddp-native` architecture check and the seven queue `ddp_gpu` opt-ins below.

## Affected queue tests

All seven tests are in `tests/test_native_ddp_gpu.py` and carry the `ddp_gpu`
marker (`pyproject.toml`). `tests/conftest.py` deselects them from ordinary
`pytest` unless they are requested explicitly.

- `test_physical_native_pipeline`: four cases, direct or queued, eager or compiled.
- `test_physical_queued_failure_cleanup`: three cases, `queued-rank-exit`,
  `queued-cancel` and `queued-guardian-death`.

## Status

The seven opt-ins stay deselected. They were never run on physical multi-GPU
hardware, and earlier records already exclude them from pass counts (for example
[the CY 0.46 pair](../plans/cy-046-compatibility/verification.md): 584 passed,
7 deselected). The tests and their harness stay in the repository unchanged. This
record does not claim multi-GPU correctness, failure recovery or cleanup; any
future physical run needs its own dated evidence.
