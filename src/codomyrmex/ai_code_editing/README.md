# src/codomyrmex/ai_code_editing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Core module providing AI-powered code assistance and generation capabilities for the Codomyrmex platform. This module enables intelligent code creation, refactoring, and enhancement through integration with multiple Large Language Models (LLMs) including OpenAI, Anthropic, and Google AI.

## AI Code Editing Workflow

```mermaid
graph TB
    subgraph UserInput [User Input]
        NaturalPrompt[Natural Language<br/>Description]
        ExistingCode[Existing Code<br/>to Refactor]
        AnalysisRequest[Code Analysis<br/>Request]
        BatchRequests[Multiple<br/>Requests]
    end

    subgraph Validation [Input Validation]
        ValidatePrompt{Prompt<br/>Valid?}
        ValidateCode{Code<br/>Valid?}
        ValidateLanguage{Language<br/>Specified?}
        ValidateProvider{Provider<br/>Supported?}
    end

    subgraph ProviderSelection [Provider Selection]
        CheckAPI{API Key<br/>Available?}
        OpenAIClient[OpenAI<br/>Client]
        ClaudeClient[Anthropic<br/>Client]
        GeminiClient[Google<br/>Client]
        FallbackProvider[Fallback to<br/>Available Provider]
    end

    subgraph Processing [AI Processing]
        PromptEngineering[Prompt<br/>Engineering]
        LanguageInstructions[Language-Specific<br/>Instructions]
        ContextIntegration[Context<br/>Integration]
        TemperatureControl[Temperature<br/>Control]
    end

    subgraph LLMInteraction [LLM Interaction]
        APICall[API Call<br/>with Retry Logic]
        RateLimitHandling[Rate Limit<br/>Handling]
        ErrorRecovery[Error<br/>Recovery]
        TokenTracking[Token Usage<br/>Tracking]
    end

    subgraph OutputProcessing [Output Processing]
        ResponseParsing[Response<br/>Parsing]
        CodeExtraction[Code<br/>Extraction]
        MetadataGeneration[Metadata<br/>Generation]
        QualityValidation[Quality<br/>Validation]
    end

    subgraph ResultFormatting [Result Formatting]
        StructuredOutput[Structured<br/>Dictionary Output]
        ErrorDetails[Error<br/>Details]
        ExecutionMetrics[Execution<br/>Metrics]
        UsageStatistics[Usage<br/>Statistics]
    end

    subgraph SpecializedWorkflows [Specialized Workflows]
        CodeGeneration[Code<br/>Generation]
        CodeRefactoring[Code<br/>Refactoring]
        CodeAnalysis[Code<br/>Analysis]
        BatchProcessing[Batch<br/>Processing]
        CodeComparison[Code<br/>Comparison]
        DocumentationGen[Documentation<br/>Generation]
    end

    %% Flow connections
    NaturalPrompt --> ValidatePrompt
    ExistingCode --> ValidateCode
    AnalysisRequest --> ValidateLanguage
    BatchRequests --> ValidateProvider

    ValidatePrompt -->|Valid| ProviderSelection
    ValidateCode -->|Valid| ProviderSelection
    ValidateLanguage -->|Valid| ProviderSelection
    ValidateProvider -->|Valid| ProviderSelection

    ProviderSelection --> CheckAPI
    CheckAPI -->|Available| OpenAIClient
    CheckAPI -->|Available| ClaudeClient
    CheckAPI -->|Available| GeminiClient
    CheckAPI -->|Unavailable| FallbackProvider

    OpenAIClient --> Processing
    ClaudeClient --> Processing
    GeminiClient --> Processing
    FallbackProvider --> Processing

    Processing --> PromptEngineering
    PromptEngineering --> LanguageInstructions
    LanguageInstructions --> ContextIntegration
    ContextIntegration --> TemperatureControl
    TemperatureControl --> LLMInteraction

    LLMInteraction --> APICall
    APICall --> RateLimitHandling
    RateLimitHandling --> ErrorRecovery
    ErrorRecovery --> TokenTracking
    TokenTracking --> OutputProcessing

    OutputProcessing --> ResponseParsing
    ResponseParsing --> CodeExtraction
    CodeExtraction --> MetadataGeneration
    MetadataGeneration --> QualityValidation
    QualityValidation --> ResultFormatting

    ResultFormatting --> StructuredOutput
    ResultFormatting --> ErrorDetails
    ResultFormatting --> ExecutionMetrics
    ResultFormatting --> UsageStatistics

    StructuredOutput --> CodeGeneration
    StructuredOutput --> CodeRefactoring
    StructuredOutput --> CodeAnalysis
    StructuredOutput --> BatchProcessing
    StructuredOutput --> CodeComparison
    StructuredOutput --> DocumentationGen

    style CodeGeneration fill:#90EE90
    style CodeRefactoring fill:#90EE90
    style CodeAnalysis fill:#90EE90
    style BatchProcessing fill:#90EE90
    style CodeComparison fill:#90EE90
    style DocumentationGen fill:#90EE90
```

## Key Features

- **Multi-Provider Support**: Integration with OpenAI GPT, Anthropic Claude, and Google Gemini
- **Intelligent Prompt Engineering**: Context-aware prompt composition and optimization
- **Comprehensive Code Operations**: Generation, refactoring, analysis, documentation, and comparison
- **Batch Processing**: Efficient handling of multiple code requests
- **Robust Error Handling**: Automatic retry logic, rate limiting, and fallback providers
- **Quality Validation**: Built-in code quality assessment and improvement suggestions
- **Performance Monitoring**: Token usage tracking, execution time measurement, and metrics collection

## Directory Contents
- `.cursor/` – Subdirectory
- `.gitignore` – File
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `PROMPT_ENGINEERING.md` – File
- `SECURITY.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `ai_code_helpers.py` – File
- `claude_task_master.py` – File
- `docs/` – Subdirectory
- `droid/` – Subdirectory
- `droid_manager.py` – File
- `openai_codex.py` – File
- `prompt_composition.py` – File
- `prompt_templates/` – Subdirectory
- `requirements.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Src Hub**: [src](../../../src/README.md)
