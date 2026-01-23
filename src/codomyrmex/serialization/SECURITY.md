# Security Policy for Serialization Module

This document outlines security procedures and policies for the Serialization module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Serialization Module - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Serialization` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

## Security Considerations for Serialization Module

### Deserialization Security

- **Unsafe Deserialization**: Never use `pickle` or similar unsafe deserialization on untrusted data.
- **Type Validation**: Validate object types during deserialization.
- **Schema Validation**: Validate data against expected schemas before processing.

### Format-Specific Security

#### JSON Security
- Use `json.loads()` instead of `eval()` for JSON parsing.
- Validate JSON schema before processing.
- Set maximum depth limits to prevent stack overflow.

#### YAML Security
- Use `yaml.safe_load()` instead of `yaml.load()`.
- Never use `yaml.load()` with `Loader=yaml.FullLoader` on untrusted data.
- Be aware of YAML billion laughs attacks.

#### XML Security
- Disable external entity processing (XXE).
- Disable DTD processing when not needed.
- Use defusedxml or similar secure XML parsers.

#### Pickle Security
- **NEVER deserialize pickle data from untrusted sources**.
- Pickle can execute arbitrary code during deserialization.
- Use JSON, MessagePack, or other safe formats for untrusted data.

### Common Vulnerabilities Mitigated

1. **Remote Code Execution (RCE)**: Avoid unsafe deserialization (pickle, yaml.load).
2. **Denial of Service (DoS)**: Size limits and depth limits on input.
3. **XML External Entity (XXE)**: Disabled external entity processing.
4. **Billion Laughs Attack**: Size and depth limits on recursive structures.
5. **Type Confusion**: Strict type validation during deserialization.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Never deserialize untrusted data with unsafe methods (pickle, yaml.load).
- Validate input data against schemas before processing.
- Set size limits on serialized data to prevent DoS.
- Use typed serialization formats when possible (JSON Schema, Protocol Buffers).
- Log deserialization errors for security monitoring.
- Prefer JSON for data interchange with untrusted sources.
- Follow the principle of least privilege when configuring access or permissions.
- Regularly review configurations and logs for suspicious activity.

## Secure Configuration

```python
# Example secure serialization usage
import json
import yaml
from codomyrmex.serialization import serialize, deserialize

# SAFE: Using JSON for untrusted data
data = json.loads(untrusted_json_string)

# SAFE: Using yaml.safe_load()
config = yaml.safe_load(yaml_content)

# UNSAFE - NEVER DO THIS with untrusted data:
# import pickle
# obj = pickle.loads(untrusted_bytes)  # DANGEROUS!

# UNSAFE - NEVER DO THIS:
# yaml.load(untrusted_yaml)  # Can execute arbitrary code!

# Recommended approach with schema validation
from jsonschema import validate, ValidationError

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "value": {"type": "number"}
    },
    "required": ["name", "value"]
}

try:
    data = json.loads(input_string)
    validate(instance=data, schema=schema)
except (json.JSONDecodeError, ValidationError) as e:
    logger.error(f"Invalid input data: {e}")
```

## Security Audit Checklist

- [ ] Pickle is not used for untrusted data
- [ ] yaml.safe_load() is used instead of yaml.load()
- [ ] JSON parsing uses json.loads() (not eval)
- [ ] XML parsing has XXE protection enabled
- [ ] Input size limits are enforced
- [ ] Schema validation is implemented
- [ ] Deserialization errors are logged
- [ ] Type validation is performed on deserialized objects
- [ ] Recursive structure depth limits are set
- [ ] All serialization formats are explicitly specified (not auto-detected)

Thank you for helping keep Codomyrmex and the Serialization module secure.
