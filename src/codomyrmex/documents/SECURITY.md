# Security Policy for Documents Module

This document outlines security procedures and policies for the Documents module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Documents Module - [Brief Description]".

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

This security policy applies only to the `Documents` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

## Security Considerations for Documents Module

### File I/O Security

- **Path Traversal Prevention**: Always validate and sanitize file paths to prevent directory traversal attacks (e.g., `../../../etc/passwd`).
- **File Type Validation**: Validate file types by content inspection, not just extensions.
- **File Size Limits**: Implement file size limits to prevent denial of service through resource exhaustion.
- **Temporary Files**: Use secure temporary file creation; clean up temporary files promptly.

### Format-Specific Security

#### JSON/YAML Handling
- Use safe loaders (e.g., `yaml.safe_load()`) to prevent code execution through deserialization attacks.
- Validate JSON/YAML structures against schemas before processing.
- Limit recursion depth to prevent stack overflow attacks.

#### PDF Handling
- Be aware that PDFs can contain JavaScript; consider sanitizing or restricting features.
- Validate PDF structure before processing to prevent parser exploits.
- Use sandboxed rendering for untrusted PDFs.

#### Markdown Handling
- Sanitize HTML in markdown output to prevent XSS attacks.
- Disable or sanitize embedded HTML and JavaScript.
- Validate URLs in links to prevent SSRF attacks.

### Document Parsing Security

- **Input Validation**: Validate all input documents against expected schemas.
- **Encoding Detection**: Handle encoding detection securely; default to safe encodings.
- **Resource Limits**: Set limits on parsing time, memory usage, and recursion depth.

### Common Vulnerabilities Mitigated

1. **Path Traversal**: Validate all file paths; use allowlists for permitted directories.
2. **XML External Entity (XXE)**: Disable external entity processing in XML parsers.
3. **Deserialization Attacks**: Use safe deserialization methods; validate before deserializing.
4. **Denial of Service**: Implement size limits, timeouts, and resource quotas.
5. **Cross-Site Scripting (XSS)**: Sanitize document content before rendering in web contexts.

### Document Storage Security

- Store sensitive documents with appropriate file permissions
- Consider encryption at rest for confidential documents
- Implement access control for document operations
- Audit document access and modifications

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Validate file paths against an allowlist of permitted directories.
- Set appropriate file size limits for your use case.
- Use content-type detection, not just file extensions, for validation.
- Sanitize document content before displaying in web interfaces.
- Handle encoding errors gracefully; don't expose error details to users.
- Implement logging for document operations without logging sensitive content.
- Follow the principle of least privilege for file system access.
- Regularly review and update document format handlers.

## Secure Configuration

```python
# Example secure configuration
from codomyrmex.documents import DocumentReader, DocumentValidator

# Always validate documents before processing
# validator = DocumentValidator()
# validator.set_max_file_size(10 * 1024 * 1024)  # 10MB limit
# validator.set_allowed_formats(['json', 'yaml', 'markdown', 'text'])

# Use safe loaders for YAML
# from codomyrmex.documents import read_yaml
# data = read_yaml(path)  # Uses yaml.safe_load internally

# Sanitize paths before file operations
# import os
# base_dir = "/safe/document/directory"
# safe_path = os.path.normpath(os.path.join(base_dir, user_input))
# if not safe_path.startswith(base_dir):
#     raise SecurityError("Path traversal attempt detected")
```

Thank you for helping keep Codomyrmex and the Documents module secure.
