# CY 0.46 paired verification — 2026-11-05

Status: frozen CY 0.46.0 candidate installed with queue 0.1.9; ordinary queue
integration and configured checks passed. Review, architecture acceptance and final actual
post-hook source/installed checks remain pending. Prior CY 0.45.1/0.45.2 results
do not establish compatibility with this proposed pair.

Inspected latest queue base:
`694c12f9c2a1a0064284a69d010e846108d43875` (queue 0.1.8).
The isolated compatibility work targets queue 0.1.9 and CY 0.46.0.

The preserved force diff was inspected for added record fields, estimator keys,
GPU inventory signatures and CLI entrypoints. Queue runtime keeps its existing
pipeline/train composition and process/lifecycle interfaces; estimate records are
exercised by its integration tests. No queue runtime change is required by this
inspection. Final policy inspection and full paired tests remain required.

No operational installation, shared worker, GPU admission configuration, ownership
record or service was changed. The original dirty queue checkout and original CY
checkout/environment are excluded from this task's writes.

## Preparation checks

The architecture plan validator exited 0 before executable metadata/test changes.
The new boundary regression was run with queue's isolated existing environment and
failed as expected against `clearml-yolo>=0.38,<0.46`: CY 0.46.0 was rejected.
Only after observing that failure was the bound widened to `<0.47` and queue
source version changed to 0.1.9. The same regression then checks acceptance of
0.46.0 and rejection of 0.47.0. This metadata-only observation does not establish
the final installed pair; the isolated environment intentionally retains its
historical installation until the parent supplies frozen final CY source.

No queue lockfile exists and none was created. No dependency revision or external
source was changed. Full final-pair checks remain pending.

| Preparation check | Result |
| --- | --- |
| Architecture validator, plan phase | Exit 0 before metadata implementation |
| `python -m pytest -q tests/test_standalone_training.py::test_supported_cy_range_includes_forced_batch_estimation_minor`, old bound | Exit 1; expected assertion failure because `<0.46` rejected 0.46.0 |
| Same focused test, updated bound | Exit 0; 1 passed, 19 upstream deprecation warnings |
| `ruff check tests/test_standalone_training.py` | Exit 0 |
| `ruff format --check tests/test_standalone_training.py` | Exit 0 |
| `git diff --check` | Exit 0 |

These focused checks used the existing isolated environment and prove only the
boundary regression and edited test's static validity. Its installed queue metadata
had not yet been refreshed at that preparation stage.

## Frozen final candidate verification

The parent supplied a frozen candidate containing the complete DINOv3, scoped
campaign and force integration, based on CY
`66279a6e47a1bcb1dd64e1445f4ae5f4c28ea67d`. The source manifest covers 909 files,
including 588 application inputs. Every candidate file matches that manifest after
normalizing only the candidate root package versions from 0.46.0 to the source's
0.45.1 through the candidate's existing `scripts.verify.version_bytes` function.
No runtime/test source discrepancy or dependency-pin change was found. The source
manifest SHA-256 is
`916dde43c6adabeb76af335028afac7ecb4065f695e4005e948d0454fc90348c`;
the concrete candidate file-hash manifest SHA-256 is
`e400bf3a5f1ae417a59c4c2aa35e3fa252bb1744494c4b62d936d5a34342b035`.
Both latest fetched default refs still matched the inspected CY and queue bases.

Normal editable installation resolved the final CY candidate and queue 0.1.9
together in the isolated queue environment, constrained by the existing frozen
CY requirements and approved external dependencies. No `--no-deps` was used.
The optional `pi-heif==1.4.0` decoder was deliberately installed and imported before
the environment was declared ready for native verification. Environment provisioning
then stopped; no package changes are permitted during the parent's native runs.

| Final candidate check | Result |
| --- | --- |
| Normal paired installation | Exit 0 |
| `uv pip check --python .venv/bin/python` | Exit 0; installed requirements compatible |
| Candidate and queue source/installed versions and import paths | Exit 0; CY 0.46.0 / queue 0.1.9, requirement `>=0.38,<0.47` |
| `ruff check .` | Exit 0 |
| `ruff format --check .` | Exit 0 |
| `mypy .` | Exit 0; 70 source files |
| `lint-imports` | Exit 0; 2 kept, 0 broken |
| `cy-queue --help` | Exit 0 |
| Markdown and local-link check including new untracked task documents | Exit 0; 35 Markdown files, 0 issues |
| Complete ordinary queue suite, CPU numeric libraries capped at two threads | Exit 0; 583 passed, 7 physical opt-ins deselected, 19 upstream deprecation warnings in 138.10 seconds |

Raw results, metadata and manifest binding are retained in the parent task's
dated evidence under `queue/final046-*`; the candidate source remains unchanged.
Physical DDP/GPU opt-ins and the parent's native training/forced catalogue gates
are separate evidence and are not established by these controlled queue checks.

All queue verification processes completed. The environment remains frozen for
the parent's native verification; no installation or package changes occurred
after its ready notification. Fresh review and final actual post-hook identity
checks remain open parent gates, not implied successes from this candidate pass.

## Preserved preparation branch — 2026-11-06

The 0.1.9 preparation was moved onto current `main` (`29d2284`) as branch
`prep/cy-046-compatibility`. It is not merged into `main` and makes no release
claim. CY master `b07aa33` now contains the force/DINOv3 source, and still reports
version 0.45.1 because no CY release was made.

Against that CY source, in one isolated environment, both checks passed:
- normal editable installation and `uv pip check`;
- the full ordinary queue suite: 583 passed, 7 physical opt-ins deselected.

Ruff, format, strict mypy (70 files), both import contracts and `cy-queue --help`
also passed. Current `main` 0.1.8 passed the same checks against that CY source.

The paired check against the eventual CY 0.46.0 release, the fresh review and
delivery remain open, as listed above.
