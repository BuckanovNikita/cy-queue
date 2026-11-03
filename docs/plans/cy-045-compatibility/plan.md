# CY 0.45 compatibility, 2026-11-03

The CY saved-estimate listing feature adds a direct read-only inspection mode and
retains the queue-consumed configuration, process and automatic batch interfaces.
The queue currently excludes the proposed CY minor through `<0.45`; verify the
new pair and widen only the tested next-minor bound to `<0.46`. Update this package
to `0.1.8` as required by the established source-delivery procedure. There is no
queue lockfile, version-tag automation or registry publication.

## Architecture and acceptance

Distribution metadata owns the tested CY compatibility range; runtime imports,
public/shared records, process ownership and admission stay unchanged. The
[architecture record](architecture.json) maps metadata and installed-source
consistency to executable package-boundary checks. The new regression must fail
against the old bound before editing it. Run Ruff, format, strict mypy,
import-linter, the complete queue suite and documentation checks from this
checkout in the parent's isolated CY environment. The parent coordinates normal
editable installation, dependency checking and final CY 0.45.0 metadata; this
bounded task must not mutate that environment. Fresh integrated review and final
paired source/installed evidence are prerequisites to delivery.

## Tasks

- [x] Add and observe a failing proposed-minor compatibility regression.
- [x] Widen the tested bound, bump queue patch metadata and update compatibility guidance.
- [x] Run static/import/documentation checks and the complete ordinary queue suite.
- [x] Parent: verify final installed pair and obtain fresh independent review before commit/push.
