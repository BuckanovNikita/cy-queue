"""Catalogue preparation belongs to CY execution, after immutable queue composition."""

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest
from clearml_yolo.adapters.assets import preparation
from clearml_yolo.entrypoints.hydra import common
from omegaconf import OmegaConf

from cy_queue.core.queue import ResourceRequest
from cy_queue.entrypoints.hydra.queue_config import Command, compose_snapshots


@pytest.mark.parametrize("command", ["pipeline", "train"])
@pytest.mark.parametrize("pretrained", [True, False, "weights/explicit-pretrained.pt"])
def test_custom_yolo_snapshot_preserves_selectors_without_catalogue_preparation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command: Command,
    pretrained: bool | str,
) -> None:
    from cy_queue.entrypoints import queue_run

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        pytest.fail("Queue composition and runner must defer model preparation to CY execution")

    monkeypatch.setattr(preparation, "prepare_catalogue", forbidden)
    monkeypatch.setattr(common, "prepare_catalogue", forbidden)
    architecture = "models/custom-architecture.yaml"
    pretrained_override = str(pretrained).lower() if isinstance(pretrained, bool) else pretrained
    snapshot = compose_snapshots(
        [
            "ground_truth=inputs.csv",
            f"ultralytics.model={architecture}",
            f"ultralytics.pretrained={pretrained_override}",
            "ultralytics.resume=true",
        ],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
        command=command,
    )[0].model_copy(update={"owner_uid": os.geteuid()})
    settings = json.loads(snapshot.config_json)["ultralytics"]
    assert settings["model"] == architecture
    assert settings["pretrained"] == pretrained
    assert settings["resume"] is True
    private = tmp_path / "snapshot.json"
    private.write_text(snapshot.model_dump_json())
    private.chmod(0o600)
    monkeypatch.setattr(sys, "argv", ["queue-run", "--snapshot", str(private), "--devices", "1"])
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "GPU-allotted")
    calls: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(os, "execv", lambda executable, argv: calls.append((executable, argv)))
    queue_run.main()
    assert len(calls) == 1
    executable, arguments = calls[0]
    assert executable == sys.executable
    assert arguments[:4] == [sys.executable, "-u", "-m", f"clearml_yolo.entrypoints.{command}"]
    execution = OmegaConf.load(Path(arguments[5]) / f"{arguments[7]}.yaml")
    assert execution.ultralytics.model == architecture
    assert execution.ultralytics.pretrained == pretrained
    assert execution.ultralytics.resume is True
    assert execution.ultralytics.device == [0]
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "GPU-allotted"
    assert not list(tmp_path.rglob("*.pt"))
    assert not (tmp_path / ".cache" / "clearml-yolo" / "preparation").exists()
