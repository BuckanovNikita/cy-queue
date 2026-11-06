# CY 0.46 compatibility verification, 2026-11-06

## Source pair

- **CY:** master `9582e4c`, version `0.46.0`. Annotated tag `v0.46.0` is on release
  commit `60edd4b`, created by CY's local release hook after `8a1d5a9`. `8a1d5a9` passed
  every prek hook, including `pytest-full` (the complete CY suite). The generated release
  commit `60edd4b` changes only the version, `uv.lock` and `CHANGELOG.md`, and it skipped
  the heavy hooks by design. The `src` tree is identical across both commits.
- **Queue:** latest `origin/main` `29d2284` (fetched 2026-11-06), working tree clean
  before this change. Metadata moves from `0.1.8` to `0.1.9`. Only the CY upper bound
  widens, from `<0.46` to `<0.47`; the lower bound stays `>=0.38`.
- No queue workers were running. The pair was installed into the CY development
  environment `../clearml-yolo/.venv`.

## Failing observations before the change

- `test_supported_cy_range_includes_forced_estimation_minor` failed against
  `<0.46`. The run used `PYTHONPATH=src` because the queue was not yet installed.
- `uv pip install -e ../clearml-yolo -e .` with normal resolution was unsatisfiable:
  `cy-queue==0.1.8 depends on clearml-yolo>=0.38,<0.46`.

## Checks after the change

Run from this checkout through `uv run --frozen --no-sync --project ../clearml-yolo`:

| Check | Result |
| --- | --- |
| `uv pip install --python ../clearml-yolo/.venv/bin/python -e ../clearml-yolo -e .` (normal resolution, without `--no-deps`) | Installed CY `0.46.0` (replacing stale editable `0.45.1` metadata) and queue `0.1.9` |
| `uv pip check` | All 281 installed packages compatible |
| Source and installed identity | `importlib.metadata`: `0.46.0` / `0.1.9`; both packages import from these source checkouts |
| `ruff check .` | Passed |
| `ruff format --check .` | 103 files already formatted |
| `mypy .` | No issues in 70 source files |
| `lint-imports` | 2 contracts kept, 0 broken |
| `cy-queue --help` | Exit 0 |
| `CUDA_VISIBLE_DEVICES= pytest -q` | **584 passed, 7 deselected**, 19 warnings, 135.10 s (137.27 s wall), exit 0 |

The 7 deselected tests are explicit physical-GPU opt-ins and do not count as passes.
The warnings come from upstream Hydra-Zen and Pydantic deprecations. The run includes
installed-source identity, outside-checkout entrypoints, allocation-aware automatic
batch lookup and the architecture negative cases. No physical GPU, NFS or ClearML
publication outcome is claimed.

## Committed pair accepted (2026-11-06)

The pair was CY master `9582e4c` (`0.46.0`, tag `v0.46.0` on `60edd4b`) and queue
commit `4498e64` (`0.1.9`). Results:

- A normal dependency-enabled reinstall of both editable sources succeeded, and
  `uv pip check` reported all 281 packages compatible.
- Installed metadata reads `0.46.0` / `0.1.9`, matching source.
- The complete queue suite passed **584 tests, 7 physical opt-ins deselected**, with
  19 warnings, exit 0 (131.42 s).
- `cy-queue --help` exited 0.

Delivery pushes CY `master` and `v0.46.0` first, then queue `main`.
