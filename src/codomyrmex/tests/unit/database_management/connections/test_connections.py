"""
Tests for Database Connections Module
"""

import pytest

from codomyrmex.database_management.connections import (
    ConnectionPool,
    ConnectionState,
    ConnectionStats,
    HealthChecker,
    MockConnection,
    MockConnectionFactory,
    PoolConfig,
)


class TestMockConnection:
    """Tests for MockConnection."""

    def test_create(self):
        """Should create connection."""
        conn = MockConnection(1)
        assert conn.connection_id == 1
        assert conn.state == ConnectionState.IDLE

    def test_execute(self):
        """Should execute query."""
        conn = MockConnection()
        result = conn.execute("SELECT 1")

        assert result["result"] == "mock"
        assert "SELECT 1" in conn._queries

    def test_is_valid(self):
        """Should report validity."""
        conn = MockConnection()
        assert conn.is_valid() is True

        conn.close()
        assert conn.is_valid() is False

    def test_close(self):
        """Should close connection."""
        conn = MockConnection()
        conn.close()

        assert conn.state == ConnectionState.CLOSED

        with pytest.raises(RuntimeError):
            conn.execute("SELECT 1")

    def test_mark_used(self):
        """Should track usage."""
        conn = MockConnection()
        assert conn.use_count == 0

        conn.mark_used()
        assert conn.use_count == 1
        assert conn.state == ConnectionState.IN_USE


class TestConnectionPool:
    """Tests for ConnectionPool."""

    def test_create_pool(self):
        """Should create pool with min connections."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory, config=PoolConfig(min_connections=3))

        stats = pool.stats
        assert stats.total_connections == 3

        pool.close()

    def test_acquire_release(self):
        """Should acquire and release connections."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory, config=PoolConfig(min_connections=2))

        conn = pool.acquire(timeout=1.0)
        assert conn is not None
        assert conn.state == ConnectionState.IN_USE

        pool.release(conn)
        assert conn.state == ConnectionState.IDLE

        pool.close()

    def test_connection_context_manager(self):
        """Context manager should work."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory)

        with pool.connection() as conn:
            result = conn.execute("SELECT 1")
            assert result is not None

        pool.close()

    def test_max_connections_timeout(self):
        """Should timeout when max connections reached."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory, config=PoolConfig(min_connections=1, max_connections=1))

        # Acquire the only connection
        conn = pool.acquire(timeout=1.0)
        assert conn is not None

        # Now pool is at capacity — next acquire should timeout
        with pytest.raises(TimeoutError):
            pool.acquire(timeout=0.2)

        pool.release(conn)
        pool.close()

    def test_stats(self):
        """Should track stats."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory, config=PoolConfig(min_connections=2))

        stats = pool.stats
        assert stats.total_connections >= 1

        conn = pool.acquire(timeout=1.0)
        stats = pool.stats
        assert stats.active_connections == 1

        pool.release(conn)
        pool.close()


class TestHealthChecker:
    """Tests for HealthChecker."""

    def test_check_health(self):
        """Should check health."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory)
        checker = HealthChecker(pool)

        is_healthy = checker.check_health()
        assert is_healthy is True
        assert checker.is_healthy is True

        pool.close()

    def test_last_check_updated(self):
        """Should update last check time."""
        factory = MockConnectionFactory()
        pool = ConnectionPool(factory)
        checker = HealthChecker(pool)

        assert checker._last_check is None
        checker.check_health()
        assert checker._last_check is not None

        pool.close()


class TestConnectionStats:
    """Tests for ConnectionStats."""

    def test_utilization(self):
        """Should calculate utilization."""
        stats = ConnectionStats(
            total_connections=10,
            active_connections=3,
        )
        assert stats.utilization == 0.3

    def test_utilization_empty(self):
        """Should handle empty pool."""
        stats = ConnectionStats()
        assert stats.utilization == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
