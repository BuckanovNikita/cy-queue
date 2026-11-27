"""Real queue entrypoint with only the host binding isolated from production."""

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest


def queue_environment(root: Path) -> dict[str, str]:
    config = root / "queue.toml"
    config.write_text(
        f'[queue]\nname = "Test queue"\nroot = {json.dumps(str(root / "queue"))}\n'
        f"coordination_root = {json.dumps(str(root / 'locks'))}\n"
    )
    environment = dict(os.environ, CY_HOME=str(root), CY_QUEUE_CONFIG=str(config))
    if "CY_TEST_QUEUE_MEMORY" not in environment:
        memory = root / "gpu-memory.json"
        memory.write_text(json.dumps({"GPU-test": 0}))
        environment["CY_TEST_QUEUE_MEMORY"] = str(memory)
    boundary = Path(__file__).parent / "queue_nvml"
    environment["PYTHONPATH"] = os.pathsep.join((str(boundary), environment.get("PYTHONPATH", "")))
    environment.pop("CY_QUEUE_ROOT", None)
    return environment


def queue_command(root: Path) -> list[str]:
    # Test-only injection of the existing binding seam; production has no bypass.
    script = """
from pathlib import Path
from cy_queue.adapters.queue import coordination
from cy_queue.entrypoints.queue import main
bind = coordination.bind_coordination_root
coordination.bind_coordination_root = lambda host, root: bind(
    host, root, bootstrap_root=Path(BOOTSTRAP)
)
main()
""".replace("BOOTSTRAP", repr(str(root / "bootstrap")))
    return [sys.executable, "-c", script]


def queue_stdout(root: Path) -> Callable[..., str]:
    environment = queue_environment(root)
    command = queue_command(root)

    def run(*arguments: str) -> str:
        result = subprocess.run(  # noqa: S603 - isolated real CLI
            [*command, *arguments],
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        return result.stdout

    return run


def configure_queue(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from cy_queue.adapters.queue import coordination

    environment = queue_environment(root)
    monkeypatch.setenv("CY_QUEUE_CONFIG", environment["CY_QUEUE_CONFIG"])
    monkeypatch.delenv("CY_QUEUE_ROOT", raising=False)
    bind = coordination.bind_coordination_root
    monkeypatch.setattr(
        coordination,
        "bind_coordination_root",
        lambda host, location: bind(host, location, bootstrap_root=root / "bootstrap"),
    )
