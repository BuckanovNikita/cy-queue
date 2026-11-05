# cy-queue agent instructions

CY-specific persistent whole-GPU queue extracted from clearml-yolo (CY).
Compatibility and dependencies are defined by `pyproject.toml`. Source installation
shares a prepared environment with a compatible CY checkout; never assume either
package is published on an index.

## Read first

Read development, interfaces and migration before any change:

- [docs/development.md](docs/development.md): environment, checks, opt-in GPU tests,
  [paired release checks](docs/development.md#paired-release-checks), cross-repository work.
- [docs/interfaces.md](docs/interfaces.md): CY integration contract, version bounds,
  GPU memory admission, refresh/completion races.
- [docs/migration.md](docs/migration.md): coordinated offline upgrade and draining.

Reference:

- [docs/architecture.json](docs/architecture.json): package boundary record of the
  initial extraction (CY feature `clearml-yolo/specs/003-portable-training/`).

## Architecture boundaries

- Dependency direction is `cy_queue` → `clearml_yolo`; CY never imports the queue.
- `cy_queue.core` and `cy_queue.application` have no filesystem, SDK or subprocess effects.
- Adapters own storage, locks, GPU probing and guardians; entrypoint integration owns
  CY command composition.
- Package initializers stay inert; direct CY commands require no queue.
- Preserve shared record protocols, configuration paths, coordination names, ownership,
  recovery and acknowledged handoff.
- Do not edit CY's shared process/lifecycle interfaces without cross-package checks.
- Enforced by `.importlinter` (`inward-layers`, `pure-policy`) and `tests/test_architecture.py`.

## Checks

With the shared environment selected (or prefix each with
`uv run --frozen --no-sync --project ../clearml-yolo`). Bare `python` must be the shared
CY environment interpreter; `check_docs.py` needs CY's dependencies.

```bash
python -m pytest
ruff check .
ruff format --check .
mypy .
lint-imports
python ../clearml-yolo/scripts/check_docs.py --root . <changed Markdown files>  # or --all
```

Real hardware and ClearML publication claims require explicitly owned live evidence;
see docs/development.md.

## Project workflow

- Record module/import/effect ownership (a task `architecture.json` under `docs/plans/`
  or `docs/bugs/`) before implementation; use the module architecture planning and
  Python project workflow skills when available.
- Substantive work requires independent review after integrated verification.
- Preserve unrelated changes and local overrides; do not bypass hooks or alter shared
  services.
- README.md is Russian; other documentation is English.

## Release and delivery

- Before every release or delivery of either CY or cy-queue, run the
  [paired release checks](docs/development.md#paired-release-checks) on the latest
  versions of both together: source and installed metadata, normal dependency
  resolution and queue integration against the proposed release versions.
  Incompatibility or unavailable evidence blocks delivery; one package passing alone
  is insufficient.
- Use Conventional Commits after verification; push verified changes to `main` of
  `git@github.com:BuckanovNikita/cy-queue.git` when delivery is authorized.
- No version-tag automation, deployment or registry publication is established.
