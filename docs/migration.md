# Coordinated offline upgrade

The extracted distribution changes Python module paths and installation identity.
Its wire record protocol remains `shared-cy-queue-v1`. Existing records, history,
configuration locations, coordination roots, lock namespaces and ownership evidence
must remain intact. Do not delete queue state to make an upgrade pass.

1. Coordinate all users of the shared queue and host coordination root. Stop submission
   and let active work finish, or use the existing owner cancellation/recovery procedure.
   Confirm guardians and their owned descendants have completed cleanup. Do not kill
   unrelated processes or infer cleanup solely from stale metadata.
2. Stop each owner's worker before changing either installation. Retain a backup of
   durable records and the exact old environment for diagnosis. Do not mix old/new live
   workers or run two copies against the same ownership records during upgrade.
3. Prepare approved dependencies externally for offline installation. Install compatible
   CY from source first, then `cy-queue` into the same Python environment. Both package
   versions/code and the interpreter environment contribute to snapshot identity.
4. Keep the existing `queue.toml`, metadata root and coordination root. The default
   settings path remains `clearml-yolo/queue.toml`; extraction does not rename it.
5. Pending snapshots from the changed installation must be cancelled and resubmitted
   using the new environment. They are retained as history and are never silently
   rewritten or automatically retried. Uncertain jobs still require owner recovery.
6. Verify `cy-queue config`, `cy-queue list --json` and `cy-queue submit --help`, then
   restart the owners' workers. New submissions use `pipeline` unless `--command train`
   is provided. Full native/task publication verification is separate from CLI checks.

Rollback restores both package installations together after workers are stopped and
active cleanup is verified. Preserve all records created since upgrade; changed
snapshots again need explicit cancellation/resubmission rather than identity editing.
Neither source checkout is assumed to be published on PyPI. Offline delivery consists
of source and externally prepared dependencies, not registry publication by this tool.

## Configurable memory threshold

Queue 0.1.6 adds optional `queue.max_used_memory_gib`; existing configuration files
retain the 2.0 GiB default. Stop and replace workers through the coordinated procedure
above, then inspect the effective configuration and the restarted worker's startup
log. Editing a file alone does not change a live worker or guardian's policy.

The shared `shared-cy-queue-v1` public records, snapshots and lock protocol are
unchanged. The private `GuardianPayload` adds a positive finite
`max_used_memory_gib` field. New code reads historical private payloads that omit it
with the previous default of 2.0, so startup recovery keeps its original policy.
New workers persist their selected value and guardians do not reread configuration.
Older binaries reject the new private field and configuration option; do not mix
versions. Before a downgrade, finish active work and resolve any uncertain new
private payloads with the compatible newer installation. Retain the new records
for diagnosis and history; never delete fields or rewrite ownership evidence to
make an older reader accept them. Restore compatible configuration and both
package installations together using the rollback procedure above.
