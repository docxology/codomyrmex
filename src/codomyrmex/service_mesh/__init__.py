"""
Service Mesh Module

Microservice communication patterns, circuit breakers, and load balancing.
"""

__version__ = "0.1.0"

import random
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
import asyncio


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    half_open_max_calls: int = 3


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.config.timeout_seconds:
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        return True
                return False
            
            if self.state == CircuitState.HALF_OPEN:
                return self.half_open_calls < self.config.half_open_max_calls
            
            return False
    
    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
    
    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self.can_execute():
            raise CircuitOpenError(f"Circuit {self.name} is open")
        
        if self.state == CircuitState.HALF_OPEN:
            with self._lock:
                self.half_open_calls += 1
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class CircuitOpenError(Exception):
    """Raised when circuit is open."""
    pass


class LoadBalancerStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"


@dataclass
class ServiceInstance:
    """A service instance endpoint."""
    id: str
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    connections: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


class LoadBalancer:
    """Load balancer for service instances."""
    
    def __init__(
        self,
        strategy: LoadBalancerStrategy = LoadBalancerStrategy.ROUND_ROBIN,
    ):
        self.strategy = strategy
        self._instances: Dict[str, ServiceInstance] = {}
        self._round_robin_index = 0
        self._lock = threading.Lock()
    
    def register(self, instance: ServiceInstance) -> None:
        """Register a service instance."""
        with self._lock:
            self._instances[instance.id] = instance
    
    def deregister(self, instance_id: str) -> None:
        """Deregister a service instance."""
        with self._lock:
            if instance_id in self._instances:
                del self._instances[instance_id]
    
    def get_instance(self) -> Optional[ServiceInstance]:
        """Get next instance based on strategy."""
        with self._lock:
            healthy = [i for i in self._instances.values() if i.healthy]
            if not healthy:
                return None
            
            if self.strategy == LoadBalancerStrategy.RANDOM:
                return random.choice(healthy)
            
            elif self.strategy == LoadBalancerStrategy.ROUND_ROBIN:
                self._round_robin_index = (self._round_robin_index + 1) % len(healthy)
                return healthy[self._round_robin_index]
            
            elif self.strategy == LoadBalancerStrategy.WEIGHTED:
                total_weight = sum(i.weight for i in healthy)
                r = random.uniform(0, total_weight)
                current = 0
                for instance in healthy:
                    current += instance.weight
                    if r <= current:
                        return instance
                return healthy[-1]
            
            elif self.strategy == LoadBalancerStrategy.LEAST_CONNECTIONS:
                return min(healthy, key=lambda i: i.connections)
            
            return healthy[0]
    
    def mark_healthy(self, instance_id: str, healthy: bool) -> None:
        """Update instance health status."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].healthy = healthy


class RetryPolicy:
    """Retry policy for failed requests."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Get delay for retry attempt."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay *= random.uniform(0.5, 1.5)
        
        return delay
    
    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.get_delay(attempt))
        
        raise last_error


class ServiceProxy:
    """Proxy for service calls with resilience patterns."""
    
    def __init__(
        self,
        service_name: str,
        load_balancer: Optional[LoadBalancer] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        self.service_name = service_name
        self.load_balancer = load_balancer or LoadBalancer()
        self.circuit_breaker = circuit_breaker or CircuitBreaker(service_name)
        self.retry_policy = retry_policy or RetryPolicy()
    
    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Make a service call with full resilience stack."""
        instance = self.load_balancer.get_instance()
        if not instance:
            raise NoHealthyInstanceError(f"No healthy instances for {self.service_name}")
        
        def wrapped():
            return self.circuit_breaker.execute(func, instance, *args, **kwargs)
        
        return self.retry_policy.execute(wrapped)


class NoHealthyInstanceError(Exception):
    """Raised when no healthy instances are available."""
    pass


# Convenience functions
def with_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None,
) -> Callable:
    """Decorator for circuit breaker protection."""
    cb = CircuitBreaker(name, config)
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return cb.execute(func, *args, **kwargs)
        return wrapper
    
    return decorator


def with_retry(
    max_retries: int = 3,
    **kwargs,
) -> Callable:
    """Decorator for retry logic."""
    policy = RetryPolicy(max_retries=max_retries, **kwargs)
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return policy.execute(func, *args, **kwargs)
        return wrapper
    
    return decorator


__all__ = [
    # Core classes
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "LoadBalancer",
    "LoadBalancerStrategy",
    "ServiceInstance",
    "ServiceProxy",
    "RetryPolicy",
    # Exceptions
    "CircuitOpenError",
    "NoHealthyInstanceError",
    # Decorators
    "with_circuit_breaker",
    "with_retry",
]
