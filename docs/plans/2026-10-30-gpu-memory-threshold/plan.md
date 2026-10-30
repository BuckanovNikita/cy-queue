# Configurable queue GPU memory threshold — 2026-10-30

Expose the already supported GPU inventory memory threshold through strict queue
configuration, keeping the portable default 2.0 GiB. The worker must use the same
positive finite threshold for scheduler observations and the guardian's fresh
startup check. Usage equal to or greater than the configured threshold remains
unavailable, as does missing telemetry. Whole-GPU reservations, holds and ownership
rules are unchanged. The user-selected machine value belongs in private local
configuration, not this repository.

This isolated checkout starts from queue 0.1.5 at 397753c. It owns only queue paths.
Python compatibility remains >=3.12.13,<3.14, uv_build remains the backend and the
approved CY >=0.38,<0.45 dependency remains unchanged. Existing prepared tools may
be read through CY's environment, but this task must not install into it or the
companion-owned paired environment. Package fix version is 0.1.6. Initial implementation
stopped before commit or push.
After paired verification and fresh review, the parent authorized the task-scoped
commit; final release-source refresh and publication remain parent-owned.

## Architecture

[architecture.json](architecture.json) records responsibilities, explicit interfaces,
effect ownership and acceptance. Reuse tests/test_architecture.py (including
forbidden-edge negative cases) and .importlinter. No new module is warranted:
settings validates at the configuration boundary, entrypoint composition injects
inventory/process dependencies, private transport carries the frozen policy, and
the existing guardian adapter applies it without rereading configuration.
Historical private payloads without the new field use 2.0; older binaries do not
understand new private payloads, so coordinated upgrade guidance must describe
that constraint. Shared public protocol, job snapshots and lock records stay unchanged.

## Tasks and sequence

- [x] Inspect current implementation, configuration, tests, existing changes and native workflow.
- [x] Validate this architecture plan before code edits.
- [x] Add failing regressions for default/configured threshold and invalid values.
- [x] Implement configuration-to-admission-to-guardian propagation and diagnostic display.
- [x] Update portable documentation and migration notes; bump queue to 0.1.6.
- [x] Run focused regression, full/static/import and documentation checks; record actual evidence.
  The borrowed-environment metadata failure is preserved in verification history;
  the normally resolved candidate pair subsequently passed the complete suite.
- [x] Parent integrates and verifies the current normally resolved CY/queue candidate pair.
- [x] Parent obtains fresh independent review and reconciles the actual task-owned diff.
- [x] Validate final architecture acceptance and documentation.
  The task-scoped Conventional Commit follows these accepted checks.
- [ ] Parent refreshes the installed pair against the actual CY release commit before publication.

Implementation is sequential because settings, process transport and entrypoint
composition share one contract. Parent and companion agents independently own
private environment configuration, CY release, paired installation and corporate
portable documentation. This bounded agent must not delegate further. No physical
GPU workload or running-worker intervention is needed for these checks.
