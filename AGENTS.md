# cy-queue agent instructions

Persistent whole-GPU queue for clearml-yolo (CY) commands, shared by cooperating Linux
users: durable jobs run as their owner, with reservations, holds, handoff, cancellation,
recovery and a Textual UI. Product contract, terms, interfaces and operations:
[DOCS.md](DOCS.md). User documentation (Russian): [README.md](README.md) and
[docs/](docs/README.md).

## User documentation

- The user documentation is [README.md](README.md) (entry page) and the pages that
  [docs/README.md](docs/README.md) lists. Each fact has one owning page: the page that
  index lists for its subcommand, file or topic. Other pages link to the owner.
  `README.md`, `docs/README.md` and [GLOSSARY.md](GLOSSARY.md) restate a fact only to
  summarize or define.
- A behavior or interface change updates, in the same PR, every DOCS.md section that
  states the fact, the owning user page and every other place that restates it. Search
  `DOCS.md`, `README.md`, `docs/` and `GLOSSARY.md` for the key, value, message and output
  text, not only the identifier.
- Each claim the change adds or edits matches the code and does not contradict DOCS.md;
  DOCS.md may be less detailed than a user page. If the code and DOCS.md disagree, the
  code's current behavior is the fact: fix DOCS.md in the same PR, or record the mismatch
  in the Linear issue when fixing it is out of scope. Record a mismatch noticed elsewhere
  in the Linear issue.
- A fact the index assigns to no page goes on the page of its subcommand or, if it belongs
  to none, on the nearest reference page (`docs/configuration.md`, `docs/state.md`,
  `docs/setup.md`); extend the index entry to name it.
- Adding, renaming or removing a subcommand updates the DOCS.md "CLI" synopsis, the
  `README.md` subcommand table, the `docs/README.md` index entry, `docs/formats/json.md`
  when the subcommand accepts `--json`, and its command page: an existing page in
  `docs/commands/` for a closely related subcommand, else a new page. Adding, renaming or
  removing a page updates `docs/README.md`.
- GLOSSARY.md defines the user-facing terms in English with their Russian wording and
  lists the names the pages keep in English; developer and contract terms stay in the
  DOCS.md "Domain terms" section. User pages use the glossary's Russian wording. A change
  that introduces, renames, removes or narrows a user-facing term, or a name the glossary
  lists as kept in English (state value, key, flag), updates GLOSSARY.md in the same
  change.

## Layout

- `src/cy_queue/core`, `application`: pure queue policy and ports.
- `src/cy_queue/adapters/queue`: storage, locks, generations, guardians, settings, runtime.
- `src/cy_queue/adapters/runtime`: NVML GPU probing and resources.
- `src/cy_queue/entrypoints`: `cy-queue` CLI, Hydra composition, `queue_run` runner, TUI.
- `tests/`: routine suite (temporary storage, fake NVML in `tests/queue_nvml`, real owned
  subprocesses) plus opt-in physical/multiuser harnesses.
- `scripts/release.py`: CI-only release driver. `.importlinter`, `ruff.toml`,
  `pyproject.toml` hold tool configuration.

## Environment

- Source-only: neither CY nor cy-queue is published on an index. Install compatible CY
  from source, then this package, into one prepared environment; never let a resolver
  replace CY with an index package. Dependency installation stays external; the queue
  carries no lockfile. Install this repo's `dev` dependency group (pytest, ruff, mypy,
  import-linter, hypothesis, packaging) into that environment too.
- Python and CY bounds live in `pyproject.toml` (CY: minimum only, never an upper bound).
- Reuse CY's prepared uv environment from this repository root so this repo's tool
  configuration applies: `uv run --frozen --no-sync --project <clearml-yolo checkout> <cmd>`.
  `--project` does not change the working directory. Bare `python` must be that interpreter.
- Linux with pidfd/subreaper support is required for execution.

## Checks

Run from the repository root (prefix each with the `uv run` form above):

```bash
python -m pytest
ruff check .
ruff format --check .
mypy .
lint-imports
```

- There are no git hooks or CI checks; run these directly before committing.
- `ddp_gpu` tests need `--run-ddp-gpu`, `--ddp-devices`, `--ddp-clearml-project`,
  `--ddp-artifacts` (see `pytest --help`); they stay deselected. The multiuser harness
  provisions temporary Unix identities; read its `--help` first. Physical scenarios use
  an existing `queue.toml` and its host coordination root, overriding only the metadata
  root; never change host coordination to bypass other workloads.
- Routine tests prove state/process behavior with fake NVML only; real GPU, multi-GPU
  handoff, ClearML publication or cleanup claims need new owned live evidence.

## Architecture boundaries

- Dependency direction `cy_queue` → `clearml_yolo`; CY never imports the queue. Direct
  CY commands must work without queue install, settings, workers, Textual or NVML.
- `core` and `application` have no filesystem, SDK or subprocess effects and never import
  `clearml_yolo`, `hydra`, `textual`, `pynvml`, `torch`, `clearml`, `ultralytics`.
- Layers point inward: entrypoints → adapters → application → core. Adapters own storage,
  locks, GPU probing and guardians; only entrypoint integration composes CY commands.
- Package initializers stay inert; defer SDK imports.
- Enforced by `.importlinter` (`inward-layers`, `pure-policy`) and
  `tests/test_architecture.py` (also pins exact CY interface ownership and subprocess targets).
- Do not change CY's shared process/lifecycle interfaces without cross-package checks.

## Hard constraints

- Preserve public record protocols (`shared-cy-queue-v1` and GPU control/generation
  protocols), configuration paths, coordination/lock names, durable identifiers,
  ownership evidence, recovery and acknowledged handoff. Never delete queue state or
  coordination evidence to make anything pass.
- Never broaden access to private snapshots or logs; public output omits claim tokens,
  full UUIDs and private process data.
- Uncertain cleanup → explicit owner recovery; never automatic retry; never infer cleanup
  from heartbeat expiry, low memory or stale metadata.
- Memory admission is strict less-than the threshold; equality and unknown telemetry block.
- New private payload fields must stay readable when absent (default to prior behavior).
- Use loguru, never stdlib `logging` (ruff bans it).

## Decisions that bind changes

- Raise the CY minimum in `pyproject.toml` when using a newer CY interface; never add an
  upper bound.
- A behavior or interface change updates documentation in the same PR as specified in
  [User documentation](#user-documentation).
- Version changes come only from the release workflow: never edit `project.version` or
  `CHANGELOG.md` by hand, and do not create `CHANGELOG.md` (semantic-release does).
  Do not run `scripts/release.py` locally.

## Delivery and release

- Plans, acceptance criteria and status live in Linear, team `SIP`, project `cy-queue`.
  Record evidence (source SHAs, checks, outcomes, limitations) in the issue and the PR;
  the repo keeps no evidence directory.
- Work on a task branch; push it and open a PR against `main` of
  `BuckanovNikita/cy-queue`. Humans merge. Never push `main` or merge into it locally.
  After pushing, confirm the remote branch points at the verified commit. Explicit
  no-commit/no-push limits take precedence.
- PR title and every branch commit need an accurate Conventional Commit type; they
  decide the version. A change to installed behavior, requirements or package metadata
  is `fix`, `perf` or `feat`.
- Linear readiness labels (separate from lifecycle state): `needs-triage`, `needs-info`,
  `ready-for-agent`, `ready-for-human`, `wontfix`. Mark an issue Done only after its
  changes reach `main` and its acceptance criteria are met.
- Lifecycle states: Backlog, Todo, In Progress, In Review, Done, Canceled, Duplicate. Move
  to In Review when implementation and required verification are ready. A ready label
  never overrides dependencies: start dependent work only after its prerequisite is
  implemented and verified on its base branch; a canceled prerequisite forces replanning
  or removing dependent work, never bypassing it.
- Default to one branch and PR per cohesive feature (may cover several issues); link
  issues, PRs and evidence both ways; keep issues open until the PR merges.
- Stacks: first PR targets `main`, children target their parent branch; humans merge
  bottom-up, then restack, inspect diffs and repeat affected checks and review. Rewrite
  only task-owned branches, with `--force-with-lease`. Do not assume GitHub checks,
  branch protection or Linear automation is configured.
- A human merge into `main` triggers an automatic release: a version commit and an
  annotated `v{version}` tag only (no GitHub Release, package or deployment).
  `.github/workflows/release.yml` runs only for merged PRs, one at a time. Semantic Release
  bumps from Conventional Commits since the last `v{version}` tag (squash merge: PR title
  plus listed commits): `fix`/`perf` → patch, `feat` or breaking (major 0) → minor,
  others release nothing. `scripts/release.py` requires exactly one new commit touching
  only `pyproject.toml`/`CHANGELOG.md` with an annotated tag and a higher version, pushes
  both atomically and never force-pushes. After an uncertain push, inspect remote refs
  before rerunning; an already published release reruns as a no-op. The job needs
  `GITHUB_TOKEN` with `contents: write`; never overwrite an existing tag. Unmerged
  closures, plain pushes and tag creation do not release; closely spaced merges may share
  one release. Repository rules must permit the bot commit on `main`; if they block it,
  arrange explicit release-bot authorization without weakening human branch protection.
  A local rehearsal is no evidence of GitHub permissions. After a release, record the
  workflow run, source and release SHAs, version and confirmed remote tag identity in the
  Linear issue.
- Paired release checks before every merge of either CY or cy-queue: verify the latest
  sources of both together, on the final PR head with current `main`, from this checkout:

  ```bash
  uv pip install --python <cy-venv>/bin/python -e <clearml-yolo> -e .
  uv pip check --python <cy-venv>/bin/python
  uv run --frozen --no-sync --project <clearml-yolo> pytest -q
  uv run --frozen --no-sync --project <clearml-yolo> cy-queue --help
  ```

  plus the static checks. Use normal resolution (no `--no-deps`). Incompatible bounds,
  stale installed metadata or unavailable checks block merge. One package passing alone
  is insufficient. Fetch both remotes first; never assume a stale sibling checkout or
  installed metadata is the latest. The install step changes the shared environment:
  drain it first or use an isolated prepared environment. If either `main` moves before
  the merge, repeat the affected checks; after a release in either repo, pull, reinstall
  and repeat in every environment still in use. Report both source SHAs, versions,
  resolver and integration results in the Linear issue and the PR. CY's `paired-check`
  task runs the same pair in a temporary environment; it needs a clean queue checkout
  containing the latest remote `main`.
- Drain workers per DOCS.md "Operations" before changing an operational environment.

## Pitfalls

- The check commands assume `cy-queue` and its `dev` group are installed (editable) in the
  shared environment.
  Without it `lint-imports` cannot find `cy_queue`, and tests that read installed
  `cy-queue` metadata fail with `PackageNotFoundError`. That error then cascades into
  `GlobalHydra is already initialized` errors in later tests.
- Installation tests compare `project.version` with installed metadata: reinstall after
  any version change or pulled release, or they fail on stale metadata.
- `uv run` without `--no-sync` against CY's project removes the separately installed queue.
- `--frozen --no-sync` proves nothing about dependency completeness or lock freshness.
- Missing the latest annotated release tag (the tool restarts from the first commit) or a
  hand-edited `project.version` fails the release job without publishing; fix by restoring
  the annotated tag on its release commit or reverting the version edit, then rerun.

## Language standards

- Python: syntax and annotations compatible with the `requires-python` floor; no
  `from __future__ import annotations`; explicit typing; Pydantic for validated models;
  loguru; pytest.
- Catch specific exceptions at a boundary that handles them; keep the cause when
  translating; never silently discard unexpected failures.
- Preserve public imports, CLI output, exit codes, config precedence and persisted formats.
- Ruff `select = ["ALL"]` with preview, line length 120: keep per-file ignores and stated
  reasons in `ruff.toml`; add `noqa` only with a specific code; apply lint fixes before
  formatting; never widen rules to pass.
- mypy strict with extra error codes from `pyproject.toml`; scope overrides to modules; no
  blanket `ignore_missing_imports` or `Any` to pass.
- Cleanup: trace consumers before removing code; leave dependency pins intact.

## Working agreement
- At the start of work, state the worktree path, the current branch and its relation to the default branch; say when remote refs were not fetched.
- Inspect existing and staged changes before editing. Preserve unrelated work and local overrides; stage only task-owned paths and inspect the staged diff.
- Report what each executed check establishes and what remains unverified; distinguish mocked checks, live outcomes and historical evidence. Clean up task-owned processes and temporary resources.
- Tests must exercise product code, never project tooling.
- Changes to behavior, interfaces, dependencies, security or operational policy need a fresh independent review after integration and verification. Small wording edits may be self-reviewed.
- Split large work into independent delegated tasks with explicit write ownership and acceptance evidence; delegated agents do not delegate further.
- Use Conventional Commits. Commit automatic formatting separately from logic. Local commits within the task scope need no approval.
- README.md and docs/ are Russian; AGENTS.md, DOCS.md and GLOSSARY.md are English. Keep observed counts, timings and deployment status out of all of them.
- Keep machine-specific paths, endpoints and settings in local configuration, not in these files.
