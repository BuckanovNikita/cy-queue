"""Queue integration contracts extracted from CY tests."""

import subprocess
from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from loguru import logger

from cy_queue.adapters.runtime import gpu_resources


@pytest.fixture
def traces(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[str]]:
    monkeypatch.setenv("LOGURU_LEVEL", "TRACE")
    messages: list[str] = []
    sink = logger.add(lambda message: messages.append(str(message)), level="TRACE")
    try:
        yield messages
    finally:
        logger.remove(sink)


def test_probe_failure_diagnostics_do_not_echo_subprocess_payload(
    monkeypatch: pytest.MonkeyPatch,
    traces: list[str],
) -> None:
    result = SimpleNamespace(returncode=1, stderr="probe-secret", stdout="")
    monkeypatch.setattr(subprocess, "run", lambda *_args, **_kwargs: result)
    with pytest.raises(RuntimeError, match="failed"):
        gpu_resources.GPUInventory().visible()
    text = "\n".join(traces)
    assert "FAILED gpu.visibility_probe" in text
    assert "FAILED gpu.visibility" in text
    assert "probe-secret" not in text
