# Codomyrmex Agents — cursorrules/file-specific

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

File-specific cursor rules that take **highest priority** in the rule hierarchy. Apply these rules based on the file type you are editing.

## Active Rules (6)

| Rule | File Pattern | Auto-Apply |
|------|--------------|------------|
| `python.cursorrules` | `*.py` | ✅ Always |
| `yaml.cursorrules` | `*.yaml`, `*.yml` | ✅ Always |
| `json.cursorrules` | `*.json` | ✅ Always |
| `CHANGELOG.cursorrules` | `CHANGELOG.md` | ✅ Always |
| `SPEC.cursorrules` | `SPEC.md` | ✅ Always |
| `README.md.cursorrules` | `README.md` | ✅ Always |

## Agent Guidelines

### Rule Selection Algorithm

```
1. Match file extension/name to file-specific rule
2. If match found → Apply file-specific rule
3. Then check module-specific rules
4. Then check cross-module rules
5. Fall back to general.cursorrules
```

### When Editing Python Files

1. Run `ruff` or `flake8` for linting
2. Ensure type hints on all functions
3. Add Google-style docstrings
4. Write tests in `tests/` directory

### When Editing YAML/JSON Files

1. Validate against schema if available
2. Use 2-space indentation
3. Add inline documentation (YAML only)
4. Test configuration loads correctly

### When Editing Documentation

1. Follow RASP pattern for directories
2. Use Keep a Changelog for CHANGELOG.md
3. Include Mermaid diagrams in SPEC.md
4. Add navigation links in README.md

## Key Requirements by File Type

| File Type | Critical Requirements |
|-----------|----------------------|
| Python | PEP 8, type hints, docstrings, 80%+ coverage |
| YAML | 2-space indent, schema validation, quotes for strings |
| JSON | 2-space indent, valid schema, no trailing commas |
| CHANGELOG | Semantic versioning, Keep a Changelog format |
| SPEC | Mermaid diagrams, architecture section, contracts |
| README | Overview, structure, navigation, RASP compliance |

## Operating Contracts

- File-specific rules override all other rules for matching files
- Always check file extension before applying module rules
- Maintain consistency within file types across the project
- Update file-specific rules when project standards change

## Navigation Links

- **📁 Parent Directory**: [../README.md](../README.md) - cursorrules root
- **📦 Module Rules**: [../modules/](../modules/) - 60 module rules
- **🔗 Cross-Module**: [../cross-module/](../cross-module/) - 8 cross-module rules
- **🏠 Project Root**: [../../README.md](../../README.md)
