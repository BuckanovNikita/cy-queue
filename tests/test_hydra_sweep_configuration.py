"""Queue integration contracts extracted from CY tests."""

import json
import subprocess
from pathlib import Path

import pytest
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

from cy_queue.core.queue import ResourceRequest
from cy_queue.entrypoints.hydra.queue_config import compose_snapshots, write_execution_config
from queue_cli_helpers import queue_command, queue_environment


def _configuration(root: Path, *, mode: str | None, epochs: str = "1,2") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    config = {
        "defaults": ["pipeline", "_self_"],
        "ground_truth": "input.csv",
        "hydra": {"mode": mode, "sweeper": {"params": {"ultralytics.epochs": epochs}}},
    }
    OmegaConf.save(OmegaConf.create(config), root / "sweep.yaml")
    return root


@pytest.mark.parametrize(
    ("mode", "arguments", "expected"),
    [
        (None, ["-m"], [1, 2]),
        ("MULTIRUN", [], [1, 2]),
        (None, ["hydra.mode=MULTIRUN"], [1, 2]),
        ("RUN", ["-m"], [1, 2]),
        ("MULTIRUN", ["ultralytics.epochs=3,4"], [3, 4]),
        ("MULTIRUN", ["ultralytics.epochs=5"], [5]),
        ("RUN", [], [100]),
    ],
)
def test_queue_expands_saved_parameters_with_cli_precedence(
    tmp_path: Path, mode: str | None, arguments: list[str], expected: list[int]
) -> None:
    config = _configuration(tmp_path / "config", mode=mode)
    snapshots = compose_snapshots(
        ["--config-dir", str(config), "--config-name", "sweep", *arguments],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
    )
    assert [json.loads(item.config_json)["ultralytics"]["epochs"] for item in snapshots] == expected


def test_invalid_saved_sweep_is_rejected_before_manifest_commit(tmp_path: Path) -> None:
    config = _configuration(tmp_path / "config", mode="MULTIRUN", epochs="1,0")
    result = subprocess.run(  # noqa: S603 - fixed queue CLI and invalid saved fixture
        [
            *queue_command(tmp_path),
            "submit",
            "--gpus",
            "1",
            "--",
            "--config-dir",
            str(config),
            "--config-name",
            "sweep",
        ],
        env=queue_environment(tmp_path),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode != 0
    assert "epochs" in result.stderr
    assert not list((tmp_path / "queue").rglob("snapshot.json"))


@pytest.mark.parametrize("source", ["cli", "saved"])
def test_queue_labels_use_frozen_job_local_task_names(tmp_path: Path, source: str) -> None:
    arguments = ["-m", "ground_truth=input.csv", "ultralytics.epochs=1,2"]
    if source == "cli":
        arguments.append("clearml.task_name=Experiment-${hydra:job.num}")
    else:
        config = _configuration(tmp_path / "config", mode="MULTIRUN")
        saved = OmegaConf.load(config / "sweep.yaml")
        saved.clearml = {"task_name": "Experiment-${hydra:job.num}"}
        OmegaConf.save(saved, config / "sweep.yaml")
        arguments = ["--config-dir", str(config), "--config-name", "sweep"]
    snapshots = compose_snapshots(
        arguments,
        ResourceRequest(gpus=1),
        project_root=tmp_path,
    )
    assert [item.label for item in snapshots] == ["Experiment-0", "Experiment-1"]
    assert [json.loads(item.config_json)["clearml"]["task_name"] for item in snapshots] == [
        item.label for item in snapshots
    ]


@pytest.mark.parametrize("plugin", ["sweeper", "launcher"])
def test_nonsequential_sweep_plugins_are_rejected_before_instantiation(tmp_path: Path, plugin: str) -> None:
    with pytest.raises(ValueError, match="BasicSweeper/BasicLauncher"):
        compose_snapshots(
            ["-m", "ground_truth=input.csv", f"hydra.{plugin}._target_=unsupported.Launch"],
            ResourceRequest(gpus=1),
            project_root=tmp_path,
        )


@pytest.mark.parametrize(
    ("weight_decay", "expected"),
    [(None, [0.02]), ("0.03", [0.03]), ("0.03,0.04", [0.03, 0.04])],
)
def test_worker_config_preserves_training_overrides_and_binds_allocated_devices(
    tmp_path: Path, weight_decay: str | None, expected: list[float]
) -> None:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "chosen.yaml").write_text(
        "defaults:\n  - pipeline\n  - _self_\nground_truth: input.csv\n"
        "ultralytics:\n  weight_decay: 0.02\n  compile: false\n"
        "skip_predict: true\nskip_metrics: true\nskip_compare: true\nskip_report: true\n"
        "fiftyone:\n  enabled: false\n"
    )
    arguments = ["--config-dir", str(config_dir), "--config-name", "chosen"]
    if weight_decay is not None:
        arguments.append(f"ultralytics.weight_decay={weight_decay}")
    if weight_decay is not None and "," in weight_decay:
        arguments.append("-m")
    snapshots = compose_snapshots(arguments, ResourceRequest(gpus=2), project_root=tmp_path)
    for index, (snapshot, decay) in enumerate(zip(snapshots, expected, strict=True)):
        assert json.loads(snapshot.config_json)["ultralytics"]["weight_decay"] == decay
        worker_dir = tmp_path / f"worker-{index}"
        worker_dir.mkdir()
        executable = write_execution_config(snapshot, 2, worker_dir)
        with initialize_config_dir(config_dir=str(worker_dir), version_base="1.3"):
            settings = compose(config_name=executable.stem).ultralytics
        assert settings.weight_decay == decay
        assert settings.device == [0, 1]
