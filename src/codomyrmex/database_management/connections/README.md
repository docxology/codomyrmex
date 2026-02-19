# connections

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Connection pooling, health checks, and connection lifecycle management for databases. Provides an abstract `Connection` base class with usage tracking and lifetime metrics, a `ConnectionFactory` interface for creating connections, and a thread-safe `ConnectionPool` with configurable min/max connections, acquire timeouts, idle eviction, max lifetime validation, and a context manager for automatic checkout/release. A `HealthChecker` runs periodic validation queries in a background thread to monitor pool health.

## Key Exports

- **`ConnectionState`** -- Enum of connection states (idle, in_use, closed, error)
- **`ConnectionStats`** -- Dataclass with pool-level statistics: total/active/idle connections, waiting requests, checkout count, timeout count, average wait time, and utilization percentage
- **`PoolConfig`** -- Configuration dataclass for pool behavior: min/max connections, acquire timeout, idle timeout, max lifetime, validation interval, and health check query
- **`Connection`** -- Abstract base class for database connections with age/idle tracking, use counting, and abstract execute/is_valid/close methods
- **`ConnectionFactory`** -- Abstract factory for creating `Connection` instances
- **`MockConnection`** -- Testing implementation of `Connection` that records executed queries
- **`MockConnectionFactory`** -- Testing factory that produces `MockConnection` instances with auto-incrementing IDs
- **`ConnectionPool`** -- Thread-safe pool with queue-based checkout, lifetime/validity checks on acquire, automatic replenishment to min_connections on release, and a `connection()` context manager for safe acquire/release
- **`HealthChecker`** -- Background health checker that periodically acquires a connection from the pool and runs a validation query, exposing an `is_healthy` property

## Directory Contents

- `__init__.py` - All connection logic: state enum, pool config, abstract connection/factory, mock implementations, connection pool, health checker
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [database_management](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
