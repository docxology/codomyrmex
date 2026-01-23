# Security Policy for Events Module

This document outlines security procedures, threat models, and policies for the Events module.

## Security Overview

The Events module provides event-driven communication capabilities including event bus, emitters, listeners, and logging functionality. Event systems are critical security components as they facilitate inter-component communication and can be exploited for injection attacks, unauthorized access, and denial of service.

### Security Principles

- **Event Integrity**: Ensure events originate from authorized sources and are unmodified
- **Subscriber Authorization**: Only authorized handlers receive events
- **Availability**: Protect against event flooding and resource exhaustion
- **Non-repudiation**: Maintain audit trails for security-relevant events

## Threat Model

### Assets Protected

- Event payloads and metadata
- Subscriber registrations and configurations
- Event history and logs
- System state affected by events

### Threat Actors

1. **External Attackers**: Attempting to inject malicious events or disrupt event flow
2. **Malicious Insiders**: Subscribing to unauthorized events or injecting false events
3. **Compromised Components**: Using events to propagate attacks or exfiltrate data
4. **Automated Systems**: Flooding events for denial of service

### Attack Vectors

#### Event Injection

**Threat Level**: High

**Description**: Attackers inject malicious or unauthorized events into the event system.

**Attack Scenarios**:
- Injecting events that trigger privileged actions
- Spoofing event sources to bypass authorization
- Injecting malformed events to crash handlers
- Using events to propagate malicious payloads

**Mitigations**:
- Validate event sources and authenticate emitters
- Implement strict event schema validation
- Use signed events for critical operations
- Sanitize event payloads before processing

```python
# Example: Event source validation
from codomyrmex.events import EventBus

def validate_event_source(event):
    """Validate that event comes from authorized source."""
    allowed_sources = ["auth_service", "user_service", "api_gateway"]
    if event.source not in allowed_sources:
        raise SecurityError(f"Unauthorized event source: {event.source}")
    return True
```

#### Denial of Service via Event Flooding

**Threat Level**: High

**Description**: Attackers overwhelm the event system with excessive events, causing resource exhaustion.

**Attack Scenarios**:
- Publishing high-volume events to exhaust queue capacity
- Creating many event subscriptions to consume resources
- Triggering expensive event handlers repeatedly
- Causing event storms through circular event chains

**Mitigations**:
- Implement rate limiting on event publishing
- Set queue size limits with overflow policies
- Monitor event volumes and alert on anomalies
- Use circuit breakers for event processing

```python
# Example: Rate limiting configuration
event_bus = EventBus(
    max_queue_size=10000,
    rate_limit_per_second=1000,
    enable_circuit_breaker=True
)
```

#### Unauthorized Subscriptions

**Threat Level**: High

**Description**: Attackers subscribe to events they should not have access to.

**Attack Scenarios**:
- Subscribing to authentication events to capture credentials
- Listening to internal events to map system architecture
- Capturing sensitive business events for competitive intelligence
- Subscribing with malicious handlers to intercept and modify events

**Mitigations**:
- Implement subscription authorization
- Use event namespaces with access controls
- Audit subscription registrations
- Validate handler integrity

```python
# Example: Subscription authorization
def authorize_subscription(event_type: str, subscriber_id: str) -> bool:
    """Check if subscriber is authorized for event type."""
    acl = get_event_acl()
    return acl.can_subscribe(subscriber_id, event_type)

# Register with authorization check
if authorize_subscription("user.credentials", subscriber_id):
    event_bus.subscribe("user.credentials", handler)
else:
    raise PermissionDenied("Not authorized for this event type")
```

#### Event Replay Attacks

**Threat Level**: Medium

**Description**: Attackers capture and replay legitimate events to cause unauthorized actions.

**Attack Scenarios**:
- Replaying authentication success events
- Replaying transaction events to duplicate operations
- Replaying admin commands to gain privileges
- Replaying events out of order to cause inconsistencies

**Mitigations**:
- Include timestamps and nonces in events
- Implement idempotency for critical handlers
- Track processed event IDs
- Use event sequence numbers

```python
# Example: Replay protection
class ReplayProtectedHandler:
    def __init__(self):
        self.processed_events = set()
        self.max_event_age = 300  # 5 minutes

    def handle(self, event):
        # Check for replay
        if event.id in self.processed_events:
            raise SecurityError("Event replay detected")

        # Check event age
        if time.time() - event.timestamp > self.max_event_age:
            raise SecurityError("Event too old, possible replay")

        # Process event
        self._process(event)

        # Record as processed
        self.processed_events.add(event.id)
```

## Security Controls

### Event Schema Validation

```python
from codomyrmex.events import EventSchema, EventValidator

# Define strict event schema
user_event_schema = EventSchema(
    event_type="user.*",
    required_fields=["user_id", "timestamp", "source"],
    optional_fields=["metadata"],
    field_validators={
        "user_id": lambda x: isinstance(x, str) and len(x) == 36,
        "timestamp": lambda x: isinstance(x, (int, float)) and x > 0,
    }
)

# Validate events before processing
validator = EventValidator([user_event_schema])

def secure_handler(event):
    if not validator.validate(event):
        raise InvalidEventError("Event failed schema validation")
    # Process validated event
```

### Source Authentication

```python
# Sign events for critical operations
import hmac
import hashlib

def sign_event(event, secret_key):
    """Add HMAC signature to event."""
    payload = json.dumps(event.payload, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    event.signature = signature
    return event

def verify_event_signature(event, secret_key):
    """Verify event HMAC signature."""
    payload = json.dumps(event.payload, sort_keys=True)
    expected = hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(event.signature, expected)
```

### Rate Limiting

```python
from codomyrmex.events import RateLimiter

# Configure rate limiting
rate_limiter = RateLimiter(
    events_per_second=100,
    burst_size=500,
    per_source=True
)

def publish_with_limit(event):
    if not rate_limiter.allow(event.source):
        raise RateLimitExceeded("Event rate limit exceeded")
    event_bus.publish(event)
```

### Audit Logging

```python
from codomyrmex.events import EventLogger

# Configure security audit logging
audit_logger = EventLogger(
    log_level="INFO",
    sensitive_fields=["password", "token", "api_key"],
    redact_sensitive=True
)

# Log security-relevant events
audit_logger.log_subscription("user.credentials", subscriber_id)
audit_logger.log_event(event, include_payload=False)
```

## Secure Usage Guidelines

### Do's

1. **Validate All Events**
   ```python
   def handler(event):
       # Always validate before processing
       if not is_valid_event(event):
           log.warning(f"Invalid event rejected: {event.type}")
           return
       process_event(event)
   ```

2. **Use Typed Events**
   ```python
   from dataclasses import dataclass
   from typing import Optional

   @dataclass
   class UserCreatedEvent:
       user_id: str
       email: str
       timestamp: float
       source: str
       signature: Optional[str] = None
   ```

3. **Implement Handler Isolation**
   ```python
   async def isolated_handler(event):
       try:
           async with asyncio.timeout(30):
               await process_event(event)
       except asyncio.TimeoutError:
           log.error(f"Handler timeout for event: {event.id}")
       except Exception as e:
           log.error(f"Handler error: {e}")
           # Don't propagate to other handlers
   ```

4. **Sanitize Event Data in Logs**
   ```python
   def log_event(event):
       safe_payload = redact_sensitive_fields(event.payload)
       logger.info(f"Event: {event.type}", extra={"payload": safe_payload})
   ```

5. **Set Appropriate Timeouts**
   ```python
   event_bus = EventBus(
       handler_timeout=30,  # 30 seconds max
       async_handler_timeout=60
   )
   ```

### Don'ts

1. **Never Include Credentials in Events**
   ```python
   # BAD: Including password in event
   event_bus.publish(Event("user.login", {"user": user, "password": password}))

   # GOOD: Only include necessary identifiers
   event_bus.publish(Event("user.login", {"user_id": user.id}))
   ```

2. **Avoid Unbounded Event Queues**
   ```python
   # BAD: No queue limits
   event_bus = EventBus()

   # GOOD: Set explicit limits
   event_bus = EventBus(max_queue_size=10000, overflow_policy="drop_oldest")
   ```

3. **Don't Trust Event Sources Blindly**
   ```python
   # BAD: Trusting event source claim
   if event.source == "admin_service":
       do_admin_action()

   # GOOD: Verify event signature
   if verify_signature(event, admin_service_key):
       do_admin_action()
   ```

4. **Avoid Wildcard Subscriptions in Production**
   ```python
   # BAD: Overly broad subscription
   event_bus.subscribe("*", handler)

   # GOOD: Specific subscriptions
   event_bus.subscribe("user.created", user_handler)
   event_bus.subscribe("order.placed", order_handler)
   ```

## Known Vulnerabilities

### CVE Registry

No known CVEs at this time. This section will be updated as vulnerabilities are discovered and patched.

### Security Advisories

| Date | Severity | Description | Resolution |
|------|----------|-------------|------------|
| - | - | No current advisories | - |

### Deprecated Features

- **Unvalidated Event Publishing**: Always use schema validation for production deployments.
- **Synchronous Handlers Without Timeout**: Use async handlers with timeout protection.

## Security Testing

### Automated Security Tests

```python
import pytest
from codomyrmex.events import EventBus, Event

class TestEventSecurity:

    def test_event_injection_prevention(self):
        """Verify malformed events are rejected."""
        bus = EventBus(strict_validation=True)
        malformed_event = Event(type=None, payload="not_a_dict")
        with pytest.raises(InvalidEventError):
            bus.publish(malformed_event)

    def test_rate_limiting(self):
        """Verify rate limiting prevents flooding."""
        bus = EventBus(rate_limit=10)
        for i in range(20):
            if i < 10:
                bus.publish(Event(type="test", payload={}))
            else:
                with pytest.raises(RateLimitExceeded):
                    bus.publish(Event(type="test", payload={}))

    def test_subscription_isolation(self):
        """Verify handlers only receive authorized events."""
        bus = EventBus()
        received = []
        bus.subscribe("public.*", lambda e: received.append(e))
        bus.publish(Event(type="public.test", payload={}))
        bus.publish(Event(type="private.test", payload={}))
        assert len(received) == 1
        assert received[0].type == "public.test"

    def test_replay_protection(self):
        """Verify duplicate events are detected."""
        handler = ReplayProtectedHandler()
        event = Event(id="unique-id", type="test", payload={})
        handler.handle(event)
        with pytest.raises(SecurityError):
            handler.handle(event)  # Replay attempt
```

### Penetration Testing Checklist

- [ ] Test event injection with malicious payloads
- [ ] Test denial of service via event flooding
- [ ] Verify subscription authorization
- [ ] Test event replay attacks
- [ ] Verify handler timeout enforcement
- [ ] Test event source spoofing
- [ ] Verify sensitive data is redacted from logs

### Security Scanning

```bash
# Static analysis
bandit -r src/codomyrmex/events/

# Dependency vulnerabilities
safety check

# Async security issues
pylint src/codomyrmex/events/ --load-plugins=pylint_async
```

## Incident Response

### Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Events Module - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue.

### Response Procedures

#### Event Injection Incident

1. **Immediate**: Disable affected event types or handlers
2. **Short-term**: Enable enhanced event validation and logging
3. **Investigation**: Trace injected events to identify attack vector
4. **Remediation**: Patch validation logic and redeploy
5. **Post-incident**: Review event authentication mechanisms

#### Denial of Service Incident

1. **Immediate**: Enable strict rate limiting
2. **Short-term**: Increase queue capacity and handler resources
3. **Investigation**: Identify attack source and pattern
4. **Remediation**: Block malicious sources, tune rate limits
5. **Post-incident**: Review capacity planning and circuit breakers

#### Unauthorized Access Incident

1. **Immediate**: Revoke compromised subscriptions
2. **Short-term**: Audit all active subscriptions
3. **Investigation**: Determine scope of accessed events
4. **Notification**: Alert affected parties if sensitive data accessed
5. **Remediation**: Strengthen subscription authorization

#### Event Replay Incident

1. **Immediate**: Enable enhanced replay detection
2. **Short-term**: Invalidate compromised event signatures
3. **Investigation**: Identify replayed events and affected systems
4. **Remediation**: Rotate signing keys, implement idempotency
5. **Post-incident**: Review event lifecycle management

### Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Events` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

Thank you for helping keep Codomyrmex and the Events module secure.
