# CY 0.46 compatibility, 2026-11-06

CY 0.46.0 adds forced batch estimation (`cy-batch-estimate --force`) and official
Hugging Face DINOv3 weight preparation. Its native release hook produced the release
from the previously unreleased `c16dbb1 feat(batch)`. Queue 0.1.8 excludes that release
through `<0.46`, which blocks the paired release check. Verify the new pair and widen
only the tested next-minor bound to `<0.47`. Bump this package to `0.1.9`, following the
source-delivery procedure. There is no queue lockfile, version-tag automation or
registry publication.

## Interface review

`git diff v0.45.1 v0.46.0 -- src` in CY changes none of the 15 CY runtime modules the
queue imports directly; queue tests also import `core.batch_estimation` and
`adapters.runtime.gpu_inventory`, which did change. `core.batch_estimation.SearchSettings`
gained `force`. Ordinary records omit it when serialized, so existing estimate keys are
unchanged. Forced records get distinct keys, and `compatibility_issues` still accepts
them, so worker batch resolution can select a compatible forced record; its
recommendation is labelled `forced/background-sensitive`. DEIMv2 `l`/`x` pretrained
backbones may now come from the gated Hugging Face checkpoint inside the admitted
process. Both effects are documented in [interfaces](../../interfaces.md).

## Architecture and acceptance

Distribution metadata owns the tested CY compatibility range. Runtime imports,
public and shared records, process ownership and admission do not change. The
[architecture record](architecture.json) maps metadata and installed-source
consistency to the existing executable package-boundary checks. The new regression
must fail against the old bound before that bound is edited. Then run, from this
checkout in the shared CY environment: Ruff, format, strict mypy, import-linter, the
complete queue suite, queue help and the documentation checks. Fresh independent
review and the final paired source/installed evidence are prerequisites to delivery.

## Tasks

- [x] Add a regression for the next CY minor and observe it fail against the old bound.
- [x] Widen the tested bound, bump the queue patch version, and update compatibility guidance.
- [x] Install the pair with normal resolution, then run the static, import and documentation checks and the complete queue suite.
- [x] Fresh independent review; commit; push CY master with tag `v0.46.0` and queue `main`; verify the remote refs.
