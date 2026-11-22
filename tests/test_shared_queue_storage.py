"""Durable owner-private snapshots and public, revision-checked ordering."""

import json
import os
import stat
import sys
from pathlib import Path

import pytest

from cy_queue.adapters.queue.storage import NFSQueueStore
from cy_queue.core.queue import JobSnapshot


def test_namespace_is_public_under_restrictive_umask(tmp_path: Path) -> None:
    from cy_queue.adapters.queue.coordination import host_directory

    previous = os.umask(0o077)
    try:
        directory = host_directory("restricted-host", tmp_path / "coordination")
    finally:
        os.umask(previous)
    records = list(directory.glob("namespace-*.json"))
    assert len(records) == 1
    assert stat.S_IMODE(records[0].stat().st_mode) == 0o644
    assert stat.S_IMODE(directory.stat().st_mode) == 0o1777


def _store(root: Path, host: str = "test-host") -> NFSQueueStore:
    from cy_queue.adapters.queue.storage import NFSQueueStore
    from cy_queue.core.queue import WorkerIdentity

    return NFSQueueStore(root, WorkerIdentity(owner_uid=os.geteuid(), host_id=host, boot_id="boot"))


def _snapshot(project: Path, label: str = "first") -> JobSnapshot:
    from cy_queue.core.queue import JobSnapshot

    return JobSnapshot(
        command="train",
        label=label,
        config_json='{"token":"private-value"}',
        project_root=str(project),
        cwd=str(project),
        interpreter=sys.executable,
        package_version="1",
        package_identity="source-hash",
    )


def test_private_snapshot_public_summary_and_immutable_hash(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    snapshot_path = store.snapshot_path(job.id)
    assert stat.S_IMODE(snapshot_path.stat().st_mode) == 0o600
    assert snapshot_path.stat().st_uid == os.geteuid()
    assert "private-value" not in store.view().model_dump_json()
    assert store.load_snapshot(job.id).config_json == '{"token":"private-value"}'
    raw = json.loads(snapshot_path.read_text())
    raw["config_json"] = '{"token":"changed"}'
    snapshot_path.write_text(json.dumps(raw))
    with pytest.raises(RuntimeError, match="hash"):
        store.load_snapshot(job.id)


def test_move_revision_and_relative_order_are_atomic(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    jobs = store.submit(tuple(_snapshot(tmp_path, label) for label in ("a", "b", "c")))
    view = store.view()
    moved = store.move(jobs[2].id, "before", view.revision, relative_job_id=jobs[0].id)
    assert [job.label for job in moved.jobs] == ["c", "a", "b"]
    with pytest.raises(RuntimeError, match="revision"):
        store.move(jobs[1].id, "top", view.revision)
    moved = store.move(jobs[2].id, "bottom", moved.revision)
    assert [job.label for job in moved.jobs] == ["a", "b", "c"]


def test_foreign_host_is_view_only_and_corrupt_public_record_blocks(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    other_host = _store(tmp_path / "queue", "other-host")
    assert other_host.view().jobs == ()
    assert other_host.view("test-host").jobs[0].id == job.id
    with pytest.raises(ValueError, match="missing"):
        other_host.cancel(job.id)
    store.public_path(job.id).write_text('{"protocol":999}')
    with pytest.raises(RuntimeError, match=r"corrupt|protocol"):
        store.view()


def test_submission_validates_entire_batch_before_any_commit(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    good = _snapshot(tmp_path)
    bad = good.model_copy(update={"project_root": "/nonexistent/project"})
    with pytest.raises(ValueError, match="project"):
        store.submit((good, bad))
    assert store.view().jobs == ()


def test_effective_uid_cannot_be_asserted_by_configuration(tmp_path: Path) -> None:
    from cy_queue.adapters.queue.storage import NFSQueueStore
    from cy_queue.core.queue import WorkerIdentity

    with pytest.raises(PermissionError, match="effective"):
        NFSQueueStore(tmp_path, WorkerIdentity(owner_uid=os.geteuid() + 1, host_id="h", boot_id="b"))


def test_competing_start_does_not_replace_committed_guardian_payload(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    assert store.prepare_start(job.id, ("GPU-a",), '{"first":true}')
    assert not store.prepare_start(job.id, ("GPU-b",), '{"second":true}')
    path = store.snapshot_path(job.id).parent / "guardian.json"
    assert path.read_text(encoding="utf-8") == '{"first":true}'


def test_submission_sequence_survives_wall_clock_moving_backwards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import time

    store = _store(tmp_path / "queue")
    monkeypatch.setattr(time, "time", lambda: 100.0)
    first = store.submit((_snapshot(tmp_path, "first"),))[0]
    monkeypatch.setattr(time, "time", lambda: 1.0)
    second = store.submit((_snapshot(tmp_path, "second"),))[0]
    assert [job.id for job in store.view().jobs] == [first.id, second.id]
    assert first.submission_sequence < second.submission_sequence


def test_reorder_after_admission_decision_rejects_stale_claim(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    jobs = store.submit((_snapshot(tmp_path, "first"), _snapshot(tmp_path, "second")))
    view = store.view()
    store.move(jobs[1].id, "top", view.revision)
    assert not store.prepare_start(jobs[0].id, ("GPU-a",), "{}", expected_revision=view.revision)
    assert all(job.state == "pending" for job in store.view().jobs)


def test_pending_move_crosses_completed_history_using_pending_neighbors(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    jobs = store.submit(tuple(_snapshot(tmp_path, label) for label in ("first", "finished", "last")))
    store.update(jobs[1].id, "completed")
    view = store.view()
    moved = store.move(jobs[2].id, "up", view.revision)
    assert [job.label for job in moved.jobs if job.state == "pending"] == ["last", "first"]
    store.update(jobs[0].id, "completed")
    assert [job.label for job in store.view().jobs] == ["last", "first", "finished"]


def _raw(store: NFSQueueStore, identifier: str) -> dict[str, object]:
    record: dict[str, object] = json.loads(store.public_path(identifier).read_text(encoding="utf-8"))
    return record


@pytest.mark.parametrize("transition", ["prepare_start", "update", "cancel"])
def test_leaving_pending_clears_the_recorded_waiting_reason(tmp_path: Path, transition: str) -> None:
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    store.set_waiting({job.id: "Owner worker unavailable"})
    assert _raw(store, job.id)["waiting_reason"] == "Owner worker unavailable"
    if transition == "prepare_start":
        assert store.prepare_start(job.id, ("GPU-a",), "{}")
    elif transition == "update":
        store.update(job.id, "running", devices=("GPU-a",))
    else:
        store.cancel(job.id)
    raw = _raw(store, job.id)
    assert raw["state"] != "pending"
    assert raw["waiting_reason"] is None


@pytest.mark.parametrize("state", ["starting", "running", "cancelling", "completed", "failed", "cancelled"])
def test_stale_waiting_reason_on_disk_reads_as_none_without_a_write(tmp_path: Path, state: str) -> None:
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    public = store.public_path(job.id)
    record = _raw(store, job.id)
    # An older release left the last pending reason in non-pending records.
    record |= {"state": state, "waiting_reason": "Owner worker unavailable"}
    public.write_text(json.dumps(record), encoding="utf-8")
    revision = store.view().revision
    stored = public.read_bytes()
    view = store.view()
    assert view.jobs[0].state == state
    assert view.jobs[0].waiting_reason is None
    assert view.revision == revision
    assert public.read_bytes() == stored


def test_recovery_clears_a_stale_waiting_reason_on_disk(tmp_path: Path) -> None:
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    store.update(job.id, "recovery_required")
    public = store.public_path(job.id)
    stale = _raw(store, job.id) | {"waiting_reason": "Owner worker unavailable"}
    public.write_text(json.dumps(stale), encoding="utf-8")
    store.finish_recovery(job.id, lambda: None)
    assert _raw(store, job.id)["waiting_reason"] is None


def test_cancel_records_the_state_change_time(tmp_path: Path) -> None:
    import time

    store = _store(tmp_path / "queue")
    pending, active = store.submit((_snapshot(tmp_path, "pending"), _snapshot(tmp_path, "active")))
    assert pending.updated_at == 0
    before = time.time()
    cancelled = store.cancel(pending.id)
    assert cancelled.state == "cancelled"
    assert cancelled.updated_at >= before
    assert _raw(store, pending.id)["updated_at"] == cancelled.updated_at

    store.update(active.id, "running", devices=("GPU-a",))
    before = time.time()
    cancelling = store.cancel(active.id)
    assert cancelling.state == "cancelling"
    assert cancelling.updated_at >= before
    assert _raw(store, active.id)["updated_at"] == cancelling.updated_at


def test_cancel_of_recovery_required_job_keeps_the_record_unchanged(tmp_path: Path) -> None:
    # Guard: cancel changes no state here, so it must not stamp updated_at either.
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    store.update(job.id, "recovery_required")
    stored = store.public_path(job.id).read_bytes()
    assert store.cancel(job.id).state == "recovery_required"
    assert store.public_path(job.id).read_bytes() == stored


def test_repeated_cancel_of_a_cancelling_job_keeps_its_state_change_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import time

    clock = [1_000.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    store.update(job.id, "running", devices=("GPU-a",))
    clock[0] = 2_000.0
    first = store.cancel(job.id)
    assert first.state == "cancelling"
    assert first.updated_at == 2_000.0
    clock[0] = 3_000.0
    second = store.cancel(job.id)
    assert second.state == "cancelling"
    assert second.updated_at == 2_000.0
    assert _raw(store, job.id)["updated_at"] == 2_000.0
    assert _raw(store, job.id)["state"] == "cancelling"
    assert store.cancelled(job.id)


def test_waiting_reason_and_progress_writes_keep_the_state_change_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import time

    clock = [1_000.0]
    monkeypatch.setattr(time, "time", lambda: clock[0])
    store = _store(tmp_path / "queue")
    pending, active = store.submit((_snapshot(tmp_path, "pending"), _snapshot(tmp_path, "active")))
    # Give both records a non-zero state change time, so "unchanged" is observable.
    store.update(pending.id, "pending")
    store.update(active.id, "running", devices=("GPU-a",))
    clock[0] = 2_000.0
    store.set_waiting({pending.id: "Owner worker unavailable"})
    store.publish_status(active.id, progress=0.5, clearml_url="https://clearml.example/task")
    assert _raw(store, pending.id)["waiting_reason"] == "Owner worker unavailable"
    assert _raw(store, pending.id)["updated_at"] == 1_000.0
    assert _raw(store, active.id)["progress"] == 0.5
    assert _raw(store, active.id)["updated_at"] == 1_000.0


def test_recovery_records_the_state_change_time(tmp_path: Path) -> None:
    import time

    store = _store(tmp_path / "queue")
    job = store.submit((_snapshot(tmp_path),))[0]
    store.update(job.id, "recovery_required")
    before = time.time()
    recovered = store.finish_recovery(job.id, lambda: None)
    assert recovered.state == "cancelled"
    assert recovered.updated_at >= before
    assert _raw(store, job.id)["updated_at"] == recovered.updated_at
