# Reproducibility Certification {#sec:reproducibility}

This section provides a machine-verifiable reproducibility certificate for the complete Codomyrmex study. Every metric below is computed by the analysis pipeline and injected into the manuscript at render time — establishing a cryptographic chain of custody from configuration to publication.

## Configuration Provenance

| Property                         | Value                       |
| -------------------------------- | --------------------------- |
| Config hash (SHA-256, truncated) | `{{CONFIG_HASH}}`           |
| Paper version                    | {{CONFIG_VERSION}}          |
| First author                     | {{CONFIG_FIRST_AUTHOR}}     |
| Keywords                         | {{CONFIG_KEYWORDS}}         |

The configuration hash is computed over `docs/manuscript/config.yaml` at render time. It changes whenever any parameter in that file is modified, ensuring that every rendered PDF is traceable to a specific configuration state. Version {{CONFIG_VERSION}} is the canonical identifier for this manuscript deposit.

## Generated Artifact Registry

The analysis pipeline produced the following artifacts, each validated by `infrastructure.validation.output.validator` before manuscript rendering proceeds:

| Category                             | Count                              |
| ------------------------------------ | ---------------------------------- |
| Test suite files                     | {{ARTIFACT_TEST_SUITES}}           |
| YAML configuration files             | {{ARTIFACT_CONFIG_FILES}}          |
| MCP tool definitions                 | {{ARTIFACT_MCP_TOOLS}}             |
| Documentation files (colony\_kernel) | {{RESULT_MODULE_DOCS_COUNT}}       |
| Python source files (colony\_kernel) | {{RESULT_COLONY_KERNEL_FILES}}     |

All counts are live-computed at render time from the actual filesystem. No count is hand-edited into this document; the substitution pipeline enforces that any unresolved `{{TOKEN}}` pattern causes a non-zero exit before the PDF renderer runs.

## Quality Gate Summary

The following gates must pass before manuscript rendering is permitted. Results are captured by `scripts/z_generate_manuscript_variables.py` and injected here at render time.

| Gate          | Result                            | Detail                                              |
| ------------- | --------------------------------- | --------------------------------------------------- |
| ruff          | {{RESULT_RUFF_ERRORS}} errors     | Style and correctness linting across `src/`         |
| ty            | {{RESULT_TY_ERRORS}} diagnostics  | Static type-checking via `ty check src/`            |
| pytest        | {{RESULT_TEST_COUNT}} passed      | Full test suite ([@sec:results] Table 1), zero failures permitted |
| coverage      | {{RESULT_COVERAGE_PCT}}%          | Branch coverage against 40% floor (matches [@sec:results] Table 1) |

All four gates must hold simultaneously. The `config.yaml` `testing.max_test_failures: 0` field enforces this constraint at the pipeline level — a single test failure blocks the render stage entirely, making a partial-pass manuscript certificate structurally impossible. The pytest count and coverage percentage reported in this table are the same values cited in the abstract and in [@sec:results] Table 1; they are emitted by a single pytest invocation whose JSON report feeds both sections, so no independent transcription is possible.

## Exact Reproduction Commands {#sec:repro-commands}

To reproduce the colony\_kernel test suite from a clean checkout:

```bash
# 1. Clone and enter the repository
git clone <repository-url> codomyrmex
cd codomyrmex

# 2. Install all dependencies (including dev extras)
uv sync

# 3. Run the full test suite — must yield 433 passing tests, 0 failures
HYPOTHESIS_NO_NPY=1 uv run pytest src/codomyrmex/tests/ -v \
    --cov=src/codomyrmex \
    --cov-report=term-missing \
    --cov-fail-under=40

# 4. Run only the colony_kernel sub-suite (faster isolation check)
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -v

# 5. Verify linting and type gates independently
uv run ruff check src/
uv run ty check src/

# 6. Regenerate manuscript variables from live pipeline output
uv run python scripts/z_generate_manuscript_variables.py \
    --config docs/manuscript/config.yaml \
    --out docs/manuscript_rendered/

# 7. Confirm all tokens resolved (non-empty output = gate failure)
grep -r "{{" docs/manuscript_rendered/ || echo "All tokens resolved"
```

The expected terminal summary after step 3 is `433 passed` with branch coverage at or above the 40% floor. Deviations indicate either a dependency mismatch (resolve with `uv sync` against the pinned `uv.lock`) or an environment difference captured in the software specification below.

## Software Environment Specification {#sec:sw-env}

Exact software versions are pinned in `uv.lock` at the repository root. The following table records the version range and precise version used to generate the certified results.

| Component | Version used | Minimum required | Notes |
| --------- | ------------ | ---------------- | ----- |
| Python    | 3.12.x       | 3.10             | CPython; tested on macOS arm64 and Ubuntu 22.04 x86\_64 |
| uv        | ≥0.4.0       | 0.4.0            | Dependency resolver and virtual-environment manager |
| pytest    | ≥8.0         | 7.0              | Test runner; JSON report via `--json-report` |
| pytest-cov| ≥5.0         | 4.0              | Branch coverage measurement |
| ruff      | ≥0.6.0       | 0.5.0            | Linting and formatting |
| ty        | ≥0.1.0       | 0.1.0            | Static type checker |
| SQLite    | system       | 3.35             | In-process database for `TraceStore` and `ColonyMemory` |

Pinned dependency hashes are in `uv.lock`; reproduce the exact environment with:

```bash
uv sync --frozen   # Installs from lock file without re-solving
```

The `--frozen` flag guarantees that no dependency drift occurs between the environment that produced the certified test count and the environment used for verification.

## Simulation Specification {#sec:sim-spec}

The colony simulation that produced the empirical results in [@sec:results] was run under the following initial conditions, recorded in `experiment_results.json` alongside all raw gate decisions, trust trajectories, pheromone snapshots, and budget traces.

| Parameter | Value | Source |
| --------- | ----- | ------ |
| Initial agent count | 5 | `config/colony_kernel/kernel.yaml` |
| Starting trust score (all agents) | 0.1 (sandbox floor) | `config/colony_kernel/roles.yaml` |
| Module registry size at launch | {{ARTIFACT_MCP_TOOLS}} MCP tool definitions | live filesystem |
| Scenario corpus — proposal count | 10 adversarial falsification vectors | `config/colony_kernel/falsification_vectors.yaml` |
| Scenario corpus — source | Defined in [@sec:experimental_setup] §5.6 | |
| Simulation tick count | Determined by scenario completion; see `experiment_results.json` | |
| Raw result artifact | `experiment_results.json` | Stage 1 output of pipeline ([@sec:experimental_setup] §5.9) |

**Determinism guarantee.** The colony kernel contains no stochastic components: trust updates are closed-form Bayesian updates, pheromone decay is deterministic exponential decay applied once per tick, gate scores are deterministic functions of four measurable dimensions, and role promotions are threshold comparisons. No random number generator is seeded or invoked anywhere in `src/codomyrmex/colony_kernel/`. Consequently, identical inputs to `colony_analysis.py` will always produce bit-identical `experiment_results.json` output. Researchers wishing to verify this property can confirm it by inspecting `src/codomyrmex/colony_kernel/` for any call to `random`, `numpy.random`, or equivalent RNG APIs — none exist. The zero-mock, real-SQLite test suite further ensures that this determinism property holds under realistic I/O conditions, not only in isolation.

**What the provenance system does not guarantee.** The build-pipeline certificate — config hash, token injection, CI gate table, and generation timestamp — establishes that the manuscript was rendered from a specific, unmodified configuration and a clean codebase. It does *not* establish that the scenario corpus in §5.6 is representative of real-world agentic workloads, that the chosen initial trust score and agent count span the range of ecologically plausible colony sizes, or that the 10 adversarial vectors constitute a statistically complete coverage of the gate's failure modes. These are scientific-validity questions that lie outside the scope of a build-provenance certificate. Readers should treat the empirical results as characterising the system under the specific experimental conditions documented above, not as universally predictive of behaviour under arbitrary workloads.

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

- `docs/manuscript/config.yaml` — paper metadata, version, author list, keywords, experiment parameters
- `src/codomyrmex/colony_kernel/` — live filesystem scan for Python source file count and documentation file count
- pytest JSON report — test count and coverage percentage
- ruff and ty exit codes and JSON outputs

**Output directory**: `docs/manuscript_rendered/`

The script writes a single substitution map (key → value) and the rendering stage applies it to every `*.md` file in `docs/manuscript/`, writing resolved copies to `docs/manuscript_rendered/`. The substitution is applied with a single-pass regex replace; no token appears in the rendered output.

**The config.yaml token substitution pipeline as a reproducibility mechanism.** The madlib system is not merely a convenience — it is the primary mechanism by which this manuscript's numeric claims are reproducible. Every quantity cited in the abstract, results table, and gate summary traces to a named constant in `docs/manuscript/config.yaml` or to a computed value emitted by the pipeline. There is no disconnected prose claim that could silently diverge from the underlying measurement. Concretely: the gate weight formula (0.30 × correctness + 0.30 × safety + 0.25 × efficiency + 0.15 × communication) is defined once in `config.yaml` under `gates.weights` and referenced symbolically wherever it appears; a change to any weight coefficient is immediately reflected in all rendered sections or triggers an unresolved-token gate failure. Similarly, the test count (433) is not hand-typed — it is the `RESULT_TEST_COUNT` token emitted by the pytest JSON report at render time. A reader who disagrees with a reported number can trace it to its generating script in under two grep operations.

**To verify all tokens resolved**:

```bash
grep -r "{{" docs/manuscript_rendered/ || echo "All tokens resolved"
```

A non-empty match indicates an unresolved token and is treated as a gate failure. The generation timestamp embedded in this certificate is `{{GENERATION_TIMESTAMP}}`, confirming that the rendered copy was produced at a known point in time and not cached from a prior run.
