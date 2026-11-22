# cy-queue reference

Product contract and reference for cy-queue. Read on demand; binding rules for agents
are in [AGENTS.md](AGENTS.md); user-facing syntax is in [README.md](README.md) and
[docs/](docs/README.md) (Russian).

## Architecture and data flow

- Layering: AGENTS.md. The runtime starts `cy_queue.entrypoints.queue_run` as a literal
  subprocess target, not a reverse import.
- Flow: `submit` validates the whole Hydra sweep, freezes a private snapshot per job and
  appends public summaries → owner's `worker` selects jobs, checks admission, reserves
  devices, starts a guardian per job → guardian re-checks memory and opens the exec gate;
  runner execs the CY entrypoint with allocation-relative logical device indexes.

## Domain terms

- **Job**: one owner's durable request to run a frozen experiment; outcome outlives its
  devices. **Allocation**: the ordered physical devices assigned to a job.
- **Reservation**: current exclusive claim on a device; release proves neither process stop
  nor success. **Hold**: a user's exclusion of a device from new allocations.
- **Recovery required** (`recovery_required`): owner must resolve uncertain process
  ownership or cleanup; does not replace the scientific outcome.
- **Metadata root** (shareable, may be NFS) vs **coordination root** (host-local locks);
  **handoff**: post-training contraction of an allocation to its first device.

## Decisions

No ADR or decision ids exist; code cites none. Binding decisions:

- CY minimum-only bound, source-only installs and release rules: AGENTS.md.
- Admission is background-memory admission, not a model-fit guarantee or per-job quota.
- Running jobs never move or get preempted.
- Free/release need no cleanup proof, confirmation or force flag and send no signals.

## Configuration contract

- Settings file: exactly one of absolute `CY_QUEUE_CONFIG`, else
  `$XDG_CONFIG_HOME/clearml-yolo/queue.toml` (absolute non-empty XDG only), else
  `~/.config/clearml-yolo/queue.toml`. No merging, auto-creation or project-local fallback.
- `[queue]` requires `name`, absolute `root` (metadata) and absolute `coordination_root`.
  Optional `max_used_memory_gib`: positive finite TOML int/float, default `2.0`; booleans,
  strings, zero, negatives, nan/inf rejected. No worker CLI override.
- `--root` overrides only metadata storage (legacy root settings must agree). `--help` needs
  no settings; `config` creates no directories, locks, host binding or workers.
- Storage: Linux local FS or NFS with consistent Unix UID mapping, hard mount, shared cache
  and host-local flock (`local_lock=flock` or `all`). Reject `soft`, `softerr`,
  `nosharecache`, remote/unknown flock. NFS outages may block indefinitely; contention
  timeout is not an outage bound. Host coordination locks are process-lifetime exclusive
  across users, metadata roots and mount aliases. Unsupported identity, permissions,
  protocols or locking fail explicitly. Administrators provision mounts, accounts and
  privileged services.
- All participants on one host share machine identity, PID/mount namespaces and the same
  coordination binding; distinct hosts are distinct scheduling partitions. Conflicting
  coordination roots fail before allocation. A reboot starts a new process-identity epoch.
- Public summaries and ordering events are actor-owned; executable snapshots and logs stay
  private to the owner. New shared roots get sticky permissions; existing modes untouched.

## CLI

`cy-queue config|submit|worker|list|move|cancel|recover|archive|restore|tui|gpu`; `gpu`
has `list|disable|enable|free|release`. Most accept `--json`. `cancel`/`recover` take one
owned job; `archive`/`restore` take owned finished jobs.

- `submit`: `pipeline` by default, `--command train` for standalone training; Hydra args
  after `--`. `--gpus N` or `--devices` (exact), never both; at least one whole GPU.
  `--gpus N` above the host's NVML physical GPU count is rejected at submit; when NVML
  cannot be read, the job is accepted unchecked with one stderr warning. A missing
  mandatory CY setting is a one-line `cy-queue:` error naming the key.
  Integer selectors use CUDA-visible logical order and freeze physical identities.
- `move JOB up|down|top|bottom|before|after [REL] --revision N`: stale revisions rejected.
- `gpu` selectors are physical NVML indexes (re-resolve after hardware change or reboot)
  or short labels; absent devices get distinct aliases and older aliases stay valid.

## Submission and scheduling

- Validate the entire sweep before persisting any job; never download model assets at
  submit. Snapshot freezes effective settings, project/directory, interpreter, package
  identity and resources; revalidate before execution; changed installation identity
  requires resubmission. Credentials come from the owner.
- `batch=null` stays unresolved until the worker: CY resolves its editable
  `batch-sizes.yaml` per allocated GPU (exact name/capacity first, then equal-or-lower-VRAM
  fallback); global batch = allocation size × smallest per-GPU batch. Provenance keeps
  table digest, entries and fallback sources. Internal JSON evidence is not a fallback.
  The queue never forwards the standalone estimator's `--force`.
- A sweep gets one fresh shared group tag (explicit tags kept); single runs get none.
  Explicit CPU phases stay CPU; there is no zero-GPU queue mode.
- One worker per owner/root runs concurrent jobs with disjoint allocations. Pick the
  earliest runnable local-host job, skipping owners without workers and jobs lacking a
  complete allocation. Anyone may reorder pending local jobs; only owners cancel, alter
  or recover theirs. Viewing another host is read-only.
- Queued DEIMv2 `l`/`x` pretrained runs may fetch a gated Hugging Face DINOv3 checkpoint
  inside the admitted process using the owner's credentials; no admission bypass.

## GPU memory admission

- Available only if not reserved, not held by anyone, and known used memory is strictly
  below `max_used_memory_gib * 1024**3` bytes. Equality, missing/invalid telemetry or
  unknown ownership blocks launch; stale unlocked metadata alone does not.
- The worker freezes the threshold at startup, injects it into `QueueGPUInventory` and
  `QueueProcesses`, and each `GuardianPayload` carries it for the final fresh check before
  the exec gate. Config edits affect only the next worker start. Reported in
  `config --json` (number), text `max used memory gib`, and the worker startup log.

## Execution, handoff and recovery

- Before launch, establish owner/process identity and independent lifetime protection;
  reject unsupported supervision (pidfd/subreaper). Worker death never frees a live
  workload. Cleanup is bounded, identity-proven, covers descendants, spares reused PIDs.
- Handoff: after successful training a pipeline may keep only its first device. Order:
  durably contract the claim, release extras, acknowledge. No training-finished
  notification → keep full allocation. Lost acknowledgement after contraction stops
  inference and never restores extras. Retained device stays reserved through descendant
  exit unless an operator frees it.
- Cancel: verified owner gets up to 90 s to shut down and publish diagnostics, keeping its
  allocation; then verified whole-tree cleanup. Preserve logs and uncertain evidence.
- Guardian death or uncertain cleanup → `recovery_required`. Recovery needs conservative
  ownership discovery; inaccessible/ambiguous evidence blocks it. Heartbeat expiry, low
  memory or missing parents never prove cleanup. Storage failure stops new admission but
  protects active claims.
- Outcomes: success may precede cleanup; later supervisor uncertainty marks
  `recovery_required` without rewriting a successful ClearML result. Training failure
  fails the job. A pipeline with verified successful training may finish with downstream
  warnings and failed/skipped stages; standalone and skip-training stay strict. Job
  completion never proves capacity release.
- Refresh race guard: worker recovery refresh compares observed public-record revision
  and state inside the storage transaction; newer completion/failure/cancellation/launch
  records stay unchanged and the race is not an error. After seeing a dead guardian,
  refresh rereads the claim and proceeds only if the full retained claim still matches.
  A terminal record with a dead retained claim can still require recovery.

## Device controls

- `disable` adds the caller's hold across all queue roots on the host; any user's hold
  excludes the device. `enable` removes only the caller's hold.
- `free` ≡ `release`: clear all holds and the reservation on that device only, even for
  another owner or an inaccessible queue directory. Idempotent; never touches siblings or
  job outcomes, never cancels/recovers jobs or bypasses the next fresh memory check.
- Operator actions are recorded and fence older reservation generations: earlier
  guardians cannot recreate freed claims, clear newer claims or overwrite newer holds.
  Incompatible workers fail closed; never delete coordination evidence to bypass this.

## Inspection, archive and TUI

- Stable job numbers (`job-17`) survive reorder, archive and restart; never reused.
  Show owner, position, state, requested/allocated devices, wait reason, progress and
  ClearML links. Human output uses readable references; JSON keeps documented fields,
  never private snapshots. Inspection never evaluates saved model config, recovers jobs
  or releases reservations.
- One unreadable private status/snapshot keeps its public summary with a transient
  warning; healthy jobs keep refreshing. Warning counts cover visible jobs only and clear
  after a successful refresh. Queue-wide config/manifest/coordination failure is an
  error; the TUI keeps its last rows. Stale/legacy jobs stay inspectable, never executable.
- Archive hides owned completed/failed/cancelled jobs only; restore never restarts;
  repeats keep the revision. Validate all targets before writes; report partial storage
  failure as retryable. A later recovery requirement unarchives the job.
- TUI: select, reorder, cancel, recover, archive/restore, switch views, open task links;
  keeps selection across refresh; closing it leaves workers running.

## Wire protocols and CY interfaces

- Public record protocol `shared-cy-queue-v1`; GPU controls
  `shared-cy-queue-gpu-controls-v1`; generations `shared-cy-queue-gpu-generations-v2`.
  Keep durable identifiers, record formats, history, config paths and lock names.
- Private `GuardianPayload.max_used_memory_gib` defaults to 2.0 when absent. Older
  binaries reject both that field and the `max_used_memory_gib` config option; never mix
  versions.
- CY modules the queue uses (raise the CY minimum when using a newer interface):
  `adapters.runtime.process_tree` (process identity, pidfd/subreaper, owned-tree cleanup),
  `adapters.runtime.execution_lifecycle` (lifecycle socket/handoff protocol),
  `adapters.runtime.bootstrap`, `adapters.storage.filesystem`,
  `adapters.observability.diagnostics`/`tracing`, `core.presentation`, `core.redaction`,
  `entrypoints.hydra.configs`/`sweeps`/`validation`,
  `application.use_cases.pipeline`/`train`, `application.contracts`,
  `adapters.yolo.config`, `entrypoints.pipeline`/`train`.
  `tests/test_architecture.py` pins exactly this ownership.

## Operations: coordinated upgrade and rollback

Do not delete queue state to make an upgrade pass.

1. Coordinate all users of the metadata and coordination roots; stop submission; let
   work finish or owner-cancel/recover it; confirm guardians and descendants cleaned up.
2. Stop each owner's worker; back up durable records and keep the old environment.
   Never mix old and new live workers.
3. Install compatible CY from source first, then `cy-queue`, into the same environment
   with externally prepared dependencies. Keep `queue.toml` and both roots unchanged.
4. Cancel and resubmit pending jobs whose installation identity changed; never rewrite
   or auto-retry them. Uncertain jobs still need owner recovery.
5. Verify `cy-queue config`, `cy-queue list --json` and `cy-queue submit --help`; restart
   the owners' workers and check each startup log for the applied settings.

Rollback: same drain; restore both packages and a compatible `queue.toml` together; keep
records created since the upgrade. Cancel and resubmit pending snapshots whose identity
changed again; never edit identity, delete fields or rewrite ownership evidence. Before a
downgrade, resolve new private payloads with the newer installation.
Relocating roots requires offline coordination, completed cleanup/recovery and preserved
ownership evidence; a new root cannot bypass live reservations.

## History

The full pre-compression documents are in git at commit `9bcd8fa`; read one with
`git show 9bcd8fa:<path>`. Removed top-level paths: `CLAUDE.md`, `GLOSSARY.md`, `specs/`
(`baseline.md`), `docs/` (`development.md`, `interfaces.md`, `migration.md`, `agents/`).
The current `GLOSSARY.md` and `docs/` are the user glossary and user documentation written
after that commit, not the removed files.
