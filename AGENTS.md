# cy-queue engineering instructions

This package is a CY-specific queue extracted from clearml-yolo. Read
[development](docs/development.md), [interfaces](docs/interfaces.md) and
[migration](docs/migration.md) before changes. Python compatibility and dependencies
are defined by pyproject.toml; source installation shares a prepared environment
with compatible CY. Never assume either package is published on an index.

Keep dependency direction cy_queue → clearml_yolo. Queue core/application have no
filesystem, SDK or subprocess effects. Adapters own storage, locks, GPU probing and
guardians; entrypoint integration owns CY command composition. Preserve shared
record protocols, configuration paths, coordination names, ownership, recovery and
acknowledged handoff. Do not edit CY's shared process/lifecycle interfaces without
cross-package checks. Initializers stay inert and direct CY commands require no queue.

Use the Python project workflow and module architecture planning skills. Record
module/import/effect ownership before implementation, run the configured pytest,
Ruff, strict mypy and import-linter checks, and validate Markdown/links. Substantive
work requires independent review after integrated verification. Real hardware and
ClearML publication claims require explicitly owned live evidence. Preserve unrelated
changes and local overrides; do not bypass hooks or alter shared services.

Write README.md in Russian and other documentation in English. Use Conventional
Commits after verification. Public source lives at
`git@github.com:BuckanovNikita/cy-queue.git`; push verified changes to `main` when
delivery is authorized. No version-tag automation, deployment or registry publication
is established. The initial extraction is recorded in CY feature 003;
docs/architecture.json records its package boundary.

Before every release or delivery of either CY or cy-queue, verify the latest versions
of both together using the [paired release checks](docs/development.md#paired-release-checks).
Check source and installed metadata, normal dependency resolution and queue integration
against the proposed release versions. Incompatibility or unavailable evidence blocks
delivery; a successful check of one package alone is insufficient.
