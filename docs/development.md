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

Architecture planning and acceptance for the extraction are recorded in
[architecture.json](architecture.json). New tasks keep their own architecture and
dated verification records. Cross-repository work follows the active CY task ledger
and fresh independent review requirement.

## Paired release checks

Before every release or delivery of **either** repository, verify the latest CY and
cy-queue source revisions together, including the proposed release versions. Fetch
both remotes, inspect their default branches/tags and preserve unrelated local work;
do not assume a stale sibling checkout or installed metadata represents the latest.
Coordinate workers and drain active jobs using [migration](migration.md) before
changing an operational environment, or use an isolated prepared environment.

From this checkout, with CY's approved external dependencies prepared:

```bash
uv pip install --python ../clearml-yolo/.venv/bin/python -e ../clearml-yolo -e .
uv pip check --python ../clearml-yolo/.venv/bin/python
uv run --frozen --no-sync --project ../clearml-yolo pytest -q
uv run --frozen --no-sync --project ../clearml-yolo cy-queue --help
```

Run the configured static/import checks above too. The installation tests compare
the source and installed requirements/versions; reinstall after version changes.
Use normal resolution for acceptance, without `--no-deps`, and preserve approved
external source revisions. Record both source SHAs, versions, resolver and queue
integration results in dated evidence. Check the proposed version before creating
or pushing a CY release tag, and recheck the final installed pair if hooks change
either version. Incompatible bounds, stale metadata, missing current sources or
failed/unavailable checks block delivery. Update the bounded CY requirement only
after checking the newly supported interfaces. Future minors are not assumed compatible.

Public source delivery uses Conventional Commits on `main` and
`git@github.com:BuckanovNikita/cy-queue.git`. Update the package version for a package
fix, verify and review the pair, commit only task-owned changes, then push the
authorized branch and verify remote identity. There is no version-tag automation,
deployment, GitHub Release object, asset upload or package registry publication.
