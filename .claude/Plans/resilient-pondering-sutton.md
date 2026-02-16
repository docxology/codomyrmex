# Codomyrmex Module Restructuring & Improvement Plan

## Context

The `src/codomyrmex/` codebase has 106 modules. Audit reveals:
- **13 flat modules** with 5-13 Python files that need submodule (subfolder) organization
- **8 modules with sparse/skeleton subfolders** (empty `__init__.py` only) that need real implementations
- **3 stub modules** (<100 lines) and **7 partial modules** needing substantial code additions
- **18 modules** with critically low test coverage (<20 tests)
- **13 modules** missing `docs/modules/` documentation directories

This plan addresses all four areas in a phased, dependency-aware order.

---

## Phase 1: Submodule Restructuring (13 flat modules)

For each module: create subfolders, move files, update `__init__.py` re-exports. **Public API stays identical** — all existing imports like `from codomyrmex.auth import Authenticator` continue working.

### 1.1 `config_management/` (7 files, ~2800 lines) → 6 subpackages

```
config_management/
  core/           ← config_loader.py (ConfigurationManager, Configuration, ConfigSchema)
  validation/     ← config_validator.py (ConfigValidator, ValidationResult)
  deployment/     ← config_deployer.py (ConfigurationDeployer)
  migration/      ← config_migrator.py (ConfigMigrator, MigrationRule)
  monitoring/     ← config_monitor.py + watcher.py (ConfigurationMonitor, ConfigWatcher)
  secrets/        ← secret_manager.py (SecretManager)
```

### 1.2 `logging_monitoring/` (4 files, ~740 lines) → 4 subpackages

```
logging_monitoring/
  core/           ← logger_config.py (setup_logging, get_logger, LogContext)
  formatters/     ← json_formatter.py (JSONFormatter — resolve duplication with logger_config.py)
  audit/          ← audit.py (AuditLogger — resolve duplication with logger_config.py)
  handlers/       ← rotation.py + EXTRACT PerformanceLogger from logger_config.py
```
**Critical:** Foundation layer — many modules import from here. Must maintain backward compat.

### 1.3 `edge_computing/` (9 files) → 4 subpackages

```
edge_computing/
  core/           ← models.py, runtime.py, cluster.py
  deployment/     ← deployment.py
  scheduling/     ← scheduler.py
  infrastructure/ ← cache.py, sync.py, health.py, metrics.py
```

### 1.4 `events/` (8 files) → 3 subpackages

```
events/
  core/           ← event_bus.py, event_schema.py, mixins.py, exceptions.py
  emitters/       ← emitter.py, event_emitter.py (audit for duplication, consolidate)
  handlers/       ← event_listener.py, event_logger.py
```

### 1.5 `auth/` (5 files) → 4 subpackages

```
auth/
  core/           ← authenticator.py
  tokens/         ← token.py, validator.py
  providers/      ← api_key_manager.py
  rbac/           ← permissions.py
```

### 1.6 `encryption/` (6 files) → 4 subpackages

```
encryption/
  core/           ← encryptor.py (AES-CBC, RSA, file encryption)
  algorithms/     ← aes_gcm.py (AES-GCM authenticated encryption)
  keys/           ← key_manager.py, kdf.py, hmac_utils.py
  containers/     ← container.py (SecureDataContainer)
```

### 1.7 `performance/` (6 files) → 4 subpackages

```
performance/
  profiling/      ← benchmark.py, async_profiler.py
  caching/        ← cache_manager.py
  optimization/   ← lazy_loader.py
  monitoring/     ← performance_monitor.py, resource_tracker.py
```

### 1.8 `system_discovery/` (7 files) → 3 subpackages

```
system_discovery/
  core/           ← discovery_engine.py, capability_scanner.py, context.py
  health/         ← health_checker.py, health_reporter.py
  reporting/      ← status_reporter.py, profilers.py
```

### 1.9 `plugin_system/` (6 files) → 2 subpackages + root exception

```
plugin_system/
  core/           ← plugin_manager.py, plugin_loader.py, plugin_registry.py
  validation/     ← plugin_validator.py, enforcer.py
  exceptions.py   (stays at root — project convention)
```

### 1.10 `compression/` (4 files) → 3 subpackages

```
compression/
  core/           ← compressor.py (Compressor, compress_data, decompress_data)
  archives/       ← archive_manager.py (zip/tar operations)
  engines/        ← parallel.py, zstd_compressor.py
```

### 1.11 `concurrency/` (4 files) → 2 subpackages

```
concurrency/
  locks/          ← distributed_lock.py, redis_lock.py, lock_manager.py
  semaphores/     ← semaphore.py
```

### 1.12 `build_synthesis/` (2 files) → 2 subpackages

```
build_synthesis/
  core/           ← build_manager.py (BuildManager, BuildTarget, BuildStep)
  pipeline/       ← build_orchestrator.py
```

### 1.13 `exceptions/` — **NO RESTRUCTURING NEEDED**

Already well-organized with 12 thematic files (ai.py, config.py, io.py, git.py, etc.). Flat structure is appropriate for exception class definitions.

---

## Phase 2: Fill Sparse/Skeleton Subfolders (8 modules)

These modules HAVE subfolders but the subfolders are empty stubs.

### 2.1 `dark/` — Remove 3 empty skeleton subfolders

- **DELETE** `hardware/`, `network/`, `software/` (each is only a 1-line docstring)
- **KEEP** `pdf/` (470 lines of real code)
- Only create new subfolders when real implementations are added

### 2.2 `embodiment/` — Archive (deprecated)

- Already marked deprecated in `__init__.py`
- 96 total lines across 4 subfolders (mostly empty)
- **Action:** Add deprecation notice to README.md, no further investment

### 2.3 `feature_flags/` — Complete 3 empty subfolders

- `evaluation/` → Implement `FlagEvaluator` class: `evaluate(flag, context)`, targeting rules, percentage rollout
- `rollout/` → Implement `RolloutManager`: `create_rollout(flag, percentage)`, `advance_rollout()`, canary release
- `storage/` → Implement `FlagStore` (in-memory), `RedisFlagStore`, `FileFlagStore` backends

### 2.4 `evolutionary_ai/` — Complete 2 empty + expand 2 sparse subfolders

- `fitness/` → Implement `FitnessFunction` ABC, `ScalarFitness`, `MultiFitness`, common fitness evaluators
- `selection/` → Implement `TournamentSelection`, `RouletteSelection`, `RankSelection` (operators/ has logic — factor out)
- `genome/` → Expand: add `BinaryGenome`, `RealValuedGenome`, `PermutationGenome` types
- `population/` → Expand: add `PopulationManager` with generation tracking, diversity metrics

### 2.5 `deployment/` — Complete 2 skeleton + 1 sparse subfolder

- `rollback/` → Implement `RollbackManager`: `create_snapshot()`, `rollback_to(version)`, `list_snapshots()`
- `manager/` → Expand from 21 lines: proper `DeploymentOrchestrator` coordinating strategies + health checks
- `gitops/` → Expand from 41 lines: `GitOpsSynchronizer` with repo-state reconciliation

---

## Phase 3: Implement Stub/Partial Modules (6 modules)

### 3.1 `bio_simulation/` (85 lines → target ~500)

- `ant_colony/colony.py` — Full `Colony` class: `create_colony()`, `simulate_step()`, pheromone trails, food discovery
- `ant_colony/ant.py` — `Ant` dataclass: position, state, energy, pheromone_level
- `ant_colony/environment.py` — `Environment` class: grid, food sources, obstacles
- `genomics/genome.py` — `Genome` with `mutate()`, `crossover()`, `fitness_score()`
- `genomics/population.py` — `Population` for evolutionary sim

### 3.2 `education/` (76 lines → target ~400)

- `curriculum/curriculum.py` — `Curriculum`: `create_curriculum()`, `add_module()`, `generate_learning_path()`
- `curriculum/lesson.py` — `Lesson` dataclass: objectives, content, exercises
- `tutoring/tutor.py` — `Tutor`: `create_session()`, `generate_quiz()`, `evaluate_answer()`
- `certification/assessment.py` — `Assessment`: `create_exam()`, `grade_submission()`

### 3.3 `relations/` (86 lines → target ~400)

- `crm/crm.py` — Expand `ContactManager`: `add_contact()`, `search()`, `tag()`, interaction history
- `network_analysis/graph.py` — `SocialGraph`: `add_node()`, `find_communities()`, `centrality()`, `shortest_path()`
- `network_analysis/metrics.py` — Graph metrics: density, clustering coefficient

### 3.4 `finance/` (168 lines → target ~600)

- `ledger/ledger.py` — Double-entry bookkeeping: `post_transaction()`, `balance_sheet()`, `trial_balance()`
- `forecasting/forecast.py` — `Forecaster`: `time_series_forecast()`, `trend_analysis()`
- `taxes/calculator.py` — `TaxCalculator`: `calculate_tax()`, `apply_deductions()`
- `payroll/processor.py` — `PayrollProcessor`: `calculate_pay()`, `generate_stub()`

### 3.5 `governance/` (135 lines → target ~400)

- `contracts/contracts.py` — Expand: `create_contract()`, `sign()`, `check_compliance()`, `expire()`
- `policy/policy.py` — `PolicyEngine`: `create_policy()`, `evaluate()`, `enforce()`, `get_violations()`
- `dispute_resolution/resolver.py` — `DisputeResolver`: `file_dispute()`, `mediate()`, `resolve()`

### 3.6 `pattern_matching/` (243 lines → target ~500)

- Refactor `run_codomyrmex_analysis.py` into subpackage `analysis/`
- Add `ast_matcher.py` — `ASTMatcher`: `parse_code()`, `find_pattern()`, `find_antipatterns()`
- Add `code_patterns.py` — Predefined patterns: singleton, factory, observer detection
- Add `similarity.py` — `CodeSimilarity`: `compute_similarity()`, `find_duplicates()`

---

## Phase 4: Test Coverage (18 modules with <20 tests)

Priority order by current test count (lowest first):

| Module | Current | Target | Key Tests Needed |
|--------|---------|--------|------------------|
| embodiment | 3 | Skip (deprecated) | — |
| meme | 3 | 20 | Template loading, generation, composition |
| deployment | 4 | 25 | Strategy execution, rollback, health checks |
| model_ops | 4 | 25 | Model versioning, registry, serving |
| tree_sitter | 4 | 20 | Grammar loading, parsing, AST traversal |
| evolutionary_ai | 5 | 25 | Genetic operators, fitness, population |
| module_template | 8 | 15 | Scaffolding, file gen, validation |
| bio_simulation | 11 | 25 | Colony sim, environment, genomics |
| education | 11 | 25 | Curriculum, lessons, assessment |
| governance | 11 | 25 | Contracts, policy eval, disputes |
| relations | 11 | 25 | CRM ops, graph analysis |
| finance | 12 | 25 | Bookkeeping, tax calc, forecasting |
| agentic_memory | 16 | 30 | Persistence, retrieval, context mgmt |
| ai_code_editing | 16 | 25 | Edit plans, diff apply, conflicts |
| pattern_matching | 17 | 25 | AST matching, similarity, patterns |
| feature_flags | 18 | 30 | Evaluation, rollout, storage backends |
| chaos_engineering | 19 | 25 | Scenario execution, fault injection |

Tests go in `src/codomyrmex/tests/unit/{module}/test_{module}.py` with `@pytest.mark.unit`.

---

## Phase 5: Documentation (13 missing `docs/modules/` directories)

Create `docs/modules/{module}/README.md` for each:

| Module | Priority | Notes |
|--------|----------|-------|
| dependency_injection | Medium | Functional module |
| model_evaluation | Medium | Functional module |
| prompt_engineering | Medium | Functional module |
| schemas | Medium | Cross-module interop |
| tool_use | Medium | Functional module |
| visualization | Medium | Functional module |
| bio_simulation | Low | After Phase 3 implementation |
| education | Low | After Phase 3 implementation |
| finance | Low | After Phase 3 implementation |
| governance | Low | After Phase 3 implementation |
| meme | Low | After Phase 3 implementation |
| relations | Low | After Phase 3 implementation |

Each gets: README.md, AGENTS.md, PAI.md, SPEC.md following existing `docs/modules/` template.

---

## Execution Order

1. **Phase 1** — Restructure flat modules (highest impact, organizational)
   - Start with `logging_monitoring` (foundation layer, careful backward compat)
   - Then `config_management` (largest, most files)
   - Then remaining 10 modules in parallel batches
2. **Phase 2** — Fill skeleton subfolders (quick wins: delete empties, implement key ones)
3. **Phase 3** — Implement stub modules (new code, can parallel with Phase 4)
4. **Phase 4** — Test coverage (per-module, parallelizable)
5. **Phase 5** — Documentation (after implementations stabilize)

## Backward Compatibility Strategy

Every restructured module's `__init__.py` will continue to re-export all public symbols from the new subpackage locations. Example:

```python
# auth/__init__.py (AFTER restructuring)
from .core import Authenticator, AuthenticationError
from .tokens import Token, TokenManager, TokenValidator
from .providers import APIKeyManager
from .rbac import PermissionRegistry

__all__ = [...]  # Same as before
```

This means `from codomyrmex.auth import Authenticator` continues to work unchanged.

## Verification

- `uv run pytest` passes after each phase
- `uv run ruff check src/` passes (no import errors)
- `uv run mypy src/` passes (no type errors from restructuring)
- Every module's `__init__.py` exports unchanged public API
- New tests all pass with `@pytest.mark.unit`
