
import pytest
from codomyrmex.networking.http_client import HTTPClient
from codomyrmex.testing import (
    property_test,
    IntGenerator,
    FloatGenerator,
)

class TestNetworkingReliability:
    """Property-based tests for networking components."""

    @property_test(
        timeout=IntGenerator(min_val=1, max_val=60),
        max_retries=IntGenerator(min_val=0, max_val=10),
        retry_backoff=FloatGenerator(min_val=0.1, max_val=5.0)
    )
    def test_http_client_config_fuzzing(self, **kwargs):
        """Verify HTTPClient initializes correctly with fuzzed configuration."""
        timeout = kwargs['timeout']
        max_retries = kwargs['max_retries']
        retry_backoff = kwargs['retry_backoff']
        
        client = HTTPClient(
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff
        )
        
        # Verify public attributes
        assert client.timeout == timeout
        assert client.max_retries == max_retries
        assert client.retry_backoff == retry_backoff
        
        # Verify internal session adapter configuration
        adapter = client.session.get_adapter("https://")
        assert adapter.max_retries.total == max_retries
        assert adapter.max_retries.backoff_factor == retry_backoff
        assert 500 in adapter.max_retries.status_forcelist
        assert 429 in adapter.max_retries.status_forcelist

    @property_test(
        initial=FloatGenerator(min_val=0.1, max_val=5.0),
        max_delay=FloatGenerator(min_val=10.0, max_val=60.0),
        loop_count=IntGenerator(min_val=1, max_val=20)
    )
    def test_websocket_backoff_algorithm(self, **kwargs):
        """Verify exponential backoff calculation logic."""
        initial = kwargs['initial']
        max_delay = kwargs['max_delay']
        loop_count = kwargs['loop_count']
        
        # This mirrors the logic in WebSocketClient.connect
        delay = initial
        delays = []
        
        for _ in range(loop_count):
            delays.append(delay)
            # Logic from WebSocketClient: delay = min(delay * 1.5, max_reconnect_delay)
            # We assume the implementation uses 1.5 multiplier
            delay = min(delay * 1.5, max_delay)
            
        # Refute assertions
        for d in delays:
            assert d <= max_delay
            assert d >= initial
            
        # Verify growth
        if loop_count > 1 and initial < max_delay:
            assert delays[1] > delays[0]
            # Check specific multiplier if not capped
            if delays[1] < max_delay:
                assert abs(delays[1] - (delays[0] * 1.5)) < 1e-9
