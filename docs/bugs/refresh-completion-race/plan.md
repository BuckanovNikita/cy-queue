# Preserve newer job outcomes during recovery refresh

**Date**: 2026-11-02. Base: queue 2fbaed2 (0.1.6), CY 6fcc78c (0.44.6).
The user resumed the CY delivery goal after its companion-race blocker was explained;
this bounded fix and package delivery are the required interoperability dependency.
The active CY cleanup ledger owns cross-repository stage order. No operational queue
installation, GPU reservation, shared service, dependency bound or protocol changes.

## Failure and remediation

Final CY/queue integration caught a stale running revision overwriting guardian
completion with recovery_required. A deterministic read-only probe reproduced the
actual runtime/storage writes: completed revision 6 became recovery_required 7 from
stale running revision 5. Guard both recovery writes in QueueProcesses._refresh_job
with one storage-owned transaction comparing observed revision AND state. A changed
record is returned unchanged; a genuinely unchanged lost job still requires recovery.
An unchanged terminal job with a dead retained claim still requires recovery: no
blanket terminal-state exemption. Ownership checks and verified lease release remain.
Do not replace normal races with expected_state exceptions, increase timeouts or retry
until green. Existing public update/transaction_update signatures remain intact.

## Architecture and ownership

[architecture.json](architecture.json) records affected adapters, immutable observation
interface and effect ownership. Storage owns its existing NFS transaction/publication;
runtime owns process/claim observations and calls the guarded transition. No new
module, inner-layer effect, dependency edge or interface exemption is introduced.
Existing import contracts and injected-negative architecture tests remain unchanged.
The bounded implementer owns only storage.py, runtime.py and the new regression test
file. Parent owns this plan/record, package version, contract docs, acceptance and
release. No child delegation. Fresh independent review follows parent verification.

## Tasks and acceptance

- [x] Capture deterministic red interleavings for both recovery branches, newer terminal/launch/same-state revisions, unchanged genuine loss and terminal retained-claim protection.
- [x] Implement the minimal storage transaction guard and route both refresh writes through it; preserve ownership and recovery contracts.
- [x] Update patch version to 0.1.7 and current interface guidance; inspect README/migration and record no-change reasons for unchanged CLI/protocol.
- [x] Run configured full pytest, Ruff/format, strict mypy, import contracts, source/installed metadata/normal resolution, pip consistency and help with current CY 0.44.6; rerun the original real-process failure case.
- [x] Validate changed Markdown/links, obtain fresh independent integrated review, reconcile all task-owned changes and validate architecture acceptance.
- [x] Commit using Conventional Commits and push verified main; no queue tags, GitHub Release objects, assets or registry publication. Reconcile final committed CY/queue sources before CY delivery.

Only isolated task-owned environments/processes and temporary test records are used.
Physical GPU/multiuser/live-stand outcomes remain outside these CPU/fake-telemetry checks.

## Integrated review correction

Fresh queue_final_acceptance returned fix-first for a second ordering of the same
completion race: refresh sees terminal record and retained claim, then guardian
verified release/exit occurs before liveness returns dead. Public revision/state
are unchanged, so the first guard alone cannot distinguish the removed claim.
Before conditional recovery after dead liveness, reread the claim and act only on
the identical retained observation; absent/changed ownership or generation is deferred
to a fresh refresh. Preserve genuinely unchanged dead claims and NFS/GPU lock ordering;
do not nest pool transactions or blanket-exempt terminal records. Add deterministic
terminal-disappearance and changed-claim/generation regressions. Repeat affected/full
paired checks and obtain fresh integrated review before acceptance or delivery.
