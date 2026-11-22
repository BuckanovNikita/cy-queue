# CHANGELOG


## v0.1.11 (2026-11-22)

### Bug Fixes

- **cli**: Make five messages state their real cause and a step the user can take (SIP-227)
  ([#8](https://github.com/BuckanovNikita/cy-queue/pull/8),
  [`71ba978`](https://github.com/BuckanovNikita/cy-queue/commit/71ba9786fb82ccf8341d89a6a5b30b840776e595))

- **cli**: Point the interpreter mismatch at a step submit really has (SIP-227)
  ([#8](https://github.com/BuckanovNikita/cy-queue/pull/8),
  [`71ba978`](https://github.com/BuckanovNikita/cy-queue/commit/71ba9786fb82ccf8341d89a6a5b30b840776e595))

- **cli**: Print copyable paths, a uniform remote header, a recover hint and quieter recovery logs
  (SIP-230) ([#9](https://github.com/BuckanovNikita/cy-queue/pull/9),
  [`34842ff`](https://github.com/BuckanovNikita/cy-queue/commit/34842ff3aaa4cd81cf6a63d181d7933452e227bb))

- **records**: Keep repeated cancels, committed changes and launch cancels true to the job (SIP-226)
  ([#7](https://github.com/BuckanovNikita/cy-queue/pull/7),
  [`ae3d591`](https://github.com/BuckanovNikita/cy-queue/commit/ae3d591a05d15451ab3c977fac5ccc1d4f9380a7))

- **records**: Keep waiting reason, update time and cancel error true to the job state (SIP-226)
  ([#7](https://github.com/BuckanovNikita/cy-queue/pull/7),
  [`ae3d591`](https://github.com/BuckanovNikita/cy-queue/commit/ae3d591a05d15451ab3c977fac5ccc1d4f9380a7))

- **submit**: Report a missing key, --gpus 0 and an unsatisfiable GPU count in one line (SIP-224)
  ([#6](https://github.com/BuckanovNikita/cy-queue/pull/6),
  [`710368a`](https://github.com/BuckanovNikita/cy-queue/commit/710368a1ad2bf44890f2c23e158d1b7070c6b4d1))

### Code Style

- **tests**: Format handoff lifecycle observation
  ([`349c13b`](https://github.com/BuckanovNikita/cy-queue/commit/349c13b2729ade73cd944c5839854574eb407b19))

- **tests**: Format lifecycle observation condition
  ([`79a944e`](https://github.com/BuckanovNikita/cy-queue/commit/79a944ed831dac40f8ee4bbe40886d0ebc52df41))

### Continuous Integration

- Adopt Linear, GitHub PR and automated release workflow
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

- Keep pending releases queued and report metadata errors
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

- Refuse a release that does not advance the version
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

- Release automatically after merges to main
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

### Documentation

- Add command pages for job management and gpu (SIP-200)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add command pages for submit and config (SIP-198)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add command pages for worker, list and tui (SIP-199)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add facts from the previous manual and correct pages after the live pass (SIP-202)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add host setup, configuration and state pages (SIP-196)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add scenarios and the index, shorten the README to an entry page (SIP-201)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add the --json output reference (SIP-197)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add the Russian user documentation tree (SIP-194)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add the user documentation rules for agents (SIP-201)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Add the user glossary with Russian wording (SIP-195)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Adopt Linear planning and GitHub PR delivery
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

- Compress agent instructions and docs into AGENTS.md and DOCS.md
  ([#2](https://github.com/BuckanovNikita/cy-queue/pull/2),
  [`eb2ef8d`](https://github.com/BuckanovNikita/cy-queue/commit/eb2ef8d029279685965766a661770ce741a89d34))

- Compress agent instructions and docs into AGENTS.md and DOCS.md (SIP-159)
  ([#2](https://github.com/BuckanovNikita/cy-queue/pull/2),
  [`eb2ef8d`](https://github.com/BuckanovNikita/cy-queue/commit/eb2ef8d029279685965766a661770ce741a89d34))

- Correct archive/restore failure, updated_at and cancel error rules (SIP-226)
  ([#7](https://github.com/BuckanovNikita/cy-queue/pull/7),
  [`ae3d591`](https://github.com/BuckanovNikita/cy-queue/commit/ae3d591a05d15451ab3c977fac5ccc1d4f9380a7))

- Correct ten statements found by the code review (SIP-194)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Do not call the Hydra exception line the last traceback line (SIP-224)
  ([#6](https://github.com/BuckanovNikita/cy-queue/pull/6),
  [`710368a`](https://github.com/BuckanovNikita/cy-queue/commit/710368a1ad2bf44890f2c23e158d1b7070c6b4d1))

- Drop the CLAUDE.md loader shim ([#2](https://github.com/BuckanovNikita/cy-queue/pull/2),
  [`eb2ef8d`](https://github.com/BuckanovNikita/cy-queue/commit/eb2ef8d029279685965766a661770ce741a89d34))

- Keep new contract facts in DOCS.md and surface code and contract mismatches (SIP-201)
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

- Make the Linear status carry the triage role (SIP-236)
  ([#5](https://github.com/BuckanovNikita/cy-queue/pull/5),
  [`0b020d6`](https://github.com/BuckanovNikita/cy-queue/commit/0b020d682610846873b8face28971c97ea20b54e))

- Narrow the release type rule and correct release wording
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

- Rewrap the Linear project rule (SIP-236) ([#5](https://github.com/BuckanovNikita/cy-queue/pull/5),
  [`0b020d6`](https://github.com/BuckanovNikita/cy-queue/commit/0b020d682610846873b8face28971c97ea20b54e))

- Say that any change other than state or error logs INFO (SIP-230)
  ([#9](https://github.com/BuckanovNikita/cy-queue/pull/9),
  [`34842ff`](https://github.com/BuckanovNikita/cy-queue/commit/34842ff3aaa4cd81cf6a63d181d7933452e227bb))

- Say that archive and restore change nothing when their first read fails (SIP-226)
  ([#7](https://github.com/BuckanovNikita/cy-queue/pull/7),
  [`ae3d591`](https://github.com/BuckanovNikita/cy-queue/commit/ae3d591a05d15451ab3c977fac5ccc1d4f9380a7))

- Say that only some CY composition errors print a traceback (SIP-224)
  ([#6](https://github.com/BuckanovNikita/cy-queue/pull/6),
  [`710368a`](https://github.com/BuckanovNikita/cy-queue/commit/710368a1ad2bf44890f2c23e158d1b7070c6b4d1))

- State that a mistyped CY override key still prints a traceback (SIP-224)
  ([#6](https://github.com/BuckanovNikita/cy-queue/pull/6),
  [`710368a`](https://github.com/BuckanovNikita/cy-queue/commit/710368a1ad2bf44890f2c23e158d1b7070c6b4d1))

- State that the worker start line is logged at the first poll (SIP-227)
  ([#8](https://github.com/BuckanovNikita/cy-queue/pull/8),
  [`71ba978`](https://github.com/BuckanovNikita/cy-queue/commit/71ba9786fb82ccf8341d89a6a5b30b840776e595))

- State what decides a version and what follows a release
  ([#1](https://github.com/BuckanovNikita/cy-queue/pull/1),
  [`9bcd8fa`](https://github.com/BuckanovNikita/cy-queue/commit/9bcd8fa16b886e9f1c6ec6a5a792b1df62c9800a))

- **readme**: Rewrite the user guide around everyday queue use
  ([#3](https://github.com/BuckanovNikita/cy-queue/pull/3),
  [`74e9074`](https://github.com/BuckanovNikita/cy-queue/commit/74e90747b7e6f9a6dd047d4b9862fd94daaaf66d))

### Testing

- Keep the suite out of the host-wide coordination directory (SIP-230)
  ([#9](https://github.com/BuckanovNikita/cy-queue/pull/9),
  [`34842ff`](https://github.com/BuckanovNikita/cy-queue/commit/34842ff3aaa4cd81cf6a63d181d7933452e227bb))

- Pin updated_at for non-state writes and CLI waiting reasons (SIP-226)
  ([#7](https://github.com/BuckanovNikita/cy-queue/pull/7),
  [`ae3d591`](https://github.com/BuckanovNikita/cy-queue/commit/ae3d591a05d15451ab3c977fac5ccc1d4f9380a7))

- Prove the worker start line and binding message on real code (SIP-227)
  ([#8](https://github.com/BuckanovNikita/cy-queue/pull/8),
  [`71ba978`](https://github.com/BuckanovNikita/cy-queue/commit/71ba9786fb82ccf8341d89a6a5b30b840776e595))

- **batch**: Verify editable table lookup on assigned GPUs
  ([`d3627a0`](https://github.com/BuckanovNikita/cy-queue/commit/d3627a0da85968429ddeaff4920c05825e6e05e2))

- **queue**: Await complete lifecycle observations
  ([`9e720d6`](https://github.com/BuckanovNikita/cy-queue/commit/9e720d6ca081178f814e10772a08c141f3464ed6))

- **queue**: Await remaining reservations after handoff cleanup
  ([`859cc2c`](https://github.com/BuckanovNikita/cy-queue/commit/859cc2cf4e8974b0f8bd93d717665d9d9c00fb39))

- **queue**: Await reservation cleanup across lifecycle checks
  ([`36c8f77`](https://github.com/BuckanovNikita/cy-queue/commit/36c8f77d0e396f68c12ea860bab77f14ed9d8d5f))


## v0.1.10 (2026-11-17)

### Bug Fixes

- Support current CY versions and require paired release checks
  ([`89938c2`](https://github.com/BuckanovNikita/cy-queue/commit/89938c2367c6ed143ae2eab96ae6513ab70bb392))

- Support CY 0.41 batch estimation
  ([`ae252ed`](https://github.com/BuckanovNikita/cy-queue/commit/ae252ed8e633e7548180577739673ff0506e1c0c))

- Support CY 0.42 native weight preparation
  ([`4205b9b`](https://github.com/BuckanovNikita/cy-queue/commit/4205b9ba58f70cd69ffd9d8380ef0dd5556a3937))

- Support CY 0.43 local documentation release
  ([`114b972`](https://github.com/BuckanovNikita/cy-queue/commit/114b97272ab5bb406a90c146ea62d8fdd19d75b1))

- **compat**: Require only a minimum clearml-yolo version
  ([`e938967`](https://github.com/BuckanovNikita/cy-queue/commit/e93896734905b54129723f9d0ff3d8a70b9d7e00))

- **compat**: Support CY 0.45 saved estimate listing
  ([`4cf32f0`](https://github.com/BuckanovNikita/cy-queue/commit/4cf32f0cd84730aebd3cf930829f80ba47d5af24))

- **compat**: Support CY 0.46 forced estimation release
  ([`4498e64`](https://github.com/BuckanovNikita/cy-queue/commit/4498e64991c5f2612fca35152a9b87b2e8ae29bc))

- **compatibility**: Accept verified CY 0.44 release
  ([`397753c`](https://github.com/BuckanovNikita/cy-queue/commit/397753c123f379ade50f06a2babf5e4b1476b9d2))

- **queue**: Preserve newer completion during recovery refresh
  ([`b976789`](https://github.com/BuckanovNikita/cy-queue/commit/b976789301d814a4249d3683739b8d6918819a73))

### Chores

- Remove documentation-specific tests and checks
  ([`3a5b25f`](https://github.com/BuckanovNikita/cy-queue/commit/3a5b25f63b44f7c85bbfe854f94bde732f66fe29))

- **tooling**: Consolidate agent and verification policies
  ([`adad7e9`](https://github.com/BuckanovNikita/cy-queue/commit/adad7e9f451094c55a1b7d51154c57e6dd58c080))

### Code Style

- Apply Ruff formatting
  ([`1a08c3d`](https://github.com/BuckanovNikita/cy-queue/commit/1a08c3d1262d59837237da2a1b544b6c4719dbed))

### Documentation

- Allow targeted verification skips for intermediate commits
  ([`445dfce`](https://github.com/BuckanovNikita/cy-queue/commit/445dfce36137770fdca9826279353027261de376))

- Avoid naming a nonexistent evidence location
  ([`c7db3da`](https://github.com/BuckanovNikita/cy-queue/commit/c7db3dae84e28dfd91a1bd415ffa0455afd04d71))

- Clarify domain boundaries and preserve specification meaning
  ([`b4d2c36`](https://github.com/BuckanovNikita/cy-queue/commit/b4d2c363696362de6bddad44fa89b1fe75116a78))

- Consolidate specifications into functional descriptions
  ([`c209ca3`](https://github.com/BuckanovNikita/cy-queue/commit/c209ca3d6efd9fdcddad489c164544dd848d07f9))

- Define self-contained functional behavior
  ([`dbf131b`](https://github.com/BuckanovNikita/cy-queue/commit/dbf131b88811ea402c78bca373fc9c1decc81559))

- Fix dangling evidence and config references
  ([`0baaae3`](https://github.com/BuckanovNikita/cy-queue/commit/0baaae32d75f194037e4c57d2049df148e3ba390))

- Reconcile preserved instruction migration receipts
  ([`694c12f`](https://github.com/BuckanovNikita/cy-queue/commit/694c12f9c2a1a0064284a69d010e846108d43875))

- Record CY 0.43 committed-pair verification
  ([`4e18ec6`](https://github.com/BuckanovNikita/cy-queue/commit/4e18ec622121c228474dd454b0b46d4af902cf92))

- Record CY 0.46 committed-pair verification
  ([`5cf1c35`](https://github.com/BuckanovNikita/cy-queue/commit/5cf1c355aba5a73582cb09adae88d6e1cc003d40))

- Record guarded recovery delivery
  ([`4e539f2`](https://github.com/BuckanovNikita/cy-queue/commit/4e539f227f06e600d95753e27049baf6df517398))

- Record public queue delivery
  ([`9a6fccd`](https://github.com/BuckanovNikita/cy-queue/commit/9a6fccd86b8958a77809e4d2e7e2cc178d0a73ee))

- Record verified instruction publication
  ([`0139152`](https://github.com/BuckanovNikita/cy-queue/commit/0139152c999a97dde816a72d5524d10a2ba8ad7f))

- Replace progress records with fresh problem specifications
  ([`5ab17f0`](https://github.com/BuckanovNikita/cy-queue/commit/5ab17f06f111de7ea0b1fc51c4b8dd9acd1d0dd6))

- Standardize shared agent instruction discovery
  ([`2392b90`](https://github.com/BuckanovNikita/cy-queue/commit/2392b9065b8e83f14072a4e37fa8bc0f24020fa4))

- **agents**: Refactor agent instructions and skills to current best practices
  ([`29d2284`](https://github.com/BuckanovNikita/cy-queue/commit/29d2284d90d3102b6972984107bf2d39703773d6))

- **agents**: Refactor agent instructions and skills to current best practices
  ([`b86360e`](https://github.com/BuckanovNikita/cy-queue/commit/b86360e0b423824a836df83e8a2b93af9ef719c1))

- **ledger**: Reconcile queue plans and record the DDP waiver
  ([`0c486b5`](https://github.com/BuckanovNikita/cy-queue/commit/0c486b5257da8950932aded99dc2a2f1b3680286))

- **plans**: Add verification-from-zero plan for 2026-11-07
  ([`6f26444`](https://github.com/BuckanovNikita/cy-queue/commit/6f2644406c7fedfc3d94029f538d7ce18cd4e2c6))

### Features

- Extract CY queue with standalone training support
  ([`1be96a6`](https://github.com/BuckanovNikita/cy-queue/commit/1be96a6d916d6a26a5ef07715d87a1853709602f))

- **compat**: Prepare queue 0.1.9 for CY 0.46
  ([`3ebd78a`](https://github.com/BuckanovNikita/cy-queue/commit/3ebd78af91e65958961cd4f5f7860f43f8b4ca2a))

- **queue**: Configure GPU memory admission threshold
  ([`2fbaed2`](https://github.com/BuckanovNikita/cy-queue/commit/2fbaed25fa7c572757d30cb9b1b343d22e645e3a))

### Testing

- Remove development tooling self-tests
  ([`cd85a0c`](https://github.com/BuckanovNikita/cy-queue/commit/cd85a0cb6fac86d485291d5bac558881068116fa))

- **queue**: Align saved batch fixtures with CY search policy
  ([`32bea01`](https://github.com/BuckanovNikita/cy-queue/commit/32bea017b609a258300619cef2d170a14a8aa2a7))
