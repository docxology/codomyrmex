# Codomyrmex Agents — scripts/documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Documentation files and guides.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `analyze_content_quality.py` – Project file
- `audit_documentation.py` – Project file
- `bootstrap_agents_readmes.py` – Project file
- `deepen_src_docs.py` – Project file
- `doc_generator.py` – Project file
- `enforce_quality_gate.py` – Project file
- `enrich_docs_layer.py` – Project file
- `enrich_module_docs.py` – Project file
- `enrich_spec_and_submodules.py` – Project file
- `enrich_src_docs.py` – Project file
- `enrich_thin_readmes.py` – Project file
- `examples/` – Directory containing examples components
- `fix_docs_readmes.py` – Project file
- `fix_documentation.py` – Project file
- `fix_docusaurus_module_links.py` – Rewrites SPEC/PAI/mcp_tools links under `documentation/docs/modules` to repo-root-relative targets (run after syncing module docs)
- `fix_formatting.py` – Project file
- `fix_install_sections.py` – Project file
- `fix_readme_quality.py` – Project file
- `generate_dashboard.py` – Project file
- `improve_crossrefs.py` – Project file
- `orchestrate.py` – Project file
- `validate_agents_structure.py` – Project file
- `validate_links_comprehensive.py` – Project file

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `analyze_content_quality.py`
- `audit_documentation.py`
- `bootstrap_agents_readmes.py`
- `deepen_src_docs.py`
- `doc_generator.py`
- `enforce_quality_gate.py`
- `enrich_docs_layer.py`
- `enrich_module_docs.py`
- `enrich_spec_and_submodules.py`
- `enrich_src_docs.py`
- `enrich_thin_readmes.py`
- `fix_docs_readmes.py`
- `fix_documentation.py`
- `fix_docusaurus_module_links.py`
- `fix_formatting.py`
- `fix_install_sections.py`
- `fix_readme_quality.py`
- `generate_dashboard.py`
- `improve_crossrefs.py`
- `orchestrate.py`
- `validate_agents_structure.py`
- `validate_links_comprehensive.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
