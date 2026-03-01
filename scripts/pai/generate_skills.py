"""Auto-Generate Codomyrmex SKILL.md Files.

Queries get_skill_manifest() to get all tools with their categories,
groups them by logical skill domain, and writes/updates SKILL.md files
under ~/.claude/skills/.  Also rebuilds the skill index via
GenerateSkillIndex.ts at the end.

Usage::

    uv run python scripts/pai/generate_skills.py [options]

    --category CATEGORY   Generate only this skill group (default: all)
    --dry-run             Print SKILL.md to stdout, no writes
    --output-dir DIR      Override output dir (default: ~/.claude/skills/)
    --no-rebuild-index    Skip GenerateSkillIndex.ts at end
    --force               Overwrite existing skills (default: merge)
    --list-categories     Show all discovered categories and exit
"""

import re
import sys
import argparse
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Category → Skill group mapping
# Maps @mcp_tool(category=...) values to the skill directory name.
# New categories not in this map are auto-named Codomyrmex{Category.title()}.
# ---------------------------------------------------------------------------
CATEGORY_GROUP_MAP: dict[str, str] = {
    # ── Git ──────────────────────────────────────────────────────────────
    "git_operations": "CodomyrmexGit",
    "git_analysis": "CodomyrmexGit",
    "git": "CodomyrmexGit",
    "git_status": "CodomyrmexGit",
    # Single-tool static git categories (derived from tool name by mcp_bridge)
    "apply_stash": "CodomyrmexGit",
    "clone_repository": "CodomyrmexGit",
    "commit_changes": "CodomyrmexGit",
    "create_branch": "CodomyrmexGit",
    "create_tag": "CodomyrmexGit",
    "create_commit_timeline_diagram": "CodomyrmexGit",
    "create_git_branch_diagram": "CodomyrmexGit",
    "create_git_workflow_diagram": "CodomyrmexGit",
    "create_repository_structure_diagram": "CodomyrmexGit",
    "get_commit_history": "CodomyrmexGit",
    "get_current_branch": "CodomyrmexGit",
    "get_status": "CodomyrmexGit",
    "initialize_git_repository": "CodomyrmexGit",
    "list_stashes": "CodomyrmexGit",
    "list_tags": "CodomyrmexGit",
    "merge_branch": "CodomyrmexGit",
    "pull_changes": "CodomyrmexGit",
    "push_changes": "CodomyrmexGit",
    "rebase_branch": "CodomyrmexGit",
    "stash_changes": "CodomyrmexGit",
    "switch_branch": "CodomyrmexGit",
    # ── Security ─────────────────────────────────────────────────────────
    "security": "CodomyrmexSecurity",
    "crypto": "CodomyrmexSecurity",
    "formal_verification": "CodomyrmexSecurity",
    # ── AI / LLM / Reasoning ─────────────────────────────────────────────
    "agents": "CodomyrmexAI",
    "agents.core": "CodomyrmexAI",
    "cerebrum": "CodomyrmexAI",
    "llm": "CodomyrmexAI",
    "orchestrator": "CodomyrmexAI",
    "collaboration": "CodomyrmexAI",
    "email": "CodomyrmexAI",
    "calendar": "CodomyrmexAI",
    "list_workflows": "CodomyrmexAI",
    # ── Code execution / analysis ─────────────────────────────────────────
    "coding": "CodomyrmexCode",
    "analyze_file": "CodomyrmexCode",
    "analyze_project": "CodomyrmexCode",
    "analyze_python": "CodomyrmexCode",
    "execute_code": "CodomyrmexCode",
    # ── Data / Visualization / Scraping ───────────────────────────────────
    "data_visualization": "CodomyrmexData",
    "scrape": "CodomyrmexData",
    "relations": "CodomyrmexData",
    "create_bar_chart": "CodomyrmexData",
    "create_line_plot": "CodomyrmexData",
    "create_pie_chart": "CodomyrmexData",
    "checksum_file": "CodomyrmexData",
    "json_query": "CodomyrmexData",
    # ── Deploy / Infrastructure ───────────────────────────────────────────
    "containerization": "CodomyrmexDeploy",
    "cloud": "CodomyrmexDeploy",
    # ── Test / Quality ────────────────────────────────────────────────────
    "performance": "CodomyrmexTest",
    "maintenance": "CodomyrmexTest",
    "validation": "CodomyrmexTest",
    "run_tests": "CodomyrmexTest",
    # ── Memory ────────────────────────────────────────────────────────────
    "agentic_memory": "codomyrmexMemory",
    # ── Search ────────────────────────────────────────────────────────────
    "search": "codomyrmexSearch",
    "search_codebase": "codomyrmexSearch",
    # ── Docs ──────────────────────────────────────────────────────────────
    "documentation": "codomyrmexDocs",
    "generate_documentation": "codomyrmexDocs",
    "get_module_readme": "codomyrmexDocs",
    # ── Status / Discovery ────────────────────────────────────────────────
    "system_discovery": "codomyrmexStatus",
    "logging": "codomyrmexStatus",
    "model_context_protocol": "codomyrmexStatus",
    "plugins": "codomyrmexStatus",
    "list_directory": "codomyrmexStatus",
    "list_module_functions": "codomyrmexStatus",
    "list_modules": "codomyrmexStatus",
    "module_info": "codomyrmexStatus",
    "pai_awareness": "codomyrmexStatus",
    "pai_status": "codomyrmexStatus",
    "read_file": "codomyrmexStatus",
    # ── Events ────────────────────────────────────────────────────────────
    "events": "CodomyrmexEvents",
    # ── Config ────────────────────────────────────────────────────────────
    "config_management": "CodomyrmexConfig",
    # ── Meta / General (main umbrella skill) ──────────────────────────────
    "general": "Codomyrmex",
    "call_module_function": "Codomyrmex",
    "invalidate_cache": "Codomyrmex",
    "run_command": "Codomyrmex",
    "write_file": "Codomyrmex",
}

# ---------------------------------------------------------------------------
# Per-skill description text (USE WHEN triggers for frontmatter)
# ---------------------------------------------------------------------------
SKILL_DESCRIPTIONS: dict[str, str] = {
    "CodomyrmexGit": (
        "Git operations and history analysis via Codomyrmex modules. "
        "USE WHEN user wants git analysis, commit timeline, contributor stats, "
        "branch diagrams, git log, push/pull/clone operations, repository history "
        "insights, git status, git diff, create branch, switch branch, commit, tag, "
        "stash, rebase, merge, compare branches, find commit, contributor analysis, "
        "git history, git blame, or cherry-pick."
    ),
    "CodomyrmexSecurity": (
        "Security scanning, crypto operations, and formal verification via Codomyrmex. "
        "USE WHEN user wants security scan, scan secrets, audit code security, "
        "scan vulnerabilities, crypto key generation, hash data, verify hash, "
        "z3 constraint, formal verify, check for leaked secrets, security audit, "
        "cryptographic operations, formal proof, find vulnerabilities, check secrets, "
        "certificate validation, key generation, hashing, prove invariant, or check "
        "satisfiability."
    ),
    "CodomyrmexAI": (
        "AI agents, reasoning, orchestration, and LLM operations via Codomyrmex. "
        "USE WHEN user wants reasoning trace, thinking agent, cerebrum knowledge, "
        "orchestrate workflow, llm provider, ask llm, generate text, execute agent, "
        "get agent memory, workflow dependencies, agentic memory, store intelligence, "
        "query knowledge base, set reasoning depth, retrieve reasoning trace, knowledge "
        "retrieval, run agent, ask question, generate response, or run thought process."
    ),
    "CodomyrmexCode": (
        "Code execution, analysis, and static analysis via Codomyrmex. "
        "USE WHEN user wants execute code, sandbox code, run python, run javascript, "
        "static analysis, code debug, analyze code error, code quality, pattern matching, "
        "find code pattern, code complexity, code review, pylint, bandit, security lint, "
        "run code in sandbox, code review, linting check, check code quality, run "
        "snippet, or debug error."
    ),
    "CodomyrmexData": (
        "Data search, scraping, and visualization via Codomyrmex. "
        "USE WHEN user wants full text search, fuzzy search, scrape html, extract content "
        "from webpage, text similarity, bar chart, pie chart, line plot, data "
        "visualization, generate chart, export dashboard, create visualization, HTML "
        "dashboard, data analysis charts, create chart, plot data, html report, "
        "visualize data, chart comparison, or data similarity."
    ),
    "CodomyrmexDeploy": (
        "Infrastructure and deployment operations via Codomyrmex. "
        "USE WHEN user wants docker build, container scan, list containers, list cloud "
        "instances, s3 bucket, upload to s3, ci pipeline, build automation, container "
        "runtime, container security scan, cloud vm, deploy, infrastructure, "
        "containerization, CI/CD, deploy code, build image, scan dockerfile, push to "
        "cloud, list running containers, or cloud storage."
    ),
    "CodomyrmexTest": (
        "Testing and performance benchmarking via Codomyrmex. "
        "USE WHEN user wants run tests, benchmark, performance regression, compare "
        "benchmarks, run pytest, test a module, check performance, benchmark comparison, "
        "detect regression, run codomyrmex tests, test suite, performance analysis, "
        "measure performance, coverage report, run unit tests, check performance, "
        "regression check, or test module."
    ),
    "codomyrmexMemory": (
        "Agentic long-term memory storage and retrieval via Codomyrmex. "
        "USE WHEN user says 'add to memory', 'store memory', 'remember this', "
        "'save to memory', 'retrieve memory', 'search memory', 'what do I remember "
        "about', 'store this for later', 'recall from memory', 'list memories', "
        "'what have you stored', 'delete memory', 'forget this', 'tagged memory', or "
        "'recall from earlier'."
    ),
    "codomyrmexSearch": (
        "High-performance codebase and document search via Codomyrmex. "
        "USE WHEN user says 'search codebase', 'find in code', 'grep pattern', "
        "'search for pattern', 'find all occurrences', 'full text search', 'fuzzy "
        "search', 'search documents', 'find files matching', 'find all uses of', "
        "'locate pattern', 'where is function', 'grep recursively', 'find definition', "
        "or wants regex/pattern search across code or text."
    ),
    "codomyrmexDocs": (
        "Retrieve and generate Codomyrmex module documentation. "
        "USE WHEN user says 'get module docs', 'module documentation', 'show me the "
        "readme for', 'what does module X do', 'generate docs', 'audit RASP "
        "compliance', 'module readme', 'module spec', 'show me the api', 'module "
        "capabilities', 'read the spec', 'what is in module', 'module exports', or "
        "wants documentation for any Codomyrmex module."
    ),
    "codomyrmexStatus": (
        "System health check and PAI awareness report for Codomyrmex. "
        "USE WHEN user says 'system status', 'health check', 'pai status', 'codomyrmex "
        "health', 'is codomyrmex working', 'check pai awareness', 'list modules', "
        "'module inventory', 'how many tools', 'system overview', 'check health', "
        "'module count', 'what modules exist', 'codomyrmex inventory', or wants a "
        "status dashboard."
    ),
    "CodomyrmexEvents": (
        "Event bus operations via Codomyrmex events module. "
        "USE WHEN user wants emit event, publish event, subscribe to events, listen for "
        "events, event history, event bus, trigger event, event type registry, "
        "event-driven, or async event handling."
    ),
    "CodomyrmexConfig": (
        "Configuration management via Codomyrmex config_management module. "
        "USE WHEN user wants get config, set config, validate config, config management, "
        "app configuration, config key, configuration store, settings management, "
        "read settings, or update settings."
    ),
    "Codomyrmex": (
        "Full-spectrum coding workspace skill providing 171 MCP tools across 33 modules. "
        "USE WHEN user says 'verify codomyrmex', 'codomyrmexVerify', 'audit codomyrmex', "
        "'trust codomyrmex', 'codomyrmexTrust', 'trust tools', 'enable destructive tools', "
        "'check pai status', 'codomyrmex tools', 'codomyrmex analyze', 'codomyrmex search', "
        "'codomyrmex memory', 'codomyrmex docs', 'codomyrmex status', 'codomyrmex git', "
        "'codomyrmex security', 'codomyrmex ai', 'codomyrmex code', 'codomyrmex data', "
        "'codomyrmex deploy', 'codomyrmex test', 'list capabilities', 'codomyrmex help', "
        "'what can codomyrmex do', 'codomyrmex capabilities', or uses any 'codomyrmex' "
        "automation tools."
    ),
}

# ---------------------------------------------------------------------------
# Algorithm phase mapping: hardcoded defaults derived from existing PAI.md files.
# These are merged with dynamically extracted phase mappings from module PAI.md.
# ---------------------------------------------------------------------------
DEFAULT_PHASE_MAPS: dict[str, dict[str, list[str]]] = {
    "CodomyrmexGit": {
        "OBSERVE": ["git_repo_status", "git_log", "git_current_branch", "git_is_repo"],
        "THINK": ["git_diff", "create_commit_timeline_diagram", "create_git_branch_diagram"],
        "BUILD": ["git_create_branch", "git_switch_branch", "stash_changes"],
        "EXECUTE": ["git_commit", "git_push", "git_pull", "git_clone"],
        "VERIFY": ["git_repo_status", "git_diff", "list_tags"],
        "LEARN": ["create_git_workflow_diagram", "create_repository_structure_diagram"],
    },
    "CodomyrmexSecurity": {
        "OBSERVE": ["audit_code_security", "scan_vulnerabilities", "scan_secrets"],
        "THINK": ["get_model", "add_item", "solve_model"],
        "VERIFY": ["scan_secrets", "verify_hash", "audit_code_security"],
        "LEARN": ["hash_data", "generate_key"],
    },
    "CodomyrmexAI": {
        "OBSERVE": ["execute_agent", "get_case_reference", "ask"],
        "THINK": ["set_reasoning_depth", "add_case_reference", "ask"],
        "PLAN": ["analyze_workflow_dependencies", "list_workflows"],
        "BUILD": ["execute_agent", "generate_text"],
        "EXECUTE": ["execute_agent", "execute_workflow", "ask"],
        "VERIFY": ["get_agent_memory", "retrieve_reasoning_trace"],
        "LEARN": ["store_reasoning_trace", "add_case_reference"],
    },
    "CodomyrmexCode": {
        "OBSERVE": ["code_review_file", "code_review_project", "analyze_python"],
        "THINK": ["code_review_file"],
        "BUILD": ["code_execute", "code_debug"],
        "EXECUTE": ["code_execute"],
        "VERIFY": ["code_review_file", "code_list_languages"],
    },
    "CodomyrmexData": {
        "OBSERVE": ["full_text_search", "fuzzy_search", "scrape_html"],
        "BUILD": ["generate_chart", "create_bar_chart", "create_pie_chart"],
        "EXECUTE": ["export_dashboard"],
        "VERIFY": ["full_text_search"],
    },
    "CodomyrmexDeploy": {
        "OBSERVE": ["container_list", "container_runtime_status", "list_cloud_instances"],
        "BUILD": ["container_build"],
        "EXECUTE": ["container_build", "upload_to_s3"],
        "VERIFY": ["container_security_scan", "container_list"],
    },
    "CodomyrmexTest": {
        "OBSERVE": ["health_check", "run_benchmark"],
        "EXECUTE": ["run_benchmark", "compare_benchmarks"],
        "VERIFY": ["detect_regression", "validate_schema", "health_check"],
    },
    "codomyrmexMemory": {
        "OBSERVE": ["search_memories", "list_memories"],
        "EXECUTE": ["store_memory"],
        "VERIFY": ["search_memories"],
        "LEARN": ["store_memory", "add_memory_tag"],
    },
    "codomyrmexSearch": {
        "OBSERVE": ["full_text_search", "fuzzy_search", "indexed_search"],
        "THINK": ["full_text_search"],
        "VERIFY": ["full_text_search"],
    },
    "codomyrmexDocs": {
        "OBSERVE": ["audit_rasp_compliance"],
        "BUILD": ["generate_module_docs"],
        "VERIFY": ["audit_rasp_compliance"],
    },
    "codomyrmexStatus": {
        "OBSERVE": ["pai_status", "list_modules", "dependency_tree", "health_check"],
        "VERIFY": ["pai_status", "health_check"],
    },
    "CodomyrmexEvents": {
        "EXECUTE": ["emit_event"],
        "OBSERVE": ["get_event_history", "list_event_types"],
        "VERIFY": ["get_event_history"],
    },
    "CodomyrmexConfig": {
        "OBSERVE": ["get_config"],
        "BUILD": ["set_config"],
        "VERIFY": ["validate_config", "get_config"],
    },
}

# ---------------------------------------------------------------------------
# Repo root for finding PAI.md files
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _REPO_ROOT / "src" / "codomyrmex"


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def collect_tools() -> list[dict[str, Any]]:
    """Query get_skill_manifest() and return annotated tool list."""
    from codomyrmex.agents.pai.mcp_bridge import get_skill_manifest
    from codomyrmex.agents.pai.trust_gateway import DESTRUCTIVE_TOOLS

    manifest = get_skill_manifest()
    tools: list[dict[str, Any]] = manifest.get("tools", [])

    for t in tools:
        name = t.get("name", "")
        t["trust_level"] = "TRUSTED" if name in DESTRUCTIVE_TOOLS else "VERIFIED"

    return tools


def group_by_skill(tools: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group tools by skill name using CATEGORY_GROUP_MAP."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for tool in tools:
        cat = tool.get("category", "general")
        skill_name = CATEGORY_GROUP_MAP.get(cat)
        if skill_name is None:
            # Auto-name new categories
            skill_name = "Codomyrmex" + "".join(
                w.capitalize() for w in cat.replace("-", "_").split("_")
            )
        groups[skill_name].append(tool)
    return dict(groups)


# ---------------------------------------------------------------------------
# Phase mapping extraction from module PAI.md files
# ---------------------------------------------------------------------------

def _find_pai_md_for_categories(categories: list[str]) -> list[Path]:
    """Find PAI.md files for module directories matching the given categories."""
    pai_mds: list[Path] = []
    for cat in categories:
        # Category value like "git_operations" → module dir "git_operations"
        module_dir = _SRC_ROOT / cat
        pai_md = module_dir / "PAI.md"
        if pai_md.exists():
            pai_mds.append(pai_md)
    return pai_mds


def extract_phase_mapping(categories: list[str], skill_name: str) -> dict[str, list[str]]:
    """Extract phase → [tool_names] from module PAI.md files.

    Falls back to DEFAULT_PHASE_MAPS if no PAI.md found or no matches.
    Merges dynamic extraction with hardcoded defaults.
    """
    phase_map: dict[str, list[str]] = defaultdict(list)

    pai_mds = _find_pai_md_for_categories(categories)
    for pai_md in pai_mds:
        try:
            content = pai_md.read_text(encoding="utf-8")
        except OSError:
            continue

        for phase in ("OBSERVE", "THINK", "PLAN", "BUILD", "EXECUTE", "VERIFY", "LEARN"):
            # Match rows like: | **OBSERVE** | ... `tool_name` ... |
            pattern = rf"\|\s*\*\*{phase}\*\*\s*\|\s*(.+?)\s*\|"
            for match in re.finditer(pattern, content):
                cell = match.group(1)
                # Extract backtick-quoted tool names
                tool_names = re.findall(r"`([a-z_][a-z0-9_]*)`", cell)
                for t in tool_names:
                    if t not in phase_map[phase]:
                        phase_map[phase].append(t)

    # Merge with defaults (defaults fill in gaps, dynamic overrides nothing)
    defaults = DEFAULT_PHASE_MAPS.get(skill_name, {})
    for phase, tools_list in defaults.items():
        if phase not in phase_map or not phase_map[phase]:
            phase_map[phase] = list(tools_list)

    return dict(phase_map)


# ---------------------------------------------------------------------------
# Manual section preservation
# ---------------------------------------------------------------------------

def extract_keep_blocks(existing_content: str) -> list[str]:
    """Extract <!-- keep-start --> ... <!-- keep-end --> blocks."""
    pattern = r"<!--\s*keep-start\s*-->(.*?)<!--\s*keep-end\s*-->"
    return re.findall(pattern, existing_content, re.DOTALL)


# ---------------------------------------------------------------------------
# SKILL.md rendering
# ---------------------------------------------------------------------------

def _build_trust_note(tools: list[dict[str, Any]]) -> str:
    """Generate a trust note if any tool is TRUSTED (destructive)."""
    trusted = [t["name"] for t in tools if t.get("trust_level") == "TRUSTED"]
    if not trusted:
        return ""
    tool_list = ", ".join(f"`{n}`" for n in trusted[:5])
    if len(trusted) > 5:
        tool_list += f" and {len(trusted) - 5} more"
    return (
        "\n> [!WARNING]\n"
        f"> The following tools are **TRUSTED** (destructive) and require "
        f"`/codomyrmexTrust` before use: {tool_list}\n"
    )


def _build_common_operations(tools: list[dict[str, Any]], skill_name: str) -> str:
    """Build a minimal 'Common Operations' section with a usage example."""
    if not tools:
        return ""

    # Pick up to 3 representative tools for the example
    sample = tools[:3]
    lines = [
        "## Common Operations\n",
        "```python",
        "from codomyrmex.agents.pai import trusted_call_tool\n",
    ]
    for t in sample:
        name = t["name"]
        # Build a simple call with placeholder args from schema
        schema = t.get("input_schema", {})
        props = schema.get("properties", {}) if isinstance(schema, dict) else {}
        required = schema.get("required", []) if isinstance(schema, dict) else []
        if required:
            args = ", ".join(f'{k}="..."' for k in required[:3])
            lines.append(f'result = trusted_call_tool("{name}", {args})')
        else:
            lines.append(f'result = trusted_call_tool("{name}")')
    lines.append("```")
    return "\n".join(lines)


def _build_key_tools_table(tools: list[dict[str, Any]]) -> str:
    """Build the Key Tools markdown table."""
    rows = ["## Key Tools\n", "| Tool | Description | Trust Level |", "|------|-------------|-------------|"]
    for t in sorted(tools, key=lambda x: x["name"]):
        name = t["name"]
        desc = (t.get("description") or "").split("\n")[0].strip()
        # Cap description at 80 chars
        if len(desc) > 80:
            desc = desc[:77] + "..."
        desc = desc.replace("|", "\\|")
        trust = t.get("trust_level", "VERIFIED")
        rows.append(f"| `{name}` | {desc} | {trust} |")
    return "\n".join(rows)


def _build_phase_mapping(phase_map: dict[str, list[str]]) -> str:
    """Build the Algorithm Phase Mapping table."""
    if not phase_map:
        return ""

    ordered_phases = ["OBSERVE", "THINK", "PLAN", "BUILD", "EXECUTE", "VERIFY", "LEARN"]
    rows = ["## Algorithm Phase Mapping\n", "| Phase | Tools |", "|-------|-------|"]
    for phase in ordered_phases:
        tools_list = phase_map.get(phase, [])
        if tools_list:
            tool_str = ", ".join(f"`{t}`" for t in tools_list)
            rows.append(f"| **{phase}** | {tool_str} |")
    return "\n".join(rows)


def render_skill_md(
    skill_name: str,
    tools: list[dict[str, Any]],
    categories: list[str],
    existing_content: str = "",
) -> str:
    """Render a complete SKILL.md file for the given skill group."""
    description = SKILL_DESCRIPTIONS.get(skill_name, _auto_description(skill_name, categories))
    phase_map = extract_phase_mapping(categories, skill_name)

    # Preserve manual keep blocks
    keep_blocks = extract_keep_blocks(existing_content)

    # Determine module summary line
    module_str = ", ".join(f"`{c}`" for c in sorted(set(categories)))
    summary = f"{skill_name} operations using Codomyrmex modules: {module_str}."

    parts = [
        f"---",
        f"name: {skill_name}",
        f"description: {description}",
        f"---",
        f"# {skill_name}",
        "",
        summary,
        "",
    ]

    # Trust warning if applicable
    trust_note = _build_trust_note(tools)
    if trust_note:
        parts.append(trust_note)

    # Common operations
    common_ops = _build_common_operations(tools, skill_name)
    if common_ops:
        parts.append(common_ops)
        parts.append("")

    # Key tools table
    tools_table = _build_key_tools_table(tools)
    if tools_table:
        parts.append(tools_table)
        parts.append("")

    # Phase mapping
    phase_section = _build_phase_mapping(phase_map)
    if phase_section:
        parts.append(phase_section)
        parts.append("")

    # Re-inject preserved keep blocks
    for block in keep_blocks:
        parts.append(f"<!-- keep-start -->{block}<!-- keep-end -->")
        parts.append("")

    return "\n".join(parts)


def _auto_description(skill_name: str, categories: list[str]) -> str:
    """Generate a fallback description for skills not in SKILL_DESCRIPTIONS."""
    cat_str = ", ".join(categories)
    return (
        f"{skill_name} operations via Codomyrmex. "
        f"USE WHEN user wants {cat_str} operations, "
        f"or uses any codomyrmex {cat_str} tools."
    )


# ---------------------------------------------------------------------------
# Write and index rebuild
# ---------------------------------------------------------------------------

def write_skill(
    skill_name: str,
    content: str,
    output_dir: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> None:
    """Write (or print) the SKILL.md for a skill."""
    if dry_run:
        print(f"\n{'='*70}")
        print(f"DRY RUN: {output_dir / skill_name / 'SKILL.md'}")
        print('='*70)
        print(content)
        return

    skill_dir = output_dir / skill_name
    skill_path = skill_dir / "SKILL.md"

    if skill_path.exists() and not force:
        # Merge: read existing, preserve keep blocks, regenerate rest
        existing = skill_path.read_text(encoding="utf-8")
        # Content was already rendered with keep blocks — just write it
        print(f"  [merge] {skill_path}")
    else:
        print(f"  [write] {skill_path}")

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(content, encoding="utf-8")


def rebuild_index(output_dir: Path) -> None:
    """Run GenerateSkillIndex.ts to rebuild the skill index."""
    index_script = Path.home() / ".claude" / "skills" / "PAI" / "Tools" / "GenerateSkillIndex.ts"
    if not index_script.exists():
        print(f"  [skip] GenerateSkillIndex.ts not found at {index_script}")
        return

    print(f"  [rebuild] Running {index_script}...")
    result = subprocess.run(
        ["bun", str(index_script)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode == 0:
        print("  [ok] Skill index rebuilt.")
    else:
        print(f"  [warn] GenerateSkillIndex.ts exited {result.returncode}")
        if result.stderr:
            print(f"         stderr: {result.stderr[:200]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--category",
        metavar="SKILL",
        help="Generate only this skill group (e.g. CodomyrmexGit)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print SKILL.md to stdout; no writes",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=str(Path("~/.claude/skills").expanduser()),
        help="Output directory (default: ~/.claude/skills/)",
    )
    parser.add_argument(
        "--no-rebuild-index",
        action="store_true",
        help="Skip GenerateSkillIndex.ts at end",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing skills without merging keep blocks",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="Show all discovered @mcp_tool categories and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()

    print("Collecting tools from get_skill_manifest()...")
    try:
        tools = collect_tools()
    except ImportError as exc:
        print(f"ERROR: Could not import codomyrmex: {exc}", file=sys.stderr)
        print("Run this script via: uv run python scripts/pai/generate_skills.py", file=sys.stderr)
        return 1

    print(f"  Found {len(tools)} tools.")

    # List categories mode
    if args.list_categories:
        cats: dict[str, int] = defaultdict(int)
        for t in tools:
            cats[t.get("category", "general")] += 1
        print("\nDiscovered categories:")
        for cat, count in sorted(cats.items()):
            skill = CATEGORY_GROUP_MAP.get(cat, f"Codomyrmex{cat.title()}")
            print(f"  {cat:<28} ({count:3} tools) → {skill}")
        return 0

    # Group tools by skill
    groups = group_by_skill(tools)
    print(f"  Grouped into {len(groups)} skills: {', '.join(sorted(groups))}")

    # Filter to specific skill if requested
    if args.category:
        if args.category not in groups:
            print(f"ERROR: Skill '{args.category}' not found. Known: {', '.join(sorted(groups))}")
            return 1
        groups = {args.category: groups[args.category]}

    # Build reverse mapping: skill_name → categories
    skill_to_cats: dict[str, list[str]] = defaultdict(list)
    for cat, skill_name in CATEGORY_GROUP_MAP.items():
        skill_to_cats[skill_name].append(cat)

    # Generate each skill
    generated = 0
    for skill_name, skill_tools in sorted(groups.items()):
        categories = skill_to_cats.get(skill_name, [])
        if not categories:
            # Auto-named category: derive from skill name
            categories = [skill_name.replace("Codomyrmex", "").lower()]

        # Read existing content for keep-block preservation
        existing_path = output_dir / skill_name / "SKILL.md"
        existing_content = ""
        if existing_path.exists() and not args.force:
            existing_content = existing_path.read_text(encoding="utf-8")

        content = render_skill_md(skill_name, skill_tools, categories, existing_content)

        write_skill(
            skill_name,
            content,
            output_dir,
            dry_run=args.dry_run,
            force=args.force,
        )
        generated += 1

    if not args.dry_run:
        print(f"\nGenerated {generated} SKILL.md files in {output_dir}")

        if not args.no_rebuild_index:
            rebuild_index(output_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
