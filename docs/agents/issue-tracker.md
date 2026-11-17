# Issue tracker: Linear and GitHub PRs

Use Linear team `SIP`, project `cy-queue`, for implementation plans, acceptance criteria,
dependencies, ownership, discussion and status. Resolve an issue by its Linear identifier
or URL. GitHub PRs in `BuckanovNikita/cy-queue` own implementation review and delivery.
Link issues, PRs and evidence in both directions.

The product contract stays in this repository: the
[product specification](../../specs/baseline.md) and [interfaces](../interfaces.md).
A change to behavior updates them in the same PR; an issue never replaces them.

## Planning and acceptance

Each issue records the outcome, scope, implementation plan where needed, blockers,
compatibility constraints, acceptance criteria and selected verification. Discover
current source and configuration before relying on historical claims.

Use the team's lifecycle states: Backlog, Todo, In Progress, In Review, Done, Canceled,
and Duplicate. Readiness labels follow [triage guidance](triage-labels.md). A ready label
does not override dependencies. Start dependent implementation only when its prerequisite
is implemented and verified on the branch used as its base; merge dependencies remain.
Move to In Review when implementation and required verification are ready for review.

Record evidence in the issue and the PR, with source/environment identities, actual
checks and outcomes, exclusions, reuse reasons and remaining limitations; this repository
keeps no evidence directory. Mark an issue Done only after its changes reach `main` and
its acceptance criteria are satisfied. Verification-only work completes on its recorded
acceptance outcome.

## PR grouping and authorization

Default to one branch and PR for a cohesive feature, including multiple tickets when
appropriate. Link every included issue and map its acceptance criteria to implementation
and evidence. Keep those issues open until the shared PR merges and criteria are met.
Use stacked PRs when separate review units or dependency sequencing benefit delivery;
record the grouping in Linear before implementation. Routine grouping needs no approval.

Agents may push task branches and create PRs. Humans merge PRs. Use Conventional Commits,
the existing SSH remote, and task-owned branches; never deliver by merging locally into
`main` or pushing `main` from an agent session. Explicit session restrictions take
precedence.

Human merges to `main` authorize automatic version commits and annotated tags through
the [release workflow](../development.md#delivery-and-releases). The PR title and the
branch commit messages decide the version: give each an accurate Conventional Commit
type, with `fix` or `feat` for every change to the installed package. Never edit
`project.version` or `CHANGELOG.md` by hand. After pushing a task branch, confirm that the
remote branch points at the verified commit. Complete verification, independent review and the
[paired release checks](../development.md#paired-release-checks) before merge; record
the workflow result and remote tag identity in the linked issue when a release is produced.

For stacks, the first PR targets `main`; descendants target their parent branches.
Link parent PRs and merge order. Review incremental diffs and verify the cumulative
feature delta against `main`, recording base/head SHAs. Draft PRs may contain incomplete
work; required deferred verification blocks merge readiness. Independent review follows
integrated verification for behavior, interface, dependency, security and policy changes.

Humans merge stacks bottom-up. Retarget or restack remaining branches after each merge,
inspect the resulting diffs, reassess evidence applicability, and repeat affected checks
and independent review. Use force-with-lease only for task-owned branch rewrites. A canceled
prerequisite requires replanning or removing dependent work, never silently bypassing it.
Do not assume GitHub checks, branch protection or Linear automation is configured.
