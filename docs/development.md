# Development

Use the source-first shared-environment installation in the README. Install the `dev`
group through your externally managed environment together with CY's approved dependencies.
Do not let a resolver replace CY with an index package. Source checkout testing is the
normal verification route; no routine distribution build or package publication is required.

From this repository, with that environment selected:

```bash
python -m pytest
ruff check .
ruff format --check .
mypy .
lint-imports
```

Use `uv run --frozen --no-sync --project /path/to/clearml-yolo <tool>` when deliberately
reusing CY's prepared uv environment; run from this repository so its check configuration
is selected. Dependency installation remains external and the queue does not carry a
lockfile that resolves a nonexistent index release of CY.

The routine suite uses temporary storage, controlled GPU telemetry and real owned
subprocesses. Opt-in `ddp_gpu` tests require explicit physical devices, ClearML project,
output evidence and authorization options exposed by `pytest --help`. The multiuser
harness additionally provisions temporary Unix identities; inspect its `--help` and
ownership contract before explicit execution. Physical queued scenarios additionally require
an existing valid `queue.toml` (or `CY_QUEUE_CONFIG`) and retain its host coordination
root so real GPU locks still coordinate with other users. They override only the durable
metadata root with the scenario-owned path. Do not change host coordination to bypass
other workloads. The multiuser harness uses controlled devices and test-owned identities.

Architecture planning and acceptance are recorded in [architecture.json](architecture.json).
The parent CY feature ledger owns cross-repository acceptance and the fresh independent
review. This repository's delivery stopping point is a verified Conventional Commit.
There is no remote creation, push, version tag, deployment or package publication workflow.
