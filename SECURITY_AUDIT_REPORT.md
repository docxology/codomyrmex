# Codomyrmex Security Audit & Threat Model

**Reviewers**: critical_review.code_security_review + critical_review.threat_model_review  
**Date**: 2026-07-31  
**Scope**: PAI bridge trust gateway, Docker sandbox, MCP tool surface (655 tools), identity/wallet crypto, dependency supply chain, command injection, CI/CD  
**Confidence**: High — every finding is pinned to file:line evidence and corroborated by manual tracing.

---

## Executive Summary

Codomyrmex exposes **655 `@mcp_tool`-decorated functions across 185 files**, including destructive operations (`write_file`, `run_command`, `run_tests`, `call_module_function`). A three-tier trust model (UNTRUSTED → VERIFIED → TRUSTED) exists in `trust_gateway.py` and is correctly enforced on the **direct Python API path**. However, the **MCP protocol handler bypasses the trust gateway entirely**, making every tool — including destructive ones — callable without trust verification by any MCP client. Additional findings include overly permissive auto-merge criteria, several `shell=True` calls that accept user-influenced input, and restricted `eval()`/`exec()` calls in workflow and orchestration paths.

---

## Threat Model: Trust Boundaries

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Client (external)                        │
│  e.g. PAI agent, Claude, Gemini, any MCP stdio/HTTP client       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    MCP Protocol (tools/call)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCPServer._call_tool()  [transport/server.py:362]               │
│  1. Schema validation ✅                                         │
│  2. Rate-limit check ✅                                         │
│  3. Trust gateway check ❌ ← BYPASS                              │
│  4. Direct execution via _tool_registry.execute() ❌             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tool Handler (e.g. write_file, run_command, run_tests)         │
│  655 tools, many destructive                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Direct Python API: call_tool()  [mcp/server.py:214]            │
│  → trusted_call_tool()  [trust_gateway.py:638]                  │
│    1. Schema validation ✅                                      │
│    2. Trust level check ✅ (VERIFIED for safe, TRUSTED for      │
│       destructive)                                              │
│    3. Confirmation token (optional) ✅                           │
│    4. Audit log ✅                                              │
│    5. Execute via registry.call() ✅                            │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight**: Two call paths exist. Only the Python API path enforces trust. The MCP protocol path does not.

---

## Findings Table

| ID | Finding | Severity | CVSS | File:Line | Exploitability |
|----|---------|----------|------|-----------|----------------|
| F1 | MCP protocol handler bypasses trust gateway | **CRITICAL** | 9.8 | `transport/server.py:362-435` | Unauthenticated RCE via any MCP client |
| F2 | `tool_call_module_function` allows arbitrary function invocation | **CRITICAL** | 9.1 | `mcp/proxy_tools.py:116-171` | Calls any public function in any module with arbitrary kwargs |
| F3 | `trust_all()` one-shot promotion of all 655 tools | **HIGH** | 8.1 | `trust_gateway.py:480-493` | Single call grants TRUSTED to all tools including destructive |
| F4 | Auto-merge: broad branch-name pattern matching | **HIGH** | 7.5 | `auto-merge.yml:48-53` | Attacker creates branch matching pattern → auto-merge |
| F5 | `shell=True` with user-influenced commands (13 sites) | **HIGH** | 7.2 | Multiple (see below) | Command injection if input is not sanitized upstream |
| F6 | `eval()` in workflow executors (restricted builtins) | **MEDIUM** | 6.5 | `testing/workflow/executors.py:101` | Sandbox escape via attribute traversal |
| F7 | `eval()` in orchestrator mcp_tools (restricted builtins) | **MEDIUM** | 6.3 | `orchestrator/mcp_tools.py:153` | Same restricted-eval pattern |
| F8 | `exec()` in Z3 backend (validated DSL) | **MEDIUM** | 5.9 | `formal_verification/backends/z3_backend.py:133` | Executes model items in namespace |
| F9 | Docker sandbox: no seccomp profile | **MEDIUM** | 5.3 | `sandbox/resource_limits.py:12-21` | Relies only on `--cap-drop=ALL` |
| F10 | Auto-merge: `contents:write` + `pull-requests:write` permissions | **MEDIUM** | 5.0 | `auto-merge.yml:10-12` | Broad token scope for merge automation |
| F11 | HD wallet: SHA3-256 used instead of Keccak-256 for Ethereum | **MEDIUM** | 4.6 | `crypto/currency/wallet.py:270` | Produces incorrect Ethereum addresses |
| F12 | Trust ledger: env var path injection | **LOW** | 3.7 | `trust_gateway.py:337` | `CODOMYRMEX_TRUST_LEDGER_PATH` can redirect ledger |
| F13 | Vendored directories contain only docs (no vendored code) | **LOW** | 2.1 | 4 vendor dirs | No actual vendored code found |

---

## Detailed Findings

### F1: MCP Protocol Handler Bypasses Trust Gateway — CRITICAL (CVSS 9.8)

**Evidence**: `src/codomyrmex/model_context_protocol/transport/server.py:362-435`

The `MCPServer._call_tool()` method handles `tools/call` requests from MCP clients. It:
1. ✅ Validates arguments against `inputSchema`
2. ✅ Checks rate limits
3. ❌ Does NOT check trust level
4. ❌ Does NOT route through `trusted_call_tool()`
5. ❌ Directly calls `self._tool_registry.execute(tool_call)` (line 430/435)

The `create_codomyrmex_mcp_server()` function (`mcp/server.py:109-211`) creates the server with default configuration and registers tools directly. It does NOT inject the trust-enforcing `call_tool` function as `call_tool_fn`.

**Contrast**: The direct Python API `call_tool()` (`mcp/server.py:214`) correctly routes through `trusted_call_tool()`, which enforces:
- Trust level checks (VERIFIED for safe, TRUSTED for destructive)
- Schema validation before trust check
- Confirmation tokens for destructive tools
- Audit logging

**Trust boundary**: Any MCP client (PAI agent, Claude, Gemini, external tool) connecting via stdio or HTTP can invoke any of the 655 registered tools — including `codomyrmex.write_file`, `codomyrmex.run_command`, `codomyrmex.run_tests`, `codomyrmex.call_module_function` — without trust verification.

**Attack path**: 
1. Attacker-controlled or compromised MCP client connects to Codomyrmex MCP server
2. Sends `tools/call` with `name: "codomyrmex.run_command"` and arbitrary `arguments`
3. Server validates schema, checks rate limit, executes directly — no trust check
4. Arbitrary command execution on host

**Remediation**: In `create_codomyrmex_mcp_server()`, inject the trust-enforcing `call_tool` function:
```python
server = MCPServer(config=config, call_tool_fn=call_tool)
```
Or modify `_call_tool` to route through `trusted_call_tool` for destructive tools.

---

### F2: `tool_call_module_function` Allows Arbitrary Function Invocation — CRITICAL (CVSS 9.1)

**Evidence**: `src/codomyrmex/agents/pai/mcp/proxy_tools.py:116-171`

The `tool_call_module_function` tool accepts a `function` string (e.g., `"encryption.encrypt"`) and `kwargs` dict, then:
1. Auto-prefixes with `codomyrmex.` if not already prefixed
2. Splits on `.` to get module path and function name
3. Uses `importlib.import_module(module_path)` — **arbitrary module import**
4. Calls `func(**kwargs)` — **arbitrary function call with arbitrary arguments**

The only guard is `if func_name.startswith("_"): return error` — private functions are blocked, but any public function in any `codomyrmex.*` module is callable.

**Exploit path**: An attacker can call any public function in the entire Codomyrmex package surface — including functions that execute shell commands, write files, modify state, or access secrets. This tool is registered as `codomyrmex.call_module_function` and is in the `DESTRUCTIVE_TOOLS` set, but as shown in F1, the MCP protocol path doesn't enforce trust.

**Remediation**: Restrict the module allowlist, or enforce trust gateway at the MCP protocol level.

---

### F3: `trust_all()` One-Shot Promotion — HIGH (CVSS 8.1)

**Evidence**: `src/codomyrmex/agents/pai/trust_gateway.py:480-493`

```python
def trust_all(self) -> list[str]:
    """Promote **all** tools to TRUSTED. Return promoted names."""
    for name in self._levels:
        if self._levels[name] != TrustLevel.TRUSTED:
            self._levels[name] = TrustLevel.TRUSTED
            promoted.append(name)
```

A single `trust_all()` call promotes **all 655 tools** to TRUSTED, including every destructive tool. The function is also exposed as the public API `trust_all()` (line 611) and is listed in the skill manifest's `codomyrmexTrust` workflow (`mcp/server.py:367`).

While the trust model is opt-in (default is UNTRUSTED), the convenience function makes full trust escalation trivial. Any agent that calls `trust_all()` immediately gains the ability to execute all destructive tools.

**Remediation**: Consider requiring per-tool trust promotion for destructive tools, or add a confirmation gate before `trust_all()`.

---

### F4: Auto-Merge: Broad Branch-Name Pattern Matching — HIGH (CVSS 7.5)

**Evidence**: `.github/workflows/auto-merge.yml:48-53`

```python
is_jules = any(kw in branch for kw in [
    'fix-', 'feat-', 'feat/', 'improve-', 'refactor-',
    'jules-', 'add-', 'feature/', 'code-health/', 'cleanup-',
    'bolt/', 'defense-', 'bio-simulation-', 'calendar-',
    'ai-gateway-', 'simulation-'
])
```

The auto-merge workflow triggers on `check_suite` completion and `pull_request` labeled events. It auto-merges PRs where:
- The branch name contains any of 15 common prefix patterns, OR
- The PR has an `auto-merge` or `automated` label

An attacker who can create a branch (e.g., `feat-inject-malicious`) and push a PR can potentially trigger auto-merge if CI checks pass. The check-passed logic (line 60-65) also accepts `None` conclusion as passing:
```python
all_passed = all(
    c.get('conclusion') in ('SUCCESS', 'NEUTRAL', 'SKIPPED', None)
    or c.get('state') in ('SUCCESS', 'EXPECTED', 'PENDING')
    for c in checks
) if checks else False
```

A check with `conclusion: None` (pending/incomplete) is treated as passed.

**Remediation**: 
1. Require explicit `auto-merge` label only — remove branch-name heuristics
2. Treat `conclusion: None` as NOT passed
3. Require review approval before auto-merge

---

### F5: `shell=True` with User-Influenced Commands — HIGH (CVSS 7.2)

**Evidence**: 13 occurrences of `shell=True` across the codebase.

| File | Line | Risk |
|------|------|------|
| `operating_system/base.py` | 24, 253 | `run_shell(cmd)` — accepts raw command string |
| `operating_system/windows/provider.py` | 36 | Windows command execution |
| `orchestrator/_shell_exec.py` | 65 | `shell(command)` — accepts raw command string |
| `model_context_protocol/tools.py` | 449 | Shell tool exposed as MCP tool |
| `ci_cd_automation/pipeline/_execution.py` | 140 | Pipeline command execution |
| `ci_cd_automation/deployment_orchestrator.py` | 567 | Deployment hooks |
| `agents/claude/mixins/system_ops.py` | 164 | Claude agent shell executor |
| `terminal_interface/shells/_shell_session.py` | 146 | Interactive shell session |
| `cli/handlers/quick.py` | 143 | CLI pipe executor |

All carry `# nosec B602` comments asserting "trusted" context. However, several of these are reachable from MCP tools (`model_context_protocol/tools.py:449` is an MCP-exposed shell tool) and from agent invocations (`claude/mixins/system_ops.py:164`). If the MCP protocol bypass (F1) allows calling these without trust verification, the `shell=True` pattern becomes a direct command injection vector.

**Remediation**: Use `subprocess.run(["cmd", "arg1"], shell=False)` with argument lists wherever possible. For the MCP-exposed shell tool, enforce trust gateway at the protocol level.

---

### F6: `eval()` in Workflow Executors — MEDIUM (CVSS 6.5)

**Evidence**: `src/codomyrmex/testing/workflow/executors.py:101`

```python
result = eval(  # nosec B307 - restricted workflow expression DSL
    step.config.get("expression", "True"),
    {"__builtins__": {}},
    {\"ctx\": context},
)
```

Restricted builtins (`__builtins__: {}`) and limited locals (`ctx` only). However, Python's `eval` with empty builtins is still not fully sandboxed — attribute traversal via `ctx.__class__.__bases__[0].__subclasses__()` can reach dangerous types. The expression comes from `step.config`, which is workflow configuration that could be user-supplied.

---

### F7: `eval()` in Orchestrator MCP Tools — MEDIUM (CVSS 6.3)

**Evidence**: `src/codomyrmex/orchestrator/mcp_tools.py:153`

```python
return lambda *_a, **_kw: eval(  # nosec B307 - restricted expression DSL
    expr, {"__builtins__": {}}, safe_locals
)
```

Double-underscore check (`"__" in expr`) provides partial protection. Safe locals are limited to `len, sum, min, max, abs, round`. Same attribute-traversal concern as F6.

---

### F8: `exec()` in Z3 Backend — MEDIUM (CVSS 5.9)

**Evidence**: `src/codomyrmex/formal_verification/backends/z3_backend.py:133`

```python
exec(item, namespace)  # nosec B102 - validated Z3 model DSL
```

Executes Z3 model items in a namespace containing solver and optimizer objects. The items come from `self._items`, which are Z3 model definitions. If an attacker can control the model input, they can inject arbitrary Python code.

---

### F9: Docker Sandbox: No Seccomp Profile — MEDIUM (CVSS 5.3)

**Evidence**: `src/codomyrmex/coding/sandbox/resource_limits.py:12-21`

```python
DEFAULT_DOCKER_ARGS = [
    "--network=none",
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges",
    "--read-only",
    "--memory=256m",
    "--memory-swap=256m",
    "--cpus=0.5",
    "--pids-limit=50",
]
```

Good: `--network=none`, `--cap-drop=ALL`, `--security-opt=no-new-privileges`, `--read-only`, resource limits.  
Missing: No `--security-opt=seccomp=<profile>` — relies solely on `--cap-drop=ALL` for syscall filtering. Docker's default seccomp profile is applied, but a custom restrictive profile would be more robust.

**Podman shim detection**: `container.py:32-44` correctly detects `"emulate docker cli using podman"` in stderr/stdout and refuses to proceed. ✅  
**Path traversal prevention**: `container.py:121-124` validates `temp_dir` is within system temp. ✅  
**stdin file validation**: `container.py:142-145` validates `stdin_file` is inside `temp_dir`. ✅  
**Temp file creation**: `security.py:28` uses `tempfile.mkdtemp(prefix="codomyrmex_sandbox_")`. ✅

---

### F10: Auto-Merge: Broad Token Permissions — MEDIUM (CVSS 5.0)

**Evidence**: `.github/workflows/auto-merge.yml:10-12`

```yaml
permissions:
  contents: write
  pull-requests: write
```

Uses `secrets.GITHUB_TOKEN` (line 28). The `contents: write` permission allows direct commits to `main` (via squash merge). While necessary for the merge operation, this is broader than a least-privilege approach — a dedicated deploy key or restricted token would be safer.

**Good**: The AGENTS.md documentation states all workflows have `permissions: {}` at top-level (deny-all default). The `security.yml` workflow correctly uses `permissions: {}` at top level and job-level grants. ✅

---

### F11: HD Wallet: SHA3-256 Instead of Keccak-256 — MEDIUM (CVSS 4.6)

**Evidence**: `src/codomyrmex/crypto/currency/wallet.py:270`

```python
addr_hash = hashlib.sha3_256(pub_body).digest()
```

Ethereum addresses use Keccak-256, not NIST SHA3-256. These are different algorithms (different padding). This produces **incorrect Ethereum addresses**. The code acknowledges this: `"We use SHA3-256 as a simplified stand-in"`.

**Impact**: Any Ethereum address generated by this wallet will be wrong, potentially causing funds to be sent to non-existent addresses.

**Good**: The wallet is documented as "educational/reference implementation" (line 9). Key range validation is correct (lines 53-54, 164-165). BIP-32 derivation follows the standard correctly.

---

### F12: Trust Ledger: Environment Variable Path Injection — LOW (CVSS 3.7)

**Evidence**: `src/codomyrmex/agents/pai/trust_gateway.py:337`

```python
configured_path = ledger_path or os.environ.get("CODOMYRMEX_TRUST_LEDGER_PATH")
```

An attacker who can set environment variables can redirect the trust ledger to an arbitrary path. The ledger file is loaded with `json.loads()` (line 401) and processed, but invalid values are caught. The ledger path is chmod'd to 0600 (line 419-422). This is primarily a test-isolation feature, not a production attack vector.

---

### F13: Vendored Directories — LOW (CVSS 2.1)

**Evidence**: Four vendor directories found:
- `agents/openfang/vendor/` — contains only AGENTS.md, README.md, SPEC.md
- `dark/pdf/vendor/` — contains only AGENTS.md, PAI.md, README.md, SPEC.md
- `formal_verification/vendor/` — contains only AGENTS.md, README.md, SPEC.md
- `git_analysis/vendor/` — contains only AGENTS.md, README.md, SPEC.md

No actual vendored source code was found. All directories contain only documentation files. ✅

---

## Dependency Supply Chain Assessment

**Positive findings**:
- `uv.lock` pins all dependencies ✅
- `security.yml` runs 6 scanners: pip-audit, bandit, semgrep, codeql, trufflehog ✅
- `dependency-review.yml` runs GitHub dependency review on PRs ✅
- `dependabot.yml` configured for 3 ecosystems (pip, github-actions, npm) ✅
- Dependabot auto-labels with `automated` + `auto-merge` ✅ (but see F4)

**Concerns**:
- 655 MCP tools means 655 potential attack surfaces — each tool is a potential supply-chain entry point
- The `@mcp_tool` decorator auto-registers functions without trust-level assignment — trust is applied at call time, but only via the Python API (F1)
- No vendored code found (F13), but the `documentation/node_modules/` directory contains npm packages that are not covered by `uv.lock`

---

## CI/CD Assessment

| Control | Status | Evidence |
|---------|--------|----------|
| Top-level `permissions: {}` (deny-all) | ✅ Enforced | `security.yml`, documented in AGENTS.md |
| Job-level least-privilege | ✅ | `security.yml` job grants minimal permissions |
| Action version pinning | ✅ | All actions pinned to `@v4` / `@v5` tags |
| Concurrency groups | ✅ | `security.yml` has `concurrency:` block |
| Auto-merge branch-name matching | ❌ Too broad | F4 |
| Auto-merge check-passed logic | ❌ Accepts None | F4 |
| Dependabot auto-approve | ⚠️ | `dependabot-auto-approve.yml` mentioned in AGENTS.md |
| Stale PR handling | ✅ | Jules PRs exempt from stale closure |

---

## Assumption Register

| Assumption | Validated? | Risk if wrong |
|-----------|-----------|---------------|
| MCP clients are trusted | ❌ Unvalidated | F1: full RCE via any MCP client |
| `shell=True` callers sanitize input | ❌ Unvalidated | F5: command injection |
| Workflow expressions are trusted | ⚠️ Partially | F6: attribute traversal escape |
| Z3 model items are trusted | ⚠️ Partially | F8: arbitrary code exec |
| Auto-merge branch names indicate Jules | ❌ Overly broad | F4: attacker matches pattern |
| Docker default seccomp is sufficient | ⚠️ Unvalidated | F9: syscall escape |

---

## Remediation Priority

1. **P0 (Critical)**: F1 — Route MCP protocol `tools/call` through `trusted_call_tool()` in `create_codomyrmex_mcp_server()`
2. **P0 (Critical)**: F2 — Add module allowlist to `tool_call_module_function` or remove it from MCP exposure
3. **P1 (High)**: F3 — Gate `trust_all()` behind confirmation or remove it
4. **P1 (High)**: F4 — Restrict auto-merge to label-only, fix check-passed logic
5. **P1 (High)**: F5 — Audit each `shell=True` call path for user-controlled input
6. **P2 (Medium)**: F6-F8 — Replace `eval()`/`exec()` with AST-based evaluators
7. **P2 (Medium)**: F9 — Add custom seccomp profile to Docker sandbox
8. **P2 (Medium)**: F10 — Use restricted deploy token for auto-merge
9. **P3 (Low)**: F11 — Replace SHA3-256 with Keccak-256 for Ethereum addresses
10. **P3 (Low)**: F12 — Document env var as test-only
