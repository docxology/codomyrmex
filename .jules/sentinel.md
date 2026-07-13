## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-03-01 - Fix Insecure Deserialization in Cache PickleSerializer

**Vulnerability:**
The `PickleSerializer` in `src/codomyrmex/cache/serializers/__init__.py` relied entirely on the standard library `pickle` to deserialize incoming byte payloads. Since `pickle.loads()` can execute arbitrary code encoded in the payload, this permitted remote code execution (RCE) if an attacker could inject or modify cached data.

**Learning:**
Relying on documented warnings (e.g., "Only use this with trusted data") is insufficient defense against insecure deserialization, especially in generic caching libraries that might inadvertently process untrusted network input. An active mitigation is required even when preserving the core capability.

**Prevention:**
When the functionality of unsafe deserializers (like `pickle`) is strictly required for preserving complex internal state (e.g., non-JSON serializable objects), implement mandatory HMAC (Hash-based Message Authentication Code) signature wrapping. By prepending a 32-byte cryptographic signature generated using a secret key, the deserializer can verify payload integrity in constant time before invoking the hazardous unpickling operation.
