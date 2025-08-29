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
│   ├── contributing.md           # Contributing guidelines
│   └── documentation-reorganization-summary.md
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

Each module follows this documentation structure:

```
src/codomyrmex/[module]/
├── README.md                     # Module overview
├── API_SPECIFICATION.md          # Detailed API documentation
├── MCP_TOOL_SPECIFICATION.md     # MCP tools (if applicable)
├── USAGE_EXAMPLES.md             # Practical usage examples
├── CHANGELOG.md                  # Module version history
├── SECURITY.md                   # Security considerations
├── requirements.txt              # Module dependencies
├── docs/                         # Extended documentation
│   ├── index.md                  # Documentation index
│   ├── technical_overview.md     # Architecture details
│   └── tutorials/                # Module-specific tutorials
└── tests/
    └── README.md                 # Testing documentation
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
[GitHub Repository](https://github.com/codomyrmex/codomyrmex)

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
**Feedback**: [Open an issue](https://github.com/codomyrmex/codomyrmex/issues) for documentation improvements
