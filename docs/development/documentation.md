# Documentation Guidelines

This guide provides standards and best practices for maintaining and contributing to Codomyrmex documentation.

## 📋 Documentation Philosophy

### **Core Principles**

1. **User-Centric**: Documentation is organized by user intent, not code structure
2. **Show, Don't Tell**: Provide working examples rather than abstract descriptions
3. **Progressive Complexity**: Start simple, build to advanced topics
4. **Maintenance-First**: Easy to maintain and keep up-to-date
5. **Accessible**: Clear language, good structure, searchable content

### **Documentation Types**

| Type | Location | Purpose | Audience |
|------|----------|---------|----------|
| **Project Documentation** | `docs/` | Information about Codomyrmex | Users, Contributors |
| **Module Documentation** | `src/codomyrmex/[module]/` | Module-specific information | Module users |
| **Documentation Tools** | `src/codomyrmex/documentation/` | Website generation tools | Other projects |
| **API References** | `*/API_SPECIFICATION.md` | Technical API details | Developers |

## Mermaid diagrams (`docs/`)

Diagrams use fenced code blocks with the `mermaid` language tag. Conventions:

1. **No hard-coded theme styling** — Do not use `style … fill:…`, `classDef`, or `:::class` on nodes. Diagrams must render legibly in light and dark themes (see Cursor Mermaid rules).
2. **Subgraphs** — Prefer `subgraph graphId [Human-readable label]` so the graph id has no spaces and labels with punctuation stay in brackets.
3. **Edges and nodes** — Use quoted edge labels when they contain parentheses or slashes. Avoid node ids that are Mermaid reserved words (`end`, `graph`, …).
4. **Edges only between real nodes** — Do not point an edge at a subgraph name unless your renderer supports it; connect to an explicit node inside the subgraph instead.
5. **Maintenance scripts** (repo root): `uv run python scripts/strip_mermaid_style_lines.py` removes legacy `style` lines; `uv run python scripts/normalize_mermaid_subgraphs.py` converts `subgraph "Title"` to `subgraph sg_… [Title]`.

Hermes-specific examples and agent-doc rules: [docs/agents/hermes/AGENTS.md](../agents/hermes/AGENTS.md) (Diagram conventions).

## 🏗️ Documentation Structure

### **Main Documentation (`docs/`)**

```
docs/
├── README.md                     # Documentation overview
├── getting-started/              # User onboarding
│   ├── installation.md           # Installation guide
│   ├── quickstart.md             # Quick start guide
│   └── tutorials/                # Step-by-step tutorials
├── project/                      # Project-level documentation
│   ├── architecture.md           # System architecture
│   └── contributing.md           # Contributing guidelines
├── modules/                      # Module system documentation
│   ├── overview.md               # Module system overview
│   └── relationships.md          # Inter-module dependencies
├── development/                  # Developer documentation
│   ├── environment-setup.md      # Development environment
│   └── documentation.md          # This file
└── reference/                    # Reference materials
    ├── troubleshooting.md        # Troubleshooting guide
    ├── cli.md                    # CLI reference
    ├── api.md                    # API reference index
    └── changelog.md              # Version history (redirects to root)
```

### **Module Documentation Pattern**

Each module follows this standardized documentation structure:

```
src/codomyrmex/[module]/
├── README.md                     # ✅ REQUIRED: Module overview
├── AGENTS.md                     # ✅ REQUIRED: Agent configuration
├── SECURITY.md                   # ✅ REQUIRED: Security considerations
├── API_SPECIFICATION.md          # ⚠️ Required if referenced in docs/index.md
├── MCP_TOOL_SPECIFICATION.md     # ⚠️ Required if referenced in docs/index.md
├── USAGE_EXAMPLES.md             # ⚠️ Required if referenced in docs/index.md
├── CHANGELOG.md                  # Optional: Module version history
├── pyproject.toml              # Project dependencies
├── docs/                         # Extended documentation
│   ├── index.md                  # ✅ REQUIRED if docs/ exists
│   ├── technical_overview.md     # Optional: Architecture details
│   └── tutorials/                # Optional: Module-specific tutorials
│       └── example_tutorial.md   # ⚠️ Required if referenced in docs/index.md
└── tests/
    └── README.md                 # Optional: Testing documentation
```

#### **Required Files**

All modules **MUST** have:

- **README.md**: Module overview, features, quick start, and usage examples
- **AGENTS.md**: Agent configuration, operating contracts, and navigation links
- **SPEC.md**: Functional specification and design principles
- **PAI.md**: Personal AI Infrastructure integration notes
- **SECURITY.md**: Security considerations and vulnerability reporting process

#### **Conditionally Required Files**

These files are required **if referenced** in documentation:

- **API_SPECIFICATION.md**: Required if `docs/index.md` references it
- **MCP_TOOL_SPECIFICATION.md**: Required if `docs/index.md` references it
- **USAGE_EXAMPLES.md**: Required if `docs/index.md` references it
- **docs/tutorials/example_tutorial.md**: Required if `docs/index.md` references it

#### **Link Standards**

All internal links must follow these conventions:

- **Contributing Guidelines**: Always link to `../../docs/project/contributing.md` (from module root) or `../../../docs/project/contributing.md` (from `docs/` directory)
- **Module Documentation**: Use relative paths from current file location
- **Cross-Module References**: Use paths relative to repository root

#### **Validation**

Module documentation is automatically validated using:

- `scripts/documentation/module_docs_auditor.py` - Comprehensive audit tool
- `scripts/documentation/validate_module_docs.py` - CI/CD validation tool

Run validation before committing:

```bash
python3 scripts/documentation/validate_module_docs.py
```

## ✍️ Writing Standards

### **Markdown Style**

```markdown
# Document Title

Brief description of what this document covers.

## 🎯 Section with Emoji

Use descriptive emojis to make sections scannable.

### **Bold Subsection Headers**

Use bold for important subsections.

#### Regular Subsection

Use regular headers for detailed breakdowns.

### **Code Examples**

```python
# Always include complete, working examples
from codomyrmex.module import function

result = function("example", param="value")
print(f"Result: {result}")
```

### **Tables for Reference Information**

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |

### **Callout Boxes**

> **⚠️ Important**: Critical information users must know.

> **💡 Tip**: Helpful suggestions for better experience.

> **🔍 Note**: Additional context or clarification.

```

### **Link Conventions**

```markdown
# Internal links (relative to current file)
[Architecture Guide](../project/architecture.md)
[Module Template](../../src/codomyrmex/module_template/README.md)

# External links
[GitHub Repository](https://github.com/docxology/codomyrmex)

# Anchor links within document
[See Installation Section](#installation)
```

### **Code Example Standards**

1. **Complete Examples**: Always provide full, runnable code
2. **Real Implementations**: No placeholder or pseudo-code
3. **Error Handling**: Show proper error handling patterns
4. **Context**: Provide necessary imports and setup

```python
# ✅ Good example
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.data_visualization import create_line_plot
import numpy as np

# Initialize logging (required)
setup_logging()
logger = get_logger(__name__)

try:
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    # Create visualization
    create_line_plot(
        x_data=x, 
        y_data=y, 
        title="Sine Wave",
        output_path="sine_wave.png"
    )
    logger.info("Plot created successfully")
    
except Exception as e:
    logger.error(f"Failed to create plot: {e}")
    raise

# ❌ Bad example
result = some_function()
print(result)
```

## 🔍 Quality Assurance

### **Documentation Review Checklist**

- [ ] **Accuracy**: All code examples work
- [ ] **Completeness**: Covers all necessary information
- [ ] **Clarity**: Clear, concise writing
- [ ] **Structure**: Logical organization and flow
- [ ] **Links**: All internal links work correctly
- [ ] **Consistency**: Follows established patterns
- [ ] **User-Focused**: Addresses user needs and questions
- [ ] **Examples**: Includes practical, working examples
- [ ] **Maintenance**: Easy to keep up-to-date

### **Module Documentation Validation**

All module documentation is validated for consistency and completeness:

#### **Automated Validation Tools**

- **`scripts/documentation/module_docs_auditor.py`**: Comprehensive audit of all modules
  - Scans for missing required files
  - Identifies broken references
  - Checks documentation structure
  - Generates detailed reports

- **`scripts/documentation/validate_module_docs.py`**: Fast validation for CI/CD
  - Validates required files exist
  - Checks for broken references
  - Ensures link consistency
  - Returns exit code for automation

#### **Running Validation**

```bash
# Comprehensive audit (generates detailed report)
python3 scripts/documentation/module_docs_auditor.py

# Quick validation (for CI/CD)
python3 scripts/documentation/validate_module_docs.py

# Fix common issues
python3 scripts/documentation/fix_contributing_refs.py
python3 scripts/documentation/create_example_tutorials.py
python3 scripts/documentation/create_missing_doc_files.py
```

### **Link Validation**

Regular link checking is essential:

```bash
# Manual link checking
find docs/ -name "*.md" -exec grep -l "](.*\.md)" {} \; | while read file; do
    echo "Checking links in $file"
    grep -o "](.*\.md)" "$file" | sed 's/](\(.*\))/\1/' | while read link; do
        if [[ ! -f "$(dirname "$file")/$link" ]] && [[ ! -f "$link" ]]; then
            echo "❌ Broken link: $link in $file"
        fi
    done
done

# Check external links (requires network)
# Use tools like markdown-link-check or similar
```

### **Content Maintenance**

1. **Regular Reviews**: Schedule quarterly documentation reviews
2. **Version Sync**: Update documentation with code changes
3. **Link Maintenance**: Check for broken links after file moves
4. **Example Validation**: Test all code examples regularly
5. **User Feedback**: Incorporate user feedback and questions

### **Automated Maintenance**

The documentation system includes automated tools for maintenance:

#### **Pre-Commit Validation**

```bash
# Add to .git/hooks/pre-commit
python3 scripts/documentation/validate_module_docs.py
```

#### **CI/CD Integration**

See `.github/workflows/documentation-validation.yml` for automated validation in CI/CD pipelines.

#### **Regular Audits**

Run comprehensive audits periodically:

```bash
# Full repository audit
python3 scripts/documentation/comprehensive_audit.py

# Module-specific audit
python3 scripts/documentation/module_docs_auditor.py
```

## 🚀 Contributing Documentation

### **Quick Contribution Process**

1. **Identify Gap**: Find missing or outdated documentation
2. **Check Structure**: Determine correct location in documentation structure
3. **Write Content**: Follow the writing standards above
4. **Test Examples**: Ensure all code examples work
5. **Check Links**: Verify all links work correctly
6. **Submit PR**: Create pull request with clear description

### **Major Documentation Changes**

1. **Discuss First**: Open issue to discuss major structural changes
2. **Plan Migration**: Consider impact on existing links and bookmarks
3. **Update References**: Update all referring documentation
4. **Provide Redirects**: Add redirect notices for moved content
5. **Announce Changes**: Communicate changes to community

### **Documentation Tools**

```bash
# Local documentation development
cd src/codomyrmex/documentation/
npm install
npm run start  # Start development server

# Build documentation website
npm run build

# Check for broken links (if using link checker)
npm run check-links
```

## 🔧 Maintenance Tasks

### **Regular Maintenance Schedule**

#### **Weekly**

- Check for new issues asking documentation questions
- Review and merge documentation pull requests
- Update example code if APIs change

#### **Monthly**

- Run comprehensive link checking
- Review analytics for most-viewed documentation
- Update getting-started guides for new features

#### **Quarterly**

- Complete documentation structure review
- User experience testing with new contributors
- Performance review of documentation website
- Cleanup of outdated or redundant content

### **Documentation Metrics**

Track these metrics for documentation health:

1. **Coverage**: Percentage of modules with complete documentation
2. **Freshness**: Age of documentation vs. last code changes
3. **Usage**: Most and least viewed documentation pages
4. **Issues**: Number of documentation-related issues opened
5. **Contribution**: Community contributions to documentation

### **Common Issues and Solutions**

#### **Outdated Examples**

- **Problem**: Code examples break with API changes
- **Solution**: Automated testing of documentation examples
- **Prevention**: Include documentation in code review process

#### **Broken Links**

- **Problem**: Links break when files are moved or reorganized
- **Solution**: Regular link checking and relative link preferences
- **Prevention**: Use consistent link patterns and automation

#### **Structure Confusion**

- **Problem**: Users can't find information they need
- **Solution**: User testing and feedback collection
- **Prevention**: User-centric organization and clear navigation

#### **Duplicate Content**

- **Problem**: Information exists in multiple places, creating maintenance burden
- **Solution**: Single source of truth principle
- **Prevention**: Clear content ownership and regular audits

## 🎯 Success Metrics

Good documentation should achieve:

1. **Discoverability**: Users can quickly find what they need
2. **Usability**: Information is clear and actionable
3. **Completeness**: All necessary information is available
4. **Maintainability**: Easy to keep up-to-date
5. **Community**: Encourages contributions and engagement

### **User Success Indicators**

- Decreased "documentation" issues in GitHub
- Increased successful first-time installations
- More community contributions
- Positive feedback on documentation quality
- Reduced support requests for covered topics

---

**Last Updated**: Auto-generated from documentation review  
**Maintainers**: Documentation team and community contributors  
**Feedback**: [Open an issue](https://github.com/docxology/codomyrmex/issues) for documentation improvements

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
