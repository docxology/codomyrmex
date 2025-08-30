# Template Directory

This directory serves as a placeholder for project templates and boilerplate code. Currently, the primary template system is located within the main Codomyrmex package at `../codomyrmex/module_template/`.

## Template System Overview

The Codomyrmex project uses a comprehensive template system to ensure consistency across modules and maintain high code quality standards. 

### Primary Template Location
**Main Template System**: [`../codomyrmex/module_template/`](../codomyrmex/module_template/)

This contains the complete scaffolding for creating new Codomyrmex modules, including:
- Standardized file structure
- Documentation templates
- Test framework setup
- API specification templates
- MCP tool specification templates

## Available Templates

### 1. Module Template
**Location**: `../codomyrmex/module_template/`  
**Purpose**: Complete scaffolding for new Codomyrmex modules  
**Status**: ✅ Active and comprehensive

#### Template Structure
```
module_template/
├── README.md                    # Module README template
├── API_SPECIFICATION.md         # API documentation template
├── MCP_TOOL_SPECIFICATION.md    # MCP tools template
├── CHANGELOG.md                 # Version history template
├── SECURITY.md                  # Security policy template
├── USAGE_EXAMPLES.md            # Usage examples template
├── requirements.template.txt     # Dependencies template
├── __init__.py                  # Python package initializer
├── docs/                        # Documentation templates
│   ├── index.md                 # Documentation index
│   ├── technical_overview.md    # Technical documentation
│   └── tutorials/               # Tutorial templates
└── tests/                       # Test framework templates
    ├── README.md                # Testing documentation
    ├── unit/                    # Unit tests directory
    └── integration/             # Integration tests directory
```

#### Usage
To create a new module using the template:

```bash
# From project root
cp -r src/codomyrmex/module_template/ src/codomyrmex/your_new_module/

# Edit the copied files, replacing template placeholders:
# - [Module Name] → Your Module Name
# - [your_module_name] → your_actual_module_name
# - [MainClassOrComponent.py] → your actual files
```

### 2. Future Templates (Planned)
This directory may be expanded in the future to include:

- **Project Templates**: Complete project scaffolding
- **Documentation Templates**: Standalone documentation structures
- **Configuration Templates**: Common configuration patterns
- **CI/CD Templates**: GitHub Actions and other CI/CD configurations
- **Docker Templates**: Container configurations
- **Test Templates**: Testing patterns and frameworks

## Template Usage Guidelines

### Creating a New Module
1. **Copy Template**: Use the `module_template/` as your starting point
2. **Replace Placeholders**: Update all bracketed placeholders with actual values
3. **Customize Structure**: Adapt the template to your specific module needs
4. **Follow Standards**: Maintain consistency with existing modules

### Template Standards
Templates in the Codomyrmex project follow these principles:
- **Complete Coverage**: Include all necessary files and documentation
- **Clear Instructions**: Provide detailed guidance for customization
- **Consistency**: Maintain uniform structure across all modules
- **Best Practices**: Incorporate project coding standards and conventions

## Development Standards Integration

### Code Quality [[memory:7401883]]
Templates emphasize:
- Clear, coherent code examples with real methods (no pseudocode)
- Comprehensive documentation that "shows not tells"
- Practical examples demonstrating actual functionality

### Testing Approach [[memory:7401885]]
Templates include:
- Test-driven development (TDD) structure
- Comprehensive test coverage framework
- Real implementations (no mock methods)
- Iterative test execution patterns

### Output Organization [[memory:7401890]]
Templates enforce:
- Number-prepended output folders in `@output/`
- Consistent artifact organization
- Clear separation of generated content

### Package Management [[memory:7401880]]
Templates promote:
- Latest package versions
- Avoiding version pinning to old requirements
- Cutting-edge tool integration

## Template Customization

### Module-Specific Adaptations
When using templates, consider:
- **Domain Requirements**: Adapt structure for specific functionality
- **Integration Needs**: Include relevant module dependencies
- **Security Considerations**: Add appropriate security measures
- **Performance Requirements**: Include performance-related configurations

### Documentation Customization
Templates provide:
- **API Documentation**: Comprehensive interface documentation
- **Usage Examples**: Real-world usage scenarios
- **Technical Overviews**: Architectural details and design decisions
- **Testing Guides**: Complete testing instructions

## Quick Start with Templates

### Create New Module
```bash
# 1. Copy template
cp -r src/codomyrmex/module_template/ src/codomyrmex/my_new_module/

# 2. Navigate to new module
cd src/codomyrmex/my_new_module/

# 3. Customize files (replace all template placeholders)
# Edit README.md, API_SPECIFICATION.md, etc.

# 4. Set up Python package
mv requirements.template.txt requirements.txt
# Edit requirements.txt with actual dependencies

# 5. Add to main package
# Edit ../codomyrmex/__init__.py to include new module
```

### Template Validation
After customization, ensure:
- All bracketed placeholders are replaced
- Dependencies are correctly specified
- Tests are adapted to actual functionality
- Documentation reflects actual capabilities
- Integration points are correctly defined

## Support & Resources

### Template Documentation
- **[Module Template README](../codomyrmex/module_template/README.md)**: Complete template documentation
- **[Module Template API Spec](../codomyrmex/module_template/API_SPECIFICATION.md)**: API template
- **[Module Template Tests](../codomyrmex/module_template/tests/README.md)**: Testing template

### Project Resources
- **[Main Project README](../../README.md)**: Complete project overview
- **[Source Directory](../README.md)**: Source code organization
- **[Package Documentation](../codomyrmex/README.md)**: Module system overview
- **[Contributing Guide](../../CONTRIBUTING.md)**: Development workflow
- **[Architecture Documentation](../../docs/project/architecture.md)**: System design

### Quick Links
- **[Installation Guide](../../docs/getting-started/installation.md)**
- **[Module Creation Tutorial](../../docs/getting-started/tutorials/creating-a-module.md)**
- **[Development Best Practices](../../docs/project/contributing.md)**

---

*Status: Directory prepared for future template expansion*  
*Primary Templates: Located in `../codomyrmex/module_template/`*  
*For template usage instructions, see the main module template documentation*
