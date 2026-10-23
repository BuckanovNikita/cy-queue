"""Standalone queue execution uses the CY train schema and entrypoint."""

import json
from pathlib import Path

import pytest

from cy_queue.core.queue import ResourceRequest
from cy_queue.entrypoints.hydra.queue_config import compose_snapshots, validate_snapshot
from cy_queue.entrypoints.queue import _parser


def test_submission_selects_standalone_train_and_keeps_pipeline_default(tmp_path: Path) -> None:
    snapshot = compose_snapshots(
        ["ground_truth=inputs.csv", "ultralytics.epochs=1"],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
        command="train",
    )[0]
    assert snapshot.command == "train"
    values = json.loads(snapshot.config_json)
    assert values["ground_truth"] == "inputs.csv"
    assert values["ultralytics"]["epochs"] == 1
    assert "skip_train" not in values
    validate_snapshot(snapshot)
    assert _parser().parse_args(["submit", "--gpus", "1"]).command == "pipeline"
    assert _parser().parse_args(["submit", "--command", "train", "--gpus", "1"]).command == "train"


@pytest.mark.parametrize(
    "override", ["dataset_format=invalid", "required_splits=5", "ultralytics.device=2"]
)
def test_invalid_train_sweep_fails_before_submission(tmp_path: Path, override: str) -> None:
    with pytest.raises((ValueError, TypeError)):
        compose_snapshots(
            ["ground_truth=inputs.csv", override],
            ResourceRequest(gpus=1),
            project_root=tmp_path,
            command="train",
        )


def test_snapshot_identity_covers_both_distribution_versions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from cy_queue.entrypoints.hydra import queue_config

    baseline = queue_config.package_identity()
    from importlib.metadata import version as installed

    for name in ("cy-queue", "clearml-yolo"):
        monkeypatch.setattr(
            queue_config,
            "version",
            lambda package, changed=name: "changed" if package == changed else installed(package),
        )
        assert queue_config.package_identity() != baseline
    monkeypatch.setattr(queue_config, "version", installed)


@pytest.mark.parametrize("command", ["pipeline", "train"])
def test_snapshot_runner_executes_matching_cy_entrypoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    import os
    import sys

    from cy_queue.entrypoints import queue_run
    from cy_queue.entrypoints.hydra.queue_config import Command

    selected: Command = "pipeline" if command == "pipeline" else "train"
    snapshot = compose_snapshots(
        ["ground_truth=inputs.csv"],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
        command=selected,
    )[0].model_copy(update={"owner_uid": os.geteuid()})
    private = tmp_path / "snapshot.json"
    private.write_text(snapshot.model_dump_json())
    private.chmod(0o600)
    monkeypatch.setattr(sys, "argv", ["queue-run", "--snapshot", str(private), "--devices", "1"])
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "GPU-allocated")
    calls: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(os, "execv", lambda executable, argv: calls.append((executable, argv)))
    queue_run.main()
    assert len(calls) == 1
    executable, arguments = calls[0]
    assert executable == sys.executable
    assert arguments[:4] == [sys.executable, "-u", "-m", f"clearml_yolo.entrypoints.{command}"]
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "GPU-allocated"
    execution_file = Path(arguments[5]) / f"{arguments[7]}.yaml"
    from omegaconf import OmegaConf

    config = OmegaConf.load(execution_file)
    assert config.ultralytics.device == [0]


def test_installed_packages_and_console_entrypoint_work_outside_checkout(tmp_path: Path) -> None:
    import subprocess
    import sys

    code = """
from importlib.metadata import distribution
import clearml_yolo
import cy_queue
queue = distribution('cy-queue')
assert any(requirement.startswith('clearml-yolo') for requirement in queue.requires)
entry = next(item for item in queue.entry_points if item.name == 'cy-queue')
assert entry.value == 'cy_queue.entrypoints.queue:main'
assert callable(entry.load())
assert clearml_yolo.__file__ != cy_queue.__file__
"""
    result = subprocess.run(  # noqa: S603 - installed source package verification, no effects
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("package", ["clearml_yolo", "cy_queue"])
@pytest.mark.parametrize("asset", ["runtime.py", "manifest.json"])
def test_installation_identity_detects_code_and_packaged_data_in_either_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, package: str, asset: str
) -> None:
    from importlib.machinery import ModuleSpec

    from cy_queue.entrypoints.hydra import queue_config

    for name in ("clearml_yolo", "cy_queue"):
        folder = tmp_path / name
        folder.mkdir()
        (folder / "__init__.py").write_text("")
        (folder / "runtime.py").write_text("VALUE = 1\n")
        (folder / "manifest.json").write_text('{"revision":"approved"}')

    def locate(name: str) -> ModuleSpec:
        return ModuleSpec(name, loader=None, origin=str(tmp_path / name / "__init__.py"))

    monkeypatch.setattr(queue_config, "find_spec", locate)
    baseline = queue_config.package_identity()
    (tmp_path / package / asset).write_text("changed installation bytes")
    assert queue_config.package_identity() != baseline


def test_installation_identity_ignores_generated_python_bytecode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from importlib.machinery import ModuleSpec

    from cy_queue.entrypoints.hydra import queue_config

    (tmp_path / "__init__.py").write_text("")
    monkeypatch.setattr(
        queue_config,
        "find_spec",
        lambda name: ModuleSpec(name, loader=None, origin=str(tmp_path / "__init__.py")),
    )
    baseline = queue_config.package_identity()
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "runtime.cpython-312.pyc").write_bytes(b"cached code")
    assert queue_config.package_identity() == baseline


def test_minimal_custom_train_config_uses_signature_defaults_without_mutation() -> None:
    from clearml_yolo.adapters.yolo.config import native_defaults, stage_settings
    from omegaconf import OmegaConf

    from cy_queue.entrypoints.hydra.queue_config import _validate_train_configuration

    values = {
        "ground_truth": "inputs.csv",
        "ultralytics": stage_settings(native_defaults(), "train"),
        "clearml": {"project_name": "portable-review"},
    }
    config = OmegaConf.create(values)
    _validate_train_configuration(config)
    assert OmegaConf.to_container(config) == values


@pytest.mark.parametrize("missing", ["ground_truth", "ultralytics", "clearml"])
def test_custom_train_config_still_rejects_missing_required_arguments(missing: str) -> None:
    from omegaconf import OmegaConf

    from cy_queue.entrypoints.hydra.queue_config import _validate_train_configuration

    values: dict[str, object] = {
        "ground_truth": "inputs.csv",
        "ultralytics": {"model": "yolo11n.pt"},
        "clearml": {"project_name": "portable-review"},
    }
    del values[missing]
    with pytest.raises(ValueError, match=f"Missing required train setting {missing}"):
        _validate_train_configuration(OmegaConf.create(values))


def test_submit_custom_train_yaml_omitting_optional_fields_without_native_effects(
    tmp_path: Path,
) -> None:
    import subprocess

    from clearml_yolo.adapters.yolo.config import native_defaults, stage_settings
    from omegaconf import OmegaConf

    from queue_cli_helpers import queue_command, queue_environment

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    OmegaConf.save(
        OmegaConf.create(
            {
                "ground_truth": "inputs.csv",
                "ultralytics": stage_settings(native_defaults(), "train"),
                "clearml": {
                    "_target_": "clearml_yolo.application.contracts.ClearMLConfig",
                    "project_name": "portable-review",
                },
            }
        ),
        config_dir / "custom.yaml",
    )
    command = queue_command(tmp_path)
    command[2] += (
        "\nimport sys\nassert not {'torch', 'ultralytics', 'clearml'}.intersection(sys.modules)\n"
    )
    completed = subprocess.run(  # noqa: S603 - isolated actual queue CLI with controlled NVML
        [
            *command,
            "submit",
            "--command",
            "train",
            "--gpus",
            "1",
            "--json",
            "--",
            "--config-dir",
            str(config_dir),
            "--config-name",
            "custom",
        ],
        env=queue_environment(tmp_path),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    submitted = json.loads(completed.stdout)
    assert len(submitted) == 1
    assert submitted[0]["command"] == "train"
    snapshots = list((tmp_path / "queue").rglob("snapshot.json"))
    assert len(snapshots) == 1
    frozen = json.loads(json.loads(snapshots[0].read_text())["config_json"])
    assert frozen["ground_truth"] == "inputs.csv"
    assert "ultralytics_predict" not in frozen
    assert not list(tmp_path.rglob("*.pt"))
