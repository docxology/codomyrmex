# Security Submodule

Container security scanning and performance optimization.

## Components

- `security_scanner.py` - Vulnerability scanning
- `performance_optimizer.py` - Runtime optimization

## Usage

```python
from codomyrmex.containerization.security import SecurityScanner
scanner = SecurityScanner()
vulnerabilities = scanner.scan_image("myapp:latest")
```
