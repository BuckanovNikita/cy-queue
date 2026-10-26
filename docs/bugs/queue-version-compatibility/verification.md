# Paired installation verification — 2026-10-26

Pair: CY source/installed **0.40.0**, queue source/installed **0.1.1**. CY source
base is `885b85ecfadbdf5c4f53795149e605b842b1d1f9` (also fetched `origin/master`);
queue base is `1be96a6d916d6a26a5ef07715d87a1853709602f` plus this task's packaging,
test and documentation changes. Queue had no remote; public creation/push is
explicitly authorized by the user. Python compatibility remains unchanged.

## Reproduction and checks

| Check | Actual result |
| --- | --- |
| Original joint editable install, `--dry-run` | Failed with unsatisfiable CY `>=0.38,<0.39` against source 0.40.0 |
| Original `uv pip check` | Failed: installed CY 0.39.0 violated queue requirement |
| New source/installed and outside-checkout compatibility tests before metadata fix | Both failed on the original upper bound |
| Joint editable install after fix, with normal resolution | Passed; only CY 0.39.0 → 0.40.0 and queue 0.1.0 → 0.1.1 replaced |
| `uv pip check --python ../clearml-yolo/.venv/bin/python` | Passed: all 283 installed packages compatible |
| `uv run --frozen --no-sync --project ../clearml-yolo pytest -q` | 501 passed, 7 physical-GPU cases deselected, 4 upstream Pydantic warnings; 125.08 seconds |
| Configured Ruff / format / strict mypy | Passed; 77 files formatted, 67 typed source files |
| Configured import-linter | Both contracts kept; negative injected architecture edges also covered by pytest |
| Markdown/local links via CY `scripts/check_docs.py --root . --all` | Passed; task evidence also checked explicitly before acceptance |
| `cy`, `cy-train`, `cy-queue --help` from an owned temporary directory | All exited 0 with nonempty help |
| Current pipeline/train queue composition with a serialized Albumentations HorizontalFlip pipeline | Both composed, froze and validated successfully |

Commands for static checks were `ruff check .`, `ruff format --check .`, `mypy .`
and `lint-imports`, each through `uv run --frozen --no-sync --project ../clearml-yolo`
from the queue repository. Installation supplied both editable source paths in one
`uv pip install` command; no `--no-deps`, lock regeneration or upstream changes.
The initial augmentation probe omitted the required pipeline file and correctly
failed validation; supplying the serialized pipeline passed without code changes.

## Interface and publication inspection

An independent read-only inspection compared all 15 directly imported CY modules
with v0.38.0: 13 were unchanged; Hydra configs/validation gained augmentation.
The removed CY supervision facade is not imported by the queue. Shared process-tree
and lifecycle interfaces are unchanged. The original 0.38 floor remains; fresh
runtime integration evidence here covers the latest 0.40 pair, not a rerun of every
older CY or Python version.

The one-commit queue history contains source, tests, docs and configuration. A targeted
publication inspection found no credential files, private keys, tokens, private stand
endpoints or machine paths; credential-like strings were redaction test fixtures.
Historical extraction and live-evidence files remain unchanged.

## Limits and acceptance

No native GPU training, ClearML upload or multi-host/NFS acceptance is claimed.
Ordinary queue tests include real owned subprocess behavior with controlled GPU
telemetry. Both repositories retain a mandatory latest-pair release check, including
proposed versions and stale editable metadata; future CY minors remain bounded out.
Final independent review and architecture acceptance are recorded alongside this file.
