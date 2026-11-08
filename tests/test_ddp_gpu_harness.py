"""Compose product configuration from a generated distributed training input."""

import json
import sys
from pathlib import Path

from ddp_gpu_harness import (
    Evidence,
    GPUOptions,
)


def test_generated_inputs_and_native_config_compose_offline(tmp_path: Path) -> None:
    from ddp_gpu_harness import environment_for

    evidence = Evidence(GPUOptions("0,1", "owned-tests", tmp_path), "prepare-only")
    request = {
        "indexes": [0, 1],
        "project": "owned-tests",
        "compiled": False,
        "scenario": "direct-eager",
        "tag": "offline-only",
        "timeout": 1200,
    }
    (evidence.root / "request.json").write_text(json.dumps(request))
    base = environment_for(evidence)
    evidence.helper("prepare", base)
    source = Path(__file__).resolve().parents[1] / "src"
    code = (
        "import os; from pathlib import Path; "
        "from cy_queue.core.queue import ResourceRequest; "
        "from cy_queue.entrypoints.hydra.queue_config import compose_snapshots; "
        "root=Path(os.environ['CY_HOME']); "
        "jobs=compose_snapshots(['--config-dir',str(root/'config'),'--config-name','ddp'],"
        "ResourceRequest(devices=('GPU-a','GPU-b')),project_root=root); "
        "assert len(jobs)==1; assert 'pretrained' in jobs[0].config_json"
    )
    evidence.command([sys.executable, "-c", code], dict(base, PYTHONPATH=f"{source}:{base['PYTHONPATH']}"))
