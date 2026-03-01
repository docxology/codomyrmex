#!/usr/bin/env python3
"""Telemetry Module - Comprehensive Usage Script.

Demonstrates OpenTelemetry tracing with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --service-name myapp     # Custom service name
    python basic_usage.py --verbose                # Verbose output
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"
spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class TelemetryScript(ScriptBase):
    """Comprehensive telemetry module demonstration."""

    def __init__(self):
        super().__init__(
            name="telemetry_usage",
            description="Demonstrate and test OpenTelemetry tracing",
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add telemetry-specific arguments."""
        group = parser.add_argument_group("Telemetry Options")
        group.add_argument(
            "--service-name", default="codomyrmex-demo",
            help="Service name for tracing (default: codomyrmex-demo)"
        )
        group.add_argument(
            "--num-spans", type=int, default=10,
            help="Number of test spans to create (default: 10)"
        )
        group.add_argument(
            "--nested-depth", type=int, default=3,
            help="Depth of nested spans (default: 3)"
        )
        group.add_argument(
            "--simulate-errors", action="store_true",
            help="Simulate errors in some spans"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute telemetry demonstrations."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "spans_created": 0,
            "trace_operations": [],
        }

        if config.dry_run:
            self.log_info(f"Would initialize tracing for service: {args.service_name}")
            self.log_info(f"Would create {args.num_spans} spans")
            results["dry_run"] = True
            return results

        # Import telemetry module (requires opentelemetry)
        try:
            from codomyrmex.telemetry import (
                TraceContext, start_span, get_current_span, traced,
                SimpleSpanProcessor, BatchSpanProcessor, OTLPExporter
            )
        except ImportError as e:
            self.log_info(f"Telemetry dependencies not available: {e}")
            self.log_info("OpenTelemetry package required for full telemetry support.")
            self.log_info("Install with: pip install opentelemetry-api opentelemetry-sdk")
            results["skipped"] = True
            results["reason"] = str(e)
            return results

        # Test 1: TraceContext initialization
        self.log_info(f"\n1. Initializing TraceContext for '{args.service_name}'")
        try:
            TraceContext.initialize(
                service_name=args.service_name,
                attributes={"environment": "demo", "version": "1.0.0"}
            )
            tracer = TraceContext.get_tracer(args.service_name)

            results["trace_context"] = {
                "service_name": args.service_name,
                "initialized": True,
            }
            results["tests_passed"] += 1
            self.log_success(f"TraceContext initialized for {args.service_name}")
        except Exception as e:
            self.log_error(f"TraceContext initialization failed: {e}")
        results["tests_run"] += 1

        # Test 2: Basic span creation
        self.log_info(f"\n2. Creating {args.num_spans} basic spans")
        try:
            span_times = []
            for i in range(args.num_spans):
                start_time = time.perf_counter()
                span = start_span(
                    f"test_span_{i}",
                    attributes={"span_index": i, "test_type": "basic"}
                )
                time.sleep(0.001)  # Simulate work
                span.end()
                span_times.append((time.perf_counter() - start_time) * 1000)
                results["spans_created"] += 1

            results["basic_spans"] = {
                "count": args.num_spans,
                "avg_time_ms": sum(span_times) / len(span_times),
                "total_time_ms": sum(span_times),
            }
            results["tests_passed"] += 1
            self.log_success(f"Created {args.num_spans} spans, avg {results['basic_spans']['avg_time_ms']:.2f}ms")
        except Exception as e:
            self.log_error(f"Basic span creation failed: {e}")
        results["tests_run"] += 1

        # Test 3: Nested spans
        self.log_info(f"\n3. Testing nested spans (depth={args.nested_depth})")
        try:
            def create_nested_spans(depth: int, parent_span=None):
                if depth <= 0:
                    return
                span = start_span(
                    f"nested_span_depth_{depth}",
                    attributes={"depth": depth},
                    parent=parent_span
                )
                results["spans_created"] += 1
                time.sleep(0.001)
                create_nested_spans(depth - 1, span)
                span.end()

            create_nested_spans(args.nested_depth)

            results["nested_spans"] = {
                "depth": args.nested_depth,
                "spans_created": args.nested_depth,
            }
            results["tests_passed"] += 1
            self.log_success(f"Created nested spans with depth {args.nested_depth}")
        except Exception as e:
            self.log_error(f"Nested span test failed: {e}")
        results["tests_run"] += 1

        # Test 4: @traced decorator
        self.log_info("\n4. Testing @traced decorator")
        try:
            @traced(name="decorated_function", attributes={"test": True})
            def sample_traced_function(x: int) -> int:
                time.sleep(0.002)
                return x * 2

            result = sample_traced_function(5)
            results["spans_created"] += 1

            results["traced_decorator"] = {
                "function_tested": "sample_traced_function",
                "input": 5,
                "output": result,
                "success": result == 10,
            }
            results["tests_passed"] += 1
            self.log_success(f"@traced decorator: result={result}")
        except Exception as e:
            self.log_error(f"Traced decorator test failed: {e}")
        results["tests_run"] += 1

        # Test 5: Span processors and exporters (API documentation)
        self.log_info("\n5. Documenting span processors and exporters")
        try:
            results["processors"] = {
                "SimpleSpanProcessor": {
                    "description": "Synchronous span processing",
                    "requires": "exporter instance",
                },
                "BatchSpanProcessor": {
                    "description": "Batched async span processing",
                    "requires": "exporter instance",
                },
            }
            results["exporters"] = {
                "OTLPExporter": {
                    "description": "Export to OTLP collector",
                    "default_endpoint": "http://localhost:4318/v1/traces",
                },
            }
            results["tests_passed"] += 1
            self.log_success("Processors and exporters documented")
        except Exception as e:
            self.log_error(f"Documentation test failed: {e}")
        results["tests_run"] += 1

        # Summary
        results["summary"] = {
            "total_spans_created": results["spans_created"],
            "tests_passed": results["tests_passed"],
            "tests_run": results["tests_run"],
        }

        # Metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        self.add_metric("spans_created", results["spans_created"])

        return results


if __name__ == "__main__":
    script = TelemetryScript()
    sys.exit(script.execute())
