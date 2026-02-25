# Security Policy for Documents Module

This document outlines security procedures, threat models, and policies for the Documents module.

## Security Overview

The Documents module provides document parsing, transformation, and management capabilities for various formats including JSON, YAML, PDF, Markdown, and more. Document handling systems are high-risk components due to their interaction with untrusted file content and file system operations.

### Security Principles

- **Input Distrust**: Treat all document content as potentially malicious
- **Sandboxed Processing**: Isolate document parsing and transformation operations
- **Minimal File System Access**: Restrict file operations to approved directories
- **Content Sanitization**: Sanitize document content before rendering or storage

## Threat Model

### Assets Protected

- File system integrity
- Application memory and execution context
- Sensitive data within documents
- System resources (CPU, memory, disk)

### Threat Actors

1. **External Attackers**: Submitting malicious documents to exploit parsing vulnerabilities
2. **Malicious Users**: Uploading crafted files to access unauthorized data
3. **Compromised Systems**: Using documents as vectors for malware distribution
4. **Automated Scanners**: Probing for document handling vulnerabilities

### Attack Vectors

#### Path Traversal

**Threat Level**: Critical

**Description**: Attackers manipulate file paths to access files outside permitted directories.

**Attack Scenarios**:
- Using `../` sequences to escape document directories
- Exploiting symlink following to access sensitive files
- Manipulating archive extraction paths (zip slip)
- Using URL encoding to bypass path validation

**Mitigations**:
- Normalize and validate all file paths
- Use allowlists for permitted directories
- Disable symlink following
- Validate archive contents before extraction

```python
import os
from pathlib import Path

def safe_path_join(base_dir: str, untrusted_path: str) -> str:
    """Safely join paths preventing directory traversal."""
    base = Path(base_dir).resolve()
    target = (base / untrusted_path).resolve()

    # Verify the resolved path is within base directory
    if not str(target).startswith(str(base) + os.sep):
        raise SecurityError("Path traversal attempt detected")

    return str(target)

# Example usage
safe_path = safe_path_join("/documents/uploads", user_filename)
```

#### Content Injection

**Threat Level**: High

**Description**: Attackers embed malicious content within documents that executes during processing or rendering.

**Attack Scenarios**:
- JavaScript injection in PDF documents
- YAML deserialization attacks (arbitrary code execution)
- XML External Entity (XXE) attacks
- Markdown HTML/script injection
- Server-Side Template Injection (SSTI) in document templates

**Mitigations**:
- Use safe document parsers (e.g., `yaml.safe_load()`)
- Disable external entity processing in XML parsers
- Sanitize HTML in markdown output
- Use sandboxed PDF rendering
- Validate and escape template content

```python
# Safe YAML loading
import yaml

def safe_yaml_load(content: str) -> dict:
    """Load YAML content safely without code execution risk."""
    return yaml.safe_load(content)  # Never use yaml.load() with untrusted data

# Safe XML parsing
from defusedxml import ElementTree

def safe_xml_parse(content: str):
    """Parse XML with external entities disabled."""
    return ElementTree.fromstring(content)
```

#### Unauthorized Access

**Threat Level**: High

**Description**: Attackers access documents or operations they are not authorized to perform.

**Attack Scenarios**:
- Accessing other users' documents through ID enumeration
- Bypassing document access controls
- Exploiting race conditions in permission checks
- Accessing temporary files during processing

**Mitigations**:
- Implement proper access control checks
- Use unpredictable document identifiers
- Apply TOCTOU (time-of-check to time-of-use) protections
- Secure temporary file handling

```python
import secrets
import os

class DocumentManager:
    def get_document(self, doc_id: str, user_id: str):
        """Get document with authorization check."""
        document = self.storage.get(doc_id)

        # Always check authorization
        if not self.authorize(user_id, document, "read"):
            raise PermissionDenied("Not authorized to access this document")

        return document

    def generate_doc_id(self) -> str:
        """Generate unpredictable document ID."""
        return secrets.token_urlsafe(32)

    def create_temp_file(self):
        """Create secure temporary file."""
        return tempfile.NamedTemporaryFile(
            dir=self.secure_temp_dir,
            delete=True,
            mode='w+b'
        )
```

#### Data Leakage

**Threat Level**: High

**Description**: Sensitive information is exposed through document processing or storage.

**Attack Scenarios**:
- Metadata leakage (author, modification dates, internal paths)
- Error messages revealing file system structure
- Temporary files not properly cleaned up
- Document search indexing sensitive content

**Mitigations**:
- Strip metadata from documents before sharing
- Use generic error messages
- Implement proper temporary file cleanup
- Encrypt sensitive document content

```python
def strip_metadata(document):
    """Remove sensitive metadata from document."""
    sensitive_fields = [
        'author', 'creator', 'producer',
        'creation_date', 'modification_date',
        'file_path', 'internal_id'
    ]
    for field in sensitive_fields:
        if hasattr(document, field):
            setattr(document, field, None)
    return document

def safe_error_message(exception: Exception) -> str:
    """Generate safe error message without path disclosure."""
    if isinstance(exception, FileNotFoundError):
        return "Document not found"
    elif isinstance(exception, PermissionError):
        return "Access denied"
    else:
        return "Document processing error"
```

## Security Controls

### Input Validation

```python
from codomyrmex.documents import DocumentValidator

class SecureDocumentValidator:
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.txt', '.md', '.json', '.yaml', '.yml', '.pdf'}
    ALLOWED_MIME_TYPES = {
        'text/plain', 'text/markdown', 'application/json',
        'application/x-yaml', 'application/pdf'
    }

    def validate(self, file_path: str, content: bytes) -> bool:
        # Check file size
        if len(content) > self.MAX_FILE_SIZE:
            raise ValidationError("File exceeds maximum size")

        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError("File type not allowed")

        # Check MIME type by content inspection
        detected_type = magic.from_buffer(content, mime=True)
        if detected_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationError("Content type not allowed")

        return True
```

### Path Security

```python
import os
from pathlib import Path

class SecurePathHandler:
    def __init__(self, base_directory: str):
        self.base = Path(base_directory).resolve()
        if not self.base.is_dir():
            raise ConfigurationError("Base directory does not exist")

    def resolve(self, user_path: str) -> Path:
        """Resolve user path within base directory safely."""
        # Normalize and resolve
        clean_path = user_path.lstrip('/\\')
        target = (self.base / clean_path).resolve()

        # Verify containment
        try:
            target.relative_to(self.base)
        except ValueError:
            raise SecurityError("Path traversal blocked")

        return target

    def is_safe_symlink(self, path: Path) -> bool:
        """Check if symlink target is within allowed directory."""
        if not path.is_symlink():
            return True
        target = path.resolve()
        try:
            target.relative_to(self.base)
            return True
        except ValueError:
            return False
```

### Content Sanitization

```python
import bleach
import re

class ContentSanitizer:
    # Allowed HTML tags for markdown rendering
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'a']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title'], 'code': ['class']}

    def sanitize_html(self, content: str) -> str:
        """Sanitize HTML content to prevent XSS."""
        return bleach.clean(
            content,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True
        )

    def sanitize_url(self, url: str) -> str:
        """Validate and sanitize URL to prevent SSRF."""
        parsed = urllib.parse.urlparse(url)

        # Only allow http(s) schemes
        if parsed.scheme not in ('http', 'https'):
            raise ValidationError("Invalid URL scheme")

        # Block internal/private networks
        if self._is_private_ip(parsed.hostname):
            raise ValidationError("Internal URLs not allowed")

        return url
```

### Access Control

```python
from enum import Enum
from typing import Set

class DocumentPermission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"

class DocumentAccessControl:
    def __init__(self):
        self.permissions = {}  # doc_id -> {user_id -> set of permissions}

    def grant(self, doc_id: str, user_id: str, permissions: Set[DocumentPermission]):
        """Grant permissions to user for document."""
        if doc_id not in self.permissions:
            self.permissions[doc_id] = {}
        self.permissions[doc_id][user_id] = permissions

    def check(self, doc_id: str, user_id: str, permission: DocumentPermission) -> bool:
        """Check if user has permission for document."""
        doc_perms = self.permissions.get(doc_id, {})
        user_perms = doc_perms.get(user_id, set())
        return permission in user_perms

    def audit_access(self, doc_id: str, user_id: str, permission: DocumentPermission, granted: bool):
        """Log access attempt for audit trail."""
        logger.info(
            "document_access",
            doc_id=doc_id,
            user_id=user_id,
            permission=permission.value,
            granted=granted
        )
```

## Secure Usage Guidelines

### Do's

1. **Validate All Input Paths**
   ```python
   def read_document(user_path: str):
       safe_handler = SecurePathHandler("/documents/uploads")
       resolved_path = safe_handler.resolve(user_path)
       return read_file(resolved_path)
   ```

2. **Use Safe Parsers**
   ```python
   # Always use safe_load for YAML
   import yaml
   data = yaml.safe_load(yaml_content)

   # Use defusedxml for XML
   from defusedxml import ElementTree
   tree = ElementTree.parse(xml_file)
   ```

3. **Sanitize Output Content**
   ```python
   def render_document(doc):
       sanitizer = ContentSanitizer()
       safe_content = sanitizer.sanitize_html(doc.html_content)
       return render_template("document.html", content=safe_content)
   ```

4. **Implement Resource Limits**
   ```python
   # Set parsing limits
   parser = DocumentParser(
       max_depth=100,
       max_file_size=50_000_000,
       timeout=30
   )
   ```

5. **Clean Up Temporary Files**
   ```python
   import tempfile
   import contextlib

   @contextlib.contextmanager
   def secure_temp_document():
       temp_file = tempfile.NamedTemporaryFile(delete=False)
       try:
           yield temp_file
       finally:
           temp_file.close()
           os.unlink(temp_file.name)
   ```

### Don'ts

1. **Never Trust User-Provided Paths**
   ```python
   # BAD: Direct path usage
   with open(user_provided_path, 'r') as f:
       return f.read()

   # GOOD: Validate and resolve path
   safe_path = secure_path_handler.resolve(user_provided_path)
   with open(safe_path, 'r') as f:
       return f.read()
   ```

2. **Never Use Unsafe Deserialization**
   ```python
   # BAD: Using yaml.load() with untrusted data
   data = yaml.load(untrusted_yaml, Loader=yaml.FullLoader)

   # GOOD: Using safe_load()
   data = yaml.safe_load(untrusted_yaml)
   ```

3. **Avoid Direct Content Rendering**
   ```python
   # BAD: Rendering unsanitized content
   return f"<div>{document.content}</div>"

   # GOOD: Sanitize before rendering
   safe_content = bleach.clean(document.content)
   return f"<div>{safe_content}</div>"
   ```

4. **Don't Expose Internal Paths**
   ```python
   # BAD: Exposing file paths in errors
   raise Exception(f"Failed to read {full_system_path}")

   # GOOD: Generic error messages
   raise DocumentNotFoundError("Document not found")
   ```

## Known Vulnerabilities

### CVE Registry

No known CVEs at this time. This section will be updated as vulnerabilities are discovered and patched.

### Security Advisories

| Date | Severity | Description | Resolution |
|------|----------|-------------|------------|
| - | - | No current advisories | - |

### Deprecated Features

- **Direct YAML Loading**: Use `yaml.safe_load()` instead of `yaml.load()`
- **XML without defusedxml**: Always use defusedxml for untrusted XML content
- **Unvalidated Path Operations**: All file operations must use path validation

## Security Testing

### Automated Security Tests

```python
import pytest
from codomyrmex.documents import DocumentReader, DocumentWriter

class TestDocumentSecurity:

    def test_path_traversal_prevention(self):
        """Verify path traversal attacks are blocked."""
        reader = DocumentReader(base_dir="/documents")
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fetc/passwd"
        ]
        for path in malicious_paths:
            with pytest.raises(SecurityError):
                reader.read(path)

    def test_yaml_deserialization_safety(self):
        """Verify YAML parsing doesn't execute code."""
        malicious_yaml = """
        !!python/object/apply:os.system
        args: ['echo PWNED']
        """
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(malicious_yaml)

    def test_xml_xxe_prevention(self):
        """Verify XML external entities are disabled."""
        xxe_xml = """<?xml version="1.0"?>
        <!DOCTYPE foo [
          <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <foo>&xxe;</foo>"""
        from defusedxml import ElementTree
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(xxe_xml)

    def test_file_size_limits(self):
        """Verify oversized files are rejected."""
        validator = DocumentValidator(max_size=1024)
        large_content = b"x" * 10000
        with pytest.raises(ValidationError):
            validator.validate(large_content)

    def test_content_sanitization(self):
        """Verify malicious HTML is sanitized."""
        sanitizer = ContentSanitizer()
        malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
        safe_html = sanitizer.sanitize_html(malicious_html)
        assert "<script>" not in safe_html
        assert "<p>Safe content</p>" in safe_html
```

### Penetration Testing Checklist

- [ ] Test path traversal with various encoding techniques
- [ ] Test XML external entity injection
- [ ] Test YAML deserialization attacks
- [ ] Verify file size and type limits
- [ ] Test symlink following attacks
- [ ] Verify access control enforcement
- [ ] Test content injection in all document formats
- [ ] Verify temporary file security
- [ ] Test error message information disclosure

### Security Scanning

```bash
# Static analysis
bandit -r src/codomyrmex/documents/

# Dependency vulnerabilities (check for vulnerable parsers)
safety check

# SAST for path traversal
semgrep --config p/security-audit src/codomyrmex/documents/
```

## Incident Response

### Reporting a Vulnerability

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

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue.

### Response Procedures

#### Path Traversal Incident

1. **Immediate**: Disable document upload/access endpoints
2. **Short-term**: Audit file access logs for unauthorized access
3. **Investigation**: Determine files accessed and data exposure
4. **Remediation**: Patch path validation and redeploy
5. **Post-incident**: Notify affected users, review all path handling code

#### Content Injection Incident

1. **Immediate**: Quarantine affected documents
2. **Short-term**: Enable enhanced content scanning
3. **Investigation**: Identify injection vector and scope
4. **Remediation**: Update parsers and sanitizers
5. **Post-incident**: Re-scan document repository

#### Unauthorized Access Incident

1. **Immediate**: Suspend compromised accounts
2. **Short-term**: Audit document access logs
3. **Investigation**: Determine scope of unauthorized access
4. **Notification**: Alert affected document owners
5. **Remediation**: Strengthen access controls

#### Data Leakage Incident

1. **Immediate**: Remove exposed documents from public access
2. **Short-term**: Audit document metadata and search indexes
3. **Investigation**: Determine scope of data exposure
4. **Notification**: Alert affected parties per compliance requirements
5. **Remediation**: Implement metadata stripping and content filtering

### Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Documents` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

Thank you for helping keep Codomyrmex and the Documents module secure.
