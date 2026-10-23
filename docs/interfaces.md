# CY integration interfaces

The dependency direction is `cy_queue` → `clearml_yolo`. The package metadata bounds
the supported CY minor version. CY never imports the queue and its direct execution
requires no queue settings, workers, GPU reservations, Textual or NVML.

| CY interface | Queue caller and invariant |
| --- | --- |
| `adapters.runtime.process_tree` | Guardian/runtime/identity use Linux process identity, pidfd/subreaper preflight, owned-tree cleanup and interruption deferral. Shared supervision remains in CY. |
| `adapters.runtime.execution_lifecycle` | Guardian and exec gate consume the inherited lifecycle socket/owner protocol. No training-finished notification retains the full allocation. Lost acknowledgement after durable shrink stops inference without restoring released extras. |
| `adapters.runtime.bootstrap` | Snapshot runner initializes the existing CY environment after validating owner, interpreter, installation and snapshot. |
| `adapters.storage.filesystem` | Hydra integration and runner validate project-contained destinations and temporary configuration. |
| `adapters.observability.diagnostics`, `tracing` | GPU inventory preserves CY's redaction and tracing contracts without model runtime initialization. |
| `core.presentation`, `core.redaction` | Terminal presentation uses pure formatting and secret redaction. |
| `entrypoints.hydra.configs`, `sweeps`, `validation` | Composition uses registered CY roots, sequential sweep expansion, original wrapper/input/destination validation and multirun tags. |
| `application.use_cases.pipeline`, `train`; `application.contracts`; `adapters.yolo.config` | Composition validates current command signatures and native settings without executing them or resolving assets. |
| `entrypoints.pipeline`, `entrypoints.train` | Runner execs the selected existing CY entrypoint, with frozen configuration and allocation-relative logical device indexes. |

Queue policy records and application ports remain independent of CY and external SDKs.
Outer adapters own queue storage, locks, GPU inventory and guardian effects. Only the
entrypoint integration composes CY commands. The adapter runtime's literal subprocess
`cy_queue.entrypoints.queue_run` is an explicit process target, not a Python reverse
import. Initializers are inert and SDK imports are deferred.

`tests/test_architecture.py` checks all source modules, exact CY interface ownership,
SDK ownership, literal dynamic and subprocess targets, type-only imports, and negative
injected edges. `.importlinter` checks transitive policy isolation and inward layers.
Lifecycle, cancellation, recovery, admission, multiuser, handoff and installation tests
exercise the retained contracts. Real GPU/Agent/publication claims need separate live
acceptance; fake NVML tests prove state/process behavior only.
