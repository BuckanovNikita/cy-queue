# Glossary

This file fixes the meaning and the Russian wording of the terms that cy-queue defines or narrows; the Russian pages use the wording on each `_Russian_:` line.

Terms kept in English: GPU, CPU, UUID, NFS, JSON, TOML, YAML, override, sweep, multirun, worker, hold, ClearML, and every command, flag, key, file, field, state value and environment variable name.

## Queue and directories

<a id="queue"></a>
**Queue**:
The shared list of jobs of one host, kept under the queue root and named by `name` in `queue.toml`. Jobs run in queue order on whole GPUs, each by its owner's worker.
_Russian_: очередь
_Avoid_: ClearML queue, task queue

<a id="queue-root"></a>
**Queue root**:
The directory from `root` in `queue.toml` (or the `--root` flag) that holds the jobs, their order and archive marks for every host. It must be an absolute path to a directory.
_Russian_: каталог очереди (queue root)
_Avoid_: shared metadata root, NFS root

<a id="coordination-root"></a>
**Coordination root**:
The directory from `coordination_root` in `queue.toml` that holds the host-local GPU state: reservations, holds and freed-GPU events. It must be on a supported local Linux filesystem or on NFS with `hard` and `local_lock=flock` (or `local_lock=all`), and each host binds to one such directory.
_Russian_: каталог координации (coordination root)
_Avoid_: lock directory, local root

<a id="host-binding"></a>
**Host binding**:
The record `coordination-root.json` under `/tmp/clearml-yolo-queue/<host-id>/` that ties a host to one coordination root. Every subcommand except `config` checks it; a different coordination root fails with "Host coordination is already bound to another location".
_Russian_: привязка хоста (host binding)
_Avoid_: host lock, registration

<a id="host-partition"></a>
**Host partition**:
The part of the queue root that belongs to one host; `list` shows the local host's partition, and `list --host` reads another host's partition without being able to change it. A job reference that is not in the local partition gives "Queue job is missing from the local host partition".
_Russian_: раздел хоста (host partition)
_Avoid_: shard, namespace

<a id="memory-admission-threshold"></a>
**Memory admission threshold**:
The `max_used_memory_gib` key of `queue.toml` (default `2.0`, a positive number, GiB = 1024³ bytes). A GPU whose used memory is at or above it is busy and receives no new job; the worker checks it when choosing a job and again just before the job starts.
_Russian_: порог занятой памяти (memory admission threshold)
_Avoid_: free memory limit, memory reservation

## Jobs

<a id="job"></a>
**Job**:
One CY command (`pipeline` or `train`) frozen by `submit` together with its GPU request, waiting in the queue and later run by its owner's worker. A sweep submits one job per configuration.
_Russian_: задание (job)
_Avoid_: task (that is ClearML's word), run

<a id="job-reference"></a>
**Job reference**:
The name `job-<N>` that `submit` and `list` print as `Job <N>`, where `<N>` is the job's submission number in the host partition; every job command takes it as `JOB`. The full job ID from `--json` is also accepted.
_Russian_: ссылка на задание (job reference)
_Avoid_: job number, job index, position

<a id="owner"></a>
**Owner**:
The Linux user (UID) who submitted a job. Only the owner's worker runs the job, and only the owner may `cancel`, `recover`, `archive` or `restore` it. Any user may `move` a pending job of the host, including another user's.
_Russian_: владелец
_Avoid_: author, submitter

<a id="project"></a>
**Project**:
The CY project directory (`CY_HOME`) a job belongs to, frozen by `submit`. CY write paths such as `run_dir` must lie inside it, and the job writes its log and progress file under `.cy/` in it.
_Russian_: рабочий каталог (project)
_Avoid_: workspace, repository

<a id="working-directory"></a>
**Working directory**:
The current directory at `submit`, frozen in the snapshot; the job process starts in it. The job does not start if it no longer exists.
_Russian_: текущий каталог (working directory)
_Avoid_: рабочий каталог (that is the project)

<a id="package-identity"></a>
**Package identity**:
A fingerprint `submit` freezes in the snapshot: a hash of the Python version, the name and version of every installed package and the installed CY and cy-queue code. A job whose package identity no longer matches at start fails with "Queued package identity changed".
_Russian_: отпечаток окружения (package identity)
_Avoid_: checksum, environment hash

<a id="snapshot"></a>
**Snapshot**:
What `submit` freezes for each job: the fully composed CY configuration, the project and working directory, the Python interpreter, the installed CY version, the package identity (Python version, every installed package and the CY and cy-queue code) and the GPU request. Later changes to configuration files do not reach the job; the job fails at start if the interpreter, the CY version or the package identity changed, or if the project or working directory no longer exists.
_Russian_: снимок задания (snapshot)
_Avoid_: copy, config dump

<a id="sweep"></a>
**Sweep**:
A Hydra multirun given to `submit` (`-m` or `--multirun` written after `--` or after the first override; placed before them, `cy-queue` rejects it as an unrecognized argument). It expands into separate jobs, one per parameter combination, each with its own Hydra output directory and the same GPU request.
_Russian_: sweep
_Avoid_: batch, grid job

<a id="gpu-request"></a>
**GPU request**:
What a job asks for: a count of whole GPUs (`--gpus N`) or exact GPUs in order (`--devices`, CUDA indexes that `submit` turns into GPU UUIDs). `list` prints it as `request=`.
_Russian_: запрос GPU (GPU request)
_Avoid_: quota

<a id="label"></a>
**Label**:
The readable name of a job, shown after the job number. It is `--label` when given, otherwise the configured ClearML task name, otherwise `Pipeline` or `Train`.
_Russian_: имя задания (label)
_Avoid_: title, tag

## States

<a id="job-state"></a>
**Job state**:
Where a job is in its life, printed in `list` and in the `state` field of `--json`. `completed`, `failed` and `cancelled` are final; only final jobs can be archived.
_Russian_: состояние
_Avoid_: status

<a id="pending"></a>
**pending**:
The job waits in the queue for its owner's worker and its whole GPU request; `list` shows why in its waiting reason. Only pending jobs can be moved.
_Russian_: ожидает (`pending`)

<a id="starting"></a>
**starting**:
The worker has taken the job's GPUs and is starting the job process.
_Russian_: запускается (`starting`)

<a id="running"></a>
**running**:
The job process runs on its allocation.
_Russian_: выполняется (`running`)

<a id="cancelling"></a>
**cancelling**:
`cancel` was asked for a starting or running job; the job is being stopped and keeps its GPUs until it ends.
_Russian_: отменяется (`cancelling`)

<a id="completed"></a>
**completed**:
The job process exited with status 0.
_Russian_: завершено (`completed`)

<a id="failed"></a>
**failed**:
The job process exited with a non-zero status or could not be run; the `error` field says why.
_Russian_: завершено с ошибкой (`failed`)

<a id="cancelled"></a>
**cancelled**:
The job was cancelled before it ran, was stopped by `cancel`, or was cleaned up by `recover`.
_Russian_: отменено (`cancelled`)

<a id="recovery-required"></a>
**Recovery required**:
The state `recovery_required`: the queue lost track of whether the job's processes are still running (for example, its guardian died). The job's reservation ends with its guardian, so its GPUs can already show as free while leftover processes still use them. The owner runs `recover`, which stops what is left of the job and makes it `cancelled`; `cancel` alone does not change this state.
_Russian_: требуется восстановление (recovery required)
_Avoid_: crashed, stuck

<a id="waiting-reason"></a>
**Waiting reason**:
The text `list` prints at the end of a pending job's line (field `waiting_reason`), for example `Owner worker unavailable` or `Waiting for GPU capacity: 2 requested, 1 available`.
_Russian_: причина ожидания (waiting reason)
_Avoid_: error, status message

## Workers

<a id="worker"></a>
**Worker**:
The `cy-queue worker` process a user keeps running on the host. It runs only its own user's jobs, and starts a job only when it is the earliest job in queue order, of any user with a live worker, whose whole request fits; one live worker per user and queue root is allowed on a host.
_Russian_: worker
_Avoid_: воркер, обработчик, agent, daemon

<a id="guardian"></a>
**Guardian**:
The process the worker starts for each job; it owns the job's GPUs, runs the job process and cleans up after it. It keeps running when the worker stops, which messages such as "active jobs remain supervised by their guardians" refer to.
_Russian_: guardian (процесс-надзиратель задания)
_Avoid_: supervisor, wrapper

## GPUs

<a id="allocation"></a>
**Allocation**:
The whole GPUs a job holds once it has started, printed as `allocation=` in `list` (`-` when the job holds none). A job starts only when its entire request fits at once.
_Russian_: выделенные GPU (allocation)
_Avoid_: assignment, slot

<a id="reservation"></a>
**Reservation**:
A GPU taken by a job's allocation: a lock in the coordination root that the job's guardian holds while it runs. No other job is admitted to a reserved GPU, whichever queue root it uses. The guardian releases it after verifying that the job's processes are gone; if the guardian dies, the reservation ends with it.
_Russian_: резерв (reservation)
_Avoid_: lock, lease, claim

<a id="hold"></a>
**Hold**:
A mark put on a GPU by `gpu disable` for the user who ran it. While any user's hold is on a GPU, no new job starts on it; `gpu enable` removes only your own hold.
_Russian_: удержание (hold)
_Avoid_: lock, block, disable flag

<a id="gpu-selector"></a>
**GPU selector**:
How the `gpu` subcommands name one GPU: its physical index on the host (as `gpu list` prints it), a full `GPU-<uuid>`, or a short label the coordination root already knows: the GPU label `gpu-<word>-<word>-<word>-<word>` that the queue prints for a GPU it cannot number.
_Russian_: селектор GPU (GPU selector)
_Avoid_: GPU ID, device number

<a id="gpu-label"></a>
**GPU label**:
The short name `gpu-<word>-<word>-<word>-<word>` the queue prints instead of a GPU UUID when it cannot show the physical index; it stays the same for the same GPU.
_Russian_: короткое имя GPU (GPU label)
_Avoid_: alias, nickname

<a id="free-gpu"></a>
**Freeing a GPU**:
`gpu free` (same as `gpu release`) drops every reservation and every user's hold on one GPU, so the queue may admit work to it again. It does not look at or stop any process that still uses the GPU.
_Russian_: освободить GPU (free)
_Avoid_: reset, kill

<a id="gpu-generation"></a>
**GPU generation**:
A per-GPU counter in the coordination root. Freeing a GPU advances it, and reservations and holds made under an older generation no longer count; `gpu free --json` prints the new value as `generation`.
_Russian_: номер поколения GPU (generation)
_Avoid_: epoch, version

## Queue view

<a id="revision"></a>
**Revision**:
A number of the current queue view, printed as `revision N` in the first line of `list` and in `--json`; it grows with every change to the queue. `move --revision` must give the current value, otherwise the command fails with "Stale queue revision; refresh before reordering".
_Russian_: ревизия очереди (revision)
_Avoid_: version

<a id="archive"></a>
**Archive**:
A mark that the job's owner puts on a final job; it hides the job from the default `list` view; `list --archived` shows only archived jobs and `list --all` shows both. `restore` removes the mark; nothing is deleted.
_Russian_: архив / вернуть из архива
_Avoid_: delete, purge

<a id="queue-view"></a>
**Queue view**:
The jobs of one host partition as a command shows them, with the revision and the archive count: what `list` prints and what `list`, `move`, `archive` and `restore` print with `--json`.
_Russian_: вид очереди (queue view)
_Avoid_: snapshot, listing

<a id="job-record"></a>
**Job record**:
The public data of one job (reference, owner, state, request, allocation, waiting reason and the like) that `submit`, `cancel` and `recover` print with `--json` and that the queue view lists.
_Russian_: запись задания (job record)
_Avoid_: job file, row

<a id="refresh-warning"></a>
**Refresh warning**:
A note that the queue could not read a job's current status and shows its last recorded state, for example "Status unavailable; showing last recorded state"; `list` counts them as `warnings N` and `--json` lists them in `refresh_issues`.
_Russian_: предупреждение обновления (refresh warning)
_Avoid_: error
