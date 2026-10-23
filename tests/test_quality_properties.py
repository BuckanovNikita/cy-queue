"""Queue integration contracts extracted from CY tests."""

import json
import os
import sys
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

import pytest
from clearml_yolo.core.identity import ModelIdentity
from clearml_yolo.entrypoints.hydra.config_resolution import resolve_config_document
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule
from omegaconf import OmegaConf

from cy_queue.adapters.queue.coordination import host_transaction
from cy_queue.adapters.queue.storage import NFSQueueStore
from cy_queue.core.queue import JobSnapshot, JobState, WorkerIdentity

_LEXICAL = st.sampled_from(["0001", "10", "ёж", "猫", "e\u0301", "é", "001,猫"])

_CONFIDENCE = st.sampled_from([0.0, 0.2, 0.5, 0.700000000000003, 1.0])

_BOUNDS = settings(max_examples=24, deadline=None, derandomize=True, database=None)


@_BOUNDS
@given(label=_LEXICAL, image=_LEXICAL, confidence=_CONFIDENCE, enabled=st.booleans())
def test_resolved_yaml_json_snapshot_preserves_lexical_identity_and_types(
    label: str, image: str, confidence: float, enabled: bool
) -> None:
    """Saved configs must preserve string identities and exact primitive values."""
    identity = ModelIdentity(model_name=label, training_task_id="00001234")
    document = {
        "identity": identity.model_dump(mode="json"),
        "image_name": image,
        "threshold": confidence,
        "enabled": enabled,
        "device": None,
        "copy": "${identity.model_name}",
        "nested": ["${threshold}", "${enabled}", "${device}"],
    }
    saved = OmegaConf.create(OmegaConf.to_yaml(OmegaConf.create(document)))
    resolved = resolve_config_document(saved)
    snapshot = JobSnapshot(
        command="metrics",
        config_json=json.dumps(resolved, ensure_ascii=False),
        project_root="/project",
        cwd="/project",
        interpreter="/python",
        package_version="1",
        package_identity="source",
    )
    loaded = json.loads(JobSnapshot.model_validate_json(snapshot.model_dump_json()).config_json)
    assert loaded["image_name"] == image
    assert loaded["identity"]["model_name"] == loaded["copy"] == label
    assert loaded["identity"]["training_task_id"] == "00001234"
    assert loaded["nested"] == [confidence, enabled, None]
    assert type(loaded["nested"][0]) is float
    assert type(loaded["nested"][1]) is bool
    assert ModelIdentity.model_validate(loaded["identity"]) == identity


class DurableQueueSequences(RuleBasedStateMachine):
    """Compare real private/public records against a tiny independent state ledger."""

    def __init__(self) -> None:
        super().__init__()
        self.temporary = TemporaryDirectory(prefix="cy-quality-queue-")
        self.root = Path(self.temporary.name)
        self.patch = pytest.MonkeyPatch()
        self.patch.setattr(
            "cy_queue.adapters.queue.storage.host_transaction",
            partial(host_transaction, root=self.root / "coordination"),
        )
        self.store = NFSQueueStore(
            self.root / "queue",
            WorkerIdentity(owner_uid=os.geteuid(), host_id="quality", boot_id="boot"),
        )
        self.order: list[str] = []
        self.states: dict[str, JobState] = {}
        self.configurations: dict[str, str] = {}

    @rule(label=_LEXICAL)
    def submit(self, label: str) -> None:
        configuration = json.dumps({"label": label, "device": None}, ensure_ascii=False)
        snapshot = JobSnapshot(
            command="train",
            label=label,
            config_json=configuration,
            project_root=str(self.root),
            cwd=str(self.root),
            interpreter=sys.executable,
            package_version="1",
            package_identity="source",
        )
        job = self.store.submit((snapshot,))[0]
        self.order.append(job.id)
        self.states[job.id] = "pending"
        self.configurations[job.id] = configuration

    @precondition(lambda self: bool(self.order))
    @rule(index=st.integers(min_value=0, max_value=20))
    def cancel(self, index: int) -> None:
        identifier = self.order[index % len(self.order)]
        old = self.states[identifier]
        self.store.cancel(identifier)
        if old == "pending":
            self.states[identifier] = "cancelled"
        elif old in {"starting", "running"}:
            self.states[identifier] = "cancelling"

    @precondition(
        lambda self: any(
            value in {"starting", "running", "cancelling"} for value in self.states.values()
        )
    )
    @rule(index=st.integers(min_value=0, max_value=20))
    def advance(self, index: int) -> None:
        active = [
            identifier
            for identifier in self.order
            if self.states[identifier] in {"starting", "running", "cancelling"}
        ]
        identifier = active[index % len(active)]
        old = self.states[identifier]
        transitions: dict[str, JobState] = {
            "starting": "running",
            "running": "completed",
            "cancelling": "cancelled",
        }
        next_state = transitions[old]
        self.store.update(identifier, next_state, expected_state=old)
        self.states[identifier] = next_state

    @precondition(lambda self: "pending" in self.states.values())
    @rule(index=st.integers(min_value=0, max_value=20), to_front=st.booleans())
    def reorder(self, index: int, to_front: bool) -> None:
        pending = [identifier for identifier in self.order if self.states[identifier] == "pending"]
        identifier = pending[index % len(pending)]
        anchor = pending[0] if to_front else pending[-1]
        revision = self.store.view().revision
        self.store.move(identifier, "top" if to_front else "bottom", revision)
        if identifier != anchor:
            self.order.remove(identifier)
            self.order.insert(self.order.index(anchor) + int(not to_front), identifier)
            with pytest.raises(RuntimeError, match="revision"):
                self.store.move(identifier, "top", revision)

    @precondition(lambda self: bool(self.order))
    @rule(index=st.integers(min_value=0, max_value=20))
    def start(self, index: int) -> None:
        identifier = self.order[index % len(self.order)]
        should_start = self.states[identifier] == "pending"
        assert self.store.prepare_start(identifier, ("GPU-a", "GPU-b"), "original") == should_start
        if should_start:
            self.states[identifier] = "starting"
            assert not self.store.prepare_start(identifier, ("GPU-c",), "replacement")
            guardian = self.store.snapshot_path(identifier).parent / "guardian.json"
            assert guardian.read_text(encoding="utf-8") == "original"

    @invariant()
    def public_state_and_private_snapshot_match_reference(self) -> None:
        view = self.store.view()
        assert [job.id for job in view.jobs] == self.order
        assert {job.id: job.state for job in view.jobs} == self.states
        for job in view.jobs:
            assert self.store.load_snapshot(job.id).config_json == self.configurations[job.id]
            if job.state in {"starting", "running", "cancelling", "completed"}:
                assert job.devices == ("GPU-a", "GPU-b")

    @override
    def teardown(self) -> None:
        self.patch.undo()
        self.temporary.cleanup()


TestDurableQueueSequences = DurableQueueSequences.TestCase

TestDurableQueueSequences.settings = settings(
    max_examples=16,
    stateful_step_count=18,
    deadline=None,
    derandomize=True,
    database=None,
)
