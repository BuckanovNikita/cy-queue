# Development

Use the source-first shared-environment installation in the README. Install the `dev`
group through your externally managed environment together with CY's approved dependencies.
Do not let a resolver replace CY with an index package. Source checkout testing is the
normal verification route; no routine distribution build or package publication is required.

From this repository, with that environment selected:

```bash
python -m pytest
ruff check .
ruff format --check .
mypy .
lint-imports
```

Use `uv run --frozen --no-sync --project /path/to/clearml-yolo <tool>` when deliberately
reusing CY's prepared uv environment; run from this repository so its check configuration
is selected. Dependency installation remains external and the queue does not carry a
lockfile that resolves a nonexistent index release of CY.

The routine suite uses temporary storage, controlled GPU telemetry and real owned
subprocesses. Opt-in `ddp_gpu` tests require explicit physical devices, ClearML project,
output evidence and authorization options exposed by `pytest --help`. They are
user-waived and stay deselected; routine tests do not establish multi-GPU handoff,
cleanup or failure recovery, and no such pass may be claimed without new dated live
evidence. The multiuser
harness additionally provisions temporary Unix identities; inspect its `--help` and
ownership contract before explicit execution. Physical queued scenarios additionally require
an existing valid `queue.toml` (or `CY_QUEUE_CONFIG`) and retain its host coordination
root so real GPU locks still coordinate with other users. They override only the durable
metadata root with the scenario-owned path. Do not change host coordination to bypass
other workloads. The multiuser harness uses controlled devices and test-owned identities.

Cross-repository work requires fresh independent review. Report dated verification
results in the Linear issue and the PR; this repository keeps no evidence directory.

## Paired release checks

Before every release or delivery of **either** repository, verify the latest CY and
cy-queue source revisions together, including the proposed release versions. Delivery
is the human merge of a PR, so complete these checks before that merge. Fetch
both remotes, inspect their default branches/tags and preserve unrelated local work;
do not assume a stale sibling checkout or installed metadata represents the latest.
Coordinate workers and drain active jobs using [migration](migration.md) before
changing an operational environment, or use an isolated prepared environment.

From this checkout, with CY's approved external dependencies prepared:

```bash
uv pip install --python ../clearml-yolo/.venv/bin/python -e ../clearml-yolo -e .
uv pip check --python ../clearml-yolo/.venv/bin/python
uv run --frozen --no-sync --project ../clearml-yolo pytest -q
uv run --frozen --no-sync --project ../clearml-yolo cy-queue --help
```

Run the configured static/import checks above too. The installation tests compare
the source and installed requirements/versions; reinstall after version changes.
Use normal resolution for acceptance, without `--no-deps`, and preserve approved
external source revisions. Report both source SHAs, versions, resolver and queue
integration results, dated, in the Linear issue and the PR. Each repository's release
job sets its next version only after the merge, so check the proposed version before
the human merge of a releasing PR in either repository: the queue's CY requirement must
contain the proposed CY version. Repeat the checks if either PR head, default branch or
proposed version changes before the merge. Incompatible bounds, stale metadata, missing
current sources or failed/unavailable checks block merge and delivery. The CY requirement
declares only a minimum compatible version; raise it when the queue depends on a newer CY
interface and never add an upper bound.

CY's `paired-check` task runs the same pair in a temporary environment; it needs a clean
queue checkout that contains the latest remote `main`.

## Delivery and releases

Work is planned in Linear and delivered through GitHub PRs; follow the
[ticket workflow](agents/issue-tracker.md). Agents commit task-owned changes, push task
branches to `git@github.com:BuckanovNikita/cy-queue.git` and open PRs against `main`;
humans merge. Complete verification, independent review and the paired release checks
before the merge.

A human merge authorizes an automatic release; there is no local release command. The
[release workflow](../.github/workflows/release.yml) handles closed PR events only when
the PR was merged into `main`. Unmerged closures, ordinary pushes and tag creation do
not release. Jobs are serialized without canceling a running release. Each job reads the
current `main` tip with full history and tags; closely spaced merges may share one release.

Python Semantic Release computes the version from the Conventional Commits since the
last `v{version}` tag: `fix` and `perf` raise the patch version, `feat` and, while the
major version is 0, a breaking change raise the minor version. Other types release
nothing, and a run without a new version succeeds without creating a commit or tag. A
squash merge takes its commit message from the PR title, so the title must be a
Conventional Commit of the intended type. Never edit `project.version` or `CHANGELOG.md`
by hand.

`scripts/release.py` runs the tool and requires exactly one new commit that changes only
`pyproject.toml` and `CHANGELOG.md`, with an annotated tag on it, and a version above
the previous `project.version`. A missing baseline tag makes the tool restart from the
first commit; the release then fails without publishing. It then pushes the
commit and the tag atomically with explicit refs, rejects a moved remote tip or an
existing tag, and confirms the published ref identities. It never force-pushes or follows
unrelated tags. A release is that commit and tag only: no GitHub Release object, asset,
package, deployment or registry publication.

The job needs the repository-scoped `GITHUB_TOKEN` with `contents: write` and repository
rules that permit its commit on `main`. If rules block it, arrange explicit release-bot
authorization without weakening human branch protections. A local rehearsal is not
evidence of GitHub permissions. An atomically rejected push leaves both remote refs
unchanged. A connection failure can leave publication status uncertain: inspect the
remote refs before rerunning the workflow; an already published release reruns as a
successful no-op. Never overwrite an existing tag.

After a release, pull `main` and reinstall the queue before running the suite: the
installation tests compare `project.version` with the installed metadata. When a release
is produced, record the workflow run, the source and release SHAs, the version and the
confirmed remote tag identity in the Linear issue.
