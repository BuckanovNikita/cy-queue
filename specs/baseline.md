# cy-queue: functionality

Provide durable whole-GPU scheduling for clearml-yolo experiments shared by cooperating
Linux users. Jobs survive worker restart, execute only as their owner, and distinguish
scientific outcome from process cleanup and device availability. Direct CY commands
remain usable without queue installation or configuration. [Terms](../GLOSSARY.md)
distinguish these independent states.

This specification owns functional behavior. The [user guide](../README.md) supplies
command/configuration syntax; [integration interfaces](../docs/interfaces.md) supplies
exact CY integration and admission fields. Internal process/storage organization may
change while public formats, ownership and coordination guarantees remain compatible.

## Configuration, ownership and storage

Select exactly one explicit absolute CY_QUEUE_CONFIG file or the per-user
XDG/default clearml-yolo/queue.toml. Require queue name, absolute metadata root and
absolute coordination root. No configuration merging, automatic settings creation
or project-local fallback. A command root override changes only metadata storage;
legacy root settings must agree. Help needs no settings; config inspection creates
no directories, GPU locks, host binding or workers.

Metadata may be shared over NFS with consistent Unix UID mapping. Host coordination
must provide process-lifetime exclusive locking across users, metadata roots and
mount aliases. Every participant on one host must share machine identity, PID/mount
namespaces and the same coordination binding; different hosts have distinct identity
and scheduling partitions. Conflicting coordination roots fail before allocation.
A reboot establishes a new process-identity epoch while preserving prior history.

Use supported Linux local storage or NFS with effective hard, shared-cache and
host-local flock semantics (local_lock=flock or all). Reject soft, softerr,
nosharecache and remote/unknown flock behavior. NFS outages may indefinitely block
filesystem operations; a contention timeout is not an outage bound. Unsupported
identity, permissions, protocols or locking fail explicitly. Provisioning mounts,
accounts and privileged services remains an administrator responsibility.

Public summaries and ordering events are actor-owned; executable snapshots remain
private to the submitting owner. New shared roots use sticky permissions while
existing parent/root modes stay intact. Never broaden private snapshot/log access.
Keep durable identifiers, public record formats, history and coordination names.
Relocation requires offline coordination, completed cleanup/recovery and preserved
ownership evidence; selecting a new root cannot bypass live reservations.

## Submission and scheduling

Submit a pipeline by default or standalone training explicitly. Compose and validate
the entire sweep before persisting any jobs; submission does not download model
assets. Freeze effective settings, original project/directory, interpreter, package
identity and resources in each owner's immutable snapshot. Revalidate before execution;
changed installation identity requires resubmission. Credentials come from the owner.

Request at least one whole GPU by count or exact devices, never both. Integer submission
selectors use CUDA-visible logical order and freeze ordered physical identities.
Explicit CPU phases stay CPU but do not create a zero-GPU queue mode. Null training
batch remains unresolved until the actual allocation can select compatible saved CY
capacity evidence. A sweep gets one fresh shared grouping tag, preserving explicit
tags; ordinary single-run submission adds no group tag.

One worker per owner/root may run concurrent jobs with disjoint allocations. Select
the earliest runnable local-host job, skipping owners without workers and jobs without
a complete allocation. Other hosts have independent queues/capacity. All participants
may reorder pending local-host jobs; only owners cancel, alter or recover their jobs.
Running jobs neither move nor preempt. Reject stale revisions on mutations.

Admission excludes current reservations and operator holds and requires known used
VRAM strictly below the configured positive finite threshold, default 2 GiB. Equality
is blocked. This is background memory admission, not a model-fit guarantee or per-job
quota. Freeze the threshold when the worker starts and check it again immediately
before execution. Configuration edits affect the next worker, not running guardians.
Unknown telemetry/ownership blocks launch; stale unlocked metadata alone does not.

## Execution, handoff and recovery

Before launching native work, establish owner/process identity and independent lifetime
protection for allocations. Reject unsupported Linux process supervision before launch.
Worker death cannot free a live workload. Protect unrelated and reused process IDs;
cleanup must remain bounded and identity-proven, including descendants.

After successful training, a pipeline may release extra GPUs and continue inference
on its first allocated device. First durably contract the claim, then release extras
and acknowledge. Without a training-finished notification retain the full allocation.
Lost acknowledgement after contraction stops inference and never restores released
extras. The retained device remains reserved through descendant exit unless explicitly
freed by an operator.

Cancellation first gives the verified owner up to 90 seconds to shut down and publish
diagnostics while retaining its allocation, then performs verified whole-tree cleanup
if needed. Forced termination can leave publication incomplete; preserve logs and
uncertain evidence. Guardian death or uncertain cleanup requires explicit owner recovery,
never automatic retry. Recovery needs conservative ownership discovery; inaccessible or
ambiguous evidence blocks it. Heartbeat expiry, low memory or missing parents alone
cannot prove cleanup. Storage failure stops new admission while protecting active claims.

Successful computation/publication may precede completed queue cleanup. Later supervisor
uncertainty marks recovery_required without rewriting a successful ClearML result.
Training failure/interruption fails the task. A pipeline with verified successful training
may finish with explicit downstream warnings and failed/skipped stages; standalone and
skip-training commands remain strict. Job completion alone never proves capacity release.
Concurrent refresh must not replace newer launch/completion/failure/cancellation evidence
with stale observations or discard retained claims.

## Device controls

GPU inspection and disable/enable/free/release use physical NVML indexes, independent
of submission's CUDA-visible logical order. Resolve indexes again after hardware change
or reboot. Absent devices have distinct readable aliases; accepted older aliases remain
valid inputs. Public output omits claim tokens, full UUIDs and private process data.

Disable adds the caller's hold across all queue roots on that host, preventing new
allocations without disturbing active jobs. Any user's hold excludes a device. Enable
removes only the caller's hold. Free and release are equivalent explicit declarations
that clear all existing holds and the reservation on only the selected device, even
when another owner holds it or its queue directory is inaccessible. They require no
cleanup proof, confirmation, reason, token or supplementary force flag and send no signals.
Repeated freeing succeeds; sibling-device reservations and job outcomes remain unchanged.

Record the operator action and fence prior reservation generations: earlier guardians
cannot recreate freed claims, clear newer claims or overwrite newer holds. Freeing does
not cancel, complete or recover a job and does not bypass the next launch's fresh memory
check. New holds apply normally. Incompatible workers must fail closed rather than
ignore control events; never delete coordination evidence to bypass compatibility.

## Inspection, archive and terminal interface

Stable job numbers survive reorder, archive and restart and are never reused. Names
may repeat; numbers distinguish them. Show owner, position, state, requested/allocated
devices, wait reason, progress and readable ClearML links. Human output uses readable
references; explicit JSON preserves documented machine fields without private snapshots.
Viewing another host is read-only. Inspection never evaluates saved model configuration,
recovers jobs or releases reservations.

If one private status/snapshot cannot be read or validated, retain its public summary
with a transient warning and continue refreshing healthy jobs. Warning counts cover
only visible jobs and disappear after successful refresh. Queue-wide configuration,
manifest or coordination failure remains an error; the terminal view retains its last
rows. Stale/legacy jobs can remain inspectable without becoming executable.

Owners may archive completed, failed or cancelled jobs and restore visibility. Pending,
active and recovery-required jobs cannot be hidden. Restore does not restart a job;
repeated requests do not change revision. Validate all targets before writes; a storage
failure may leave earlier targets changed and must report that retryable partial result.
A later recovery requirement makes an archived job visible again.

The terminal UI supports selection, reorder, cancel, recover, archive/restore, view
switching and opening task links. Refresh preserves selection when still visible.
Closing the UI leaves workers running. Commands remain usable without the UI.

## Compatible installation and upgrades

Install compatible CY and queue sources in the same prepared environment, respecting
package metadata bounds and rejecting stale installed identity. CY does not depend on
queue packages. Neither distribution is assumed published on a package index.

Coordinate all participants before replacing packages or coordination storage: stop
submission, finish or owner-cancel/recover live jobs, verify cleanup, stop workers and
preserve records and old environment. Install the compatible pair together; pending
snapshots with changed identity must be cancelled/resubmitted, never rewritten or
silently retried. Rollback follows the same drain and retains newly created history.
Exact operator steps and private-payload compatibility are in [migration](../docs/migration.md).
