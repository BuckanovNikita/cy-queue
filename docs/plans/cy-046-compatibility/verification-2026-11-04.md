# CY 0.46 compatibility verification, 2026-11-04

Historical 0.45.0-based closure checkpoint, retained when the 2026-11-05
sequential pairing in [preparation verification](preparation-verification.md) superseded it.

## Scope and source identities

The isolated candidate starts at queue `4cf32f0cd84730aebd3cf930829f80ba47d5af24`
(0.1.8) and prepares queue 0.1.9 with `clearml-yolo>=0.38,<0.47`. The parent supplied
a separate proposed CY 0.46.0 source based on
`8be76e4faaeeb20305f4b9e3be856d8855fc5609`, including the integrated forced-batch
and campaign changes. This is a proposed-source verification checkpoint, not an
actual committed-release or native acceptance claim.

Only queue distribution metadata, its existing compatibility regression,
`docs/interfaces.md` and this task directory change. Queue runtime modules,
snapshots, shared records, configuration, process ownership and admission are
unchanged. The established migration procedure and Russian README installation
guidance remain accurate; they require a verified compatible pair and coordinated
operational upgrades. No original checkout, shared environment or worker was changed.

## Regression and environment preparation

The amended existing boundary regression first failed because `<0.46` rejected
`0.46.0`. Its failing assertion is retained in the private regression log. The
candidate keeps support for 0.45.0, admits the checked 0.46.0 pair and rejects the
still-untested 0.47.0 minor. Full source/installed and integration checks, rather
than the boundary assertion alone, establish the proposed compatibility.

Normal dependency-enabled editable installation of both proposed sources used
Python 3.12.13, copy mode, the CY lockfile's registry versions, both development
groups and the prepared `pi-heif==1.4.0` codec. Approved external sources were
unchanged: digital-metrics `6e801be1564dce458294eb23592cc1aa0939c4d9` and
report-generator `d10aa395d08f738e92e04e076cee93b3a993bf8f`. No `--no-deps`,
shared-site link or external source edit was used. The private environment contains
286 compatible packages; `uv pip check` passed. Source/installed metadata and
editable origins match CY 0.46.0 and queue 0.1.9 exactly.

The private CY candidate manifest covers 555 source/test/check and root metadata
files; its SHA-256 is
`6ac73c4eb7b5c1985d224c072d572d89651607bfc3af98f928242e2a0a851530`.
It identifies the supplied code snapshot independently of the base Git commit.

## Configured checks

From the queue source with the proposed environment selected:

- `ruff check .`: passed.
- `ruff format --check .`: passed, 104 files.
- `mypy .`: passed, 70 source files.
- `lint-imports`: both inward-layer and pure-policy contracts kept.
- `cy-queue --help`: passed with the existing command interface.

The architecture planning validator passed before metadata changes. The complete
ordinary suite then passed: **583 passed, seven physical cases deselected**, 19
Hydra-Zen/Pydantic deprecation warnings, 163.86 seconds, exit 0. This includes the
amended version-bound regression, installed/source identity, allocation-aware
automatic-batch integration, outside-checkout command checks and architecture
negative cases. Deselected physical targets are not counted as passing tests.

All 35 tracked and explicitly supplied new Markdown files passed structure and
local-link validation. The final source-manifest comparison found no changed or
removed CY inputs. Queue runtime files remain identical to the base commit;
inspection of the full tracked/untracked diff confirms only the declared metadata,
test and documentation scope. `git diff --check` passed. Architecture review remains
pending with the parent; passing component checks do not imply final acceptance.

## Acceptance boundaries

Physical GPU/NCCL, multiuser/NFS and live ClearML outcomes are not established by
these checks. The physical suite remains an explicit separate opt-in obligation.
Parent integration, fresh independent review and architecture acceptance precede
delivery. The final committed versions and sources must be paired again after CY
release hooks; candidate installation does not replace that gate. No commit, push,
queue version tag, package publication or operational installation occurred in this
bounded task.

## Independent review checkpoint

Fresh independent review accepted the compatibility-only diff against current
queue `694c12f9c2a1a0064284a69d010e846108d43875`. Source and installed bounds,
all 555 recorded CY inputs, ordinary checks and unchanged queue runtime were
confirmed. Fresh pip consistency, changed Markdown, architecture planning and
whitespace checks passed. The documentation reconciliation on current main is
also present in this candidate.

The review excludes subsequent CY changes and physical acceptance. Architecture
acceptance stays pending until the final integrated CY source is paired again;
this checkpoint does not certify the DEIM Hugging Face fallback under development.

## Final integrated-HF pairing checkpoint

On 2026-11-04, the complete queue checks were repeated after the parent integrated
the final DEIM Hugging Face fallback into the proposed CY source. This supersedes
the earlier checkpoint's source-coverage limitation. CY remains based on
`8be76e4faaeeb20305f4b9e3be856d8855fc5609`; the queue candidate now starts at
`8a40f8e79d11b9134e0633f62eaa0ca142de81d3`. These are working-source identities,
not assertions about final release commits.

The previously resolved environment was reused without installation or changes to
runtime, tests, dependency metadata or the environment. Source and installed
versions still agree on CY 0.46.0 and queue 0.1.9, with editable origins pointing
to their respective candidate sources. `uv pip check` again accepted all 286
packages.

- Ordinary CPU suite: **583 passed, seven physical cases deselected**, 19 existing
  Hydra-Zen/Pydantic deprecation warnings, 140.02 seconds, exit 0.
- Ruff check and format: passed; 105 Python files already formatted.
- Mypy: passed, 70 source files.
- Import contracts: both kept, none broken.
- Command help: passed.

Before and after the checks, inventories of all tracked and non-ignored untracked
files covered 895 CY files and 123 queue files. No files were added, removed or
changed, and Git HEADs, versions and editable origins remained identical. Both
inventory files have SHA-256
`7525b66a009d84e2b6a7c6f6955c1f7fbf64029ce092ff7a2f97d8ba82870a94`.
Raw logs and inventories are retained privately under `.tmp/closure-046/final-hf/`.
This evidence appendix was added after that unchanged-source comparison.

The checkpoint establishes queue CPU integration with the final integrated-HF
candidate. It does not establish physical GPU, native model training, ClearML
publication or actual released-commit acceptance. Parent review, architecture
acceptance and the final release-pair gate retain their separate ownership.
