---
name: slurm-execution-contract
description: Plan, submit, modify, monitor, cancel and hand off result-producing Slurm jobs (sbatch, scontrol update, scancel), including jobs submitted inside an already authorized task and campaigns of array jobs. Use whenever a scheduler job is launched or watched; not for squeue or sacct reads alone or short debugging inside an existing allocation.
---

# Slurm Execution Contract

Use this opt-in workflow to preserve the user's intended resource shape and experiment lineage. It must not turn ordinary debugging into a queued job.

## Gate: do not use Slurm by default

Keep debugging, short tests, metadata inspection, and proxy measurements in the current safe allocation or direct command when adequate. Submit a Slurm job only when the user requests it or the required resources do not fit.

If the user says “four GPU nodes,” do not treat it as “four GPUs.” If nodes, GPUs per node, CPUs, partition, target node range, or job scope are ambiguous, ask before submitting.

## Local capacity profile

Before planning a GPU placement, read [the local cluster profile](references/cluster-profile.md). Use it for stable topology and CPU/GPU coupling facts only; never use it to claim that a node is currently free.

## GPU-first resource default

For an ordinary one-process-per-GPU workload, request one task and four CPUs per GPU unless the workload has an evidenced CPU, dataloader, preprocessing, or RAM requirement. Do not reserve a whole node merely because all of its GPUs are requested.

Use a shape equivalent to the following when it fits the workload:

```bash
#SBATCH --nodes=<N>
#SBATCH --ntasks-per-node=<GPUs per node>
#SBATCH --gpus-per-node=<GPUs per node>
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=4
```

Do not add `--exclusive`, node-wide CPU requests, or large `--mem` values by default. Increase CPU or RAM only with workload-specific evidence, such as data-loader workers, CPU preprocessing, host-side tensor staging, or a measured memory requirement. If a submitted job shows an unexpectedly large CPU or memory allocation, inspect the script and scheduler output before concluding that GPUs are unavailable.

## Compilation mode

Disable runtime compilation, such as `torch.compile`, for debugging and short tests. Enable it for a result-producing or benchmark run when the workload supports it and debugging has passed. Record the compilation mode in the run card, and do not compare compiled and uncompiled runs as equivalent.

## Contract before a scheduler mutation

State the requested and actual values for:

- purpose; input subset; nodes; GPUs per node; total GPUs; CPUs per task; CPU and memory budget; concurrency; partition; time limit; output location; stop condition
- array/chunk layout; checkpoint; commit; config; split; batch size; world size; seed

Preserve the user's resource semantics and request only what the workload supports.

Make availability claims only from fresh, scoped scheduler evidence. Query the relevant job IDs and nodes with `squeue`, `sacct`, `scontrol`, or cluster-native equivalents; do not infer availability from an earlier observation or an apparently idle GPU.

## Launch, monitor, and cancel

After submission, report the job ID and exact resource shape. Preserve enough lineage to reproduce the run.

For debugging and short tests, use waits or sleeps of 10 seconds or less. Prefer a fresh scheduler/status query to blind sleeping.

Use a longer bounded wait only when the user explicitly asks to monitor, wait, babysit, or keep watching. State the cadence and monitor the named job IDs; do not promise continuous monitoring without a monitoring mechanism.

Cancel or replace only the exact job IDs explicitly authorized by the user. Verify the current state and report the result. Never broaden a named cancellation to a user-wide or pattern-wide cancellation without new authorization.

## Compare and hand off

Before interpreting a comparison, verify checkpoint, commit, config, data split, batch size, world size, and seed. State every mismatch before drawing conclusions.

Finish with the final job state, resource shape, lineage, validation result, and any pending or failed work. If validation was run and failed, state whether the failure is environmental, pre-existing, or unresolved; never describe it as passed.

## Progress is measured on outputs, not queue state

- Before reporting array or campaign progress, open at least one completed task's output artifact; "running" from `squeue` is not progress. A stage with zero outputs after its first expected completion is a failure to report immediately.
- Smoke tests use real-sized inputs for at least one task (a toy subset hides timeouts and memory faults).
- Transfers are resumable (`rsync --partial`, chunked downloads); a self-imposed cap never discards partial data.

## Polling without hand-written sleeps

Use a monitor loop (the harness Monitor tool, or `scripts/poll_jobs.sh JOBID… --interval SECONDS`) instead of repeated `sleep` calls. State the cadence once: about a quarter of the expected duration, never below 30 minutes for multi-hour jobs, back off while unchanged. A notification turn with no change says nothing.

## Outputs in shared storage

Any run whose outputs land in shared storage uses allocation-local staging and atomic publication with one writer per artifact; there is no small-run exemption. Keep results in the established artifact root; a source edit does not update submitted jobs.

## Site conventions

Read the target host's `~/.codex/host-context.md` for partition names, per-GPU CPU allowance, array caps, nice values, controller-allowed actions and staging roots; those norms override the defaults in this skill. When a convention is confirmed in a session and missing there, append it to host-context in the same turn.

## Cancellation and reuse

- Cancelling or replacing a running job, or any job you did not submit in the current task, needs the user's explicit authorization for that job ID. A pending job you submitted in this task that can no longer run, or that your own fix supersedes, may be cancelled and resubmitted within the same resource envelope; name both job IDs in your next message.
- Derive new job scripts from the last verified launch script recorded in the task state, which also lists environment failures with their fixes; do not rewrite launch scripts from memory.
- Label every reported table with checkpoint, evaluator version and cohort size; confirm from the evaluator's documentation or code what a metric scores before naming it in a claim.

## Verified additions (2026-10-17 audit)

- A load cap you chose yourself (connections, threads, CPUs) is a default, not a site rule: when the measured rate puts the ETA past the time limit, report the rate and ETA and raise the cap within host-context norms before extending the limit.
- Before the final report, list your own pending and running jobs; cancel pending ones the task no longer needs and name the IDs, and end with one yes/no question for running ones. When the user's result depends on a job, start the watcher (`scripts/poll_jobs.sh`, or `sbatch --wait` for a single job) at submission, and run a one-minute environment-only check on the target partition first.
