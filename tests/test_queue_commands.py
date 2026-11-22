"""Immutable submission composition and explicit allocation bindings."""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Literal

import pytest
from omegaconf import OmegaConf

from queue_cli_helpers import queue_command, queue_environment

Command = Literal["pipeline", "train"]


def test_queue_bindings_preserve_native_settings_and_explicit_cpu() -> None:
    from cy_queue.entrypoints.hydra.queue_config import bind_devices

    config = OmegaConf.create(
        {
            "ultralytics": {"device": None, "compile": True, "batch": 20, "amp": False},
            "ultralytics_predict": {"device": "cpu", "batch": 3},
        }
    )
    bound = bind_devices(config, 5)
    assert bound.ultralytics.device == [0, 1, 2, 3, 4]
    assert bound.ultralytics_predict.device == "cpu"
    assert (bound.ultralytics.compile, bound.ultralytics.batch, bound.ultralytics.amp) == (
        True,
        20,
        False,
    )
    assert config.ultralytics.device is None


def test_queue_binds_backend_inference_to_first_gpu() -> None:
    from cy_queue.entrypoints.hydra.queue_config import bind_devices

    config = OmegaConf.create(
        {
            "model": {
                "backend": "fasterrcnn",
                "train": {"device": "cuda"},
                "predict": {"device": "cuda"},
            }
        }
    )
    bound = bind_devices(config, 2)
    assert bound.model.train.device == [0, 1]
    assert bound.model.predict.device == [0]


def test_submission_resolves_whole_sweep_and_freezes_settings(tmp_path: Path) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    snapshots = compose_snapshots(
        [
            "-m",
            "ground_truth=outside.csv",
            "ultralytics.epochs=1,2",
            "ultralytics.compile=false",
            "ultralytics_predict.device=cpu",
        ],
        ResourceRequest(gpus=2),
        project_root=tmp_path,
    )
    assert len(snapshots) == 2
    assert [json.loads(item.config_json)["ultralytics"]["epochs"] for item in snapshots] == [1, 2]
    assert all(item.request.count == 2 for item in snapshots)
    assert all(item.cwd == str(Path.cwd()) for item in snapshots)
    assert all(json.loads(item.config_json)["ultralytics"]["compile"] is False for item in snapshots)


@pytest.mark.parametrize("override", ["ultralytics.device=0", "ultralytics_predict.device=[1,2]"])
def test_queue_rejects_conflicting_native_gpu_overrides(tmp_path: Path, override: str) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    with pytest.raises(ValueError, match=r"cy-queue.*--devices|allocation"):
        compose_snapshots(["ground_truth=input.csv", override], ResourceRequest(gpus=1), project_root=tmp_path)


def test_snapshot_rejects_execution_after_package_identity_change(tmp_path: Path) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots, validate_snapshot

    snapshot = compose_snapshots(["ground_truth=input.csv"], ResourceRequest(gpus=1), project_root=tmp_path)[0]
    with pytest.raises(ValueError, match="identity"):
        validate_snapshot(snapshot.model_copy(update={"package_identity": "old-code"}))


@pytest.mark.parametrize(
    "override",
    [
        "run_dir={outside}",
        "hydra.output_subdir={outside}",
        "+hydra.job.env_set.CUDA_VISIBLE_DEVICES=2",
    ],
)
def test_submission_rejects_escaping_paths_and_environment_allocation_override(tmp_path: Path, override: str) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    with pytest.raises(ValueError, match=r"contained|allocation"):
        compose_snapshots(
            ["ground_truth=input.csv", override.format(outside=tmp_path.parent / "escape")],
            ResourceRequest(gpus=1),
            project_root=tmp_path,
        )


def test_sweep_freezes_hydra_output_and_logging_configuration(tmp_path: Path) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    snapshots = compose_snapshots(
        [
            "-m",
            "ground_truth=input.csv",
            "ultralytics.epochs=1,2",
            f"hydra.sweep.dir={tmp_path}/sweep",
            "hydra.sweep.subdir=${hydra.job.num}",
            "hydra.output_subdir=config",
            "hydra/job_logging=disabled",
        ],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
    )
    for index, snapshot in enumerate(snapshots):
        settings = json.loads(snapshot.config_json)["hydra"]
        assert settings["run"]["dir"] == str(tmp_path / "sweep" / str(index))
        assert settings["output_subdir"] == "config"
        assert settings["job_logging"]["disable_existing_loggers"] is True


def _two_gpu_environment(root: Path) -> dict[str, str]:
    memory = root / "two-gpu-memory.json"
    memory.write_text(json.dumps({"GPU-test-a": 0, "GPU-test-b": 0}))
    return queue_environment(root) | {"CY_TEST_QUEUE_MEMORY": str(memory)}


def _submit_cli(
    root: Path,
    *arguments: str,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed package CLI and isolated local records
        [*queue_command(root), "submit", *arguments],
        env=environment or queue_environment(root),
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )


def test_cli_submits_lists_reorders_and_cancels_without_runtime(tmp_path: Path) -> None:
    command = queue_command(tmp_path)
    environment = _two_gpu_environment(tmp_path)

    def run(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603 - fixed package CLI and isolated local records
            [*command, *arguments],
            env=environment,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

    submitted = run(
        "submit",
        "--gpus",
        "2",
        "--json",
        "--",
        "-m",
        "ground_truth=input.csv",
        "ultralytics.epochs=1,2",
    )
    assert submitted.returncode == 0, submitted.stderr
    ids = [job["id"] for job in json.loads(submitted.stdout)]
    assert len(ids) == 2
    assert len(set(ids)) == 2
    listed = run("list", "--json")
    assert listed.returncode == 0, listed.stderr
    view = json.loads(listed.stdout)
    assert [job["id"] for job in view["jobs"]] == ids
    assert all(job["state"] == "pending" for job in view["jobs"])
    assert "config_json" not in listed.stdout
    moved = run("move", ids[1], "top", "--revision", str(view["revision"]))
    assert moved.returncode == 0, moved.stderr
    stale = run("move", ids[0], "top", "--revision", str(view["revision"]))
    assert stale.returncode != 0
    cancelled = run("cancel", "job-2", "--json")
    assert cancelled.returncode == 0, cancelled.stderr
    assert json.loads(cancelled.stdout)["state"] == "cancelled"
    assert run("list", "--json").returncode == 0


def test_cli_move_archive_and_restore_print_the_waiting_reasons_list_prints(tmp_path: Path) -> None:
    command = queue_command(tmp_path)
    environment = queue_environment(tmp_path)

    def run(*arguments: str) -> dict[str, object]:
        result = subprocess.run(  # noqa: S603 - fixed package CLI and isolated local records
            [*command, *arguments, "--json"],
            env=environment,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        view: dict[str, object] = json.loads(result.stdout)
        return view

    def reasons(view: dict[str, object]) -> dict[str, object]:
        jobs = view["jobs"]
        assert isinstance(jobs, list)
        return {job["reference"]: job["waiting_reason"] for job in jobs if job["state"] == "pending"}

    submitted = subprocess.run(  # noqa: S603 - fixed package CLI and isolated local records
        [*command, "submit", "--gpus", "1", "--", "-m", "ground_truth=input.csv", "ultralytics.epochs=1,2,3"],
        env=environment,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert submitted.returncode == 0, submitted.stderr
    assert run("cancel", "job-1")["state"] == "cancelled"
    listed = run("list")
    expected = reasons(listed)
    # No worker has recorded a reason, so the printed reason is the computed one.
    assert expected == {"job-2": "Owner worker unavailable", "job-3": "Owner worker unavailable"}
    assert reasons(run("move", "job-3", "top", "--revision", str(listed["revision"]))) == expected
    assert reasons(run("archive", "job-1")) == expected
    assert reasons(run("restore", "job-1")) == expected


@pytest.mark.parametrize(
    "overrides",
    [
        ["ultralytics.device=cpu,0"],
        ["metrics.evaluation.iou_threshold=0.5,2.0"],
        ["compare.q=0.05,2.0"],
        ["compare.bootstrap_iterations=100,0"],
        ["weights=model.pt", "skip_train=true,false"],
        ["+report.output=bad.csv"],
        ["compare.baseline_model.source=clearml,local"],
        ["clearml.output_uri=true,false"],
        ["fiftyone.publish_timeout_seconds=60,-1"],
        ["ultralytics_predict.imgsz=64,0"],
        ["ultralytics_predict.batch=1,0"],
        ["ultralytics_predict.mode=predict,train"],
        ["skip_train=false,garbage"],
        ["ground_truth=input.csv,123"],
        ["splits=[val,test],[123]"],
        ["ultralytics_predict.conf=0.001,2.0"],
        ["ultralytics_predict.iou=0.7,-0.1"],
        ["ultralytics_predict.save=false,1"],
        ["ultralytics.epochs=1,0"],
        ["ultralytics.compile=false,2"],
        ["ultralytics.amp=true,broken"],
    ],
)
def test_invalid_sweep_does_not_commit_partial_batch(tmp_path: Path, overrides: list[str]) -> None:
    result = subprocess.run(  # noqa: S603 - fixed CLI with invalid user-input fixture
        [
            *queue_command(tmp_path),
            "submit",
            "--gpus",
            "1",
            "--",
            "-m",
            "ground_truth=input.csv",
            *overrides,
        ],
        env=queue_environment(tmp_path),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode != 0
    assert "CY_QUEUE_CONFIG" not in result.stderr
    assert not list((tmp_path / "queue").rglob("snapshot.json"))


@pytest.mark.parametrize("command", ["pipeline", "train"])
def test_missing_mandatory_setting_names_the_key(tmp_path: Path, command: Command) -> None:
    from omegaconf.errors import MissingMandatoryValue

    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    with pytest.raises(ValueError, match=r"^Missing mandatory setting ground_truth;") as caught:
        compose_snapshots([], ResourceRequest(gpus=1), project_root=tmp_path, command=command)
    assert isinstance(caught.value.__cause__, MissingMandatoryValue)
    assert "\n" not in str(caught.value)


@pytest.mark.parametrize(
    "arguments",
    [
        ["--command", "pipeline", "--gpus", "1", "--"],
        ["--command", "train", "--gpus", "1", "--"],
        ["--gpus", "1", "--", "-m", "ultralytics.epochs=1,2"],
        ["--gpus", "1", "--", "--config-name", "saved"],
    ],
)
def test_cli_reports_missing_mandatory_setting_in_one_line(tmp_path: Path, arguments: list[str]) -> None:
    saved = tmp_path / "saved"
    saved.mkdir()
    (saved / "saved.yaml").write_text("defaults:\n  - pipeline\n  - _self_\n")
    if "saved" in arguments:
        arguments = [*arguments, "--config-dir", str(saved)]
    result = _submit_cli(tmp_path, *arguments)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert result.stderr.startswith("cy-queue: Missing mandatory setting ground_truth;")
    assert result.stderr.count("\n") == 1
    assert not list((tmp_path / "queue").rglob("snapshot.json"))


@pytest.mark.parametrize("gpus", ["0", "-1"])
def test_resource_request_rejects_nonpositive_gpus_before_the_model(gpus: str) -> None:
    from pydantic import ValidationError

    from cy_queue.entrypoints.queue import _parser, _resource_request

    parsed = _parser().parse_args(["submit", "--gpus", gpus, "--", "ground_truth=input.csv"])
    with pytest.raises(ValueError, match=r"^--gpus must be a positive integer$") as caught:
        _resource_request(parsed)
    assert not isinstance(caught.value, ValidationError)


@pytest.mark.parametrize("gpus", ["0", "-1"])
def test_cli_reports_nonpositive_gpus_in_one_line(tmp_path: Path, gpus: str) -> None:
    result = _submit_cli(tmp_path, "--gpus", gpus, "--", "ground_truth=input.csv")
    assert result.returncode == 1
    assert result.stderr == "cy-queue: --gpus must be a positive integer\n"


def test_resource_request_rejects_more_gpus_than_the_host_has(monkeypatch: pytest.MonkeyPatch) -> None:
    from cy_queue.adapters.runtime.gpu_resources import GPUInventory
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.queue import _parser, _resource_request

    monkeypatch.setattr(GPUInventory, "physical_uuids", lambda self: ("GPU-a", "GPU-b"))
    parsed = _parser().parse_args(["submit", "--gpus", "3", "--", "ground_truth=input.csv"])
    with pytest.raises(ValueError, match=r"^--gpus 3 exceeds the 2 GPU\(s\) on this host$"):
        _resource_request(parsed)
    parsed = _parser().parse_args(["submit", "--gpus", "2", "--", "ground_truth=input.csv"])
    assert _resource_request(parsed) == ResourceRequest(gpus=2)


def test_cli_rejects_more_gpus_than_the_host_has(tmp_path: Path) -> None:
    result = _submit_cli(tmp_path, "--gpus", "2", "--", "ground_truth=input.csv")
    assert result.returncode == 1
    assert result.stderr == "cy-queue: --gpus 2 exceeds the 1 GPU(s) on this host\n"
    assert not list((tmp_path / "queue").rglob("snapshot.json"))


def test_cli_accepts_unchecked_gpus_with_one_warning_without_nvml(tmp_path: Path) -> None:
    environment = queue_environment(tmp_path) | {"CY_TEST_QUEUE_MEMORY": str(tmp_path / "absent.json")}
    result = _submit_cli(tmp_path, "--gpus", "4", "--json", "--", "ground_truth=input.csv", environment=environment)
    assert result.returncode == 0, result.stderr
    assert [job["state"] for job in json.loads(result.stdout)] == ["pending"]
    warnings = [line for line in result.stderr.splitlines() if "WARNING" in line]
    assert len(warnings) == 1
    assert "--gpus 4 was not checked against the host GPU count" in warnings[0]


def test_queue_rejects_auto_gpu_with_migration_guidance_before_composition(tmp_path: Path) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    with pytest.raises(ValueError, match=r"Legacy.*cy-queue allocation"):
        compose_snapshots(
            ["ground_truth=input.csv", "+auto_gpu.enabled=true"],
            ResourceRequest(gpus=1),
            project_root=tmp_path,
        )


@pytest.mark.parametrize(
    "legacy",
    ["queue: default", "autogpu: default", "auto_gpu: default", "hydra/launcher: cy_queue"],
)
def test_saved_legacy_defaults_report_queue_migration(tmp_path: Path, legacy: str) -> None:
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    directory = tmp_path / "config"
    directory.mkdir()
    (directory / "legacy.yaml").write_text(
        f"defaults:\n  - pipeline\n  - {legacy}\n  - _self_\nground_truth: input.csv\n"
    )
    with pytest.raises(ValueError, match=r"Legacy.*cy-queue"):
        compose_snapshots(
            ["--config-dir", str(directory), "--config-name", "legacy"],
            ResourceRequest(gpus=1),
            project_root=tmp_path,
        )


def test_tui_moves_and_cancels_real_pending_jobs(tmp_path: Path) -> None:
    pytest.importorskip("textual")
    from textual.widgets import DataTable, Select

    from cy_queue.adapters.queue.identity import current_identity
    from cy_queue.adapters.queue.inventory import QueueGPUInventory
    from cy_queue.adapters.queue.runtime import QueueProcesses
    from cy_queue.adapters.queue.storage import NFSQueueStore
    from cy_queue.application.queue import QueueService
    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots
    from cy_queue.entrypoints.queue_tui import QueueApp

    identity = current_identity()
    storage = NFSQueueStore(tmp_path / "queue", identity)
    service = QueueService(
        storage,
        QueueGPUInventory(),
        QueueProcesses(storage, identity, local_root=tmp_path / "locks"),
        identity,
    )
    jobs = service.submit(
        compose_snapshots(
            ["-m", "ground_truth=input.csv", "ultralytics.epochs=1,2,3"],
            ResourceRequest(gpus=1),
            project_root=tmp_path,
        )
    )

    async def exercise() -> None:
        application = QueueApp(service)
        async with application.run_test(size=(150, 35)) as pilot:
            await pilot.press("d")
            assert service.list().jobs[0].id == jobs[1].id
            await pilot.press("c")
            assert next(job for job in service.list().jobs if job.id == jobs[0].id).state == "cancelled"
            await pilot.press("x")
            assert jobs[0].id not in {job.id for job in service.list().jobs}
            await pilot.press("v")
            assert str(application.visibility) == "archived"
            assert [job.id for job in application.view.jobs] == [jobs[0].id]
            table = application.query_one("#jobs", DataTable)
            assert table.get_row_at(0)[3] == "cancelled (archived)"
            await pilot.press("s")
            assert application.view.jobs == ()
            await pilot.press("v", "v")
            assert str(application.visibility) == "main"
            table = application.query_one("#jobs", DataTable)
            table.move_cursor(row=0)
            selected = application._selected()
            assert selected is not None
            assert selected.id == jobs[1].id
            await pilot.press("a")
            target = application.query_one("#relative", Select)
            assert bool(target.display)
            target.value = jobs[2].id
            await pilot.pause()
            assert not bool(target.display)
            pending = [job.id for job in service.list().jobs if job.state == "pending"]
            assert pending == [jobs[2].id, jobs[1].id]
            await pilot.press("q")

    asyncio.run(exercise())
    assert next(job for job in service.list().jobs if job.id == jobs[1].id).state == "pending"
