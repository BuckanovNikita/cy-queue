"""Queue integration contracts extracted from CY tests."""

import json
from pathlib import Path

import pytest
from clearml_yolo.application.contracts import ClearMLDatasetRef
from clearml_yolo.application.ground_truth import normalize_ground_truth


@pytest.mark.parametrize(
    "override",
    [
        "ground_truth={dataset_id:id}",
        'ground_truth={project_name:p,name:n,version:"1.0.0"}',
    ],
)
def test_queue_preserves_selector_without_fetching(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    override: str,
) -> None:
    from clearml_yolo.adapters.clearml.datasets import ClearMLGroundTruthRepository

    from cy_queue.core.queue import ResourceRequest
    from cy_queue.entrypoints.hydra.queue_config import compose_snapshots

    monkeypatch.setattr(
        ClearMLGroundTruthRepository,
        "resolve",
        lambda *args: pytest.fail("queue submission downloaded dataset"),
    )
    (snapshot,) = compose_snapshots([override], ResourceRequest(gpus=1), project_root=tmp_path)
    selected = json.loads(snapshot.config_json)["ground_truth"]
    assert normalize_ground_truth(selected) == (
        ClearMLDatasetRef(dataset_id="id")
        if "dataset_id" in override
        else ClearMLDatasetRef(project_name="p", name="n", version="1.0.0")
    )
