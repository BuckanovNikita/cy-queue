# Admit verified CY 0.44 compatibility

Date: 2026-10-29. Companion task for CY feature 009.

Queue 0.1.4 requires `clearml-yolo>=0.38,<0.44`, which excludes the
proposed CY 0.44.0 release. Verify the latest remote source pair in isolated
checkouts, then admit only the newly checked minor with `>=0.38,<0.45` and
increment queue to 0.1.5. Future minor 0.45 remains excluded.

The affected interface is distribution metadata in `pyproject.toml`; queue
runtime, command composition, records, ownership, effects and dependency direction
remain unchanged. The [architecture record](architecture.json) maps the boundary
to existing metadata, exact CY caller/negative-edge and inward-import checks.

## Scope and sequence

1. Fetch current source refs and inspect CY changes against latest released 0.43
   source. Confirm the queue integration interfaces in [interfaces](../../interfaces.md)
   are unchanged and the old requirement rejects 0.44.0.
2. Validate architecture planning before editing metadata. Change only queue
   version and its checked CY upper bound in the isolated queue checkout.
3. Once the parent makes the isolated CY candidate environment available, install
   both proposed sources normally with approved external source dependencies;
   never use `--no-deps`. Verify pip consistency, matching source/installed versions,
   requirements and editable origins. Preserve the original operational environment.
4. Run the complete ordinary queue suite, Ruff, formatting, strict mypy, both import
   contracts and installed help. Record opt-in exclusions accurately. Inspect source
   drift and newest default branches before acceptance.
5. Validate scoped Markdown/local links. Existing development, interface and migration
   guidance needs no update if runtime and upgrade protocols remain unchanged.
   Parent owns fresh integrated review, architecture acceptance and delivery.

This bounded task creates no commits, pushes, release tags or GitHub releases.
Physical GPU/ClearML execution and operational upgrades are outside its claims.
Parent CY verification can proceed independently before shared candidate installation;
normal installation and metadata checks precede queue integration verification.
