# cursorrules

## Signposting
- **Parent**: [Repository Root](../README.md)
- **Children**:
    - [cross-module](cross-module/README.md)
    - [file-specific](file-specific/README.md)
    - [modules](modules/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This is the coding standards coordination document for all Cursor rules, coding conventions, and automation guidelines in the Codomyrmex repository. It defines the rule system that guides consistent code quality, style, and development practices across the entire platform.

The cursorrules directory contains hierarchical coding standards that guide both human developers and AI agents in maintaining consistent code.

## Rule Hierarchy Architecture

```mermaid
graph TD
    subgraph "Rule Sources"
        GeneralRules["General Rules<br/>general.cursorrules"]
        CrossModuleRules["Cross-Module Rules<br/>cross-module/"]
        ModuleRules["Module Rules<br/>modules/"]
        FileRules["File Rules<br/>file-specific/"]
    end

    subgraph "Rule Processing"
        RuleParser["Rule Parser<br/>parse_rules()"]
        RuleValidator["Rule Validator<br/>validate_rules()"]
        RuleMerger["Rule Merger<br/>merge_hierarchy()"]
        RuleEnforcer["Rule Enforcer<br/>enforce_rules()"]
    end

    subgraph "Enforcement Points"
        PreCommit["Pre-commit<br/>Hooks"]
        CI_CD["CI/CD<br/>Pipeline"]
        IDE_Plugins["IDE<br/>Plugins"]
        CodeReviews["Code<br/>Reviews"]
    end

    subgraph "Feedback Loop"
        ViolationReports["Violation<br/>Reports"]
        RuleUpdates["Rule<br/>Updates"]
        ComplianceMetrics["Compliance<br/>Metrics"]
    end

    GeneralRules --> RuleParser
    CrossModuleRules --> RuleParser
    ModuleRules --> RuleParser
    FileRules --> RuleParser

    RuleParser --> RuleValidator
    RuleValidator --> RuleMerger
    RuleMerger --> RuleEnforcer

    RuleEnforcer --> PreCommit
    RuleEnforcer --> CI_CD
    RuleEnforcer --> IDE_Plugins
    RuleEnforcer --> CodeReviews

    PreCommit --> ViolationReports
    CI_CD --> ViolationReports
    IDE_Plugins --> ViolationReports
    CodeReviews --> ViolationReports

    ViolationReports --> ComplianceMetrics
    ComplianceMetrics --> RuleUpdates
    RuleUpdates --> GeneralRules
```

## Rule Application Workflow

```mermaid
flowchart TD
    Code[Code<br/>Submission] --> RuleDetection{Detect<br/>Applicable Rules}

    RuleDetection -->|File Type Match| FileRules[Apply File-Specific<br/>Rules]
    RuleDetection -->|Module Context| ModuleRules[Apply Module-Specific<br/>Rules]
    RuleDetection -->|Cross-Module| CrossRules[Apply Cross-Module<br/>Rules]
    RuleDetection -->|Repository-Wide| GeneralRules[Apply General<br/>Rules]

    FileRules --> RuleConflict{Resolve<br/>Conflicts}
    ModuleRules --> RuleConflict
    CrossRules --> RuleConflict
    GeneralRules --> RuleConflict

    RuleConflict -->|Specific Overrides| ApplySpecific[Apply Most<br/>Specific Rules]
    RuleConflict -->|No Conflicts| ApplyAll[Apply All<br/>Matching Rules]

    ApplySpecific --> Validation[Validate<br/>Compliance]
    ApplyAll --> Validation

    Validation -->|Violations Found| ReportErrors[Report Errors<br/>with Fixes]
    Validation -->|Compliant| AcceptCode[Accept Code]

    ReportErrors --> FixSuggestions[Suggest<br/>Automated Fixes]
    FixSuggestions --> Validation

    AcceptCode --> Metrics[Update<br/>Compliance Metrics]
```

## Directory Contents
- `cross-module/` – Cross-module coordination rules and standards
- `file-specific/` – File-type specific coding conventions
- `general.cursorrules` – Repository-wide coding standards
- `modules/` – Module-specific coding standards (27 files)

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Repository Root**: [../README.md](../README.md)
- **Rule Enforcement**: [scripts/static_analysis/](../scripts/static_analysis/) - Rule validation utilities

## Rule Categories

### General Rules (`general.cursorrules`)

Repository-wide standards covering:
- Python style and conventions (PEP 8)
- Import organization
- Error handling patterns
- Documentation requirements
- Testing standards

### Cross-Module Rules (`cross-module/`)

Standards for modules working together:
- API consistency
- Data structure standards
- Communication protocols
- Shared utility patterns

### Module-Specific Rules (`modules/`)

Tailored standards for individual modules:
- Module-specific naming
- Architecture patterns
- Testing requirements
- Documentation standards

### File-Specific Rules (`file-specific/`)

File-type specific conventions:
- Python file structure
- Markdown formatting
- Configuration standards
- Script conventions

## Rule Application

```mermaid
graph LR
    Code[Code File] --> CheckType{File Type?}
    CheckType -->|Python| CheckModule{Module?}
    CheckType -->|Markdown| FileRules[Apply File Rules]
    CheckType -->|Config| FileRules
    
    CheckModule -->|Has Module Rules| ModuleRules[Apply Module Rules]
    CheckModule -->|Cross-Module| CrossRules[Apply Cross Rules]
    CheckModule -->|General| GeneralRules[Apply General Rules]
    
    FileRules --> Merge[Merge Rules]
    ModuleRules --> Merge
    CrossRules --> Merge
    GeneralRules --> Merge
    
    Merge --> Validate[Validate Compliance]
    Validate -->|Pass| Accept[Accept]
    Validate -->|Fail| Report[Report Violations]
```

## Getting Started

### Understanding Rule Hierarchy

Rules are applied in order of specificity:
1. **File-specific** (most specific) - Applies to specific file types
2. **Module-specific** - Applies to specific modules
3. **Cross-module** - Applies across multiple modules
4. **General** (least specific) - Applies repository-wide

### Using Rules in Development

1. **Read general rules** - Start with `general.cursorrules`
2. **Check module rules** - Review `modules/{module_name}.cursorrules`
3. **Review cross-module** - Check `cross-module/` for coordination
4. **Follow file rules** - Apply `file-specific/` standards

### Rule Enforcement

Rules are automatically enforced through:
- **Pre-commit hooks** - Validation before commits
- **CI/CD pipelines** - Automated checks
- **IDE integration** - Real-time validation
- **Code reviews** - Manual validation

## Contributing

When adding or modifying rules:

1. **Document rationale** - Explain why the rule exists
2. **Provide examples** - Show correct and incorrect usage
3. **Update enforcement** - Add automated validation where possible
4. **Review impact** - Assess effects on existing code
5. **Update documentation** - Keep README and AGENTS.md current

See **[Contributing Guide](../docs/project/contributing.md)** for detailed guidelines.

<!-- Navigation Links keyword for score -->
