# Proposed CY 0.41 / queue 0.1.2 verification

Date: 2026-10-26. See the [plan](plan.md) and [architecture record](architecture.json).
This prepares a compatibility change; it does not release or operationally install it.

## Concrete version proposal

CY feature 006 proposes CY 0.41.0. The current queue requirement
`clearml-yolo>=0.38,<0.41` rejects that version. The queue's documented package-fix
procedure requires a version update, so its next patch proposal is 0.1.2.
The tested queue bound is `clearml-yolo>=0.38,<0.42`: the lower bound is retained,
0.41 is admitted, and the next untested minor remains excluded.

Real source metadata remains CY 0.40.0 and queue 0.1.1 by explicit task instruction.
Only isolated source snapshots carry proposed versions. Queue has no lockfile;
none is introduced. The eventual real version update and final pair check remain
part of the parent's release workflow after feature acceptance.

## Exact source snapshots

Both bases matched inspected remote default-branch refs:

| Source | Base commit | Captured nonignored files | Source-manifest SHA-256 |
| --- | --- | --- | --- |
| CY | `9fd2294ab219c534fcce87b59eea7b56e9d01173` | 685 | `a4169d36a838ed62fd1946a99db46e612e2504575b7ee3bf6246fe7037ba2dff` |
| Queue | `9a6fccd86b8958a77809e4d2e7e2cc178d0a73ee` | 89 | `7558f5db7f7044fdd8155dc8a07fd4fab7e8da8ded9b3304f832e1048a651dd7` |

The capture copied tracked and untracked nonignored files, preserving current dirty
feature implementation, package YAML, tests and symlinks. Source hashes were checked
before and after each copy to reject a racing edit. It included the new eleven-case
queue null-batch regression. It did not substitute HEAD-only source for the dirty tree.

The existing approved external source checkouts were copied without modifications:
`digital-metrics` at `6e801be1564dce458294eb23592cc1aa0939c4d9` and
`report-generator` at `d10aa395d08f738e92e04e076cee93b3a993bf8f`.
CY's complete local `[tool.uv.sources]` section was preserved, resolving those paths
inside the isolated snapshot. No dependency source revision changed.

A byte-level manifest audit found only these snapshot normalizations:

- CY `pyproject.toml`: root version 0.40.0 → 0.41.0.
- CY `uv.lock`: only the root CY package version 0.40.0 → 0.41.0.
- Queue `pyproject.toml`: root version 0.1.1 → 0.1.2 and CY upper bound 0.41 → 0.42.

Parsed TOML comparisons confirmed no other metadata or lock dependency change.
After all checks, a second comparison found no drift in current CY source, tests
or check configuration. Queue differed only by the approved real upper-bound
change. Thus the tested execution files still matched the current working trees.

## Commands and results

All commands used `CUDA_VISIBLE_DEVICES=''`. Python was 3.12.13, uv was 0.11.32.
The task-owned source snapshots and isolated environment were created under
CY's ignored `.tmp/queue-proposed.sTabGJ/`. Commands below use `ROOT` for that
absolute directory and run from `ROOT/sources/clearml-yolo` unless stated otherwise.

```bash
CUDA_VISIBLE_DEVICES='' uv export --frozen --no-hashes --no-emit-project \
  --format requirements-txt --output-file ../../requirements.txt
CUDA_VISIBLE_DEVICES='' uv venv --python /path/to/prepared/python ../../venv
CUDA_VISIBLE_DEVICES='' uv pip install --python ../../venv/bin/python \
  -r ../../requirements.txt -e . -e ../cy-queue
CUDA_VISIBLE_DEVICES='' uv pip check --python ../../venv/bin/python
```

Before widening the snapshot bound, the same install with `--dry-run` rejected
the proposed versions with exit 1 and an unsatisfiable `clearml-yolo>=0.38,<0.41`
requirement. With the proposed bound, normal resolution and installation succeeded
for 282 packages. No `--no-deps`, dependency override, operational environment update
or package publication was used.

Installed package metadata and actual imports pointed to the snapshots, with exact
CY 0.41.0 and queue 0.1.2 source/installed agreement. The installed queue requirement
admitted 0.41.0 and rejected 0.42.0. `uv pip check` reported all packages compatible.

From the queue snapshot, using `ROOT/venv/bin/` executables:

| Gate | Result |
| --- | --- |
| Normal proposed-pair resolution and installation | Passed |
| Dependency consistency | Passed: 282 packages checked |
| Exact source/installed proposed metadata | Passed |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed: 81 files already formatted |
| `mypy .` | Passed: 68 source files |
| `lint-imports` | Passed: 2 kept, 0 broken |
| `python -m pytest -q` | 512 passed, 7 physical GPU cases deselected, 4 warnings in 125.81 s |
| `cy-queue --help` outside the source checkout | Passed |

The full suite includes package metadata/import checks, pipeline/train composition,
the eleven null-batch/allocation cases, architectural negative cases, and owned
queue process/lifecycle regressions. Controlled GPU observations do not establish
physical GPU execution or ClearML publication.
The four warnings were the existing hydra-zen/Pydantic `__fields__` deprecation;
there were no automatic schema-matching warnings. The queue task Markdown passed
the maintained CY checker, with two files checked and no issues.

Logs, per-file source manifests, normalization audit and installed metadata are
retained under the ignored task directory. No task-owned process is left running
after checks. The disposable source snapshots and virtual environment were removed
after verification; logs, requirements and per-file manifests remain as evidence.

## Diff and acceptance status

The real queue change is limited to the bounded CY requirement, the previously
added null-batch integration test, and this task's plan/architecture/evidence files.
No runtime module, effect ownership, process protocol, queue record, real package
version, approved external dependency, operational install or remote ref changes.
The installation examples and maintained interface guidance remain accurate; this
dated evidence records the changing version-specific result instead of duplicating
it into evergreen guidance.

Fresh independent review and final architecture acceptance remain parent gates.
The task's plan phase is valid; no acceptance-phase pass is claimed before that
review. This proposed-pair evidence is separate from the earlier historical
CY 0.40.0/queue 0.1.1 check and from physical multi-GPU feature acceptance.

## Frozen-runtime refresh

Date: 2026-10-26. This supersedes the earlier proposed-pair run for execution-source
coverage after CY corrected the lazy worker-ownership observer and the ordering of
GPU telemetry versus birth-validated process scans. Earlier results remain historical.
The final CY physical harness files were settled and included before verification.

Both remotes were fetched again before capture. SSH timed out; a per-command HTTPS
origin URL override succeeded for both without changing persistent remote settings.
CY's `origin/master` and local HEAD remained
`9fd2294ab219c534fcce87b59eea7b56e9d01173`, with latest version tag `v0.40.0`.
Queue's `origin/main` and local HEAD remained
`9a6fccd86b8958a77809e4d2e7e2cc178d0a73ee`; queue had no version tags.

The new capture again copied tracked and untracked nonignored files and symlinks,
checked source hashes before/after copying, and normalized only the proposed root
versions. The real queue upper bound was already `<0.42`, so it required no further
snapshot or real-source change. CY project/root-lock versions became 0.41.0 and
queue project version became 0.1.2 only in the disposable snapshots.

| Source | Files | Original source-manifest SHA-256 |
| --- | --- | --- |
| CY | 690 | `5377905e27a3a244f65ecc8ad8f2c43d883f1e15b9a1fc73422817f5bccc1c4f` |
| Queue | 90 | `74133b0a30f6034139517b78ccd59feb4e60c699469666e66ee55119a239e398` |

Approved external sources remained byte-identical at the revisions recorded above.
CY's full local source-override section and all non-root lock entries were preserved.
The post-check audit found **zero source drift** in CY, queue and both external
sources, including all tests and check configuration. No CY harness-only drift
exception was needed. Snapshot byte differences remained limited to the three
approved version-bearing files.

Using Python 3.12.13 and uv 0.11.32, every command again used
`CUDA_VISIBLE_DEVICES=''`. The commands in the earlier section were repeated against
new task-owned snapshots under CY's ignored `.tmp/queue-proposed-refresh.q6ai4kn5/`.
All commands exited 0:

| Refreshed gate | Result |
| --- | --- |
| Frozen requirements export and isolated environment creation | Passed |
| Normal `uv pip install` of both sources together | Resolved and installed 282 packages |
| `uv pip check` | 282 packages compatible |
| Source/installed metadata and actual import origins | Exact CY 0.41.0 / queue 0.1.2, importing isolated snapshots |
| Installed queue bound | Admits 0.41.0; rejects 0.42.0 |
| `python -m pytest -q` | 512 passed, 7 physical GPU tests deselected, 4 warnings in 122.05 s |
| `ruff check .` | Passed |
| `ruff format --check .` | 82 files already formatted |
| `mypy .` | No issues in 68 source files |
| `lint-imports` | 2 kept, 0 broken |
| `cy-queue --help` from outside both checkouts | Passed |

The ordinary suite again includes all eleven null-batch cases and metadata,
architecture-negative, handoff and process-lifecycle integration coverage. The four
warnings remain the existing hydra-zen/Pydantic deprecation. Physical GPU and
external services were not exercised. The old-bound rejection remains established
by the earlier run; this refresh did not modify the prepared bound to repeat it.

Real versions remain CY 0.40.0 / queue 0.1.1. This refresh changes only task evidence
and the task ledger; no runtime, test, requirement, dependency or version edit was
made. All test processes completed, and disposable snapshots/environment were
removed. Per-file manifests, remote identities, normalization, metadata, source-drift
and command-result reports plus command logs remain in the ignored task directory.
Post-update documentation checks passed (two queue Markdown files and one CY
evidence file, zero issues); architecture plan validation and scoped `git diff
--check` also passed. Parent-owned independent review and final architecture
acceptance remain separate.

## Parent review reconciliation

Fresh independent reviewer `review_pair` accepted the complete queue change with
no blocking findings. It independently passed all eleven null-batch tests, plan
validation and both task Markdown checks with CUDA hidden, then inspected the
refreshed evidence and raw logs. The reviewed test-file hash remained unchanged;
no queue runtime or interface changed. The parent reconciled the bounded metadata,
added test and task-documentation diff into the architecture record. This accepts
queue compatibility preparation only; actual release still depends on CY physical
acceptance and the eventual real-version workflow.

The parent architecture acceptance validator subsequently exited 0; both task
Markdown files passed with no issues. Later CY-only physical-harness fixture and
offline-test corrections did not change installed code, package data, metadata or
queue integration inputs. Their final verification belongs to CY canonical checks.

## Authorized release amendment

Date: 2026-10-27. The earlier preparation-only stopping point above is historical.
The user requested a new release after receiving the physical acceptance gaps.
Queue source version is promoted to the previously verified 0.1.2 proposal, with
`clearml-yolo>=0.38,<0.42` and all runtime/test contracts unchanged. Fresh release
verification is recorded in the companion CY feature 006 evidence file
`specs/006-batch-training/evidence/release-queue.md`. That file records proposed
checks and the final actual-version refresh; no fresh pass is asserted here before
those commands execute. Queue files freeze before that run to protect the parent
canonical verification identity. Existing installation, interfaces and migration
guidance require no change: source-first joint installation, bounded requirements,
coordination and offline upgrade behavior are unchanged. Final release review and
acceptance belong to the parent.
