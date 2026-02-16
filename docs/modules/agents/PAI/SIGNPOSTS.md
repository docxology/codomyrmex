# PAI Code Signposting

Precise, line-level pointers to every piece of integration code connecting Codomyrmex with [PAI](https://github.com/danielmiessler/Personal_AI_Infrastructure).

---

## Module: `agents/pai` — PAI Bridge Layer

### [pai_bridge.py](../../../src/codomyrmex/agents/pai/pai_bridge.py)

| Symbol | Lines | Purpose |
|:---|:---:|:---|
| `PAI_UPSTREAM_URL` | [L40](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Canonical upstream reference |
| `PAIConfig` | [L49-127](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Full PAI filesystem path layout (15 properties) |
| `PAIConfig.skill_md` | [L66-68](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Path to `SKILL.md` (The Algorithm) |
| `PAIConfig.telos_dir` | [L122-125](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Path to `USER/` (TELOS identity files) |
| `PAIConfig.memory_dir` | [L92-94](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Path to `MEMORY/` (three-tier store) |
| `PAIConfig.hooks_dir` | [L97-99](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Path to `hooks/` (lifecycle events) |
| `PAIConfig.security_dir` | [L101-104](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Path to `PAISECURITYSYSTEM/` |
| `PAISkillInfo` | [L128-138](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Frozen dataclass for skill metadata |
| `PAIToolInfo` | [L140-147](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Frozen dataclass for tool metadata |
| `PAIHookInfo` | [L149-157](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Frozen dataclass for hook metadata |
| `PAIAgentInfo` | [L159-166](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Frozen dataclass for agent personality |
| `PAIMemoryStore` | [L168-175](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Frozen dataclass for memory stores |
| `ALGORITHM_PHASES` | [L181-189](../../../src/codomyrmex/agents/pai/pai_bridge.py) | The 7 phases of The Algorithm v0.2.25 |
| `RESPONSE_DEPTH_LEVELS` | [L191-195](../../../src/codomyrmex/agents/pai/pai_bridge.py) | FULL / ITERATION / MINIMAL depth levels |
| `PAI_PRINCIPLES` | [L197-214](../../../src/codomyrmex/agents/pai/pai_bridge.py) | All 16 PAI Principles as structured data |
| `PAIBridge` | [L222-238](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Main bridge class (zero-mock filesystem ops) |
| `PAIBridge.is_installed` | [L247-249](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Check `SKILL.md` exists |
| `PAIBridge.get_status` | [L251-265](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Full system inventory |
| `PAIBridge.get_components` | [L267-289](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Enumerate all PAI components with counts |
| `PAIBridge.get_algorithm_version` | [L314-329](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Parse version from `SKILL.md` |
| `PAIBridge.list_skills` | [L335-368](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Scan `~/.claude/skills/` |
| `PAIBridge.list_tools` | [L388-410](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Scan `PAI/Tools/*.ts` |
| `PAIBridge.list_hooks` | [L423-453](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Scan `hooks/*.hook.*`, detect archived |
| `PAIBridge.list_active_hooks` | [L455-457](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Filter non-archived hooks |
| `PAIBridge.list_agents` | [L470-495](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Scan `~/.claude/agents/*.md` |
| `PAIBridge.list_memory_stores` | [L508-536](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Enumerate `MEMORY/` subdirs |
| `PAIBridge.get_security_config` | [L549-571](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Read security policies |
| `PAIBridge.get_telos_files` | [L577-593](../../../src/codomyrmex/agents/pai/pai_bridge.py) | List TELOS identity files |
| `PAIBridge.get_pai_env` | [L607-617](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Extract PAI environment variables |
| `PAIBridge.has_codomyrmex_mcp` | [L634-640](../../../src/codomyrmex/agents/pai/pai_bridge.py) | Check MCP registration in Desktop config |

---

### [mcp_bridge.py](../../../src/codomyrmex/agents/pai/mcp_bridge.py)

| Symbol | Lines | Purpose |
|:---|:---:|:---|
| `_TOOL_DEFINITIONS` | [L275-512](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | 15 static core tool definitions + 3 universal proxy tools |
| `_tool_list_modules` | [L63-67](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: list all Codomyrmex modules |
| `_tool_module_info` | [L70-87](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: module docstring, exports, path |
| `_tool_list_module_functions` | [L94-138](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: introspect any module's public API |
| `_tool_call_module_function` | [L141-184](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: call any public function by path |
| `_tool_get_module_readme` | [L187-215](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: read README/SPEC for any module |
| `_tool_pai_status` | [L218-222](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: PAI installation status via PAIBridge |
| `_tool_pai_awareness` | [L225-233](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: missions, projects, tasks, TELOS, memory |
| `_tool_run_tests` | [L236-267](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Handler: run pytest (120s timeout) |
| `_RESOURCE_DEFINITIONS` | [L519-533](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | 2 MCP resources (modules, status) |
| `_PROMPT_DEFINITIONS` | [L540-626](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | 10 prompt templates (analyze, debug, test, workflows) |
| `_discover_dynamic_tools` | [L637-684](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Two-phase scanner (@mcp_tool + auto-discovery) |
| `get_tool_registry` | [L691-724](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Create populated MCPToolRegistry (static + dynamic) |
| `create_codomyrmex_mcp_server` | [L727-795](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Full MCP server factory (tools, resources, prompts) |
| `call_tool` | [L798-833](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Direct Python tool invocation (no MCP overhead) |
| `get_skill_manifest` | [L836-993](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | PAI-compatible skill manifest with algorithm mapping |
| `algorithm_mapping` | [L934-942](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | Maps Algorithm phases → Codomyrmex tools |
| `knowledge_scope` | [L943-992](../../../src/codomyrmex/agents/pai/mcp_bridge.py) | 9-domain knowledge categorization of 100+ modules |

---

### [trust_gateway.py](../../../src/codomyrmex/agents/pai/trust_gateway.py)

| Symbol | Lines | Purpose |
|:---|:---:|:---|
| `TrustLevel` | [L49-54](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Enum: UNTRUSTED, VERIFIED, TRUSTED |
| `DESTRUCTIVE_TOOLS` | [L58-63](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Explicit destructive tool frozenset |
| `_DESTRUCTIVE_PATTERNS` | [L66-71](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Pattern matching for auto-discovered tools |
| `_is_destructive` | [L74-83](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Check if tool name matches destructive patterns |
| `TrustRegistry` | [L206-333](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Persistent trust ledger singleton |
| `TrustRegistry._load` | [L226-240](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Load from `~/.codomyrmex/trust_ledger.json` |
| `TrustRegistry.verify_all_safe` | [L261-273](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Promote read-only tools → VERIFIED |
| `TrustRegistry.trust_all` | [L288-301](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Promote all tools → TRUSTED |
| `verify_capabilities` | [L344-472](../../../src/codomyrmex/agents/pai/trust_gateway.py) | `/codomyrmexVerify` backing function |
| `trust_tool` | [L475-491](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Promote single tool to TRUSTED |
| `trust_all` | [L494-505](../../../src/codomyrmex/agents/pai/trust_gateway.py) | `/codomyrmexTrust` backing function |
| `trusted_call_tool` | [L518-557](../../../src/codomyrmex/agents/pai/trust_gateway.py) | Gated tool execution with trust enforcement |

---

## Module: `agents/claude` — Claude API Layer

### [claude_client.py](../../../src/codomyrmex/agents/claude/claude_client.py)

| Symbol | Lines | Purpose |
|:---|:---:|:---|
| `CLAUDE_PRICING` | [L34-42](../../../src/codomyrmex/agents/claude/claude_client.py) | Cost/1M tokens for 7 Claude models |
| `ClaudeClient.__init__` | [L63-118](../../../src/codomyrmex/agents/claude/claude_client.py) | Setup: API key, retry config, 9 capabilities |
| `ClaudeClient.register_tool` | [L123-153](../../../src/codomyrmex/agents/claude/claude_client.py) | Register function calling tools |
| `ClaudeClient._execute_impl` | [L159-168](../../../src/codomyrmex/agents/claude/claude_client.py) | Core execution entry point |
| `ClaudeClient._execute_with_retry` | [L170-284](../../../src/codomyrmex/agents/claude/claude_client.py) | Exponential backoff (3 retries, ±25% jitter) |
| `ClaudeClient._build_messages_with_system` | [L458-519](../../../src/codomyrmex/agents/claude/claude_client.py) | System prompt extraction + conversation history |
| `ClaudeClient._calculate_cost` | [L521-539](../../../src/codomyrmex/agents/claude/claude_client.py) | USD cost estimation from token usage |
| `ClaudeClient.execute_with_session` | [L543-589](../../../src/codomyrmex/agents/claude/claude_client.py) | Multi-turn session management |
| `ClaudeClient.execute_with_tools` | [L639-739](../../../src/codomyrmex/agents/claude/claude_client.py) | Auto tool execution loop (max 10 rounds) |
| `ClaudeClient.edit_file` | [L743-800+](../../../src/codomyrmex/agents/claude/claude_client.py) | AI-guided file editing |

### [claude_integration.py](../../../src/codomyrmex/agents/claude/claude_integration.py)

| Symbol | Lines | Purpose |
|:---|:---:|:---|
| `ClaudeIntegrationAdapter` | [L14-37](../../../src/codomyrmex/agents/claude/claude_integration.py) | Bridge between Claude and Codomyrmex modules |
| `adapt_for_ai_code_editing` | [L48-144](../../../src/codomyrmex/agents/claude/claude_integration.py) | Code generation with language/style optimization |
| `adapt_for_llm` | [L177-244](../../../src/codomyrmex/agents/claude/claude_integration.py) | OpenAI-compatible message format adapter |
| `adapt_for_code_execution` | [L246-319](../../../src/codomyrmex/agents/claude/claude_integration.py) | Code analysis (general/security/bugs/performance) |
| `adapt_for_code_refactoring` | [L321-374](../../../src/codomyrmex/agents/claude/claude_integration.py) | AI-guided code refactoring |
| `_build_code_generation_system_prompt` | [L376-409](../../../src/codomyrmex/agents/claude/claude_integration.py) | Optimized system prompt for PAI BUILD phase |
| `_extract_code_from_response` | [L411-436](../../../src/codomyrmex/agents/claude/claude_integration.py) | Code block extraction from markdown |
| `_parse_analysis_output` | [L438-468](../../../src/codomyrmex/agents/claude/claude_integration.py) | Structured output parser for analysis results |

---

## Module: `agents/pai/__init__.py` — Public API Surface

**Source**: [**init**.py](../../../src/codomyrmex/agents/pai/__init__.py)

Exports 30+ symbols organized into:

- **Core**: `PAIBridge`, `PAIConfig`
- **Data classes**: `PAISkillInfo`, `PAIToolInfo`, `PAIHookInfo`, `PAIAgentInfo`, `PAIMemoryStore`
- **Constants**: `ALGORITHM_PHASES`, `RESPONSE_DEPTH_LEVELS`, `PAI_PRINCIPLES`, `PAI_UPSTREAM_URL`
- **MCP Bridge**: `create_codomyrmex_mcp_server`, `get_tool_registry`, `get_skill_manifest`, `call_tool`
- **Trust Gateway**: `TrustLevel`, `TrustRegistry`, `verify_capabilities`, `trust_tool`, `trust_all`, `trusted_call_tool`

## Module: `agents/claude/__init__.py` — Public API Surface

**Source**: [**init**.py](../../../src/codomyrmex/agents/claude/__init__.py)

Exports:

- `ClaudeClient` — Full API client
- `ClaudeIntegrationAdapter` — Module bridge
- `CLAUDE_PRICING` — Cost reference
