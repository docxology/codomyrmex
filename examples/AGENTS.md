# Codomyrmex Agents — examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Example implementations and demonstrations.

## Active Components
- `README.md` – Project file
- `invalid_prompt_demo.py` – Project file
- `sample_api.py` – FastAPI sample (`uv run python examples/sample_api.py` with `fastapi` and `uvicorn`; not collected by default pytest)

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `README.md`
- `invalid_prompt_demo.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **🏠 Project Root**: ../README.md - Main project documentation
