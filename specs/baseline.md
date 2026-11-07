# cy-queue: functionality

## Problem

Experiment operators share scarce GPUs and need durable scheduling without launching
work under another user's identity, losing jobs on restart, freeing live allocations,
or confusing successful computation with verified process cleanup.

## Function

Provide a persistent CY-specific whole-GPU queue with explicit submission, owner-run
workers, cancellation, recovery, inspection and a terminal interface. Direct
clearml-yolo commands remain usable without installing or configuring the queue.

## How scheduling works

- Install compatible source versions of both distributions in one environment; enforce
  package metadata bounds and reject stale installed identity. Queue depends on CY;
  CY never imports queue packages. Pure queue policy has no filesystem/SDK effects.
- Resolve explicit or XDG/default per-user configuration without merging or implicit
  storage creation. Metadata and host coordination have distinct ownership and locking
  requirements. Preserve shared record formats, identifiers and coordination names.
- Submit pipeline by default or explicit standalone training. Validate an entire sweep
  before persisting jobs, freeze effective inputs and preserve explicit CPU phases.
  A changed interpreter or installation identity requires resubmission.
- Workers launch only their Unix owner's jobs. Admission reserves whole devices and
  fails closed for uncertain telemetry/ownership. Apply the configured positive finite
  memory threshold at allocation and immediately before execution; equality is blocked.
  Running guardians retain their worker's frozen threshold.
- Guardians retain process/lock ownership through worker death and verified cleanup.
  Training completion may durably shrink allocation to the first GPU before acknowledged
  handoff; missing notification retains all devices and lost acknowledgement stops
  inference without restoring released extras.
- Cancellation has bounded, identity-proven cleanup. Uncertain ownership requires
  explicit recovery; no operation signals unrelated or reused processes. Computation
  success does not prove released leases.
- Concurrent refresh compares observed revisions/state and rereads retained claims;
  stale observations never overwrite newer completion, failure, cancellation or launch.
- Stable job numbers survive reorder, archive and restart. Owner archive/restore changes
  visibility only; recovery-required jobs remain visible. Per-job refresh failure keeps
  the public summary and does not hide healthy jobs or mutate reservations.
- Physical-device release is generation fenced, preserves sibling claims and outcomes,
  and never bypasses fresh launch admission. Terminal inspection reports truthful state.
- Upgrade by coordinated drain and compatible installation; retain persistent history
  and ownership rather than trying to translate private in-flight payloads.

## Detailed contracts

[Integration interfaces](../docs/interfaces.md) define CY composition, GPU memory
admission and refresh races. [Migration](../docs/migration.md) defines drain, upgrade
and resubmission. The [user guide](../README.md) defines commands and configuration.
The maintained [CY queue contract](https://github.com/BuckanovNikita/clearml-yolo/blob/master/docs/queue.md)
defines storage eligibility, ownership, device operations and lifecycle semantics.
