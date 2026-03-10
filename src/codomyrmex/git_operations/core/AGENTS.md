# Codomyrmex Agents — src/codomyrmex/git_operations/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `commands/` – Directory containing commands components
- `git.py` – Project file
- `metadata.py` – Project file
- `repository.py` – Project file
- `repository_metadata.json` – Project file
- `repository_metadata.json.backup.20260304_191335` – Project file
- `repository_metadata.json.backup.20260304_191336` – Project file
- `repository_metadata.json.backup.20260304_191338` – Project file
- `repository_metadata.json.backup.20260304_191339` – Project file
- `repository_metadata.json.backup.20260304_191340` – Project file
- `repository_metadata.json.backup.20260306_145341` – Project file
- `repository_metadata.json.backup.20260306_145343` – Project file
- `repository_metadata.json.backup.20260306_145344` – Project file
- `repository_metadata.json.backup.20260306_145345` – Project file
- `repository_metadata.json.backup.20260306_145346` – Project file
- `repository_metadata.json.backup.20260307_175359` – Project file
- `repository_metadata.json.backup.20260307_175400` – Project file
- `repository_metadata.json.backup.20260307_175402` – Project file
- `repository_metadata.json.backup.20260307_175403` – Project file
- `repository_metadata.json.backup.20260307_175404` – Project file
- `repository_metadata.json.backup.20260307_181611` – Project file
- `repository_metadata.json.backup.20260307_181613` – Project file
- `repository_metadata.json.backup.20260307_181615` – Project file
- `repository_metadata.json.backup.20260307_181616` – Project file
- `repository_metadata.json.backup.20260307_181617` – Project file
- `repository_metadata.json.backup.20260307_181618` – Project file
- `repository_metadata.json.backup.20260307_190032` – Project file
- `repository_metadata.json.backup.20260307_190034` – Project file
- `repository_metadata.json.backup.20260307_190035` – Project file
- `repository_metadata.json.backup.20260307_190036` – Project file
- `repository_metadata.json.backup.20260307_190037` – Project file
- `repository_metadata.json.backup.20260307_190038` – Project file
- `repository_metadata.json.backup.20260307_203448` – Project file
- `repository_metadata.json.backup.20260307_203449` – Project file
- `repository_metadata.json.backup.20260307_203451` – Project file
- `repository_metadata.json.backup.20260307_203452` – Project file
- `repository_metadata.json.backup.20260307_203453` – Project file
- `repository_metadata.json.backup.20260307_203454` – Project file
- `repository_metadata.json.backup.20260307_204327` – Project file
- `repository_metadata.json.backup.20260307_204329` – Project file
- `repository_metadata.json.backup.20260307_204335` – Project file
- `repository_metadata.json.backup.20260307_204336` – Project file
- `repository_metadata.json.backup.20260307_204337` – Project file
- `repository_metadata.json.backup.20260307_204338` – Project file
- `repository_metadata.json.backup.20260308_132233` – Project file
- `repository_metadata.json.backup.20260308_132235` – Project file
- `repository_metadata.json.backup.20260308_132237` – Project file
- `repository_metadata.json.backup.20260308_132238` – Project file
- `repository_metadata.json.backup.20260308_132239` – Project file

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
- `__init__.py`
- `git.py`
- `metadata.py`
- `repository.py`
- `repository_metadata.json`
- `repository_metadata.json.backup.20260304_191335`
- `repository_metadata.json.backup.20260304_191336`
- `repository_metadata.json.backup.20260304_191338`
- `repository_metadata.json.backup.20260304_191339`
- `repository_metadata.json.backup.20260304_191340`
- `repository_metadata.json.backup.20260306_145341`
- `repository_metadata.json.backup.20260306_145343`
- `repository_metadata.json.backup.20260306_145344`
- `repository_metadata.json.backup.20260306_145345`
- `repository_metadata.json.backup.20260306_145346`
- `repository_metadata.json.backup.20260307_175359`
- `repository_metadata.json.backup.20260307_175400`
- `repository_metadata.json.backup.20260307_175402`
- `repository_metadata.json.backup.20260307_175403`
- `repository_metadata.json.backup.20260307_175404`
- `repository_metadata.json.backup.20260307_181611`
- `repository_metadata.json.backup.20260307_181613`
- `repository_metadata.json.backup.20260307_181615`
- `repository_metadata.json.backup.20260307_181616`
- `repository_metadata.json.backup.20260307_181617`
- `repository_metadata.json.backup.20260307_181618`
- `repository_metadata.json.backup.20260307_190032`
- `repository_metadata.json.backup.20260307_190034`
- `repository_metadata.json.backup.20260307_190035`
- `repository_metadata.json.backup.20260307_190036`
- `repository_metadata.json.backup.20260307_190037`
- `repository_metadata.json.backup.20260307_190038`
- `repository_metadata.json.backup.20260307_203448`
- `repository_metadata.json.backup.20260307_203449`
- `repository_metadata.json.backup.20260307_203451`
- `repository_metadata.json.backup.20260307_203452`
- `repository_metadata.json.backup.20260307_203453`
- `repository_metadata.json.backup.20260307_203454`
- `repository_metadata.json.backup.20260307_204327`
- `repository_metadata.json.backup.20260307_204329`
- `repository_metadata.json.backup.20260307_204335`
- `repository_metadata.json.backup.20260307_204336`
- `repository_metadata.json.backup.20260307_204337`
- `repository_metadata.json.backup.20260307_204338`
- `repository_metadata.json.backup.20260308_132233`
- `repository_metadata.json.backup.20260308_132235`
- `repository_metadata.json.backup.20260308_132237`
- `repository_metadata.json.backup.20260308_132238`
- `repository_metadata.json.backup.20260308_132239`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [git_operations](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
