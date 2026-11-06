# CY 0.46 compatibility — 2026-11-05

The selected parent integration combines the DINOv3 fix, scoped campaign
improvements and forced batch-estimation support into CY 0.46.0. Queue 0.1.8
currently excludes that minor. Prepare queue 0.1.9 with the next tested bounded
requirement `clearml-yolo>=0.38,<0.47`; complete final paired verification against
the parent's frozen CY 0.46.0 candidate before acceptance or delivery.

## Inspected interfaces and architecture

The preserved force diff adds an optional strict boolean `SearchSettings.force`,
defaulting to false, keeps historical ordinary estimate keys, and creates distinct
forced keys. GPU inventory functions gain keyword-only optional arguments; their
existing callers retain their interfaces. The direct estimation CLI consumes the
new switch. Queue runtime does not call those estimator or inventory functions:
its composition freezes native training settings, leaves automatic batch values
unresolved until allocated execution, and execs existing CY pipeline/train roots.
Queue integration tests consume CY estimate records and therefore need the final
paired suite, not an assumption of compatibility from metadata alone.

No queue runtime code, public records, lifecycle socket, reservation, cancellation,
recovery, ownership, or GPU admission policy changes are planned. The distribution
metadata owns the compatibility declaration. The [architecture record](preparation-architecture.json)
maps that declaration to existing installation, inward-dependency and negative
architecture tests. There is no queue lockfile; do not create one or resolve a new
CY dependency graph. Parent CY lock changes remain under the parent task's ownership.

The preserved force implementation is inspection input, not final-source evidence:
the parent is reconciling its final policy. Inspect and test the frozen candidate
after the parent signals readiness. Previous CY 0.45.1/0.45.2 passes are historical
and do not establish compatibility with the new minor.

## Scope and sequence

1. Validate the architecture plan before changing compatibility contracts.
2. Add the proposed-minor boundary regression; observe failure with the old bound.
3. Bump queue patch metadata, widen only the tested next-minor bound, and document
   the inspected unchanged runtime/upgrade contracts.
4. Wait for the frozen CY 0.46.0 candidate. Install both sources normally into the
   isolated queue environment, preserving approved external revisions and using
   neither `--no-deps` nor the parent's running environment.
5. Verify dependency resolution, matching source/installed metadata, full ordinary
   queue integration, statics/imports, command help and Markdown/local links.
6. Parent: obtain fresh independent integrated review, reconcile the complete diff,
   validate architecture acceptance, and verify the actual final source/installed
   pair before authorized delivery. This bounded task does not commit or push.

## Tasks

- [x] Validate the scoped architecture plan.
- [x] Observe a failing CY 0.46 acceptance / CY 0.47 rejection regression.
- [x] Update version, bounded dependency, boundary test and interface guidance.
- [x] Receive and inspect the frozen final CY candidate.
- [x] Run normal paired installation and all required checks; record exact identities.
- [ ] Parent: fresh review, final reconciliation and architecture acceptance.
- [ ] Parent: verify actual post-hook versions before delivery.
