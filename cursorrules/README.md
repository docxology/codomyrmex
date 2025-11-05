# Cursor Rules Organization

This directory contains all `.cursorrules` files for the Codomyrmex project, organized by type and purpose.

## Directory Structure

```
cursorrules/
├── README.md                          # This file - documentation of the cursorrules organization
├── general.cursorrules                 # Root project-wide rules (applies to entire project)
├── modules/                           # Module-specific rules
│   ├── ai_code_editing.cursorrules
│   ├── documentation.cursorrules
│   ├── environment_setup.cursorrules
│   ├── git_operations.cursorrules
│   ├── logging_monitoring.cursorrules
│   ├── model_context_protocol.cursorrules
│   └── module_template.cursorrules
├── cross-module/                      # Cross-cutting concerns affecting multiple modules
│   ├── build_synthesis.cursorrules
│   ├── code_execution_sandbox.cursorrules
│   ├── data_visualization.cursorrules
│   ├── logging_monitoring.cursorrules
│   ├── model_context_protocol.cursorrules
│   ├── output_module.cursorrules
│   ├── pattern_matching.cursorrules
│   ├── static_analysis.cursorrules
│   └── template_module.cursorrules
└── file-specific/                     # Rules for specific files or file types
    └── README.md.cursorrules
```

## Organization Rationale

### `general.cursorrules`
The root-level general rules that apply to the entire Codomyrmex project. All other cursorrules files supplement these general principles.

### `modules/`
Contains rules specific to individual Codomyrmex modules. These rules apply when working *within* a specific module's directory, focusing on developing and maintaining that module itself. They supplement the general rules.

### `cross-module/`
Contains rules for concerns that span multiple modules or are used across the project. These focus on *using* shared functionality across modules. Examples include:
- Build and synthesis processes
- Code execution sandboxes
- Data visualization
- Pattern matching
- Static analysis
- Template usage (using templates across the project)
- Using logging_monitoring in other modules
- Using MCP (Model Context Protocol) in other modules

**Important**: Some modules appear in both `modules/` and `cross-module/`:
- **`modules/<module>.cursorrules`**: Rules for developing/maintaining the module itself
- **`cross-module/<module>.cursorrules`**: Rules for using that module in other modules

This distinction exists for:
- `logging_monitoring`: Module implementation vs. cross-module logging patterns
- `model_context_protocol`: MCP specification/implementation vs. using MCP across modules
- `template_module` vs `module_template`: Using templates vs. maintaining the template itself

### `file-specific/`
Contains rules for specific files or file types that require special handling. Currently includes rules for the root `README.md` file.

## How Cursor Loads These Files

Cursor looks for `.cursorrules` files in specific locations:
1. **Root level**: `general.cursorrules` (or `.cursorrules`) at the project root
2. **Module directories**: `.cursor/.cursorrules` in module directories

To maintain compatibility, we use symlinks:
- A symlink from the root `general.cursorrules` → `cursorrules/general.cursorrules`
- Symlinks in module directories pointing to the appropriate files in `cursorrules/modules/`

## Adding New Cursor Rules

### Adding a Module-Specific Rule
1. Create a new file in `cursorrules/modules/<module_name>.cursorrules`
2. Follow the structure of existing module rules
3. Reference `general.cursorrules` in the preamble
4. Create a symlink in the module's `.cursor/.cursorrules` if needed

### Adding a Cross-Module Rule
1. Create a new file in `cursorrules/cross-module/<concern_name>.cursorrules`
2. Document which modules this rule affects
3. Reference `general.cursorrules` in the preamble

### Adding a File-Specific Rule
1. Create a new file in `cursorrules/file-specific/<filename>.cursorrules`
2. Clearly document which file(s) this rule applies to
3. Reference `general.cursorrules` in the preamble

## File Naming Conventions

- Use lowercase with underscores: `module_name.cursorrules`
- Match the module or concern name from the codebase
- Keep names descriptive and consistent

## Updating Rules

When updating cursorrules:
1. Update the relevant file in the `cursorrules/` directory
2. Ensure internal references are updated (especially path references)
3. Update this README if the organization structure changes
4. Test that Cursor can still find and load the rules correctly

## Quick Reference Table

| Module/Concern | Module-Specific | Cross-Module | Notes |
|----------------|----------------|--------------|-------|
| `ai_code_editing` | ✓ | - | Module-specific only |
| `documentation` | ✓ | - | Module-specific only |
| `environment_setup` | ✓ | - | Module-specific only |
| `git_operations` | ✓ | - | Module-specific only |
| `logging_monitoring` | ✓ | ✓ | Implementation vs. usage |
| `model_context_protocol` | ✓ | ✓ | Specification vs. consumption |
| `module_template` | ✓ | - | Template itself |
| `template_module` | - | ✓ | Using templates |
| `build_synthesis` | - | ✓ | Cross-module only |
| `code_execution_sandbox` | - | ✓ | Cross-module only |
| `data_visualization` | - | ✓ | Cross-module only |
| `output_module` | - | ✓ | Cross-module only |
| `pattern_matching` | - | ✓ | Cross-module only |
| `static_analysis` | - | ✓ | Cross-module only |
| `README.md` | - | - | File-specific |

## References in Rules

When writing cursorrules files, reference other rules using:
- `general.cursorrules` for the root general rules
- `modules/<module_name>.cursorrules` for module-specific rules (developing the module)
- `cross-module/<concern_name>.cursorrules` for cross-module rules (using shared functionality)
- Use relative paths from the `cursorrules/` directory when appropriate

## Troubleshooting

### Finding the Right Cursorrules File

**Question**: "I'm working on a module, which cursorrules should I use?"

**Answer**: 
1. Always start with `general.cursorrules` (applies to everything)
2. If working *within* a module's directory, check `modules/<module_name>.cursorrules`
3. If *using* a shared module (like logging or MCP), also check `cross-module/<module_name>.cursorrules`
4. If working with a specific file type, check `file-specific/`

**Example**: When working in `ai_code_editing` module:
- Use: `general.cursorrules` + `modules/ai_code_editing.cursorrules`
- If using logging: also reference `cross-module/logging_monitoring.cursorrules`
- If defining MCP tools: also reference `cross-module/model_context_protocol.cursorrules`

### Verifying Symlinks

To verify all symlinks are working correctly:

```bash
# Check root symlink
ls -la general.cursorrules

# Check module symlinks
find src/codomyrmex -name ".cursorrules" -type l -exec sh -c 'echo "Checking: $1"; [ -f "$(readlink "$1")" ] && echo "✓ OK" || echo "✗ BROKEN"' _ {} \;
```

### Common Issues

**Issue**: "Cursor isn't finding my cursorrules"
- **Solution**: Ensure symlinks exist in expected locations (root and module `.cursor/` directories)
- Verify symlink targets exist: `readlink -f <symlink>`

**Issue**: "Which file should I edit for a module?"
- **Solution**: Always edit the file in `cursorrules/` directory, not the symlink
- The symlink will automatically point to the updated file

**Issue**: "Module appears in both modules/ and cross-module/"
- **Solution**: This is intentional. See the "Organization Rationale" section above for the distinction
- `modules/` = developing the module itself
- `cross-module/` = using the module in other modules

## Examples

### Example 1: Adding Logging to a New Module

When adding logging to a new module:
1. Reference `general.cursorrules` (always)
2. Reference `cross-module/logging_monitoring.cursorrules` (for usage patterns)
3. Do NOT need `modules/logging_monitoring.cursorrules` (unless modifying the logging module itself)

### Example 2: Defining an MCP Tool

When defining an MCP tool in a module:
1. Reference `general.cursorrules` (always)
2. Reference `cross-module/model_context_protocol.cursorrules` (for MCP tool definition patterns)
3. Do NOT need `modules/model_context_protocol.cursorrules` (unless modifying the MCP specification)

### Example 3: Creating a New Module from Template

When creating a new module:
1. Reference `general.cursorrules` (always)
2. Reference `cross-module/template_module.cursorrules` (for template usage)
3. The new module will eventually get its own `modules/<new_module>.cursorrules`

## Maintenance

This organization was implemented to:
- Centralize all cursorrules in one location
- Make it easier to find and maintain rules
- Provide clear organization by type and purpose
- Maintain backward compatibility with Cursor's file discovery
- Separate concerns between module development and module usage

## Modules Without Cursorrules

The following modules currently do not have dedicated cursorrules files. This may be intentional if:
- The module is new and hasn't been fully developed yet
- The module follows standard patterns and doesn't need special rules
- The module is a utility or helper that doesn't require specific guidance

**Modules without cursorrules** (as of latest update):
- `api_documentation`
- `ci_cd_automation`
- `code_review`
- `config_management`
- `containerization`
- `database_management`
- `language_models`
- `modeling_3d`
- `ollama_integration`
- `performance`
- `physical_management`
- `project_orchestration`
- `security_audit`
- `system_discovery`
- `terminal_interface`
- `tests` (testing infrastructure, not a module)

**Note**: When a module grows in complexity or develops unique patterns, consider adding a cursorrules file for it. Follow the "Adding New Cursor Rules" section above.

## Validation Checklist

When updating cursorrules, verify:
- [ ] All symlinks are working (`find src/codomyrmex -name ".cursorrules" -type l`)
- [ ] Root symlink exists (`ls -la general.cursorrules`)
- [ ] All files reference `general.cursorrules` correctly
- [ ] Cross-references between related files are accurate
- [ ] Module paths in rules match actual module locations
- [ ] README reflects current organization
- [ ] Duplicate entries (modules in both `modules/` and `cross-module/`) have clear distinctions

For questions or suggestions about the cursorrules organization, refer to the project's contributing guidelines.

