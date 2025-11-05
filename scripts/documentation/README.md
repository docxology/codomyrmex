# Documentation Management Scripts

This directory contains tools for managing, validating, and fixing documentation across the Codomyrmex repository.

## Tools Overview

### Audit and Analysis Tools

#### `module_docs_auditor.py`
Comprehensive module documentation audit tool.

**Usage**:
```bash
python3 scripts/documentation/module_docs_auditor.py
```

**Outputs**:
- `docs/project/module-documentation-audit.md` - Detailed audit report
- `scripts/documentation/module_audit_data.json` - Structured data for automated fixes

**Features**:
- Scans all modules for missing documentation files
- Identifies broken internal references
- Checks documentation structure consistency
- Categorizes issues by severity

#### `comprehensive_audit.py`
Repository-wide documentation and signposting audit.

**Usage**:
```bash
python3 scripts/documentation/comprehensive_audit.py
```

**Outputs**:
- `docs/project/documentation-audit-report.md` - Complete audit report

**Features**:
- Scans entire repository for documentation issues
- Validates all markdown links
- Identifies duplicate content
- Checks examples migration references
- Validates navigation and cross-references

### Validation Tools

#### `validate_module_docs.py`
Fast CI/CD-ready module documentation validator.

**Usage**:
```bash
python3 scripts/documentation/validate_module_docs.py
```

**Features**:
- Validates required files exist
- Checks for broken references
- Ensures link consistency
- Returns exit code (0 = success, 1 = failure) for CI/CD

**Exit Codes**:
- `0` - All modules pass validation
- `1` - Validation errors found

#### `verify_api_specs.py`
Verifies that API_SPECIFICATION.md files match actual code signatures.

**Usage**:
```bash
python3 scripts/documentation/verify_api_specs.py
```

**Features**:
- Compares documented function signatures with actual code
- Detects mismatches between documentation and implementation
- Identifies functions documented but not implemented
- Identifies functions implemented but not documented
- Returns exit code (0 = all match, 1 = mismatches found)

**Outputs**:
- Console report with detailed mismatches
- Exit code suitable for CI/CD integration

#### `check_completeness.py`
Checks documentation for placeholder content and generates implementation status tracker.

**Usage**:
```bash
python3 scripts/documentation/check_completeness.py
```

**Features**:
- Detects placeholder content in documentation files
- Checks for required documentation files per module
- Generates implementation status tracker
- Creates detailed completeness reports

**Outputs**:
- `docs/project/implementation-status.md` - Implementation status tracker
- `docs/project/documentation-completeness.md` - Detailed completeness report
- Console summary with statistics

**Status Categories**:
- ✅ **Complete**: All required files present, no placeholders
- ⚠️ **Incomplete**: Missing files or has placeholder content
- 📝 **Missing Files**: Required documentation files missing
- 🔧 **Has Placeholders**: Contains placeholder content

### Fixer Tools

#### `fix_contributing_refs.py`
Automated fixer for CONTRIBUTING.md references.

**Usage**:
```bash
python3 scripts/documentation/fix_contributing_refs.py
```

**Requires**: `module_audit_data.json` (run `module_docs_auditor.py` first)

**Fixes**: All broken CONTRIBUTING.md references to point to `../../docs/project/contributing.md`

#### `create_example_tutorials.py`
Creates placeholder example_tutorial.md files.

**Usage**:
```bash
python3 scripts/documentation/create_example_tutorials.py
```

**Requires**: `module_audit_data.json` (run `module_docs_auditor.py` first)

**Creates**: Standardized placeholder tutorial files for modules that reference them

#### `create_missing_doc_files.py`
Creates missing documentation files that are referenced.

**Usage**:
```bash
python3 scripts/documentation/create_missing_doc_files.py
```

**Requires**: `module_audit_data.json` (run `module_docs_auditor.py` first)

**Creates**: API_SPECIFICATION.md and MCP_TOOL_SPECIFICATION.md placeholder files

#### `fix_template_paths.py`
Fixes template/module_template path references.

**Usage**:
```bash
python3 scripts/documentation/fix_template_paths.py
```

**Fixes**: References to `template/module_template/` to point to correct location

#### `comprehensive_fix.py`
Comprehensive fixer for all documentation issues.

**Usage**:
```bash
python3 scripts/documentation/comprehensive_fix.py
```

**Fixes**: 
- References in example_tutorial.md files
- References in docs/index.md files
- Updates broken links to point to existing files

### Legacy Tools

#### `check_docs_status.py`
Legacy documentation status checker.

#### `documentation_status_summary.py`
Generates documentation status summary reports.

#### `check_doc_links.py`
Validates markdown links in documentation directory.

## Workflow

### Complete Documentation Audit and Fix

```bash
# 1. Run comprehensive audit
python3 scripts/documentation/comprehensive_audit.py

# 2. Run module-specific audit
python3 scripts/documentation/module_docs_auditor.py

# 3. Fix common issues
python3 scripts/documentation/fix_contributing_refs.py
python3 scripts/documentation/create_example_tutorials.py
python3 scripts/documentation/create_missing_doc_files.py
python3 scripts/documentation/fix_template_paths.py
python3 scripts/documentation/comprehensive_fix.py

# 4. Verify API specifications
python3 scripts/documentation/verify_api_specs.py

# 5. Check documentation completeness
python3 scripts/documentation/check_completeness.py

# 6. Validate fixes
python3 scripts/documentation/validate_module_docs.py
```

### Quick Validation (CI/CD)

```bash
# Fast validation for CI/CD pipelines
python3 scripts/documentation/validate_module_docs.py
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Validate Module Documentation
  run: |
    python3 scripts/documentation/validate_module_docs.py
```

### Pre-commit Hook Example

```bash
#!/bin/bash
# .git/hooks/pre-commit

python3 scripts/documentation/validate_module_docs.py
if [ $? -ne 0 ]; then
    echo "Documentation validation failed. Please fix issues before committing."
    exit 1
fi
```

## Documentation Standards

All tools enforce the standards defined in `docs/development/documentation.md`:

- **Required Files**: README.md, AGENTS.md, SECURITY.md
- **Conditionally Required**: API_SPECIFICATION.md, MCP_TOOL_SPECIFICATION.md (if referenced)
- **Link Standards**: CONTRIBUTING.md references must point to `../../docs/project/contributing.md`

## Related Documentation

- [Documentation Guidelines](../../docs/development/documentation.md) - Complete documentation standards
- [Module Documentation Audit](../../docs/project/module-documentation-audit.md) - Latest audit results
- [Standardization Summary](../../docs/project/module-documentation-standardization-summary.md) - Implementation summary
