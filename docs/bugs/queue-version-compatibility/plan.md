# Latest CY compatibility and public source delivery

Date: 2026-10-26. This task follows CY's `queue-version-compatibility` bug workflow.
The user authorized compatible latest packages, a new public queue repository and
a standing paired release check. Preserve the original extraction evidence.

The resolver rejects queue 0.1.0 with CY source 0.40.0 because its requirement ends
at 0.39. Installed CY metadata is also stale (0.39.0). Widen the supported range
through 0.40 after integration checks, bump queue to 0.1.1, and refresh both editable
packages with dependency resolution. Retain the existing 0.38 compatibility floor.

[Architecture](architecture.json) covers packaging and the integration regression.
No runtime modules, process protocols, records, GPU controls or SDK ownership change.
CY 0.40 removed `adapters.runtime.supervision`, which the queue does not import;
check current pipeline/train composition and process/lifecycle callers together.

## Tasks and order

- [x] Record the failing resolver and compatibility regression.
- [x] Update bounded metadata, source installation and paired release instructions.
- [x] Resolve/install both sources together; run dependency, CLI, complete ordinary
  queue, Ruff, format, strict mypy, import-linter and documentation checks.
- [x] Reconcile actual diff and architecture evidence; obtain fresh independent review.
- [ ] Commit 0.1.1, create the authorized public remote and push `main`; verify remote
  identity. CY documentation follows its own hooks and authorized push.

Independent read-only investigation can run alongside parent planning. Parent owns
all writes and verification; independent review follows integrated checks. No GPU
workloads or ClearML publication are needed for this packaging correction. Preserve
external dependency copies and do not publish registry packages or release assets.

## Release invariant

For every future release of either repository, inspect the latest source revisions
of both repositories, install the intended pair with normal dependency resolution,
verify the proposed versions and installed metadata agree, run `uv pip check` and
the full queue suite, and record source SHAs/versions and results before pushing.
Unavailable checks or incompatible bounds block paired release acceptance.
