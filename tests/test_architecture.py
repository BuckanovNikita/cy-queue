"""Executable queue architecture, CY integration and deferred SDK boundaries."""

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1] / "src/cy_queue"
_LAYERS = {"core": 0, "application": 1, "adapters": 2, "entrypoints": 3}
_CY_ADAPTERS = {
    "clearml_yolo.adapters.runtime.process_tree",
    "clearml_yolo.adapters.runtime.execution_lifecycle",
    "clearml_yolo.adapters.observability.diagnostics",
    "clearml_yolo.adapters.observability.tracing",
}
_CY_ENTRYPOINTS = _CY_ADAPTERS | {
    "clearml_yolo.adapters.runtime.bootstrap",
    "clearml_yolo.adapters.storage.filesystem",
    "clearml_yolo.adapters.yolo.config",
    "clearml_yolo.application.contracts",
    "clearml_yolo.application.use_cases.pipeline",
    "clearml_yolo.application.use_cases.train",
    "clearml_yolo.core.presentation",
    "clearml_yolo.core.redaction",
    "clearml_yolo.entrypoints.hydra.configs",
    "clearml_yolo.entrypoints.hydra.sweeps",
    "clearml_yolo.entrypoints.hydra.validation",
    "clearml_yolo.entrypoints.pipeline",
    "clearml_yolo.entrypoints.train",
}
_SDK_OWNERS = {
    "torch": {"cy_queue.adapters.runtime.gpu_probe"},
    "pynvml": {"cy_queue.adapters.runtime.gpu_resources"},
    "textual": {"cy_queue.entrypoints.queue_tui"},
    "clearml": set(),
    "ultralytics": set(),
}


def _dynamic_dependency(node: ast.Call) -> str | None:
    if not isinstance(node.func, (ast.Name, ast.Attribute)):
        return None
    function = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
    if function not in {"import_module", "__import__"}:
        return None
    if not node.args or not isinstance(node.args[0], ast.Constant):
        raise ValueError("Dynamic imports need literal, reviewable targets")
    return str(node.args[0].value)


def _dependencies(source: str) -> set[str]:
    dependencies: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            dependencies.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise ValueError("Relative imports are not allowed")
            if node.module:
                dependencies.add(node.module)
        elif isinstance(node, ast.Call):
            if dependency := _dynamic_dependency(node):
                dependencies.add(dependency)
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.startswith(("cy_queue.", "clearml_yolo.entrypoints."))
            and " " not in node.value
        ):
            # Literal subprocess -m targets remain part of the dependency contract.
            dependencies.add(node.value)
    return dependencies


def _errors(module: str, dependencies: set[str]) -> list[str]:
    layer = module.split(".")[1]
    if layer not in _LAYERS:
        return [f"Unclassified module {module}"]
    errors = []
    for dependency in dependencies:
        root = dependency.split(".")[0]
        if dependency.startswith("cy_queue."):
            target = dependency.split(".")[1]
            worker_target = (
                module == "cy_queue.adapters.queue.runtime"
                and dependency == "cy_queue.entrypoints.queue_run"
            )
            if target in _LAYERS and _LAYERS[target] > _LAYERS[layer] and not worker_target:
                errors.append(f"Outward dependency: {module} -> {dependency}")
        elif root == "clearml_yolo":
            permitted = _CY_ENTRYPOINTS if layer == "entrypoints" else _CY_ADAPTERS
            if layer in {"core", "application"} or dependency not in permitted:
                errors.append(f"Undocumented CY interface: {module} -> {dependency}")
        elif root in _SDK_OWNERS and module not in _SDK_OWNERS[root]:
            errors.append(f"SDK ownership: {module} -> {dependency}")
        elif layer in {"core", "application"} and root in {
            "os",
            "subprocess",
            "socket",
            "http",
            "requests",
            "hydra",
            "filelock",
        }:
            errors.append(f"Policy effect: {module} -> {dependency}")
    return errors


def test_all_modules_respect_layers_sdk_ownership_and_cy_interfaces() -> None:
    errors = []
    for path in _ROOT.rglob("*.py"):
        source = path.read_text()
        if path.name == "__init__.py":
            assert all(
                isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                for node in ast.parse(source).body
            ), f"Package initializer must be inert: {path}"
            continue
        module = "cy_queue." + ".".join(path.relative_to(_ROOT).with_suffix("").parts)
        errors.extend(_errors(module, _dependencies(source)))
    assert errors == []


@pytest.mark.parametrize(
    ("module", "dependency"),
    [
        ("cy_queue.core.queue", "cy_queue.adapters.queue.storage"),
        ("cy_queue.application.queue", "clearml_yolo.core.models"),
        ("cy_queue.application.queue", "subprocess"),
        ("cy_queue.adapters.queue.runtime", "clearml_yolo.entrypoints.pipeline"),
        ("cy_queue.adapters.queue.guardian", "clearml"),
        ("cy_queue.entrypoints.queue", "torch"),
        ("cy_queue.entrypoints.queue", "clearml_yolo.adapters.clearml.session"),
    ],
)
def test_prohibited_dependencies_fail(module: str, dependency: str) -> None:
    assert _errors(module, {dependency})


@pytest.mark.parametrize(
    "source",
    [
        "import cy_queue.adapters.queue.storage",
        (
            "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n"
            " import cy_queue.adapters.queue.storage"
        ),
        "import importlib\nimportlib.import_module('cy_queue.adapters.queue.storage')",
        "argv = ['python', '-m', 'cy_queue.adapters.queue.storage']",
    ],
)
def test_static_type_only_dynamic_and_worker_edges_are_checked(source: str) -> None:
    assert _errors("cy_queue.core.queue", _dependencies(source))


def test_unknown_dynamic_target_is_rejected() -> None:
    with pytest.raises(ValueError, match="literal"):
        _dependencies("importlib.import_module(user_value)")
