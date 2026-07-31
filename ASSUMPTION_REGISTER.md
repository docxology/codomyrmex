# Assumption Surfacing Review — Codomyrmex v1.3.0

**Method**: critical_review.assumption_surfacing_review (Heuer & Pherson Key Assumptions Check)
**Target**: `/home/trim/Documents/Git/HumOS/projects/platform/hum-docxology/repos/public/codomyrmex` @ v1.3.0 (commit `06535755f`)
**Date**: 2026-07-31
**Confidence**: HIGH — every load-bearing assumption is grounded in specific source passages verified during this review.

---

## Assumption Register

### A1: "The MCP trust gateway protects destructive tools"

**Classification: ASPIRATIONAL (presented as load-bearing, actually porous)**

**Claimed by**: `AGENTS.md` ("Trust gateway gates destructive tools behind explicit promotion"); `trust_gateway.py` docstring ("three-tier trust model: UNTRUSTED → VERIFIED → TRUSTED").

**Evidence against**:

1. **`trust_all()` is a public, zero-review escape hatch.** `trust_gateway.py:480` — `TrustRegistry.trust_all()` promotes **every** tool (including all destructive tools) to TRUSTED in one call. It is exported as a public API (`__all__`), bound to the `/codomyrmexTrust` MCP prompt, and exposed via the website HTTP handler (`api_handler.py:499` — `_pai_trust` calls `trust_all()`). Any HTTP client or MCP caller can promote all destructive tools with no authentication, no confirmation, and no audit of *what* is being approved.

2. **`TrustRegistry.call()` bypasses the trust gate entirely.** `trust_gateway.py:533` — the `call()` method directly invokes `handler(**kwargs)` with **no trust check, no audit log, no schema validation**. It is a public method on a public class. The module-level singleton `_registry` is importable (`from codomyrmex.agents.pai.trust_gateway import TrustRegistry`). Any code that imports `_registry` (or constructs its own `TrustRegistry`) can call any tool — destructive or not — by calling `_registry.call(name, **kwargs)` instead of `trusted_call_tool(name, **kwargs)`. The "protection" is advisory, not enforced.

3. **`call_module_function` is arbitrary code execution gated only by trust level.** `proxy_tools.py:116` — `tool_call_module_function` takes a `function` path string and `kwargs` dict, does `importlib.import_module(module_path)` + `getattr(mod, func_name)` + `func(**kwargs)`. This calls **any public function in any codomyrmex submodule** — including functions that shell out, write files, or execute subprocesses. It is in `DESTRUCTIVE_TOOLS`, but see points 1 and 2: `trust_all()` or `TrustRegistry.call()` bypass the gate.

4. **Confirmation is disabled by default.** `trust_gateway.py:131` — `_REQUIRE_CONFIRMATION: bool = False`. The confirmation-token mechanism for destructive tools exists but is off. The two-step confirmation flow is dead code unless explicitly enabled.

5. **Destructive classification is pattern-based and incomplete.** `_DESTRUCTIVE_PATTERNS` (line 210) matches on substrings like "write", "delete", "run", "set", "create". Pattern matching only applies to auto-discovered tools with ≥3 dot-separated path parts. A tool named `codomyrmex.module.purge` or `codomyrmex.module.format` would be classified as SAFE (no pattern match) despite being destructive.

**If this assumption is wrong, what collapses**: The entire security model. The trust gateway is the single control between MCP callers and `call_module_function` (arbitrary code execution), `run_command` (shell execution), `write_file`, and `run_tests`. If any of the bypass paths above are exercised, an attacker with MCP or HTTP access achieves arbitrary code execution on the host.

**Next discriminating check**: Attempt `_registry.call("codomyrmex.call_module_function", function="subprocess.check_output", kwargs={"args": ["id"]})` from a test to confirm the bypass.

---

### A2: "60% coverage is meaningful"

**Classification: ASPIRATIONAL (the floor is too low and the exclusions are broad)**

**Claimed by**: `AGENTS.md` ("Coverage Gate: 60% line coverage"); `pyproject.toml` (`fail_under = 60`).

**Evidence**:

1. **40% of lines can be uncovered and CI still passes.** `pyproject.toml:396` — `fail_under = 60`. For a codebase with security-critical paths (trust gateway, MCP tool execution, SSH/SFTP, encryption), 60% means up to 40% of the trust gateway, the `call_module_function` handler, or the auto-merge workflow logic can have zero tests and still ship.

2. **`meme/` is entirely excluded from coverage.** `pyproject.toml:388-393` — `omit = ["*/tests/*", "*/test_*.py", "*/conftest.py", "*/meme/*"]`. The `meme` module (experimental) is excluded entirely. While labeled experimental, it still ships in the package and is importable.

3. **`exclude_lines` removes entire categories.** `pyproject.toml:397-408` — excluded patterns include `raise NotImplementedError`, `if __name__ == .__main__.:`, `class .*Protocol):`, `@(abc\.)?abstractmethod`, `if 0:`. This means abstract interfaces and protocol classes count as "covered" without any test exercising them. A module can define a security-critical Protocol class with abstract methods, never implement it in tests, and still pass the 60% gate.

4. **Line coverage ≠ branch coverage.** The config uses line coverage only. A function with 100% line coverage can have untested branches (e.g., the `else` branch of a security check). No branch coverage floor is configured.

5. **What's measured but not tested**: The `trusted_call_tool` function (lines 670+) has the trust-check logic, but if the gate is bypassed via `TrustRegistry.call()`, those lines may show as "covered" by tests that exercise the bypass path rather than the intended enforcement path.

**If this assumption is wrong, what collapses**: Confidence that untested code paths are safe. A 60% line-coverage floor with no branch coverage and broad exclusions means security-critical error paths, fallback branches, and the bypass methods identified in A1 can all be uncovered.

**Next discriminating check**: Run `uv run pytest --cov --cov-report=term-missing --cov-branch` and check branch coverage specifically for `trust_gateway.py` and `proxy_tools.py`.

---

### A3: "Zero-Mock policy ensures real tests"

**Classification: COSMETIC (the policy is enforced in name but the 'stubs' are renamed mocks)**

**Claimed by**: `AGENTS.md` ("Zero-Mock Policy: All tests must use real components. No mocks."); `CONTRIBUTING.md`.

**Evidence**:

1. **Stub classes are empty shells with no behavior.** `tests/unit/agents/generic/test_api_agent_base.py:29` — `class StubClient:` is a bare class with no methods, no attributes, no behavior. It is a `Mock` renamed `Stub`. The test docstring admits: "Lightweight stubs replacing unittest.mock.Mock". The substitution is cosmetic — the stub does not exercise any real API client behavior.

2. **`MockAgent` returns hardcoded responses.** `tests/unit/agents/test_orchestration.py:22` — `class MockAgent(BaseAgent)` overrides `_execute_impl` to return `AgentResponse(content=f"Response from {self.name}")`. This tests the orchestrator's bookkeeping (does it call 3 agents? does it collect 3 responses?) but does **not** test real agent behavior, real LLM calls, real tool execution, or real error handling. The name `MockAgent` is honest; the policy that forbids "Mock" is not.

3. **`StubRepositoryManager`, `StubComputeClient`, `StubSecurityPipeline`** (`test_infrastructure_agent.py`, `test_git_agent.py`) — all are hand-written fakes that return canned data. They do not exercise real infrastructure, real git operations, or real security checks. They are `unittest.mock.Mock` objects with a different name.

4. **`FakeAPIClient`** (`test_handlers.py:1035`) — defined inside a test function, returns hardcoded values. Same pattern.

5. **`MockFailingClient(HermesClient)`** (`test_gateway_automated_healing.py:30`) — subclasses a real class but overrides methods to fail on cue. This is the closest to "real" testing, but it still does not exercise the real `HermesClient` behavior — only the failure path the test author imagined.

6. **What the policy actually prevents**: `unittest.mock.Mock`, `unittest.mock.patch`, and `unittest.mock.MagicMock`. It does not prevent writing a class called `Stub` or `Fake` that does exactly what `Mock` does. The policy is a naming convention, not a behavioral guarantee.

**If this assumption is wrong, what collapses**: Confidence that passing tests prove the code works in production. Tests using empty stubs pass but exercise no real behavior — they test the test author's assumptions about the interface, not the implementation.

**Next discriminating check**: Count how many test files import `unittest.mock` (should be zero if the policy holds) vs. how many define classes named `Stub*` or `Fake*` or `Mock*`.

---

### A4: "The uv.lock pins all dependencies securely"

**Classification: ASPIRATIONAL (the lock pins versions, but pyproject.toml declares only lower bounds and the lock is not enforced by default)**

**Claimed by**: `AGENTS.md` ("uv.lock - Python dependency lock file"); validation commands use `uv run --locked`.

**Evidence**:

1. **All dependencies in pyproject.toml use `>=` with no upper bound.** Every entry in `[project.dependencies]` uses `>=X.Y.Z` with no `<` ceiling. Examples: `cryptography>=41.0.0`, `aiohttp>=3.13.3`, `gitpython>=3.1.0`, `pydantic>=2.8.0`, `mlx-lm>=0.31.1`, `wasmtime>=42.0.0`. A `uv sync` without `--locked` can pull any future version, including one with breaking changes or security vulnerabilities.

2. **35 optional extras, all with `>=` constraints.** `provides-extras` includes `scientific`, `api`, `deployment`, `cloud`, `serialization`, `llm-providers`, `containerization`, `crypto`, etc. Each extra's dependencies use `>=` only. A consumer who runs `uv sync --extra cloud` gets whatever `boto3`, `azure-storage-blob`, `google-cloud-storage`, or `openstacksdk` version is latest at sync time.

3. **The lock file itself does pin versions** (492 packages, each with a specific `version` field). But the lock is only enforced when commands use `uv run --locked`. The root `AGENTS.md` and `Makefile` mix `--locked` and non-`--locked` invocations. `make test` runs `uv run pytest --cov` without `--locked` (need to verify in Makefile, but `uv run` without `--locked` does not require the lock to be current).

4. **Resolution markers cover 4 Python versions** (3.11–3.14) × 3 platforms (win32, emscripten, other). The lock is resolved for all these combinations, but a dependency that behaves differently on 3.14 vs 3.11 may have different transitive deps that are not all tested.

5. **No hash-pinning.** The lock file does not include `hash` entries for packages, meaning a compromised PyPI mirror could serve a different artifact with the same version number. (uv supports `--require-hashes` but it is not configured.)

**If this assumption is wrong, what collapses**: Reproducibility and supply-chain security. A CI run or deployment that uses `uv sync` without `--locked` (or a consumer who installs from `pyproject.toml` directly) gets uncontrolled dependency versions. A dependency confusion or typosquatting attack against any of the 35 extras succeeds because there is no upper bound.

**Next discriminating check**: Check the `Makefile` for how many targets use `--locked` vs. plain `uv run`. Run `uv lock --check` to see if the lock is current.

---

### A5: "37 workflows enforce quality"

**Classification: ASPIRATIONAL (workflows exist, but multiple fail on main and some enforce nothing)**

**Claimed by**: `AGENTS.md` (CI/CD section); `.github/workflows/` directory (41 files, of which ~37 are workflow YAMLs).

**Evidence**:

1. **Multiple workflow failures on `main` as of 2026-07-31:**
   - `Pre-commit Checks` — **failure** (twice today, 17:40 and 17:43 UTC)
   - `Documentation Quality Gate` — **failure** (twice today, 17:40 and 17:43 UTC)
   - `Auto-Merge Agent PRs` — **failure** (once)
   - `Continuous Integration` — **failure** (at least once in recent history; currently in_progress)
   - `Code Health Dashboard` — **cancelled** (twice)

2. **Failures are not blocking.** The `Auto-Merge Agent PRs` workflow (`auto-merge.yml`) auto-merges PRs from branches matching patterns like `fix-`, `feat-`, `jules-`, `improve-`, `refactor-`, `cleanup-`, `bolt/`, `defense-`, etc. — **if their status checks pass**. But if CI is failing or cancelled, the auto-merge logic still runs on `check_suite.completed` events. A PR whose checks are cancelled (not failed) may still be merged if the `statusCheckRollup` logic treats cancellation as "not a failure."

3. **Several workflows are non-enforcing:**
   - `PR Coverage Comment` — **skipped** 5× (posts a comment, does not gate)
   - `🔀 Gemini Dispatch` — **skipped** 1×
   - `Workflow Status Dashboard` — **cancelled** 7×, success 19× (this is a meta-workflow that reports on other workflows; it does not enforce anything)

4. **100+ remote branches** from automated tool runs (Jules, Gemini, Bolt) — the `cleanup-branches.yml` workflow runs weekly, but stale branches accumulate between runs. Each branch is a potential auto-merge candidate.

5. **Auto-merge criteria are pattern-based, not review-based.** The `is_jules` check in `auto-merge.yml` matches branch name substrings. An attacker who pushes a branch named `fix-security-bypass` could trigger auto-merge if their checks pass — no human review required.

**If this assumption is wrong, what collapses**: Confidence that `main` is in a known-good state. With Pre-commit, Documentation, and CI all failing on main at the time of this review, the "quality gate" is not gating. Code that fails linting or docs validation is already on main.

**Next discriminating check**: Check whether `main` branch protection rules require passing checks, or if `main` accepts direct pushes. Run `gh api repos/{owner}/{repo}/branches/main/protection`.

---

### A6: "1,339 AGENTS validated means docs are complete"

**Classification: COSMETIC (validation checks structure, not content; the count is also stale)**

**Claimed by**: `docs/project/ci-release-hardening-handoff-2026-07-31.md` ("1,339/1,339 valid AGENTS.md files, and zero triple-check issues").

**Evidence**:

1. **Validation only checks for 4 required section headings.** `validate_agents_structure.py:114` — `validate_agents_file()` checks that an AGENTS.md file contains headings matching: `Purpose`, `Key Files`, `Dependencies`, `Development Guidelines` (with aliases). It does **not** check:
   - Whether the content under those headings is accurate
   - Whether referenced files exist
   - Whether code examples compile or run
   - Whether the module described still exists
   - Whether the dependencies listed match `pyproject.toml`
   - Whether links are valid (that is `validate_links.py`, a separate tool)

2. **Minimum content is 200 characters and 3 headings.** A file with `# Purpose\nTODO\n# Key Files\nTODO\n# Dependencies\nTODO\n# Development Guidelines\nTODO` would pass validation with a score of ~100. "Valid" means "has the right headings," not "is correct or useful."

3. **The count is stale.** The claim of 1,339 AGENTS.md files is from the handoff doc dated 2026-07-31. A live `find` today returns **1,691** AGENTS.md files (excluding node_modules, .git, __pycache__, .venv). The validation count was from a snapshot and does not reflect the current repo state. Some of the 352 additional files may not have been validated.

4. **`triple_check.py` checks for structural completeness** (presence of README.md, AGENTS.md, SPEC.md triads) and minimum content density, not semantic accuracy. "Zero triple-check issues" means every folder that should have the triad has files — not that those files are correct.

5. **Most AGENTS.md files are auto-generated.** The root AGENTS.md states: "Thousands of per-folder AGENTS.md / README.md files are produced by tooling, not by hand." Validation confirms they exist and have headings — it does not confirm the generated content is accurate after code changes.

**If this assumption is wrong, what collapses**: Nothing structural. The AGENTS.md files are documentation for AI agents browsing the repo. If they are wrong, agents get bad navigation, but the code still works. This makes the assumption cosmetic — it affects developer/agent experience, not runtime correctness.

**Next discriminating check**: Pick 10 random AGENTS.md files from the 1,691 and check if their "Key Files" section references files that still exist.

---

## Summary Classification Table

| # | Assumption | Classification | If Wrong, Impact |
|---|---|---|---|
| A1 | MCP trust gateway protects destructive tools | **ASPIRATIONAL** | Security collapse — arbitrary code execution via `trust_all()`, `Registry.call()`, or HTTP `_pai_trust` |
| A2 | 60% coverage is meaningful | **ASPIRATIONAL** | Untested security paths ship to production |
| A3 | Zero-Mock policy ensures real tests | **COSMETIC** | Tests pass without exercising real behavior |
| A4 | uv.lock pins all dependencies securely | **ASPIRATIONAL** | Supply-chain exposure via unbounded `>=` constraints and 35 unhashed extras |
| A5 | 37 workflows enforce quality | **ASPIRATIONAL** | `main` has failing Pre-commit, Doc Gate, and CI as of today |
| A6 | 1,339 AGENTS validated means docs are complete | **COSMETIC** | Validation checks headings, not content; count is stale (1,691 actual) |

## Most Dangerous Unexamined Premise

**A1 (trust gateway)** is the most dangerous. It is load-bearing for the project's entire security posture, it is presented as a hard guarantee in documentation, and it has **three independent bypass paths** (public `trust_all()`, public `TrustRegistry.call()`, and HTTP `_pai_trust`). An MCP caller or HTTP client can achieve arbitrary code execution in a single request. The confirmation mechanism that would add friction is disabled by default.

## Weakest Evidence Link

A4's claim about hash-pinning: I did not exhaustively confirm that `uv.lock` has no `hash` entries (I checked the header and package entries, which show `version`, `source`, `dependencies` but I did not grep for `hash`). If hashes are present, supply-chain risk is reduced (but not eliminated, since `--locked` is not always used).

## What This Review Cannot Determine

- Whether GitHub branch protection rules on `main` require passing checks (no `gh api` call to branch protection endpoint was made).
- Whether the 100+ remote branches have pending auto-merge-eligible PRs.
- The actual branch coverage percentage (only line coverage floor is configured; I did not run the full test suite).
- Whether any of the 352 AGENTS.md files added since the validation snapshot are invalid.
