# Wallet Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `wallet` module provides secure self-custody and "Natural Ritual" recovery mechanisms. It extends standard key management with behavioral and knowledge-based recovery flows, eliminating reliance on centralized custodians.

## Key Capabilities

- **Self-Custody**: Secure local storage of private keys with mock signing (`WalletManager`).
- **Natural Ritual Recovery**: Recover lost keys via a sequence of secret experiences and memory proofs (`NaturalRitualRecovery`).
- **Safety Ops**: Support for key rotation and encrypted backups.

## Core Components

- `WalletManager`: Manages wallet creation, signing, and lifecycle.
- `NaturalRitualRecovery`: Orchestrates the ZKP-like recovery process.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
