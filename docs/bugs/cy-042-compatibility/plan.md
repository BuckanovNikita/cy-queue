# Prepare CY 0.42 compatibility

Date: 2026-10-29. Companion task for CY feature 007. The published CY bound
`clearml-yolo>=0.38,<0.42` rejects proposed CY 0.42.0. Verify the proposed
CY 0.42.0 / queue 0.1.3 pair before changing real queue metadata to
`clearml-yolo>=0.38,<0.43`. Preserve prior compatibility records.

[Architecture](architecture.json) covers bounded package metadata and focused
queue-to-CY integration verification. Existing exact interface ownership and
negative import tests remain authoritative; no runtime module, dependency direction,
queue protocol, GPU ownership, shared service or operational environment changes.

## Tasks and acceptance

1. Demonstrate old-bound rejection and inspect queue/CY interfaces.
2. Add focused composition/runner tests for no bulk preparation and preservation
   of custom architecture, pretrained and resume selectors.
3. Capture current nonignored CY and queue sources plus approved external copies,
   with before/after hashes rejecting races. Normalize only proposed versions,
   queue upper bound and CY root lock version in disposable snapshots.
4. Normally resolve/install the proposed source pair using copy mode without
   `--no-deps`; assert source/installed versions, import origins and dependency
   consistency from outside the checkouts.
5. Run full queue tests, Ruff, format, strict mypy, import contracts and CLI help.
6. Only after success, prepare real queue 0.1.3 metadata and the verified upper
   bound. Validate task Markdown/links, record drift and remaining acceptance gates.

Parent owns fresh integrated independent review, final-source/version refresh,
commits and authorized delivery. This bounded task makes no commits, installations
into operational environments, live GPU/stand claims or releases. Retain isolated
sources/environment for final refresh. Changing outcomes belong in dated evidence.

## Proposed-pair outcome

The initial complete proposed pair passed normal resolution, exact metadata,
dependency consistency, all ordinary queue tests, static checks, import contracts
and installed CLI help. Real metadata is now prepared as queue 0.1.3 with the
verified `>=0.38,<0.43` range. CY asset-runtime changes during verification require
one final-source refresh. See [dated evidence](verification.md); no delivery or
architecture acceptance is claimed while that gate and parent review remain open.

## Stable-source refresh outcome

The refreshed proposed pair passed every paired check, including all 518 ordinary
queue tests, against the stable final runtime and no local uv source overrides.
Audit found only concurrent CY native-evidence prose changes; runtime/tests/checks,
queue and approved external sources stayed unchanged. Final actual committed
metadata checks and fresh independent review remain parent-owned delivery gates.
