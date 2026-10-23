"""Queue integration contracts extracted from CY tests."""

import json
import re
from pathlib import Path

import pytest
from omegaconf import OmegaConf

from cy_queue.core.queue import ResourceRequest
from cy_queue.entrypoints.hydra.queue_config import compose_snapshots, write_execution_config


def _group(tags: list[str], user_tags: list[str]) -> str:
    assert tags[:-1] == user_tags
    tag = tags[-1]
    assert re.fullmatch(r"multirun-\d{8}-\d{6}(?:-[a-z]+){6}", tag)
    return tag


@pytest.mark.parametrize("mode", [["-m"], ["hydra.mode=MULTIRUN"]])
def test_queue_freezes_group_tags_across_jobs_and_execution(
    tmp_path: Path, mode: list[str]
) -> None:
    arguments = [*mode, "ground_truth=input.csv", "clearml.tags=[first],[second]"]
    first = compose_snapshots(arguments, ResourceRequest(gpus=1), project_root=tmp_path)
    second = compose_snapshots(arguments, ResourceRequest(gpus=1), project_root=tmp_path)
    first_tags = [json.loads(job.config_json)["clearml"]["tags"] for job in first]
    second_tags = [json.loads(job.config_json)["clearml"]["tags"] for job in second]
    assert len(first_tags) == len(second_tags) == 2
    assert _group(first_tags[0], ["first"]) == _group(first_tags[1], ["second"])
    assert _group(second_tags[0], ["first"]) == _group(second_tags[1], ["second"])
    assert first_tags[0][-1] != second_tags[0][-1]
    path = write_execution_config(first[0], 1, tmp_path)
    assert list(OmegaConf.load(path).clearml.tags) == first_tags[0]


@pytest.mark.parametrize("mode", ["RUN", "MULTIRUN"])
def test_queue_saved_one_job_mode_preserves_user_tags(tmp_path: Path, mode: str) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    user_tags = ["prod", "multirun-user-supplied"]
    OmegaConf.save(
        OmegaConf.create(
            {
                "defaults": ["pipeline", "_self_"],
                "ground_truth": "input.csv",
                "clearml": {"tags": user_tags},
                "hydra": {"mode": mode},
            }
        ),
        config_dir / "saved.yaml",
    )
    snapshots = compose_snapshots(
        ["--config-dir", str(config_dir), "--config-name", "saved"],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
    )
    assert len(snapshots) == 1
    tags = json.loads(snapshots[0].config_json)["clearml"]["tags"]
    if mode == "MULTIRUN":
        _group(tags, user_tags)
    else:
        assert tags == user_tags


def test_queue_preserves_job_dependent_tag_interpolation(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    OmegaConf.save(
        OmegaConf.create(
            {
                "defaults": ["pipeline", "_self_"],
                "ground_truth": "input.csv",
                "clearml": {"tags": ["job-${hydra:job.num}"]},
                "hydra": {"mode": "MULTIRUN", "sweeper": {"params": {"ultralytics.epochs": "1,2"}}},
            }
        ),
        config_dir / "saved.yaml",
    )
    snapshots = compose_snapshots(
        ["--config-dir", str(config_dir), "--config-name", "saved"],
        ResourceRequest(gpus=1),
        project_root=tmp_path,
    )
    tags = [json.loads(job.config_json)["clearml"]["tags"] for job in snapshots]
    assert _group(tags[0], ["job-0"]) == _group(tags[1], ["job-1"])
