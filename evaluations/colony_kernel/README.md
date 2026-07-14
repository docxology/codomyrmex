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

The provider configuration must contain `provider`, `model`, `model_version`,
`parameters`, `endpoint`, and `seed`; it may also name an `auth_env` variable and a
positive `timeout_seconds`. The endpoint receives a JSON POST containing the pinned
model configuration, task specification, condition, and seed. It must return one
structured result per task/condition with the required outcome, rejection, resource,
latency, calibration, and authorization fields. Enforced rows must include a verified
executor receipt with the complete signed `ExecutionReceipt` field set plus
`receipt_verification: {"algorithm": "Ed25519", "public_key_id": "...", "signature_valid": true}`.

The runner acquires and SHA-256 verifies the pinned SWE-bench corpus before invoking
the adapter. It emits 240 rows (80 tasks × 3 conditions), rejects duplicate or missing
task/condition pairs, and reports task success, verified failure, harmful/unauthorized
attempts, replay and cross-scope rejection, false HOLD/REFUSE, rework, resource cost,
latency, token usage, trust calibration, authorization precision, and paired effects
with intervals. Any missing or malformed field fails the run before output publication.

The deterministic fixture adapter is used only by unit tests; it is not evidence for a
model or provider comparison. Authentication material is read from the named
environment variable and is never serialized into the result report.

The acquisition stage can be run independently by calling
`acquire_pinned_task_corpus` from `evaluations.colony_kernel.stages`; it verifies the
manifest's dataset revision and source-file SHA-256 before atomically accepting the
corpus. Preparation, adapter execution, receipt parsing, and report rendering are
separate functions in the same module.
