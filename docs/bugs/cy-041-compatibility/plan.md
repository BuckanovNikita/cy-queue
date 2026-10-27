# Prepare CY 0.41 compatibility

Date: 2026-10-26. This task belongs to CY feature 006, T010/T023. The earlier
`queue-version-compatibility` task and its delivered history remain unchanged.

The current queue bound `clearml-yolo>=0.38,<0.41` excludes the feature's proposed
CY 0.41.0 release. Queue policy requires a version update for a package fix, so the
concrete queue proposal is 0.1.2. Verify that proposed pair using complete isolated
source snapshots before preparing the real queue bound `>=0.38,<0.42`.

The real source versions remain CY 0.40.0 and queue 0.1.1. Only disposable snapshots
receive CY 0.41.0 and queue 0.1.2 metadata. Queue has no lockfile; no lockfile is added.
CY's snapshot lock root version changes alongside its snapshot project version;
all dependency entries and approved external source revisions remain unchanged.
No operational installation, runtime changes, commit, tag or push is authorized here.

[Architecture](architecture.json) covers the bounded metadata contract and existing
null-batch integration tests. Runtime effects, queue records, GPU ownership and
inward dependencies remain unchanged. The parent owns final independent review and
cross-feature acceptance before any later release.

## Tasks and order

- [x] Inspect current source, standing paired-check and queue package-fix rules.
- [x] Plan the metadata boundary and explicit proposed versions.
- [x] Snapshot tracked and untracked nonignored current source, including the new
  null-batch tests; record hashes and the permitted metadata normalization.
- [x] Demonstrate rejection of proposed CY 0.41.0 under the old bound.
- [x] Resolve and install proposed CY 0.41.0/queue 0.1.2 together normally, then
  check source/installed versions, dependency consistency and CLI outside checkout.
- [x] Run full queue integration, null-batch, Ruff, formatting, strict mypy and
  import checks against the same immutable snapshots with CUDA hidden.
- [x] Prepare only the real queue upper bound after successful proposed-pair checks;
  retain real source versions and inspect the complete task-owned diff.
- [x] Record results, limits and documentation checks. Final independent review and
  real-version release checks remain parent gates; no delivery occurs in this task.

## Frozen-runtime refresh

The parent requested a final proposed-pair refresh after the supervised worker's
lazy ownership observer and GPU telemetry/birth-validation ordering correction.
The public typed interfaces are unchanged. This refresh preserves the prepared
real upper bound and real versions, fetches both remotes, captures current source,
and repeats normal resolution, metadata and all queue checks. Runtime, queue tests
and check configuration must remain identical through verification; any unrelated
CY-only physical harness changes must be recorded explicitly. Final architecture
acceptance stays with the parent after independent review.

- [x] Capture current nonignored source after remote refresh and record fingerprints.
- [x] Repeat isolated proposed-version resolution, metadata, integration and static/import gates.
- [x] Audit final source drift, record outcomes, validate documentation and clean owned resources.

## Authorized release amendment

Date: 2026-10-27. The parent now carries the user's new-release request through
the release workflow, preserving the separately reported physical YOLO/DDP
acceptance gaps. Promote the already tested queue proposal to real source version
0.1.2 before freezing queue inputs for the final paired verification. The existing
CY bound and null-batch regression remain unchanged. No operational installation,
queue version tag or deployment is included.

The release companion first freezes all queue files, then repeats isolated normal
resolution, exact source/installed metadata, the full ordinary queue suite, static
checks, import contracts and installed CLI help. Use copy-mode dependency installs
to preserve the operational environment's file identities. Retain isolated sources
and environment until the final CY release metadata can be refreshed and checked.
Record fresh results in CY feature 006 `evidence/release-queue.md`; keeping this
queue record frozen avoids changing the parent's canonical verification inputs.
The parent owns final review, acceptance, commit and authorized remote delivery.
