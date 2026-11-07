# Verification from zero (2026-11-07)

Status: open. No box below is checked; nothing in this plan has been run.

## Why

On 2026-11-07 the user merged all started, unfinished, non-cancelled work across
their repositories into each default branch without verification. For cy-queue no
unmerged work remained, so `main` was unchanged by that merge pass, but the policy
applies uniformly: earlier partial verification evidence is dropped as acceptance
evidence. Every claim about the current `main` must be re-established from a clean
checkout with fresh dated evidence.

## Range

The whole history from the root commit `1be96a6d916d6a26a5ef07715d87a1853709602f`
(inclusive) through `0c486b5257da8950932aded99dc2a2f1b3680286`
(`docs(ledger): reconcile queue plans and record the DDP waiver`), that is
`git log 1be96a6..0c486b5` plus the root commit itself. The commit that adds this
plan is documentation only and is verified by the same run.

## Supersedes (as acceptance evidence)

These records stay in the repository as history; they no longer count as current
verification of `main`:

- `docs/evidence/2026-11-05-current-queue.md` (current-source single-GPU queue run)
- `docs/evidence/2026-10-23-extraction.md`, `2026-10-23-live-queue.md`,
  `2026-10-23-review.md`
- `docs/plans/cy-046-compatibility/` (`plan.md`, `verification.md`,
  `verification-2026-11-04.md`, `review.md`; `preparation-plan.md` and
  `preparation-verification.md` were already superseded by `plan.md`)
- `docs/plans/cy-045-compatibility/` (`plan.md`, `verification.md`, `review.md`)
- `docs/plans/2026-10-30-gpu-memory-threshold/` (`plan.md`, `verification.md`,
  `review.md`)
- `docs/plans/claude-codex-organization-20261102/` (`plan.md`,
  `verification-2026-11-02.md`)
- `docs/verification/batch-alignment-20261102/verification.md`
- `docs/bugs/*/verification.md` (cy-041 through cy-044 compatibility,
  queue-version-compatibility, refresh-completion-race)

Not superseded: `docs/evidence/2026-11-07-ddp-gpu-waiver.md`. It records a user
decision, not a pass, and stays in force (see step 6).

## Checklist

Run in order from a fresh clone; stop and record any failure before continuing.

### 1. Clean checkout and pairing sources

- [ ] Clone `git@github.com:BuckanovNikita/cy-queue.git` into a new directory and
      check out `main`; record the SHA (expected `0c486b5` or a descendant).
- [ ] Fetch `clearml-yolo` (CY) and record its latest `main` SHA, version (0.46.x at
      the time of writing) and tags; use a fresh clone or a clean worktree, never a
      stale sibling checkout.
- [ ] Confirm `pyproject.toml` bound `clearml-yolo>=0.38,<0.47` admits that CY
      version, and that cy-queue `version` (0.1.9) is the version under test.

### 2. Environment setup

- [ ] Prepare CY's approved external dependencies in CY's own uv environment
      (`docs/development.md`, "Paired release checks"); do not let a resolver
      replace CY with an index package.
- [ ] `uv pip install --python <cy>/.venv/bin/python -e <cy> -e .` with normal
      resolution (no `--no-deps`), then `uv pip check --python <cy>/.venv/bin/python`.
- [ ] Confirm bare `python` (or the `uv run --frozen --no-sync --project <cy>`
      prefix) resolves to the shared CY interpreter (Python >=3.12.13,<3.14).

### 3. Lint, type and import contracts

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy .` (strict, per `[tool.mypy]`)
- [ ] `lint-imports`: both `inward-layers` and `pure-policy` contracts kept.

### 4. Full routine suite

- [ ] `python -m pytest` (under `nice -n19`); record passed/deselected counts.
      Exactly the seven `ddp_gpu` tests must be deselected; any other skip or
      deselection is a failure to investigate.
- [ ] Confirm `tests/test_architecture.py` and the installation/metadata tests
      (source vs installed requirements and versions) are among the passes.

### 5. Documented gates and CLI

- [ ] `cy-queue --help` runs from the installed pair.
- [ ] Check that `README.md` (Russian), `docs/interfaces.md` and `docs/migration.md`
      still describe the integration contract, version bounds, GPU memory
      admission, refresh/completion races and offline upgrade as implemented.

### 6. Live, native and GPU acceptance (where applicable)

- [ ] Single-GPU live queue run with explicitly owned evidence: queued standalone
      `train` and `pipeline` jobs, guardian claim, configured admission threshold,
      completion with allocation release, cleanup of all tracked processes, ClearML
      SDK readback and exact-tag cleanup (the scope of the superseded 2026-11-05
      record). Requires an existing valid `queue.toml`/`CY_QUEUE_CONFIG`; do not
      change host coordination to bypass other workloads.
- [ ] Multiuser harness only with explicit authorization and its test-owned Unix
      identities (inspect `--help` and its ownership contract first).
- [ ] Physical two-GPU DDP: **waived, not run.** The seven `ddp_gpu` tests in
      `tests/test_native_ddp_gpu.py` (`test_physical_native_pipeline` x4,
      `test_physical_queued_failure_cleanup` x3) stay deselected per the user
      decision of 2026-11-06 recorded in `docs/evidence/2026-11-07-ddp-gpu-waiver.md`.
      Re-confirm the waiver still stands; the verification record must not count
      them as passed.

### 7. Architecture and record acceptance

- [ ] Re-check `docs/architecture.json` and each task's `architecture.json` against
      the code: dependency direction `cy_queue` -> `clearml_yolo` only, inert package
      initializers, effect-free `core`/`application`, adapters owning storage, locks,
      GPU probing and guardians.
- [ ] Confirm CY does not import `cy_queue` (grep the CY checkout from step 1).
- [ ] Write a new dated verification record (and architecture record if needed)
      with both source SHAs, versions, resolver result, counts and live job IDs.
- [ ] Independent review of the integrated record per `AGENTS.md`.

### 8. Release and pairing

- [ ] Run the paired release checks on the latest CY and cy-queue together; one
      package passing alone is insufficient, and incompatibility or missing evidence
      blocks delivery.
- [ ] Recheck the final installed pair if any hook or fix changes either version.
- [ ] Deliver only by Conventional Commit push to `main`; there is no version-tag
      automation, GitHub Release, asset upload or registry publication.
- [ ] Mark this plan done only when every box above is checked or explicitly waived
      by the user with a dated record.
