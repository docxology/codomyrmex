# Wallet Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Digital wallet management for cryptocurrency and token operations. Provides wallet creation, balance tracking, and transaction signing.

## Configuration Options

The wallet module operates with sensible defaults and does not require environment variable configuration. Wallet encryption keys and network endpoints are configured per-wallet instance. Private key storage uses encrypted containers.

## PAI Integration

PAI agents interact with wallet through direct Python imports. Wallet encryption keys and network endpoints are configured per-wallet instance. Private key storage uses encrypted containers.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep wallet

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/wallet/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
