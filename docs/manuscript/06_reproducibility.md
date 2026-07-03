# Reproducibility Certification {#sec:reproducibility}

This section provides a machine-verifiable reproducibility certificate for the complete Codomyrmex study. Every metric below is computed by the analysis pipeline and injected into the manuscript at render time — establishing a cryptographic chain of custody from configuration to publication.

## Configuration Provenance

[@tbl:configuration_provenance] records the source configuration identity for the rendered artifact.

| Property                         | Value                       |
| -------------------------------- | --------------------------- |
| Config hash (SHA-256, truncated) | `{{CONFIG_HASH}}`           |
| Paper version                    | {{CONFIG_VERSION}}          |
| First author                     | {{CONFIG_FIRST_AUTHOR}}     |
| Keywords                         | {{CONFIG_KEYWORDS}}         |
: Configuration provenance for the rendered manuscript. {#tbl:configuration_provenance}

The configuration hash is computed over the manuscript configuration YAML at render time. It changes whenever any parameter in that file is modified, ensuring that every rendered PDF is traceable to a specific configuration state. Version {{CONFIG_VERSION}} is the canonical identifier for this manuscript deposit.

## Generated Artifact Registry

The analysis pipeline produced the following artifacts, each validated by `infrastructure.validation.output.validator` before manuscript rendering proceeds:

[@tbl:artifact_registry] lists the generated artifact counts.

| Category                             | Count                              |
| ------------------------------------ | ---------------------------------- |
| Test suite files                     | {{ARTIFACT_TEST_SUITES}}           |
| YAML configuration files             | {{ARTIFACT_CONFIG_FILES}}          |
| MCP tool definitions                 | {{ARTIFACT_MCP_TOOLS}}             |
| Documentation files (colony\_kernel) | {{RESULT_MODULE_DOCS_COUNT}}       |
| Python source files (colony\_kernel) | {{RESULT_COLONY_KERNEL_FILES}}     |
: Generated artifact registry for the manuscript pipeline. {#tbl:artifact_registry}

All counts are live-computed at render time from the actual filesystem. No count is hand-edited into this document; the substitution pipeline enforces that any unresolved manuscript token causes a non-zero exit before the PDF renderer runs.

## Quality Gate Summary

The following gates must pass before manuscript rendering is permitted. Results are captured by `scripts/z_generate_manuscript_variables.py` and injected here at render time.

[@tbl:quality_gate_summary] repeats the quality-gate snapshot from [@tbl:quality_gates].

| Gate          | Result                            | Detail                                              |
| ------------- | --------------------------------- | --------------------------------------------------- |
| ruff          | {{RESULT_RUFF_ERRORS}} errors     | Style and correctness linting across `src/`         |
| ty            | {{RESULT_TY_ERRORS}} diagnostics  | Static type-checking via `ty check src/`            |
| pytest        | {{RESULT_TEST_COUNT}} passed      | Colony Kernel suite ([@tbl:quality_gates]), zero failures permitted |
| coverage      | {{RESULT_COVERAGE_PCT}}%          | Branch coverage against 40% floor (matches [@tbl:quality_gates]) |
: Quality gate summary used by the reproducibility certificate. {#tbl:quality_gate_summary}

All four gates must hold simultaneously. The manuscript configuration `testing.max_test_failures: 0` field enforces this constraint at the pipeline level — a single test failure blocks the render stage entirely, making a partial-pass manuscript certificate structurally impossible. The pytest count and coverage percentage reported in [@tbl:quality_gate_summary] are the same values cited in the abstract and in [@tbl:quality_gates]; they are emitted by a single pytest invocation whose JSON report feeds both sections, so no independent transcription is possible.

## Exact Reproduction Commands {#sec:repro-commands}

To reproduce the colony\_kernel test suite from a clean checkout:

```bash
# 1. Clone and enter the repository
git clone <repository-url> codomyrmex
cd codomyrmex

# 2. Install all dependencies (including dev extras)
uv sync

# 3. Run the colony_kernel suite — must yield {{RESULT_TEST_COUNT}} passing tests, 0 failures
HYPOTHESIS_NO_NPY=1 uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -v \
    --cov=src/codomyrmex/colony_kernel \
    --cov-report=term-missing \
    --cov-fail-under=40

# 4. Run the manuscript consistency guard
uv run pytest src/codomyrmex/tests/unit/colony_kernel/test_manuscript_consistency.py -v

# 5. Verify linting and type gates independently
uv run ruff check src/manuscript_variables.py src/codomyrmex/colony_kernel
uv run ty check src/manuscript_variables.py src/codomyrmex/colony_kernel

# 6. Regenerate manuscript variables from live pipeline output
uv run python scripts/z_generate_manuscript_variables.py

# 7. Confirm all tokens resolved (non-empty output = gate failure)
uv run python - <<'PY'
from pathlib import Path

needle = "{" * 2
matches = [
    str(path)
    for path in Path("output/manuscript").rglob("*")
    if path.is_file() and needle in path.read_text(encoding="utf-8", errors="ignore")
]
if matches:
    raise SystemExit("\n".join(matches))
print("All tokens resolved")
PY
```

The expected terminal summary after step 3 is `{{RESULT_TEST_COUNT}} passed` with branch coverage at or above the 40% floor. Deviations indicate either a dependency mismatch (resolve with `uv sync` against the pinned `uv.lock`) or an environment difference captured in the software specification below.

## Software Environment Specification {#sec:sw-env}

Exact software versions are pinned in `uv.lock` at the repository root. The following table records the version range and precise version used to generate the certified results.

[@tbl:software_versions] records the toolchain versions used for certification.

| Component | Version used | Minimum required | Notes |
| --------- | ------------ | ---------------- | ----- |
| Python    | {{PYTHON_VERSION}}       | 3.10             | CPython; tested on macOS arm64 and Ubuntu 22.04 x86\_64 |
| uv        | ≥0.4.0       | 0.4.0            | Dependency resolver and virtual-environment manager |
| pytest    | ≥8.0         | 7.0              | Test runner; JSON report via `--json-report` |
| pytest-cov| ≥5.0         | 4.0              | Branch coverage measurement |
| ruff      | ≥0.6.0       | 0.5.0            | Linting and formatting |
| ty        | ≥0.1.0       | 0.1.0            | Static type checker |
| SQLite    | system       | 3.35             | In-process database for `TraceStore` and `ColonyMemory` |
: Software versions used by the reproducibility certificate. {#tbl:software_versions}

Pinned dependency hashes are in `uv.lock`; reproduce the exact environment with:

```bash
uv sync --frozen   # Installs from lock file without re-solving
```

The `--frozen` flag guarantees that no dependency drift occurs between the environment that produced the certified test count and the environment used for verification.

## Evaluation Snapshot Specification {#sec:sim-spec}

The empirical snapshot reported in [@sec:results] is generated at render time
from the live repository, YAML configuration, source-code constants, and the
colony-kernel scoped pytest coverage run. The repository does not ship a
separate raw simulation trace artifact; the auditable outputs are the generated
variable snapshot, the coverage JSON, the rendered figures, and the final
HTML/PDF artifacts.

[@tbl:evaluation_snapshot] identifies the generated snapshot inputs.

| Parameter | Value | Source |
| --------- | ----- | ------ |
| Initial agent count | 5 | `config/colony_kernel/kernel.yaml` |
| Starting trust score (all agents) | 0.1 (sandbox floor) | `config/colony_kernel/roles.yaml` |
| Module registry size at launch | {{ARTIFACT_MCP_TOOLS}} MCP tool definitions | live filesystem |
| Scenario corpus — proposal count | 10 adversarial falsification vectors | `config/colony_kernel/falsification_vectors.yaml` |
| Scenario corpus — source | Defined in [@sec:falsification-vectors] | |
| Evaluation snapshot | `output/data/manuscript_variables.json` | Stage 1 output of pipeline ([@sec:pipeline-ordering]) |
| Coverage artifact | `output/data/colony_kernel_coverage.json` | pytest coverage JSON from [@sec:pipeline-ordering] |
: Evaluation snapshot inputs and generated artifacts. {#tbl:evaluation_snapshot}

**Determinism guarantee.** The colony kernel contains no stochastic components:
trust updates are closed-form updates, pheromone decay is deterministic
exponential decay applied once per tick, gate scores are deterministic
functions of four measurable dimensions, and role promotions are threshold
comparisons. No random number generator is seeded or invoked anywhere in
`src/codomyrmex/colony_kernel/`. Consequently, identical source, config, and
dependency inputs to `z_generate_manuscript_variables.py` produce the same
manuscript variable values and coverage-derived metrics. Researchers wishing to
verify this property can inspect `src/codomyrmex/colony_kernel/` for calls to
`random`, `numpy.random`, or equivalent RNG APIs; none are used in the kernel
path. The zero-mock, real-SQLite test suite further exercises this determinism
under realistic I/O boundaries, not only in isolation.

**What the provenance system does not guarantee.** The build-pipeline certificate — config hash, token injection, CI gate table, and generation timestamp — establishes that the manuscript was rendered from a specific, unmodified configuration and a clean codebase. It does *not* establish that the scenario corpus in [@sec:falsification-vectors] is representative of real-world agentic workloads, that the chosen initial trust score and agent count span the range of ecologically plausible colony sizes, or that the 10 adversarial vectors constitute a statistically complete coverage of the gate's failure modes. These are scientific-validity questions that lie outside the scope of a build-provenance certificate. Readers should treat the reported results as characterising the checked-in implementation contracts and configured protocol, not as universally predictive of behaviour under arbitrary workloads.

## Zero-Mock Verification

The colony\_kernel test suite operates under a strict zero-mock policy. All {{RESULT_TEST_COUNT}} passing tests use:

- **Real SQLite databases** — every `TraceStore` and `ColonyMemory` interaction persists to an in-process SQLite file created by pytest's `tmp_path` fixture. No in-memory mock replaces the database engine.
- **Real `TraceField` instances** — pheromone emission, decay, and signal routing are exercised on live `TraceField` objects, not stand-in dictionaries.
- **Real config loading** — `colony_kernel.config` is loaded from the actual YAML file on each test invocation. Profile state is never pre-seeded into a mock; it is read fresh from SQLite.

This policy is not merely a style preference — it is an epistemological requirement. The zero-mock constraint was what surfaced the **role-not-updating bug**: an agent's role was mutated in memory but the profile was loaded fresh from SQLite on each gate evaluation, silently discarding the mutation. A mock `ProfileStore` configured to return the updated role would have hidden this defect entirely. Real I/O forced the inconsistency into the open. Any future introduction of mocks must be treated as a reduction in the validity of the certificate this section asserts.

## Madlib Injection Verification

This manuscript demonstrates the template's token-injection ("madlib") capability: every quantitative claim is substituted from computed data at render time, not transcribed by hand.

**Which script**: `scripts/z_generate_manuscript_variables.py`

**Input files**:

- Manuscript configuration YAML — paper metadata, version, author list, keywords, experiment parameters
- `src/codomyrmex/colony_kernel/` — live filesystem scan for Python source file count
- `docs/modules/colony_kernel/` — live filesystem scan for colony-kernel documentation file count
- pytest JSON report — test count and coverage percentage
- ruff and ty exit codes and JSON outputs

**Output directory**: `output/manuscript/`

The script writes a single substitution map (key -> value) and the rendering stage applies it to every `*.md` file in `docs/manuscript/`, writing resolved copies to `output/manuscript/`. The substitution is applied with a single-pass regex replace; no token appears in the rendered output.

**The configuration token substitution pipeline as a reproducibility mechanism.** The madlib system is not merely a convenience — it is the primary mechanism by which this manuscript's numeric claims are reproducible. Every quantity cited in the abstract, results table, and gate summary traces to a named constant in the manuscript configuration YAML or to a computed value emitted by the pipeline. There is no disconnected prose claim that could silently diverge from the underlying measurement. Concretely: the weighted additive gate formula (0.30 × budget + 0.30 × risk + 0.25 × trust + 0.15 × completeness) is defined once under `experiment.gate_score_weights` and referenced symbolically wherever it appears; a change to any weight coefficient is immediately reflected in all rendered sections or triggers an unresolved-token gate failure. Similarly, the colony-kernel test count ({{RESULT_TEST_COUNT}}) is not hand-typed — it is the `RESULT_TEST_COUNT` token emitted by the pytest JSON report at render time. A reader who disagrees with a reported number can trace it to its generating script in under two grep operations.

**To verify all tokens resolved**:

```bash
uv run python - <<'PY'
from pathlib import Path

needle = "{" * 2
matches = [
    str(path)
    for path in Path("output/manuscript").rglob("*")
    if path.is_file() and needle in path.read_text(encoding="utf-8", errors="ignore")
]
if matches:
    raise SystemExit("\n".join(matches))
print("All tokens resolved")
PY
```

A non-empty match indicates an unresolved token and is treated as a gate failure. The generation timestamp embedded in this certificate is `{{GENERATION_TIMESTAMP}}`, confirming that the rendered copy was produced at a known point in time and not cached from a prior run.
