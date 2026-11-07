# Queue ownership and state

These terms distinguish experiment outcome from current capacity.

## Language

**Job**: One owner's durable request to execute a frozen experiment; its outcome persists after its devices become available.

**Allocation**: The ordered physical devices assigned to a job.

**Reservation**: The queue's current exclusive claim on a device. Releasing it does not establish that the process stopped or the job succeeded.

**Hold**: A user's explicit exclusion of a device from new allocations, independent of a running job's reservation.

**Recovery required**: A job state requiring its owner to resolve uncertain process ownership or cleanup. It does not replace the scientific outcome.
