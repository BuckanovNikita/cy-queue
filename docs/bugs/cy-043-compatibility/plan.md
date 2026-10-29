# Admit verified CY 0.43 compatibility

Date: 2026-10-29. Companion release task for CY feature 008.

The current queue 0.1.3 requirement `clearml-yolo>=0.38,<0.43` rejects the
proposed CY 0.43.0 release. The existing CY 0.42.0 tag already contains feature
007; feature 008 adds a local documentation command and refactors command schema
declarations while preserving their values. Do not reuse the earlier 007-only
paired result as evidence for the new pair.

The proposed fix admits only the newly verified minor with `>=0.38,<0.44` and
increments queue to 0.1.4 according to the package-fix version policy in
[development](../../development.md). Existing queue runtime, protocols, command
set, shared services and installed operational environments remain unchanged.
[Architecture](architecture.json) records the metadata boundary and reused
executable contracts.

## Inspection and acceptance

Queue composition imports CY Hydra registrations, validators, workflow signatures
and `ClearMLConfig`. CY 008 replaces anonymous registrations with named documented
declarations and adds field descriptions; its compatibility fixtures cover old
schemas, composed defaults, permissive overrides and parser help. Process tree,
lifecycle, storage, bootstrap and workflow invocation interfaces remain the queue
integration owners. New HTTP serving and preview workers must not enter queue
composition. The existing exact import-owner tests and forbidden-edge negative
cases remain authoritative.

1. Confirm current fetched source refs and demonstrate the old requirement excludes
   0.43.0. Capture current integrated CY, queue and approved external sources with
   manifests; retain before/after drift checks.
2. Change only proposed snapshot metadata: CY 0.43.0/root lock version, queue
   0.1.4 and its bounded requirement. Resolve/install normally without `--no-deps`
   in a private environment; compare source/installed versions, requirements and
   import origins and run dependency consistency checks.
3. Run the entire ordinary queue suite, Ruff, format, strict mypy, import contracts
   and installed help. Probe train/pipeline composition with documentation imports
   deliberately unavailable; no physical GPU or remote publication claim follows.
4. Once the proposed pair passes, apply the two queue metadata lines. Record dated
   outcomes and documentation/link checks. Existing interface/migration guidance
   needs no change because dependency direction and upgrade protocol are unchanged.
5. Parent performs fresh integrated review, final committed metadata refresh and
   authorized commits/pushes. Retain the isolated environment until refresh is done.

This bounded work makes no commits or pushes. The parent owns CY integration,
canonical verification and native evidence. Failed checks or missing final review
remain delivery gaps. Preserve prior compatibility history and unrelated changes.
