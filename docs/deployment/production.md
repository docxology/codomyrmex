# Production Deployment Guide

This guide covers deploying Codomyrmex modules and workflows in production environments, focusing on scalability, security, and reliability.

## 🎯 Deployment Overview

### **Deployment Patterns**

```mermaid
graph TB
    subgraph "Development"
        Dev["Development<br/>Environment"]
        Testing["Testing &<br/>Validation"]
    end

    subgraph "Staging"
        Staging["Staging<br/>Environment"]
        Integration["Integration<br/>Testing"]
    end

    subgraph "Production"
        Prod["Production<br/>Environment"]
        Monitor["Monitoring &<br/>Observability"]
    end

    Dev --> Testing
    Testing --> Staging
    Staging --> Integration
    Integration --> Prod
    Prod --> Monitor
    Monitor -.-> Dev
```

### **Deployment Strategies**

- **🔵 Blue-Green**: Zero-downtime deployments with instant rollback
- **🎯 Canary**: Gradual rollout with traffic splitting
- **📊 Rolling**: Sequential instance updates with health checks
- **🚀 Feature Flags**: Runtime feature toggling for safe releases

## 🏗️ Infrastructure Setup

### **Container Configuration**

#### **Production Dockerfile**

```dockerfile
# Multi-stage build for production
FROM python:3.13-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Build dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.13-slim as production

# Security: Create non-root user
RUN groupadd --gid 1000 codomyrmex && \
    useradd --uid 1000 --gid 1000 --create-home codomyrmex

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY --chown=codomyrmex:codomyrmex . /app
WORKDIR /app

# Switch to non-root user
USER codomyrmex

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
EXPOSE 8000
CMD ["python", "-m", "codomyrmex", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

#### **Docker Compose for Production**

```yaml
version: '3.8'

services:
  codomyrmex:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - CODOMYRMEX_ENV=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    depends_on:
      - database
      - cache
    networks:
      - codomyrmex-network

  database:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - codomyrmex-network

  cache:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - codomyrmex-network

  reverse-proxy:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - codomyrmex
    networks:
      - codomyrmex-network

volumes:
  postgres_data:
  redis_data:

networks:
  codomyrmex-network:
    driver: bridge
```

### **Kubernetes Deployment**

#### **Production Namespace**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: codomyrmex-prod
  labels:
    environment: production
    app: codomyrmex
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codomyrmex-api
  namespace: codomyrmex-prod
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: codomyrmex-api
  template:
    metadata:
      labels:
        app: codomyrmex-api
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: api
        image: codomyrmex/api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: CODOMYRMEX_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: codomyrmex-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: output-storage
          mountPath: /app/output
      volumes:
      - name: output-storage
        persistentVolumeClaim:
          claimName: codomyrmex-output-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: codomyrmex-api-service
  namespace: codomyrmex-prod
spec:
  selector:
    app: codomyrmex-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

## 🔒 Security Configuration

### **Environment Variables & Secrets**

```bash
# Production Environment Variables
export CODOMYRMEX_ENV=production
export LOG_LEVEL=INFO
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://user:pass@db:5432/codomyrmex
export REDIS_URL=redis://cache:6379/0

# API Keys (use secret management)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=AIza...

# Security Settings
export ALLOWED_HOSTS=api.yourdomain.com,codomyrmex.yourdomain.com
export CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
export RATE_LIMIT_PER_MINUTE=100
export MAX_FILE_SIZE_MB=50
```

### **TLS/SSL Configuration**

```nginx
# nginx.conf for HTTPS
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://codomyrmex:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### **Database Security**

```sql
-- Create production database with proper permissions
CREATE DATABASE codomyrmex_prod;
CREATE USER codomyrmex_app WITH PASSWORD 'secure_random_password';

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE codomyrmex_prod TO codomyrmex_app;
GRANT USAGE ON SCHEMA public TO codomyrmex_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO codomyrmex_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO codomyrmex_app;

-- Enable row-level security if needed
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_data_policy ON sensitive_data FOR ALL TO codomyrmex_app USING (user_id = current_user_id());
```

## 📊 Monitoring & Observability

### **Health Checks & Metrics**

```python
# Health check endpoint
from flask import Flask, jsonify
from codomyrmex.logging_monitoring import get_system_metrics

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Detailed health check for production monitoring."""
    try:
        # Check database connectivity
        db_status = check_database_connection()

        # Check cache connectivity
        cache_status = check_redis_connection()

        # Check API key validity
        api_status = check_api_keys()

        # Check disk space
        disk_status = check_disk_space()

        # Check memory usage
        memory_status = check_memory_usage()

        all_healthy = all([
            db_status['healthy'],
            cache_status['healthy'],
            api_status['healthy'],
            disk_status['healthy'],
            memory_status['healthy']
        ])

        return jsonify({
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': db_status,
                'cache': cache_status,
                'apis': api_status,
                'disk': disk_status,
                'memory': memory_status
            },
            'version': get_version(),
            'uptime': get_uptime()
        }), 200 if all_healthy else 503

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
```

### **Prometheus Metrics**

```python
# metrics.py - Production metrics collection
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Define metrics
REQUEST_COUNT = Counter('codomyrmex_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('codomyrmex_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('codomyrmex_active_connections', 'Active connections')
QUEUE_SIZE = Gauge('codomyrmex_queue_size', 'Current queue size', ['queue_name'])

# AI API metrics
AI_API_CALLS = Counter('codomyrmex_ai_api_calls_total', 'AI API calls', ['provider', 'model', 'status'])
AI_API_DURATION = Histogram('codomyrmex_ai_api_duration_seconds', 'AI API call duration', ['provider'])
AI_API_TOKENS = Histogram('codomyrmex_ai_api_tokens_used', 'AI API tokens used', ['provider', 'type'])

# Module-specific metrics
MODULE_EXECUTIONS = Counter('codomyrmex_module_executions_total', 'Module executions', ['module', 'status'])
MODULE_DURATION = Histogram('codomyrmex_module_duration_seconds', 'Module execution duration', ['module'])

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()
```

### **Logging Configuration**

```python
# production_logging.py
import logging
import logging.config
from pythonjsonlogger import jsonlogger

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': '/app/logs/codomyrmex.log',
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 10
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    },
    'loggers': {
        'codomyrmex': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'codomyrmex.agents': {
            'level': 'DEBUG',  # More verbose for AI operations
            'handlers': ['file'],
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## ⚡ Performance Optimization

### **Caching Strategy**

```python
# caching.py - Production caching
import redis
from functools import wraps
import pickle
import hashlib

redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))

def cache_result(expiry=3600, key_prefix='codomyrmex'):
    """Cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
            cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)

            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, pickle.dumps(result))

            return result
        return wrapper
    return decorator

# Usage example
@cache_result(expiry=1800)  # 30 minutes
def analyze_large_codebase(codebase_path):
    """Cache expensive static analysis results."""
    from codomyrmex.static_analysis import analyze_codebase
    return analyze_codebase(codebase_path)
```

### **Async Processing**

```python
# async_workers.py - Background task processing
from celery import Celery
from codomyrmex.agents import enhance_code
from codomyrmex.logging_monitoring import get_logger

# Configure Celery for async processing
celery_app = Celery('codomyrmex',
                   broker=os.getenv('REDIS_URL'),
                   backend=os.getenv('REDIS_URL'))

logger = get_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def async_code_enhancement(self, code, enhancement_options):
    """Process code enhancement asynchronously."""
    try:
        result = enhance_code(code, **enhancement_options)
        logger.info(f"Code enhancement completed for task {self.request.id}")
        return result

    except Exception as exc:
        logger.error(f"Code enhancement failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task
def batch_analysis_task(file_paths):
    """Process multiple files in batch."""
    from codomyrmex.static_analysis import analyze_file
    results = {}

    for file_path in file_paths:
        try:
            results[file_path] = analyze_file(file_path)
        except Exception as e:
            results[file_path] = {'error': str(e)}

    return results
```

## 🚀 CI/CD Pipeline

### **GitHub Actions Production Pipeline**

```yaml
# .github/workflows/production.yml
name: Production Deployment

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        uv sync --dev

    - name: Run comprehensive tests
      run: |
        uv run pytest src/codomyrmex/tests/ --cov=src/codomyrmex --cov-report=xml -n auto

    - name: Security scan
      run: |
        uv add --dev bandit safety
        uv run bandit -r src/codomyrmex/
        uv run safety check --json

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ghcr.io/${{ github.repository }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.prod
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || 'production' }}
    steps:
    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=./kubeconfig

        # Update deployment with new image
        kubectl set image deployment/codomyrmex-api \
          api=${{ needs.build.outputs.image-tag }} \
          -n codomyrmex-${{ inputs.environment || 'prod' }}

        # Wait for rollout to complete
        kubectl rollout status deployment/codomyrmex-api \
          -n codomyrmex-${{ inputs.environment || 'prod' }} \
          --timeout=600s

    - name: Run smoke tests
      run: |
        # Wait for service to be ready
        sleep 30

        # Basic health check
        curl -f https://api.yourdomain.com/health

        # API functionality test
        curl -f -X POST https://api.yourdomain.com/api/v1/analyze \
          -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
          -H "Content-Type: application/json" \
          -d '{"code": "print(\"Hello, World!\")"}'
```

## 🔄 Backup & Disaster Recovery

### **Database Backup Strategy**

```bash
#!/bin/bash
# backup.sh - Automated database backup

set -euo pipefail

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="codomyrmex_backup_${TIMESTAMP}.sql.gz"

# Create backup
pg_dump $DATABASE_URL | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to cloud storage
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://codomyrmex-backups/database/"

# Keep only last 30 days of backups locally
find $BACKUP_DIR -name "codomyrmex_backup_*.sql.gz" -mtime +30 -delete

# Verify backup integrity
gunzip -t "${BACKUP_DIR}/${BACKUP_FILE}"

echo "Backup completed successfully: ${BACKUP_FILE}"
```

### **Application State Backup**

```python
# state_backup.py - Backup application state
import json
import boto3
from datetime import datetime
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def backup_application_state():
    """Backup critical application state to S3."""
    s3_client = boto3.client('s3')
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    # Collect state information
    state = {
        'timestamp': timestamp,
        'active_configurations': get_active_configurations(),
        'user_preferences': export_user_preferences(),
        'module_settings': export_module_settings(),
        'api_rate_limits': get_rate_limit_state(),
        'cache_keys': list_important_cache_keys()
    }

    # Upload to S3
    backup_key = f"application-state/backup_{timestamp}.json"
    s3_client.put_object(
        Bucket='codomyrmex-backups',
        Key=backup_key,
        Body=json.dumps(state, indent=2),
        ServerSideEncryption='AES256'
    )

    logger.info(f"Application state backup completed: {backup_key}")
```

## 🔗 Related Documentation

### **Deployment Resources**

- **[Troubleshooting Production](../reference/troubleshooting.md#production-issues)**: Production issue resolution
- **[Performance Guide](../reference/performance.md)**: Performance optimization strategies
- **[Security Considerations](../reference/troubleshooting.md#security-issues)**: Security best practices

### **Operational Guides**

- **[Troubleshooting Guide](../reference/troubleshooting.md)**: Comprehensive issue resolution
- **[Performance Optimization](../reference/performance.md)**: Performance tuning strategies
- **[Architecture Overview](../project/architecture.md)**: System design for deployment considerations

### **Development Integration**

- **[Testing Strategy](../development/testing-strategy.md)**: Testing approach and best practices
- **[Development Setup](../development/environment-setup.md)**: Development environment configuration
- **[Contributing Guide](../project/contributing.md)**: How to contribute effectively

---

**Production Readiness Checklist** ✅:

- [ ] Security configuration validated
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested
- [ ] Performance benchmarks established
- [ ] CI/CD pipeline operational
- [ ] Documentation up to date
- [ ] Incident response procedures defined
- [ ] Team training completed

**Need Help?** Refer to our [Troubleshooting Guide](../reference/troubleshooting.md) or contact the team through established channels.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
