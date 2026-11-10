"""A null training batch survives submission until the worker knows its allocation."""

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest
from clearml_yolo.adapters.integrations import batch_resolution
from clearml_yolo.adapters.runtime.gpu_inventory import GPUDevice
from clearml_yolo.adapters.storage.batch_sizes import BatchSizeStore
from clearml_yolo.application.contracts import PreparedDataset
from clearml_yolo.core.models import ModelConfig
from omegaconf import OmegaConf

from cy_queue.core.queue import JobSnapshot, ResourceRequest
from cy_queue.entrypoints.hydra.queue_config import (
    Command,
    compose_snapshots,
    write_execution_config,
)


@pytest.mark.parametrize("command", ["pipeline", "train"])
@pytest.mark.parametrize(
    "selection",
    [None, "deimv2/s", "rfdetr/nano", "fasterrcnn/resnet50_fpn", "fcos/resnet50_fpn"],
)
def test_null_batch_survives_snapshot_and_worker_exec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: Command, selection: str | None
) -> None:
    from cy_queue.entrypoints import queue_run

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        pytest.fail("Submission must not inspect GPUs or resolve a training batch")

    monkeypatch.setattr(batch_resolution, "discover_gpus", forbidden)
    monkeypatch.setattr(batch_resolution, "resolve_batch_estimate", forbidden)
    prefix = "ultralytics" if selection is None else "model.train"
    arguments = ["ground_truth=inputs.csv", f"{prefix}.batch=null"]
    if selection is not None:
        arguments.append(f"model={selection}")
    snapshot = compose_snapshots(arguments, ResourceRequest(gpus=2), project_root=tmp_path, command=command)[0]
    # The real storage submission boundary stamps the submitting owner's UID.
    owned = snapshot.model_copy(update={"owner_uid": os.geteuid()})
    loaded = JobSnapshot.model_validate_json(owned.model_dump_json())
    frozen = OmegaConf.create(json.loads(loaded.config_json))
    assert OmegaConf.select(frozen, f"{prefix}.batch") is None
    assert OmegaConf.select(frozen, f"{prefix}.device") is None
    private = tmp_path / "snapshot.json"
    private.write_text(loaded.model_dump_json())
    private.chmod(0o600)
    monkeypatch.setattr(sys, "argv", ["queue-run", "--snapshot", str(private), "--devices", "2"])
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "GPU-assigned-b,GPU-assigned-a")
    calls: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(os, "execv", lambda executable, argv: calls.append((executable, argv)))
    queue_run.main()
    assert len(calls) == 1
    executable, argv = calls[0]
    assert executable == sys.executable
    assert argv[3] == f"clearml_yolo.entrypoints.{command}"
    execution = OmegaConf.load(Path(argv[5]) / f"{argv[7]}.yaml")
    assert OmegaConf.select(execution, f"{prefix}.batch") is None
    assert OmegaConf.select(execution, f"{prefix}.device") == [0, 1]
    predict = "ultralytics_predict" if selection is None else "model.predict"
    assert OmegaConf.select(execution, f"{predict}.device") == [0]
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "GPU-assigned-b,GPU-assigned-a"


def test_worker_resolves_the_allocated_gpu_count_without_replacing_requested_null(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot = compose_snapshots(
        ["ground_truth=inputs.csv", "model=fcos/resnet50_fpn", "model.train.batch=null"],
        ResourceRequest(gpus=2),
        project_root=tmp_path,
        command="train",
    )[0]
    execution = OmegaConf.load(write_execution_config(snapshot, 2, tmp_path))
    requested = ModelConfig.model_validate(OmegaConf.to_container(execution.model, resolve=True))
    assert requested.train.batch is None
    assigned = tuple(
        GPUDevice(
            index=index,
            uuid=f"GPU-assigned-{index}",
            name=f"fixture-{index}",
            total_memory_bytes=16 * 1024**3,
            used_memory_bytes=0,
            utilization=0,
        )
        for index in range(2)
    )
    store = BatchSizeStore()
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(
        "fixture-0 [16 GiB]:\n  800:\n    fcos/resnet50_fpn: 32\n"
        "fixture-1 [16 GiB]:\n  800:\n    fcos/resnet50_fpn: 8\n"
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"class_names": {"0": "class"}, "images": [{"split": "train", "boxes": 2}]}))
    prepared = PreparedDataset(
        data=tmp_path / "data.yaml",
        ground_truth=tmp_path / "truth.csv",
        manifest=manifest,
        dataset_format="coco",
        artifacts=[],
    )
    monkeypatch.setattr(batch_resolution, "discover_gpus", lambda: assigned)
    resolved, provenance = batch_resolution.resolve_native_batch(requested, prepared, None)
    assert resolved.train.batch == 16
    assert resolved.train.device == [0, 1]
    assert requested.train.batch is None
    assert json.loads(snapshot.config_json)["model"]["train"]["batch"] is None
    assert provenance is not None
    assert provenance["global_batch"] == 16
    assert provenance["per_gpu_batch"] == 8
    assert provenance["origin"] == "batch_sizes_table"
    assert provenance["table_digest"] == store.load().digest
    entries = provenance["selected_entries"]
    assert [entry["target_gpu"]["uuid"] for entry in entries] == ["GPU-assigned-0", "GPU-assigned-1"]
    assert [entry["resolved_per_gpu_batch"] for entry in entries] == [32, 8]
    assert all(entry["fallback"] is False for entry in entries)
    assert all(entry["entry"]["origin"] == "manual" for entry in entries)
