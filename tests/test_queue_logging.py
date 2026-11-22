"""Worker diagnostics stay useful without contaminating command stdout."""

import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

import pytest
from loguru import logger

from cy_queue.core.queue import PublicJob, QueueView, ResourceRequest, WorkerIdentity
from queue_cli_helpers import queue_command, queue_environment


@pytest.mark.parametrize("level", [None, "DEBUG", "WARNING"])
@pytest.mark.parametrize("threshold", [None, 12.0])
def test_real_idle_worker_logs_by_default_and_stops_cleanly(
    tmp_path: Path, level: str | None, threshold: float | None
) -> None:
    queue_root = tmp_path / "queue"
    command = [*queue_command(tmp_path), "worker"]
    if level:
        command.extend(["--log-level", level])
    environment = queue_environment(tmp_path)
    if threshold is not None:
        with (tmp_path / "queue.toml").open("a") as output:
            output.write(f"max_used_memory_gib = {threshold}\n")
    with subprocess.Popen(  # noqa: S603 - fixed CLI with an isolated empty queue
        command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        try:
            deadline = time.monotonic() + 15
            while not list(queue_root.rglob("worker.json")):
                if process.poll() is not None or time.monotonic() >= deadline:
                    pytest.fail("Worker exited or failed to register")
                time.sleep(0.02)
            process.terminate()
            stdout, stderr = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
    assert process.returncode == 0, stderr
    assert stdout == ""
    assert not list(queue_root.rglob("worker.json"))
    if level == "WARNING":
        assert stderr == ""
    else:
        assert "Starting queue worker" in stderr
        assert f"max_used_memory_gib={2.0 if threshold is None else threshold}" in stderr
        assert str(queue_root) in stderr
        assert "idle" in stderr.lower()
        assert "Queue worker stopped" in stderr
        assert ("DEBUG" in stderr) == (level == "DEBUG")


def test_worker_logs_changes_and_heartbeat_without_timestamp_noise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cy_queue.entrypoints import queue
    from cy_queue.entrypoints.queue_presentation import QueuePresentation

    clock = [0.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    messages: list[str] = []
    sink = logger.add(messages.append, format="{level}: {message}", level="INFO")
    try:
        observer = queue._WorkerLog(owner_uid=7, presentation=QueuePresentation({"GPU-one": 2}, host_id="host"))
        pending = PublicJob(
            id="own-job",
            submission_sequence=17,
            label="Training experiment",
            owner_uid=7,
            host_id="host",
            boot_id="boot",
            command="train",
            request=ResourceRequest(gpus=1),
            submitted_at=0,
            waiting_reason="Waiting for 1 available GPU",
        )
        foreign = pending.model_copy(update={"id": "foreign-job", "owner_uid": 8})
        view = QueueView(host_id="host", revision=1, jobs=(pending, foreign))
        observer(view)
        assert "Job 17 · Training experiment" in "".join(messages)
        assert "own-job" not in "".join(messages)
        assert "Waiting for 1 available GPU" in "".join(messages)
        assert "foreign-job" not in "".join(messages)
        messages.clear()
        observer(
            view.model_copy(
                update={
                    "revision": 2,
                    "jobs": (
                        pending.model_copy(update={"updated_at": 100, "revision": 2}),
                        foreign,
                    ),
                }
            )
        )
        assert not messages
        clock[0] = 61
        observer(view)
        assert "pending=1" in "".join(messages)
        running = pending.model_copy(
            update={
                "state": "running",
                "devices": ("GPU-one",),
                "waiting_reason": None,
                "progress": "Training step 5",
            }
        )
        messages.clear()
        observer(view.model_copy(update={"jobs": (running,)}))
        rendered = "".join(messages)
        assert "running" in rendered
        assert "allocation=2" in rendered
        assert "GPU-one" not in rendered
        assert "Training step 5" in rendered
        messages.clear()
        observer(
            view.model_copy(
                update={"jobs": (running.model_copy(update={"state": "failed", "error": "Child exit code 2"}),)}
            )
        )
        assert "ERROR" in "".join(messages)
        assert "Child exit code 2" in "".join(messages)
        messages.clear()
        observer(
            view.model_copy(
                update={
                    "jobs": (
                        running.model_copy(
                            update={
                                "state": "recovery_required",
                                "error": "token=private-value\nrecovery needed",
                            }
                        ),
                    )
                }
            )
        )
        assert "ERROR" in "".join(messages)
        assert "private-value" not in "".join(messages)
        assert "\\nrecovery needed" in "".join(messages)
    finally:
        logger.remove(sink)


def test_worker_logs_error_only_when_a_job_enters_a_failure_state_or_its_error_changes() -> None:
    from cy_queue.entrypoints import queue
    from cy_queue.entrypoints.queue_presentation import QueuePresentation

    messages: list[str] = []
    sink = logger.add(
        messages.append,
        format="{level}: {message}",
        level="INFO",
        filter=lambda record: record["message"].startswith("Job "),
    )

    def observer() -> queue._WorkerLog:
        return queue._WorkerLog(owner_uid=7, presentation=QueuePresentation({"GPU-one": 2}, host_id="host"))

    def levels(log: queue._WorkerLog, *jobs: PublicJob) -> list[str]:
        observed: list[str] = []
        for job in jobs:
            messages.clear()
            log(QueueView(host_id="host", revision=1, jobs=(job,)))
            assert len(messages) == 1
            observed.append(messages[0].split(":", 1)[0])
        return observed

    try:
        running = PublicJob(
            id="own-job",
            submission_sequence=17,
            label="Run",
            owner_uid=7,
            host_id="host",
            boot_id="boot",
            command="train",
            request=ResourceRequest(gpus=1),
            submitted_at=0,
            state="running",
            devices=("GPU-one",),
            progress="Training step 1",
        )
        lost = running.model_copy(update={"state": "recovery_required", "error": "Guardian exited"})
        later = lost.model_copy(update={"progress": "Training step 2"})
        released = later.model_copy(update={"devices": ()})
        cleanup = released.model_copy(update={"error": "Cleanup failed"})
        failed = cleanup.model_copy(update={"state": "failed"})
        failed_later = failed.model_copy(update={"progress": "Training step 3"})
        assert levels(observer(), running, lost, later, released, cleanup, failed, failed_later) == [
            "INFO",
            "ERROR",
            "INFO",
            "INFO",
            "ERROR",
            "ERROR",
            "INFO",
        ]
        restarted = observer()
        assert levels(restarted, lost, later) == ["ERROR", "INFO"]
        assert messages == [
            (
                "INFO: Job 17 · Run | state=recovery_required | request=1 | allocation=2 | "
                "progress=Training step 2 | error=Guardian exited\n"
            )
        ]
    finally:
        logger.remove(sink)


def test_completed_history_is_counted_without_replaying_old_jobs() -> None:
    from cy_queue.entrypoints.queue import _WorkerLog

    completed = PublicJob(
        id="old-job",
        owner_uid=7,
        host_id="host",
        boot_id="boot",
        command="train",
        request=ResourceRequest(gpus=1),
        submitted_at=0,
        state="completed",
    )
    messages: list[str] = []
    sink = logger.add(messages.append, format="{message}", level="INFO")
    try:
        _WorkerLog(7)(QueueView(host_id="host", revision=1, jobs=(completed,)))
    finally:
        logger.remove(sink)
    assert "old-job" not in "".join(messages)
    assert "completed=1" in "".join(messages)
    assert "idle" in "".join(messages)


def test_worker_observer_reports_real_waiting_reason_and_releases_registration(
    tmp_path: Path,
) -> None:
    from cy_queue.adapters.queue.runtime import QueueProcesses
    from cy_queue.adapters.queue.storage import NFSQueueStore
    from cy_queue.application.queue import QueueService
    from cy_queue.core.queue import GPUObservation, JobSnapshot, WorkerIdentity

    class BusyInventory:
        def snapshot(self) -> tuple[GPUObservation, ...]:
            return (GPUObservation(uuid="GPU-busy", available=False),)

    identity = WorkerIdentity(owner_uid=os.geteuid(), host_id="host", boot_id="boot")
    store = NFSQueueStore(tmp_path / "queue", identity)
    processes = QueueProcesses(store, identity, local_root=tmp_path / "locks")
    service = QueueService(store, BusyInventory(), processes, identity)
    service.submit(
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
    )
    views: list[QueueView] = []
    service.worker(lambda: len(views) >= 2, poll_seconds=0, observe=views.append)
    assert views[0].jobs[0].waiting_reason is None
    assert views[1].jobs[0].state == "pending"
    assert views[1].jobs[0].waiting_reason
    assert not (store.actor_root / "worker.json").exists()


def test_failed_worker_does_not_claim_clean_shutdown(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cy_queue.adapters.queue.runtime import QueueProcesses
    from cy_queue.adapters.queue.storage import NFSQueueStore
    from cy_queue.application.queue import QueueService
    from cy_queue.core.queue import GPUObservation, WorkerIdentity
    from cy_queue.entrypoints.queue import _worker

    class Inventory:
        def snapshot(self) -> tuple[GPUObservation, ...]:
            return ()

    def fail() -> int:
        raise OSError("queue storage unavailable")

    identity = WorkerIdentity(owner_uid=os.geteuid(), host_id="host", boot_id="boot")
    store = NFSQueueStore(tmp_path / "queue", identity)
    processes = QueueProcesses(store, identity, local_root=tmp_path / "locks")
    service = QueueService(store, Inventory(), processes, identity)
    monkeypatch.setattr(service, "tick", fail)
    messages: list[str] = []
    sink = logger.add(messages.append, format="{message}")
    try:
        with pytest.raises(OSError, match="queue storage unavailable"):
            _worker(service)
    finally:
        logger.remove(sink)
    assert "Queue worker stopped" not in "".join(messages)
    assert not (store.actor_root / "worker.json").exists()


class _FakeService:
    """Stand-in for QueueService.worker: registration either refuses or accepts."""

    def __init__(self, *, refuse: bool) -> None:
        self.refuse = refuse
        self.identity = WorkerIdentity(owner_uid=7, host_id="host", boot_id="boot")

    def worker(self, stop: object, *, observe: Callable[[QueueView], None]) -> None:
        del stop
        if self.refuse:
            raise RuntimeError("One live queue worker per owner/root is already registered")
        observe(QueueView(host_id="host", revision=1, jobs=()))


@pytest.mark.parametrize("refuse", [True, False])
def test_start_line_is_logged_only_for_an_accepted_worker(refuse: bool) -> None:
    from cy_queue.entrypoints import queue

    messages: list[str] = []
    sink = logger.add(messages.append, format="{message}", level="INFO")
    try:
        start = "Starting queue worker | queue=Test root=/q host=h uid=7 max_used_memory_gib=2.0"
        service = _FakeService(refuse=refuse)
        if refuse:
            with pytest.raises(RuntimeError, match="already registered"):
                queue._worker(service, start_message=start)  # type: ignore[arg-type]  # fake service
        else:
            queue._worker(service, start_message=start)  # type: ignore[arg-type]  # fake service
    finally:
        logger.remove(sink)
    started = [message for message in messages if "Starting queue worker" in message]
    assert started == ([] if refuse else [start + "\n"])


def test_second_worker_refused_by_the_real_registration_logs_no_start_line(tmp_path: Path) -> None:
    from cy_queue.adapters.queue.runtime import QueueProcesses
    from cy_queue.adapters.queue.storage import NFSQueueStore
    from cy_queue.application.queue import QueueService
    from cy_queue.core.queue import GPUObservation
    from cy_queue.entrypoints import queue

    class Inventory:
        def snapshot(self) -> tuple[GPUObservation, ...]:
            raise AssertionError("A refused worker must not probe GPUs")

    identity = WorkerIdentity(owner_uid=os.geteuid(), host_id="host", boot_id="boot")
    store = NFSQueueStore(tmp_path / "queue", identity)
    first = QueueProcesses(store, identity, local_root=tmp_path / "local")
    second = QueueProcesses(store, identity, local_root=tmp_path / "local")
    service = QueueService(store, Inventory(), second, identity)
    messages: list[str] = []
    sink = logger.add(messages.append, format="{message}", level="INFO")
    try:
        with first.worker_registration():
            with pytest.raises(RuntimeError, match="already registered"):
                queue._worker(service, start_message="Starting queue worker | queue=Test")
            assert (store.actor_root / "worker.json").exists()
    finally:
        logger.remove(sink)
    assert [message for message in messages if "Starting queue worker" in message] == []
