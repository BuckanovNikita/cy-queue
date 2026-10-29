# CY 0.42 proposed-pair verification

Date: 2026-10-29. Companion acceptance for CY feature 007. The old queue
0.1.2 requirement `clearml-yolo>=0.38,<0.42` rejected proposed CY 0.42.0,
reproduced directly with `packaging.requirements.Requirement`. This is a metadata
compatibility failure, not evidence of a broken runtime interface.

## Scope and isolation

The parent fetched both remotes before capture. Source bases were CY
`0037059dcf8a8ed16582f256b98036480cabd842` and queue
`ae252ed8e633e7548180577739673ff0506e1c0c`. Captured tracked and nonignored
untracked sources include in-progress CY feature 007 and six focused queue tests.
Before/after SHA-256 manifests reject capture races. No operational environment,
worker, shared state or external dependency source changed.

Approved external copies remain digital-metrics
`6e801be1564dce458294eb23592cc1aa0939c4d9` and report-generator
`d10aa395d08f738e92e04e076cee93b3a993bf8f`.

| Captured source | Files | Manifest SHA-256 |
| --- | --- | --- |
| CY | 712 | `4092f8ec45ff1f1471a673e902c33feb03fbc23ea03563d8821249f3e4c808e1` |
| Queue | 93 | `d7f95b6c83d13f9fe105e751d182761c38f38d50a89b8d619febe64eb81eace2` |
| digital-metrics | 129 | `88f5b0d13224e04104e0d63bcb65c8aa23ae2e7084c507fd4293159b0b009272` |
| report-generator | 45 | `f9b58fddd7a33dea362c72fdc1ddda92baaf78bcca8522340a0107584498fdd0` |

Disposable snapshots normalize only CY project/root-lock version to 0.42.0,
queue version to 0.1.3 and its bound to `>=0.38,<0.43`. Parsed TOML equality
checks preserved other version-normalized metadata. CY local uv source overrides
and locked dependency entries remain unchanged. Installs use `UV_LINK_MODE=copy`
and hide CUDA devices. Normal dependency resolution includes all dependencies,
without `--no-deps`; source packages are editable in the isolated environment.

## Checks and interfaces

The six focused tests cover pipeline/train and true/false/filename pretrained
selectors. Composition plus the actual snapshot runner preserve custom model YAML,
pretrained and resume settings and exec the matching CY entrypoint. Forbidden-call
probes reject catalogue preparation before CY execution; no asset/preparation files
are created. They do not execute a model or prove worker-side offline loading.

Normal joint resolution and installation of CY 0.42.0/queue 0.1.3 passed.
Source/installed version equality, isolated source import origins and bounded
compatibility assertions passed from outside the checkouts. `uv pip check`
reported all 282 installed packages compatible. Ruff, format, strict mypy and both
import contracts passed. The focused six-case check also passed before capture.
The full ordinary queue suite passed: 518 tests, 7 physical GPU tests deselected,
4 existing hydra-zen/Pydantic deprecation warnings, in 123.06 seconds. Format checked
84 files; strict mypy checked 69 source files; both import contracts were kept.
Installed `cy-queue --help` passed outside both checkouts. After those checks, real
queue metadata was prepared as 0.1.3 with `clearml-yolo>=0.38,<0.43`.

During the run CY runtime changed in `adapters/assets/http.py`, `hub.py`, and
`resolver.py`, plus `tests/test_hub_assets.py` and `test_model_assets_loading.py`.
Queue drift was confined to this new evidence file; approved externals had no drift.
The passing snapshot is therefore proposed-pair evidence only. A refreshed pair
against final CY source and actual release metadata remains mandatory before delivery.

Task Markdown/local links passed (two files, zero issues), and scoped whitespace
checks passed. Architecture planning validation passed. Check results are attached
to the architecture record; acceptance validation awaits fresh independent review
and the final-source paired refresh.

## Documentation and acceptance boundary

[Architecture](architecture.json) records distribution/interface ownership and reuses
existing exact/negative import contracts. Maintained development, interfaces and
migration documentation were inspected: no changes are needed because source-first
paired installation, immutable snapshots, lifecycle ownership and upgrade procedures
remain accurate. Task-specific proposed versions and observations stay here.

Fresh independent review, final actual-version/source refresh, parent acceptance
and authorized delivery remain separate gates. No commit, tag, operational install,
GPU/stand workload, ClearML publication or release was performed by this subtask.
Raw manifests, normal-resolution logs, command results and retained isolated sources
are in CY's ignored `.tmp/queue-042-pair-d9oqr9sd/`.

## Stable-source proposed-pair refresh

The parent froze runtime source after preserving native Ultralytics settings path
semantics, completing Hub endpoint handling and Drive URL redaction, adding the
related regression checks, and removing the complete local CY uv source section
for its commit procedure. Refreshed nonignored source captures:

| Source | Files | Manifest SHA-256 |
| --- | --- | --- |
| CY | 713 | `e5baf03597e3cd63480460b87f40e90167c4adfa616f615c4e3f2dbf7cd4e03d` |
| Queue | 94 | `f3225e118e1e34714d66a47c02c727fd76808532a91e68e3305c86666f273762` |

The approved external manifests match the original capture exactly. Snapshot
metadata is CY 0.42.0 and queue 0.1.3 with `>=0.38,<0.43`; neither snapshot
contains uv source overrides. The frozen requirement list explicitly selects the
unchanged copied digital-metrics/report-generator sources. Normal resolution and
copy-mode reinstall therefore retain the approved dependencies without operational
installation or `--no-deps`.

Every refreshed check passed: source/installed versions and isolated imports,
`uv pip check` (282 compatible packages), Ruff, formatting (84 files), strict mypy
(69 source files), both import contracts, full ordinary pytest (518 passed,
7 physical cases deselected, 4 existing warnings, 118.61 seconds), and installed
`cy-queue --help` from outside both checkouts.

Audit against this refreshed capture found only a concurrent CY update to
`specs/007-download-weights/native-verification.md`. Queue and both external copies
had zero drift; runtime, tests, dependency metadata and check configuration had no
drift. Initial-capture drift remains preserved separately as historical evidence.
Subsequent task-evidence edits do not change the verified runtime inputs.

The retained `check_actual.py` refreshes exact committed CY project/root-lock and
queue project metadata using `git show`, verifies parsed equality to the tested
proposal, rejects runtime/test/check or external source drift, and repeats normal
resolution and all ordinary queue checks. The parent must run it after release
metadata commits and attach actual source identities and independent review before
delivery. It does not change either operational environment or a source checkout.

## Offline-fixture refresh and later readiness regression

Refreshed sources again after the parent isolated routine CY pipeline/replay tests
from automatic catalogue downloads. CY capture remained 713 files with manifest
`6739919b3900b91f5cb32aab47945ec99641e0f77ab44ec2703c14edfeebdc2f`;
queue remained 94 files with manifest
`9f4523e8deb1a67cc2094d0b323560dc1050d979d11886c38331ab5cc57d2c38`.
Separate implementation-only manifest identities were retained for 300 CY source
files (`e8ee652ade0b0d12d1d6fce32b078077f91224c95a782395fd2d7bf20ea600e3`)
and 32 queue source files
(`47d9437b815c43ddff323d93f08f54437b86a553cc329409c7e644f3b8f1ffa0`).

Normal joint resolution/reinstall, pip check, exact source/installed metadata,
Ruff, format, strict mypy, both import contracts and installed CLI help passed
again. Full ordinary pytest passed: 518 passed, 7 physical cases deselected,
4 existing warnings in 118.63 seconds. At run-end the only drift against this
capture was CY `tests/test_hub_assets.py`; no implementation, queue or approved
external source drift had occurred at that audit.

The parent then identified a separate HF readiness case: cached weights without
required config metadata must not be considered complete on a later attempt.
A focused regression/fix is in progress. This result therefore remains historical
proposed-pair evidence; the next production-stable source needs a final paired
refresh. No final current-source acceptance or delivery is claimed. Raw results
use the `fixture-refreshed` prefix in the retained evidence directory.

## Final HF-readiness refresh

After the HF config-readiness fix and its focused regressions passed, captured
stable runtime again with the three offline routine-test fixtures included.

| Source | Files | Manifest SHA-256 |
| --- | --- | --- |
| CY | 713 | `378e941bf276fad27ca9e136690879fa8ad3c0e209b80695c6a1ed907f50745c` |
| Queue | 94 | `04104f4f54ef4003d81b8a7947c4f92a83e7a64610883f4a90d68e91997c44af` |

CY implementation-only manifest identity is
`c8431baacf55e4b6932bba6c2ca7c61fd97be5911af7fd06e0bf4ce2a254d78d`;
queue implementation identity remains
`47d9437b815c43ddff323d93f08f54437b86a553cc329409c7e644f3b8f1ffa0`.
Approved external source manifests remain unchanged.

All checks passed again: normal copy-mode joint resolver/install, exact proposed
source/installed CY 0.42.0 and queue 0.1.3 metadata, isolated imports, pip check
(282 compatible packages), Ruff, format (84 files), strict mypy (69 source files),
both import contracts, full ordinary queue suite (518 passed, 7 physical cases
deselected, 4 existing warnings in 118.16 seconds), and installed CLI help outside
both checkouts. Logs use the `readiness-refreshed` prefix.

Post-run audit against this capture found only CY documentation/evidence changes:
`docs/model-assets.md`, feature `tasks.md` and `verification.md`. The model-assets
change clarifies pinned-commit native config repair without redownloading valid
weights. Runtime, tests, package/dependency metadata and check configuration did
not drift; queue and approved external sources had zero drift. Portable usage and
evaluation now state that cached weights require valid native `config.json` at the
actual snapshot commit. Documentation/link and collection Markdown checks passed.

Final current proposed-pair compatibility is verified. Exact committed release
metadata refresh and fresh independent review remain parent-owned delivery gates;
this record does not claim either has been completed. Retained `check_actual.py`
uses this final capture for its runtime/test/check/external drift guard.

## Final isolated feature-007 proposed pair

Concurrent feature 008 work subsequently required freezing feature 007 separately.
The parent selected an isolated feature-007 release checkout at the same CY base
`0037059dcf8a8ed16582f256b98036480cabd842`, excluding feature 008 entirely.
After fresh review corrections to HF SDK logging redaction, cache publication and
preparation failure handling, the final proposed pair was captured from that isolated
CY source and the actual queue source. Original concurrent CY runtime was not an
input; approved external dependencies retained their authoritative unchanged sources.

| Source | Files | Manifest SHA-256 |
| --- | --- | --- |
| Isolated CY feature 007 | 716 | `c34c4b274f3b391a126a4196258c0823d051187f60684da01d6735dacfd44254` |
| Queue | 94 | `89374b89569557fa34545f5d23083d457483ef0fe51e55573fe6b4f2d4e3152e` |

The capture validates exact Git inventory ownership for every source and rejects
feature-008 specification paths. No feature-008 files entered the snapshots.
Normal copy-mode source installation resolved CY 0.42.0 and queue 0.1.3 with the
bounded `>=0.38,<0.43` requirement. Source/installed metadata and isolated imports
passed; pip check found 282 compatible packages. Ruff, formatting (84 files), strict
mypy (69 source files), both import contracts and installed CLI help all passed.
The full ordinary queue suite passed: 518 tests, 7 physical cases deselected,
4 existing warnings, in 121.22 seconds. Logs use the `isolated-final` prefix.

The final audit found **zero drift in all four captured sources**: isolated CY,
actual queue, digital-metrics and report-generator. Only the private paired
snapshot/environment was installed or modified. The isolated canonical-verification
environment and its immutable queue dependency copy were left untouched.

This supersedes original-checkout proposed-pair evidence for final feature-007
acceptance. Parent fresh-review/architecture records and exact committed-release
metadata checks remain open. `check_actual.py` requires this isolated CY capture,
reads committed metadata from its release HEAD and actual queue HEAD, guards runtime
and dependency drift, and repeats normal paired checks after commits. No commit,
release or operational installation was performed by this subtask.

## Approved-code final proposed pair

After the final native diagnostic/progress corrections received fresh independent
approval, repeated the complete pair with isolated feature-007 CY and actual queue.
CY capture: 716 files, manifest
`0f66b1f389194c4b60894b91a646731ba401b53ddae31e40059bbeff42d56362`.
Queue capture: 94 files, manifest
`67cb6dc51b16ba3b3d5b0cdeecf4189934967e18771aa6d4b4f4156c62f301d3`.
Approved external revisions/manifests are unchanged; feature 008 remains excluded.

All proposed CY 0.42.0 / queue 0.1.3 checks passed: normal copy-mode dependency
resolution/reinstall, exact source/installed metadata and isolated import origins,
pip check (282 compatible packages), Ruff, format (84 files), strict mypy (69 source
files), both import contracts, installed CLI help, and the full ordinary queue suite
(518 passed, 7 physical cases deselected, 4 existing warnings, 122.27 seconds).
Logs use the `approved-final` prefix in the retained private paired directory.

Run-end audit found only concurrent isolated CY feature `verification.md` prose
changes. Runtime, tests, package/dependency metadata and check configuration had zero
drift; queue and approved externals had zero drift. Canonical CY's separate
environment and immutable queue copy were untouched. Subsequent queue review and
architecture evidence edits below do not change the verified runtime/package inputs.

The [review record](review.md) records full-scope review without queue findings and
fresh closure of related CY diagnostic findings. Queue architecture acceptance and
documentation checks follow that accepted review. Exact committed-release metadata
checks remain a separate delivery gate after the parent's authorized commits.

Final queue acceptance-record validation passed after the accepted review was
attached. Markdown/local-link checks passed for all three task documents, and
`git diff --check` passed. The acceptance validator confirms record completeness;
it does not replace final committed-source paired checks or authorize delivery.
