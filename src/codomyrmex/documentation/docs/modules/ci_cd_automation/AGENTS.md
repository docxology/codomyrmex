# CI/CD Automation -- Agent Integration Guide

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The CI/CD Automation module provides pipeline management, deployment orchestration, and rollback capabilities. MCP tools are exposed for pipeline status and execution.

## Agent Interaction Patterns

Engineers use this module during BUILD and EXECUTE phases to create, run, and monitor CI/CD pipelines. The QATester agent uses pipeline reports during VERIFY.

## Trust Level

Pipeline execution tools require TRUSTED trust level as they can trigger deployments.

## Navigation

- **Source**: [src/codomyrmex/ci_cd_automation/](../../../../src/codomyrmex/ci_cd_automation/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
