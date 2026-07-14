# Colony Kernel release evaluation

This harness is deliberately fail-closed. The checked-in manifest defines the 50-task
controlled suite, a pinned 30-instance SWE-bench Lite subset, and the three comparison
conditions. A provider configuration must still pin provider, model, model version,
parameters, endpoint, and seed. No benchmark result may be reported until a concrete
provider adapter has run all tasks with an environment digest and verified receipt
evidence.

Run the release evaluation only after filling the manifest and provider configuration:

```bash
uv run python evaluations/colony_kernel/runner.py \
  --provider-config path/to/provider.json \
  --environment-digest "$(uv run python -c 'from pathlib import Path; from evaluations.colony_kernel.runner import environment_digest; print(environment_digest(Path(".")))')"
```

The deterministic fixture adapter is used only by unit tests; it is not evidence for a
model or provider comparison.

The acquisition stage can be run independently by calling
`acquire_pinned_task_corpus` from `evaluations.colony_kernel.stages`; it verifies the
manifest's dataset revision and source-file SHA-256 before atomically accepting the
corpus. Preparation, adapter execution, receipt parsing, and report rendering are
separate functions in the same module.
