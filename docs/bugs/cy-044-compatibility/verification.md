# CY 0.44 proposed-pair verification

Date: 2026-10-29. Companion task: [plan](plan.md).

## Scope and identities

Current default branch identities were fetched and rechecked remotely: CY master
`0b5f3f725fd65c760f21ea428faf2bbb5e2b6376` (0.43.0) and queue main
`4e18ec622121c228474dd454b0b46d4af902cf92` (0.1.4). The proposed CY source
adds feature 009 to that latest CY base. All 17 CY modules imported directly or
used as explicit process targets by queue are byte-identical to that base,
including command composition, runtime lifecycle and process supervision owners.
Only CY asset preparation/Hub integration and new bundle modules change runtime
behavior. Existing queue submission isolation tests cover no preparation effect.

The isolated queue patch changes only package version to **0.1.5** and the bounded
requirement to `clearml-yolo>=0.38,<0.45`. Its previous bound rejects 0.44.0;
the candidate admits 0.44.0 and rejects 0.45.0. Runtime source and tests remain
unchanged. Architecture planning passed validation before the metadata edits.

A separate CY source snapshot captured 801 tracked/nonignored paths with verified
before/after hashes. Only its project and root lock versions were normalized to
0.44.0; parsed project metadata equality was asserted with the version restored.
The parent's integration checkout and environment were preserved. Approved
external checkouts remain clean and at their original revisions:

- digital-metrics: `6e801be1564dce458294eb23592cc1aa0939c4d9`.
- report-generator: `d10aa395d08f738e92e04e076cee93b3a993bf8f`.

## Resolution and checks

A separate Python 3.12.13 environment installed the proposed pair and both approved
editable external dependencies using normal resolution, without `--no-deps`.
`CY_PAIR`, `QUEUE_PAIR`, `PAIR_ROOT` and `PAIR_PYTHON` below denote the task-owned
source snapshots and environment:

```bash
uv export --frozen --no-hashes --no-emit-project --no-emit-package digital-metrics --no-emit-package report-generator --format requirements-txt --output-file "$PAIR_ROOT/requirements.txt"
uv venv --python 3.12.13 "$PAIR_ROOT/venv"
uv pip install --python "$PAIR_PYTHON" -r "$PAIR_ROOT/requirements.txt" -e "$CY_PAIR" -e "$QUEUE_PAIR" -e "$CY_PAIR/external/digital-metrics" -e "$CY_PAIR/external/report-generator"
uv pip check --python "$PAIR_PYTHON"
```

Normal installation resolved 285 packages. `uv pip check` passed. An independent
metadata probe compared source/installed versions and normalized base requirements
for all four packages and checked each editable `direct_url.json` origin. External
origin paths were resolved through the approved source symlinks. CY and queue
imports originate from their proposed isolated sources. All assertions passed.
The first probe correctly exposed optional-extra metadata and lexical symlink
origin differences; the corrected comparison explicitly handles both without
changing package sources or installed metadata.

From the isolated queue source, with physical CUDA devices hidden:

```bash
CUDA_VISIBLE_DEVICES= "$PAIR_PYTHON" -m pytest -q
"$PAIR_ROOT/venv/bin/ruff" check .
"$PAIR_ROOT/venv/bin/ruff" format --check .
"$PAIR_ROOT/venv/bin/mypy" .
"$PAIR_ROOT/venv/bin/lint-imports"
"$PAIR_ROOT/venv/bin/cy-queue" --help
```

Ruff and formatting passed. Strict mypy passed for 69 source files. Both import
contracts passed (67 files, 205 dependencies). Installed CLI help passed.
The complete ordinary queue suite passed: **518 passed, 7 deselected, 19 upstream
hydra-zen/Pydantic deprecation warnings** in 134.51 seconds. Physical opt-in tests
were deselected and are not reported as passing. A separate train/pipeline
composition probe passed with documentation imports blocked and catalogue
preparation functions replaced by raising guards.

## Captured inventories and limits

Private task evidence retains the source inventory, real interface byte comparison,
proposed-pair metadata and logs. SHA-256 values identify canonical sorted
path-to-hash inventories before this verification prose and result annotations:

| Source | Tested inventory SHA-256 |
| --- | --- |
| CY candidate | `378730744253f7e2b527e7c52e7499a3d28eaed905083113a35f5a6ed6c97873` |
| Queue candidate | `afaee7123c1197d341bf29686197ace3c194b57ed6fc40d008c2a61f6ac49fda` |
| digital-metrics | `b9f31d58acb40c4c000851a077de4a0d68dac61cbe3c82e96aa8473086f1b1f4` |
| report-generator | `c1e84168ab74a0f898048af777c77fb3e5b1eaa4ac88f1db6ad7d462acfab418` |

Existing development, interface and migration guidance was reviewed. Its source-first
installation, bounded compatibility, dependency ownership and coordinated upgrade
procedure remain accurate; no evergreen prose change is required. The task adds
this dated evidence and the adjacent plan/architecture only.

All inventoried CY, queue and approved external files remained unchanged after
the checks. New verification prose and architecture result annotations are
acceptance bookkeeping, outside the tested runtime/metadata diff. Log SHA-256
values and proposed metadata identities are retained alongside the inventories.
Task Markdown/local-link checking passed for both new Markdown files.

Parent fresh integrated review, architecture acceptance and final committed-pair
refresh remain delivery requirements. This work makes no physical GPU, ClearML
publication or operational upgrade claim, and makes no commit or push.

## Final integrated-source pair refresh

Date: 2026-10-29. A fresh bounded verification refreshed the existing isolated CY
snapshot from the parent's integrated delivery candidate after the Artifactory
runtime, protocol fixtures, tooling-boundary contract and Russian tutorial were
integrated. The snapshot contains 803 inventoried paths. Only the project and root
lock versions were normalized from 0.43.0 to proposed 0.44.0; parsed project metadata
was otherwise equal, and both approved external dependency symlinks were preserved.
Queue metadata was not edited. The operational environment and parent's environment
were not changed.

Using the existing private Python 3.12.13 pair environment, the frozen dependency
export and normal combined editable installation were rerun for the updated CY,
queue and both approved external sources. No `--no-deps` bypass was used. Installation
resolved 285 packages, and `uv pip check` passed. The independent metadata probe
again confirmed matching source/installed versions and base requirements, editable
source origins and actual package import paths. The installed proposed pair is
CY 0.44.0 with queue 0.1.5; the bounded requirement also rejects CY 0.45.0.

The queue commands listed above were rerun against that installation. Results:

- Complete ordinary queue suite: **518 passed, 7 deselected, 19 upstream
  hydra-zen/Pydantic deprecation warnings**, in 125.42 seconds. Physical GPU acceptance
  remained deselected.
- Ruff check and formatting passed; strict mypy passed for 69 source files.
- Both import contracts passed, analyzing 67 files and 205 dependencies.
- Installed `cy-queue --help` passed.
- Installed final-source Artifactory and Hub fixture suites passed: **43 passed**
  in 9.55 seconds. The Artifactory fixture restricts Requests transport to loopback;
  these checks establish client routing, per-host authentication, integrity/fallback
  and credential-boundary behavior. They establish no live Artifactory connectivity,
  credentials, permissions, TLS handshake or server-side cache state.

Private logs, executable metadata probe, command list, source inventories and log
hashes are retained under the existing task-private evidence directory's
`final-source-refresh/` subdirectory. Inventory hashes use sorted compact JSON
path-to-hash/link mappings, consistently with the initial verification:

| Tested source | Final refresh inventory SHA-256 |
| --- | --- |
| CY 0.44.0 candidate | `d0bf4bc57506287d24611e98424786669aa4d904e0cbe111e1c2afbb9d258544` |
| Queue 0.1.5 candidate | `222a1fcc26f7ceb3e45c4681bc633b8d3990d97538cdd9af0d7233fb5c88bdd4` |
| digital-metrics | `b9f31d58acb40c4c000851a077de4a0d68dac61cbe3c82e96aa8473086f1b1f4` |
| report-generator | `c1e84168ab74a0f898048af777c77fb3e5b1eaa4ac88f1db6ad7d462acfab418` |

All four tested inventories were unchanged after the checks. Approved external
checkouts remained clean at the revisions recorded above. The parent delivery
candidate subsequently changed only feature architecture, task-ledger and verification
bookkeeping; all captured runtime, tests and user-guide bytes still matched the
refreshed snapshot. This appended evidence is later acceptance bookkeeping and is
outside the tested queue inventory.

Parent architecture acceptance, final review recording and release remain separate.
Once native hooks create the actual CY 0.44.0 source metadata, normally reinstall
both final sources and approved external dependencies into the private pair environment,
rerun `uv pip check`, and run the retained metadata probe with those final source
roots. That final metadata/origin refresh has not been run before the release exists.
This bounded verification made no commit, push, operational upgrade, model upload,
ClearML publication or live Artifactory request.

## Independent review and architecture acceptance

Fresh read-only companion review returned ship with no substantive finding after inspecting the complete metadata/documentation diff, actual resolution and static/integration logs, exact CY interface ownership and documentation. Parent reconciled the two metadata edits and three task documents; no runtime or dependency source change is present. Architecture acceptance is recorded against these executed final-source pair checks. Actual release-source version/origin refresh remains required before pushing.

## Actual release-source pair verification

Date: 2026-10-29. The native CY release hooks completed, producing actual CY 0.44.0
commit `8f95e095508ab48e523628f4fd2d106126fa28bc`. Its delivery checkout was clean,
and the local annotated `v0.44.0` tag peeled to that exact commit. This verification
used that actual release checkout directly, replacing the proposed snapshot as the
private pair environment's editable CY origin.

The queue candidate remained source base
`4e18ec622121c228474dd454b0b46d4af902cf92` with version 0.1.5 and requirement
`clearml-yolo>=0.38,<0.45`. The retained exact `pyproject.toml` metadata patch has
SHA-256 `166a8422960c53ee4f0ef3902c92e15cb8085405bd2b0c39d485803f50fd1add`.
No queue runtime source was changed.

The actual CY source was compared with the preceding proposed-pair inventory.
All runtime modules, tests, scripts and user guides were byte-identical; normalized
project/root-lock release versions already matched. Differences were limited to
`CHANGELOG.md` and feature 009 architecture, specification, task-ledger and verification
bookkeeping. Approved external source files and revisions remained unchanged.

The frozen requirement export, normal combined editable installation of the actual
CY source, queue candidate and approved external sources, `uv pip check` and the
retained source/installed metadata probe were rerun. Normal resolution admitted
285 packages without `--no-deps`; all checks passed. Installed CY 0.44.0 now imports
from the actual release checkout, and queue 0.1.5 imports from its candidate checkout.
All four installed versions, base requirements and editable origins matched their
actual source roots; the queue bound still rejects CY 0.45.0.

From the queue candidate, with physical CUDA devices hidden, the complete ordinary
suite passed again: **518 passed, 7 deselected, 19 upstream hydra-zen/Pydantic
warnings**, in 122.41 seconds. Installed `cy-queue --help` also passed. The previous
static/import results apply to byte-identical runtime and checking sources; physical
GPU acceptance remained deselected and no live Artifactory check was performed.

The retained `actual-release-source/` private evidence contains exact release/tag
identities, metadata patch, installation and consistency logs, installed/source
origins, commands, complete inventories, proposed-to-actual comparison and log hashes.
All four tested inventories were unchanged after these checks:

| Actual tested source | Inventory SHA-256 |
| --- | --- |
| CY release source | `c7523a99785cf8fe218a54ed2225ef53a899815f118b25eae2827090da7ed21c` |
| Queue candidate | `bebc0523d8310be5b28c44f20d7dcc48db3a568fdf25ccf0174c3b5c0231a3e7` |
| digital-metrics | `b9f31d58acb40c4c000851a077de4a0d68dac61cbe3c82e96aa8473086f1b1f4` |
| report-generator | `c1e84168ab74a0f898048af777c77fb3e5b1eaa4ac88f1db6ad7d462acfab418` |

CY and both approved external checkouts remained clean. This appended evidence is
subsequent queue acceptance bookkeeping outside the tested inventory. The actual
release-source metadata/origin refresh required above is now complete. Queue commit,
remote delivery and parent acceptance recording remain parent-owned. This bounded
verification made no CY source edits, commits, pushes, live Artifactory requests,
ClearML publication, operational environment changes or asset uploads.
