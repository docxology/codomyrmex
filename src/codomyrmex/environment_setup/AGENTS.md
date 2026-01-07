# Codomyrmex Agents — src/codomyrmex/environment_setup

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [scripts](scripts/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Ensures the Codomyrmex platform runs in a deterministic, validated environment. Acts as the "gatekeeper" at startup, verifying dependencies, Python versions, and configuration integrity before any other module is allowed to execute. Provides fail-fast validation with helpful error messages guiding users to solutions.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `docs/` – Directory containing docs components
- `env_checker.py` – Core environment validation implementation
- `requirements.txt` – Project file
- `scripts/` – Directory containing scripts components
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Module Functions (`env_checker.py`)
- `ensure_dependencies_installed() -> None` – Check if essential Python dependencies (e.g., `cased`, `dotenv`) are installed, prints instructional messages and calls `sys.exit(1)` if missing
- `check_and_setup_env_vars(repo_root_path: str) -> None` – Check for `.env` file existence, provides instructions if missing, loads `.env` file if exists
- `is_uv_available() -> bool` – Check if `uv` package manager is available
- `is_uv_environment() -> bool` – Check if running in a `uv` environment
- `validate_python_version(required: str = ">=3.10") -> bool` – Validate Python version meets requirements

### Validation Steps
- **Python Version Validation**: Enforce Python >= 3.10
- **Manager Detection**: Detect if running under `uv`, `venv`, or system python
- **Dependency Validation**: Check essential dependencies are installed
- **Environment Variables**: Validate required environment variables
- **Configuration Files**: Check configuration file existence

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation