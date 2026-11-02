# Queue completion-race verification — 2026-11-02

## Implementation and failing observation

Base queue 2fbaed2 (0.1.6) plus current CY 6fcc78c (0.44.6). The required final
pair caught a real queue stale-refresh overwrite: 543 passed, one failed, 7 deselected
in 137.69 seconds. Failed public records and the read-only actual-runtime/store
probe confirmed current completed revision 6 being replaced from stale running 5.
No native cleanup failure or lost lease verification was inferred from that timeout.

The bounded implementer reports an initial deterministic RED run with 10 failed and
9 passed in 0.86 seconds. Both no-claim/dead-claim branches overwrote newer completed,
failed, cancelled, starting and running records. Existing genuine loss cases passed.
After the guard, the expanded 23 regressions plus existing storage/process checks
passed 48 tests in 11.49 seconds. Scoped Ruff/format and strict mypy on all three
owned files passed. These focused results are agent evidence; parent integration
and independent review are separate gates below.

The storage guard compares current revision and state under the existing transaction,
after ownership validation. A stale observation returns the current record with no
publication; an unchanged lost record uses the existing transaction_update path.
Both refresh writes use it. Unchanged terminal records with a dead retained claim
still require recovery. No public update signature, wire field, dependency bound,
lease release, timeout or test selection changed. Patch metadata is 0.1.7.

## Documentation and compatibility scope

Current interfaces document the guarded recovery semantics. README commands/config,
migration protocol and operator actions are unchanged, so those documents need no
new examples or upgrade format. The authoritative portable CY usage source was
refetched at 83982d2: its matched-installation, owner-recovery and coordinated-upgrade
guidance remains valid. This internal concurrency fix restores promised outcomes;
there is no new CLI/shape requiring a companion skill change.

Queue has no configured mutation framework or selected targets; no new framework is
introduced. CY's selected numerical mutation sources/tests/fixtures are unchanged and
do not import queue runtime. Its recorded 433 fresh outcomes remain scoped evidence,
not a mutation claim for this adapter. Queue safety is tested by actual storage
transactions, deterministic interleavings and real-process ordinary integration.

## Parent acceptance

Full proposed-version paired integration, documentation checks, independent review
and architecture acceptance are pending. No push, physical GPU, real multiuser or
live ClearML claim is made by this checkpoint. Both existing failed evidence and
new passing evidence must remain distinguished. Delivery follows queue main commits
only, with no queue tag, GitHub Release object, package assets or registry publication.

## Full parent verification

Normal editable resolution accepted CY 0.44.6 and queue 0.1.7 with exact source,
installed version and import-origin agreement. Pip consistency, queue Ruff/format,
strict mypy over the entire checkout, both import contracts and installed help passed.
The complete ordinary suite passed **567 tests**, 7 physical opt-ins deselected and
19 warnings in 129.25 seconds. This includes the original admission completion case
and all 23 new deterministic regressions. Parent inspected the complete implementation,
new tests, root-version-only metadata and documentation diff. Fresh independent review
and final architecture reconciliation remain pending.

## Independent review finding

Fresh queue_final_acceptance inspected full code/docs and parent logs and returned
fix-first for terminal-snapshot/claim disappearance between initial claim read and
dead liveness. The 567-pass run remains a checkpoint, not final acceptance. Review
also corrected the formatting count to 95 files. No dependency or suite was rerun
by the reviewer. The plan/architecture are amended before the bounded correction;
new claim-snapshot regressions and fresh checks/review are required.

## Claim revalidation correction

The bounded implementer added fresh full-claim comparison after dead liveness and
before conditional public-record recovery. No claim, changed owner/guardian,
generation or discovered identities causes a stale write; a genuinely retained
unchanged claim still reaches recovery. No nested pool/NFS lock was introduced.
Deterministic RED gave 15 failed/23 passed; corrected regression/storage/process
checks gave 63 passed, and the final 38 regressions passed in 0.56 seconds. Scoped
Ruff/format and strict mypy passed. These are implementer-reported focused results;
the parent is refreshing the complete ordinary pair before fresh independent review.

## Corrected complete parent verification

After claim revalidation, normal resolution, pip consistency, exact CY0.44.6 /
queue0.1.7 source/installed/import identity, Ruff, format (96 files), strict mypy
(70 source files), both import contracts and installed help passed again. The
complete ordinary suite passed **582 tests**, 7 physical opt-ins deselected and
19 warnings in **128.66 seconds**. All 38 deterministic regressions and the original
real-process case are included; no timeout or selection rule changed. Earlier
567-case acceptance was superseded by this corrected-source evidence. A fresh
independent final reviewer must assess the correction before delivery.

## Final independent acceptance

Parent separately reran the original admission case plus all new regressions:
39 passed in 1.14 seconds. Fresh read-only queue_corrected_acceptance returned ship
with no blocking findings after inspecting the complete diff, new tests/docs and
related guardian/claim/recovery sequencing. It independently checked the parent
pair logs and whitespace. The previous claim-release finding is resolved without
nested locks or a terminal-state exemption. The reviewer corrected the final formatter
count to 96, as reported by the final raw log. Earlier 95-file observations remain
historical. See [review](review.md). Architecture acceptance and documentation validation
are recorded below before the implementation commit. Remote delivery remains pending.

Parent architecture acceptance validation exited zero. Changed Markdown/local links
(four documents) and final diff whitespace checks passed before commit.

## Source delivery

Implementation commit b976789301d814a4249d3683739b8d6918819a73 (queue 0.1.7) was pushed to main and its remote SHA
was verified after all acceptance gates passed. Committed source/installed versions
and import locations still match CY 0.44.6 / queue 0.1.7; no hook changed metadata.
No queue tag, GitHub Release object, distribution asset, registry publication or
operational installation was created. This final documentation closure changes no
runtime inputs; the parent CY ledger records the paired CY delivery and final refs.
