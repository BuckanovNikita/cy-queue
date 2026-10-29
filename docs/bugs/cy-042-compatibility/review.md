# CY 0.42 compatibility review — 2026-10-29

## Reviewed scope and outcome

The parent supplied fresh independent integrated review evidence from reviewers
`final_review` and `acceptance_review`. Their full feature-007 inspection included
the actual queue compatibility metadata, focused regression tests, architecture and
portable guidance. Both found no queue-specific functional or architecture blocker.
They required corrections at the CY Hugging Face diagnostic boundary, which were
tracked and fixed in the isolated CY implementation, outside this queue diff.

Fresh independent reviewer `privacy_final` then accepted the focused correction:
the native terminal progress leak was closed, real SDK progress/Xet callback
compatibility remained supported, and 77 Hub/preparation cases independently passed.
It found no new blocker. The parent accepted the combined full-scope review and
focused closure. Full detailed finding/correction history belongs to
[CY feature 007 review](https://github.com/BuckanovNikita/clearml-yolo/blob/master/specs/007-download-weights/review.md),
not to a new queue runtime change.

Accepted queue scope is exactly:

- `pyproject.toml`: queue 0.1.3 and retained lower bound with verified CY upper
  bound `clearml-yolo>=0.38,<0.43`.
- `tests/test_weight_preparation_submission.py`: six pipeline/train and
  boolean/filename-pretrained cases preserving custom architecture/pretrained/resume
  through composition and worker exec without premature catalogue preparation.
- New task plan, architecture, dated verification and this review record under
  `docs/bugs/cy-042-compatibility/`.

There are no queue runtime-module changes, renames, removals, queue protocol changes,
new reverse dependencies or effect-ownership exceptions. Existing exact CY import
ownership and forbidden-edge tests remain enforced. Native filesystem/SDK/process
effects stay in existing outer owners; queue policy remains independent of CY
configuration/effects. Concurrent CY feature 008 and unrelated changes are excluded.

## Acceptance evidence and remaining gate

The final approved-code isolated proposed pair passed all checks in
[verification](verification.md): normal CY 0.42.0/queue 0.1.3 resolution, exact
source/installed metadata, dependency consistency, complete ordinary queue suite,
static checks, import contracts and installed CLI help. Runtime/package/check inputs
did not drift during the run; only isolated CY evidence prose changed.

Review accepts this queue diff and its module/dependency boundaries. Architecture
validation checks record consistency; it does not independently prove review quality
or live GPU behavior. Physical GPU tests were deselected and no stand workload,
publication, deployment or operational installation is claimed.

The parent still owns exact committed-release metadata verification after committing
both source versions and authorized delivery. No commit or release was performed by
this bounded task; review acceptance does not waive that paired metadata gate.
