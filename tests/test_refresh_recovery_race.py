"""Recovery refresh must not overwrite a record published after its observation."""

import os
import sys
from pathlib import Path

import pytest

from cy_queue.adapters.queue import runtime, storage
from cy_queue.adapters.queue.runtime import QueueProcesses
from cy_queue.adapters.queue.storage import NFSQueueStore
from cy_queue.core.queue import GuardianClaim, JobSnapshot, JobState, PublicJob, WorkerIdentity


@pytest.fixture
def refresh_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim]:
    identity = WorkerIdentity(owner_uid=os.geteuid(), host_id="host", boot_id="boot")
    store = NFSQueueStore(tmp_path / "queue", identity, local_root=tmp_path / "local")
    job = store.submit(
        (
            JobSnapshot(
                command="train",
                config_json="{}",
                project_root=str(tmp_path),
                cwd=str(tmp_path),
                interpreter=sys.executable,
                package_version="1",
                package_identity="hash",
            ),
        )
    )[0]
    job = store.update(job.id, "running", devices=("GPU-test",))
    processes = QueueProcesses(store, identity, local_root=tmp_path / "local")
    claim = GuardianClaim(
        job_id=job.id,
        owner_uid=identity.owner_uid,
        host_id=identity.host_id,
        boot_id=identity.boot_id,
        queue_root=str(store.root),
        devices=job.devices,
        marker="test-marker",
        guardian_pid=123,
        guardian_born=456,
    )
    monkeypatch.setattr(runtime, "process_birth", lambda pid: None)
    # Exercise the expired launch path without wall-clock sleeps or live processes.
    monkeypatch.setattr(runtime, "_STARTUP_WINDOW_SECONDS", 0)
    return store, processes, job, claim


@pytest.mark.parametrize("retained_claim", [False, True], ids=["no-claim", "dead-claim"])
@pytest.mark.parametrize("new_state", ["completed", "failed", "cancelled", "starting", "running"])
def test_refresh_preserves_newer_publication(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
    monkeypatch: pytest.MonkeyPatch,
    retained_claim: bool,
    new_state: JobState,
) -> None:
    store, processes, observed, claim = refresh_case
    published: list[PublicJob] = []
    writes_after_publication: list[Path] = []
    atomic_write = storage.atomic_write

    def track_write(path: Path, payload: str, mode: int = 0o644) -> None:
        if published:
            writes_after_publication.append(path)
        atomic_write(path, payload, mode)

    def interleave(identifier: str) -> GuardianClaim | None:
        assert identifier == observed.id
        if not published:
            published.append(store.update(identifier, new_state, error="newer outcome"))
        return claim if retained_claim else None

    monkeypatch.setattr(storage, "atomic_write", track_write)
    monkeypatch.setattr(processes.pool, "claim_for", interleave)
    processes._refresh_job(observed)

    assert store.view().jobs == (published[0],)
    assert writes_after_publication == []


@pytest.mark.parametrize("retained_claim", [False, True], ids=["no-claim", "dead-claim"])
@pytest.mark.parametrize("state", ["starting", "running", "cancelling"])
def test_refresh_still_recovers_unchanged_lost_active_job(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
    monkeypatch: pytest.MonkeyPatch,
    retained_claim: bool,
    state: JobState,
) -> None:
    store, processes, job, claim = refresh_case
    observed = store.update(job.id, state)
    monkeypatch.setattr(
        processes.pool, "claim_for", lambda identifier: claim if retained_claim else None
    )
    processes._refresh_job(observed)

    result = store.view().jobs[0]
    assert result.state == "recovery_required"
    assert result.revision == observed.revision + 1
    assert result.devices == observed.devices
    assert result.error == (
        "Guardian exited without verified cleanup; owner recovery required"
        if retained_claim
        else "Execution state is uncertain; owner recovery required"
    )


@pytest.mark.parametrize("state", ["completed", "failed", "cancelled"])
def test_unchanged_terminal_with_dead_claim_still_requires_recovery(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
    monkeypatch: pytest.MonkeyPatch,
    state: JobState,
) -> None:
    store, processes, job, claim = refresh_case
    observed = store.update(job.id, state)
    monkeypatch.setattr(processes.pool, "claim_for", lambda identifier: claim)
    processes._refresh_job(observed)

    result = store.view().jobs[0]
    assert result.state == "recovery_required"
    assert result.revision == observed.revision + 1


def test_conditional_recovery_returns_current_record_without_publication(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, _, observed, _ = refresh_case
    current = store.update(observed.id, "completed")

    def unexpected_write(path: Path, payload: str, mode: int = 0o644) -> None:
        pytest.fail(f"Stale recovery published {path}")

    monkeypatch.setattr(storage, "atomic_write", unexpected_write)
    assert store.mark_recovery_if_unchanged(observed, error="lost") == current


@pytest.mark.parametrize("retained_claim", [False, True], ids=["no-claim", "dead-claim"])
def test_refresh_also_requires_matching_observed_state(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
    monkeypatch: pytest.MonkeyPatch,
    retained_claim: bool,
) -> None:
    store, processes, current, claim = refresh_case
    # Isolate state comparison from revision comparison at the storage boundary.
    observed = current.model_copy(update={"state": "starting"})
    monkeypatch.setattr(
        processes.pool, "claim_for", lambda identifier: claim if retained_claim else None
    )
    processes._refresh_job(observed)
    assert store.view().jobs == (current,)


def test_conditional_recovery_still_checks_owner_for_stale_observation(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
) -> None:
    store, _, observed, _ = refresh_case
    current = store.update(observed.id, "completed")
    store.identity = store.identity.model_copy(update={"owner_uid": os.geteuid() + 1})
    with pytest.raises(PermissionError, match="effective job owner"):
        store.mark_recovery_if_unchanged(observed, error="lost")
    assert store.view().jobs == (current,)


@pytest.mark.parametrize("state", ["completed", "failed", "cancelled"])
@pytest.mark.parametrize(
    "claim_change", ["released", "owner", "guardian", "generation", "identities"]
)
def test_terminal_refresh_defers_claim_changed_during_liveness_check(
    refresh_case: tuple[NFSQueueStore, QueueProcesses, PublicJob, GuardianClaim],
    monkeypatch: pytest.MonkeyPatch,
    state: JobState,
    claim_change: str,
) -> None:
    store, processes, job, claim = refresh_case
    observed = store.update(job.id, state)
    retained: GuardianClaim | None = claim
    reads = 0
    publications: list[Path] = []
    atomic_write = storage.atomic_write

    def read_claim(identifier: str) -> GuardianClaim | None:
        nonlocal reads
        assert identifier == observed.id
        reads += 1
        return retained

    def guardian_exited(pid: int) -> None:
        nonlocal retained
        assert pid == claim.guardian_pid
        if claim_change == "released":
            retained = None
        elif claim_change == "owner":
            retained = claim.model_copy(update={"owner_uid": claim.owner_uid + 1})
        elif claim_change == "guardian":
            retained = claim.model_copy(update={"guardian_pid": claim.guardian_pid + 1})
        elif claim_change == "generation":
            retained = claim.model_copy(update={"generations": (("GPU-test", 1),)})
        else:
            assert claim_change == "identities"
            retained = claim.model_copy(update={"identities": ((789, 123),)})

    def track_write(path: Path, payload: str, mode: int = 0o644) -> None:
        publications.append(path)
        atomic_write(path, payload, mode)

    monkeypatch.setattr(processes.pool, "claim_for", read_claim)
    monkeypatch.setattr(runtime, "process_birth", guardian_exited)
    monkeypatch.setattr(storage, "atomic_write", track_write)
    processes._refresh_job(observed)

    assert store.view().jobs == (observed,)
    assert publications == []
    assert reads == 2
