# cursorrules

## Signposting
- **Parent**: [Parent](../README.md)
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