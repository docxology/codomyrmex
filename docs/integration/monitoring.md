## 📈 Monitoring & Observability Integration

### **Prometheus & Grafana Integration**

```python
# monitoring_integration.py - Monitoring systems integration
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import asyncio
import aiohttp
from datetime import datetime, timedelta
import json

class PrometheusIntegration:
    """Integration with Prometheus for comprehensive monitoring."""

    def __init__(self, pushgateway_url: str = None):
        self.registry = CollectorRegistry()
        self.pushgateway_url = pushgateway_url

        # Define Codomyrmex-specific metrics
        self.analysis_counter = Counter(
            'codomyrmex_analyses_total',
            'Total number of analyses performed',
            ['module', 'analysis_type', 'status'],
            registry=self.registry
        )

        self.analysis_duration = Histogram(
            'codomyrmex_analysis_duration_seconds',
            'Time spent on analyses',
            ['module', 'analysis_type'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1, 5, 10, 30, 60, 300, 600]
        )

        self.active_jobs = Gauge(
            'codomyrmex_active_jobs',
            'Number of currently active jobs',
            ['job_type'],
            registry=self.registry
        )

        self.code_quality_score = Gauge(
            'codomyrmex_code_quality_score',
            'Latest code quality score',
            ['project', 'module'],
            registry=self.registry
        )

        self.ai_api_calls = Counter(
            'codomyrmex_ai_api_calls_total',
            'Total AI API calls',
            ['provider', 'model', 'status'],
            registry=self.registry
        )

        self.ai_token_usage = Counter(
            'codomyrmex_ai_tokens_used_total',
            'Total AI tokens consumed',
            ['provider', 'model', 'token_type'],
            registry=self.registry
        )

    def record_analysis(self, module: str, analysis_type: str,
                       duration: float, success: bool = True):
        """Record analysis metrics."""
        status = 'success' if success else 'error'

        self.analysis_counter.labels(
            module=module,
            analysis_type=analysis_type,
            status=status
        ).inc()

        self.analysis_duration.labels(
            module=module,
            analysis_type=analysis_type
        ).observe(duration)

    def update_active_jobs(self, job_type: str, count: int):
        """Update active job count."""
        self.active_jobs.labels(job_type=job_type).set(count)

    def record_quality_score(self, project: str, module: str, score: float):
        """Record code quality score."""
        self.code_quality_score.labels(
            project=project,
            module=module
        ).set(score)

    def record_ai_api_call(self, provider: str, model: str, success: bool = True,
                          input_tokens: int = 0, output_tokens: int = 0):
        """Record AI API usage."""
        status = 'success' if success else 'error'

        self.ai_api_calls.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()

        if input_tokens > 0:
            self.ai_token_usage.labels(
                provider=provider,
                model=model,
                token_type='input'
            ).inc(input_tokens)

        if output_tokens > 0:
            self.ai_token_usage.labels(
                provider=provider,
                model=model,
                token_type='output'
            ).inc(output_tokens)

    async def push_metrics(self, job_name: str = 'codomyrmex'):
        """Push metrics to Pushgateway."""
        if not self.pushgateway_url:
            logger.warning("No Pushgateway URL configured")
            return

        metrics_data = generate_latest(self.registry)
        url = f"{self.pushgateway_url}/metrics/job/{job_name}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=metrics_data,
                headers={'Content-Type': 'text/plain'}
            ) as response:
                if response.status == 200:
                    logger.info("Metrics pushed to Pushgateway successfully")
                else:
                    logger.error(f"Failed to push metrics: {response.status}")

class GrafanaIntegration:
    """Integration with Grafana for dashboard automation."""

    def __init__(self, grafana_url: str, api_key: str):
        self.grafana_url = grafana_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    async def create_codomyrmex_dashboard(self) -> str:
        """Create comprehensive Codomyrmex dashboard."""
        dashboard_config = {
            "dashboard": {
                "id": None,
                "title": "Codomyrmex Analytics",
                "tags": ["codomyrmex", "code-analysis"],
                "timezone": "browser",
                "refresh": "30s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    # Analysis Overview Panel
                    {
                        "id": 1,
                        "title": "Analysis Overview",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(codomyrmex_analyses_total)",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"displayMode": "list", "orientation": "auto"},
                                "mappings": [],
                                "thresholds": {
                                    "mode": "absolute",
                                    "steps": [
                                        {"color": "green", "value": None},
                                        {"color": "red", "value": 80}
                                    ]
                                }
                            }
                        }
                    },
                    # Analysis Duration Panel
                    {
                        "id": 2,
                        "title": "Analysis Duration",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, codomyrmex_analysis_duration_seconds_bucket)",
                                "refId": "A",
                                "legendFormat": "95th percentile"
                            },
                            {
                                "expr": "histogram_quantile(0.50, codomyrmex_analysis_duration_seconds_bucket)",
                                "refId": "B",
                                "legendFormat": "Median"
                            }
                        ]
                    },
                    # Code Quality Trends
                    {
                        "id": 3,
                        "title": "Code Quality Trends",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "codomyrmex_code_quality_score",
                                "refId": "A",
                                "legendFormat": "{{project}}/{{module}}"
                            }
                        ]
                    },
                    # AI API Usage
                    {
                        "id": 4,
                        "title": "AI API Usage",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum by (provider) (codomyrmex_ai_api_calls_total)",
                                "refId": "A"
                            }
                        ]
                    }
                ]
            },
            "overwrite": True
        }

        async with aiohttp.ClientSession() as session:
            url = f"{self.grafana_url}/api/dashboards/db"

            async with session.post(
                url,
                headers=self.headers,
                json=dashboard_config
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    dashboard_url = f"{self.grafana_url}/d/{result['uid']}"
                    logger.info(f"Codomyrmex dashboard created: {dashboard_url}")
                    return dashboard_url
                else:
                    error = await response.text()
                    logger.error(f"Failed to create dashboard: {error}")
                    raise Exception(f"Dashboard creation failed: {error}")

# Usage with monitoring integration
monitoring_prometheus = PrometheusIntegration("http://pushgateway:9091")
monitoring_grafana = GrafanaIntegration(
    "http://grafana:3000",
    os.getenv("GRAFANA_API_KEY")
)

async def monitored_analysis_workflow(codebase_path: str):
    """Analysis workflow with comprehensive monitoring."""
    from codomyrmex.coding.static_analysis import analyze_codebase
    import time

    start_time = time.time()

    # Update active jobs
    monitoring_prometheus.update_active_jobs('static_analysis', 1)

    try:
        # Perform analysis
        result = analyze_codebase(codebase_path)
        duration = time.time() - start_time

        # Record successful analysis
        monitoring_prometheus.record_analysis(
            'static_analysis',
            'codebase',
            duration,
            success=True
        )

        # Record quality score
        monitoring_prometheus.record_quality_score(
            Path(codebase_path).name,
            'overall',
            result.overall_quality_score
        )

        # Push metrics
        await monitoring_prometheus.push_metrics()

        return result

    except Exception as e:
        duration = time.time() - start_time

        # Record failed analysis
        monitoring_prometheus.record_analysis(
            'static_analysis',
            'codebase',
            duration,
            success=False
        )

        await monitoring_prometheus.push_metrics()
        raise

    finally:
        # Update active jobs
        monitoring_prometheus.update_active_jobs('static_analysis', 0)
```

## 🔗 Related Documentation

### **Integration Resources**

- **[Production Deployment](../deployment/production.md)**: Production integration patterns and security configuration
- **[Performance Optimization](../reference/performance.md)**: Integration performance tuning

### **Development Integration**

- **[Development Setup](../development/environment-setup.md)**: Development environment setup
- **[Testing Strategy](../development/testing-strategy.md)**: Integration testing patterns
- **[API Reference](../reference/api.md)**: Complete API documentation for integration

### **Module-Specific Integration**

- **[AI Agents API](../../src/codomyrmex/agents/API_SPECIFICATION.md)**: AI service integration
- **[Static Analysis API](../../src/codomyrmex/static_analysis/API_SPECIFICATION.md)**: Analysis service integration
- **[Data Visualization API](../../src/codomyrmex/data_visualization/API_SPECIFICATION.md)**: Visualization integration

---

**Integration Checklist** ✅:

- [ ] External service credentials configured securely
- [ ] Error handling and retry logic implemented
- [ ] Monitoring and alerting configured
- [ ] Rate limiting and API quotas managed
- [ ] Data persistence and backup strategies defined
- [ ] Integration testing automated
- [ ] Documentation and runbooks created
- [ ] Security review completed

**Need Integration Help?** Refer to our [Integration Troubleshooting Guide](../reference/troubleshooting.md#integration-issues) or check module-specific integration documentation.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
