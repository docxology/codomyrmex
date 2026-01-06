# Documentation Example

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - [examples](examples/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Complete | **Last Updated**: December 2025

## Overview

This example demonstrates comprehensive documentation generation, quality assessment, and website building using the Codomyrmex `documentation` module. It showcases automated documentation workflows from code analysis to static site generation.

## What This Example Demonstrates

### Core Features
- **Documentation Environment Setup**: Environment checking and dependency validation
- **Automated Documentation Generation**: Code-to-documentation conversion
- **Quality Assessment**: Documentation quality scoring and improvement recommendations
- **Consistency Checking**: Cross-document consistency validation
- **Static Site Building**: Documentation website generation with Docusaurus
- **Version Validation**: Documentation version consistency checking

### Key Capabilities
- Multi-format documentation generation (HTML, PDF, Markdown)
- Documentation quality metrics and scoring
- Link validation and consistency checking
- API documentation extraction from code
- Static site deployment and serving
- Documentation aggregation from multiple sources

## Tested Methods

This example references the following tested methods from `testing/unit/test_documentation.py`:

- `check_doc_environment()` - Verified in `TestDocumentation::test_documentation_module_structure`
- `install_dependencies()` - Verified in `TestDocumentation::test_documentation_module_structure`
- `build_static_site()` - Verified in `TestDocumentation::test_documentation_module_structure`
- `assess_site()` - Verified in `TestDocumentation::test_documentation_module_structure`
- `aggregate_docs()` - Verified in `TestDocumentation::test_documentation_module_structure`
- `DocumentationQualityAnalyzer` - Verified in `TestDocumentation::test_documentation_module_structure`

## Running the Example

### Quick Start

```bash
# Navigate to the example directory
cd examples/documentation

# Run with default YAML configuration
python example_basic.py

# Run with JSON configuration
python example_basic.py --config config.json

# Run with custom configuration
python example_basic.py --config my_custom_config.yaml
```

### Expected Output

The example will:
1. Check documentation environment and dependencies
2. Create sample documentation files with various quality levels
3. Validate documentation versions and consistency
4. Aggregate documentation from multiple sources
5. Assess documentation site quality and SEO
6. Analyze documentation quality metrics
7. Check documentation consistency and broken links
8. Generate comprehensive quality reports

### Sample Output Structure

```json
{
  "sample_docs_created": 3,
  "docs_directory": "/tmp/tmpXXX/docs",
  "environment_node_available": false,
  "environment_npm_available": false,
  "version_validation_completed": true,
  "docs_aggregated": true,
  "site_assessment_completed": true,
  "quality_analysis_files": 3,
  "average_readability_score": 78.5,
  "average_completeness_score": 82.3,
  "consistency_check_completed": true,
  "quality_report_generated": true,
  "analysis_results_saved": "output/analysis/documentation_analysis.json",
  "documentation_quality_analyzer_initialized": true,
  "consistency_checker_initialized": true,
  "aggregation_successful": true,
  "validation_passed": true
}
```

## Configuration Options

### Environment Configuration

Configure documentation environment requirements:

```yaml
environment:
  node_version: ">=16.0.0"      # Minimum Node.js version
  npm_version: ">=7.0.0"        # Minimum npm version
  python_version: ">=3.8.0"     # Minimum Python version
  dependencies:                 # Required dependencies
    - docusaurus
    - nodejs
    - npm
```

### Documentation Generation

Customize documentation generation settings:

```yaml
generation:
  source_dirs:                  # Source directories for docs
    - docs/
    - src/
    - examples/
  output_dir: build/            # Output directory
  formats:                      # Output formats
    - html
    - pdf
    - markdown
  include_api_docs: true        # Include API documentation
  include_examples: true        # Include code examples
  generate_toc: true           # Generate table of contents
```

### Quality Assessment

Configure quality assessment parameters:

```yaml
quality:
  metrics:                     # Quality metrics to evaluate
    - readability
    - completeness
    - structure
    - consistency
    - accuracy
  readability_thresholds:       # Readability scoring thresholds
    excellent: 90
    good: 75
    fair: 60
    poor: 45
```

### Consistency Checking

Configure consistency validation:

```yaml
consistency:
  check_broken_links: true      # Validate all links
  check_terminology: true       # Check consistent terminology
  check_style: true             # Validate style consistency
  check_versions: true          # Check version consistency
  custom_rules:                 # Custom validation rules
    - max_line_length: 100
    - heading_case: title
    - code_language_specified: true
```

## Documentation Quality Metrics

### Readability Assessment
- **Sentence complexity**: Measures sentence length and structure
- **Vocabulary diversity**: Assesses word choice variety
- **Clarity indicators**: Identifies clear vs. ambiguous language
- **Structure coherence**: Evaluates logical flow and organization

### Completeness Analysis
- **Required sections**: Checks for essential documentation elements
- **API coverage**: Validates API documentation completeness
- **Example coverage**: Assesses code example availability
- **Cross-references**: Verifies internal linking completeness

### Structure Validation
- **Heading hierarchy**: Validates proper heading levels
- **Table formatting**: Checks table structure and accessibility
- **Code block formatting**: Ensures proper syntax highlighting
- **Navigation consistency**: Validates site navigation structure

## Site Assessment Features

### SEO Analysis
- **Meta tags**: Validates meta descriptions and titles
- **Heading structure**: Assesses heading hierarchy for SEO
- **Content optimization**: Evaluates keyword usage and density
- **Link structure**: Analyzes internal and external linking

### Performance Metrics
- **Page load times**: Measures documentation site performance
- **Asset optimization**: Assesses image and resource optimization
- **Caching headers**: Validates proper caching configuration
- **Mobile responsiveness**: Checks mobile-friendly design

### Accessibility Evaluation
- **WCAG compliance**: Validates accessibility standards
- **Color contrast**: Assesses text readability
- **Keyboard navigation**: Tests keyboard accessibility
- **Screen reader compatibility**: Validates assistive technology support

## Integration Examples

### CI/CD Pipeline Integration

```python
from codomyrmex.documentation import check_doc_environment, assess_site, generate_quality_report

def validate_documentation():
    """Validate documentation in CI/CD pipeline."""

    # Check environment
    env_status = check_doc_environment()
    if not env_status.get('node_available'):
        raise Exception("Node.js required for documentation build")

    # Assess site quality
    assessment = assess_site("docs/")
    if assessment.get('seo_score', 0) < 70:
        print("Warning: SEO score below threshold")

    # Generate quality report
    report = generate_quality_report("docs/", "reports/")
    if report.get('critical_issues', 0) > 0:
        raise Exception("Critical documentation issues found")

    return True
```

### Automated Documentation Updates

```python
from codomyrmex.documentation import aggregate_docs, DocumentationQualityAnalyzer

def update_documentation():
    """Automatically update and validate documentation."""

    # Aggregate docs from multiple sources
    aggregate_docs("sources/", "docs/")

    # Analyze quality
    analyzer = DocumentationQualityAnalyzer()
    analysis = analyzer.analyze_project("docs/")

    # Generate improvement recommendations
    recommendations = []
    if analysis.get('average_readability', 0) < 75:
        recommendations.append("Improve documentation readability")

    if analysis.get('broken_links', 0) > 0:
        recommendations.append("Fix broken links")

    return {
        'analysis': analysis,
        'recommendations': recommendations
    }
```

## Output Files

The example generates several output files:

- `output/documentation_results.json` - Complete analysis results and metrics
- `output/analysis/documentation_analysis.json` - Detailed quality assessment data
- `docs/reports/quality_report.html` - HTML quality report (if generated)
- `docs/aggregated/` - Aggregated documentation files

## Dependencies

### Required Dependencies
- Python 3.8+ (for documentation processing)
- Node.js 16+ (for Docusaurus site building)
- npm 7+ (for package management)

### Optional Dependencies
- `docusaurus` - For static site generation
- `markdownlint` - For markdown quality checking
- `linkchecker` - For link validation
- `accessibility-checker` - For accessibility assessment

## Troubleshooting

### Common Issues

1. **Node.js Not Found**: Ensure Node.js 16+ is installed and in PATH
2. **npm Dependencies**: Run `npm install` in documentation directory
3. **Permission Errors**: Check write permissions for output directories
4. **Memory Issues**: Reduce analysis scope for large documentation sets

### Performance Considerations

- Use parallel processing for large documentation sets
- Enable caching to improve analysis performance
- Limit analysis depth for faster execution
- Use incremental analysis for frequent updates

## Security Considerations

- Documentation generation operates on source files only
- No execution of documentation code samples
- Output sanitization prevents XSS in generated HTML
- Access controls apply to documentation source repositories

## Related Examples

- **[Static Analysis](../static_analysis/)** - Code quality analysis integration
- **[Code Review](../code_review/)** - Documentation review integration
- **[API Documentation](../api_documentation/)** - API documentation generation
- **[Build Synthesis](../build_synthesis/)** - Documentation site building

## Module Documentation

- **[Documentation Module](../../src/codomyrmex/documentation/)** - Complete module documentation
- **[API Specification](../../src/codomyrmex/documentation/API_SPECIFICATION.md)** - Detailed API reference
- **[Usage Examples](../../src/codomyrmex/documentation/USAGE_EXAMPLES.md)** - Additional usage patterns

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)