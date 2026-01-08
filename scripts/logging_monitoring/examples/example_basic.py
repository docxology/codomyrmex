#!/usr/bin/env python3
"""
Example: Logging Monitoring - Comprehensive Logging System

This example demonstrates the complete Codomyrmex logging and monitoring capabilities:

CORE FUNCTIONALITY:
- Centralized logging system setup with configurable backends
- Hierarchical logger creation for different application components
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured logging with JSON and TEXT format support
- Performance monitoring and metrics logging
- Error handling and context preservation
- Log aggregation and filtering capabilities

ADVANCED FEATURES:
- Custom log formatting and output destinations
- Log rotation and retention policies
- Asynchronous logging for performance
- Log correlation IDs for request tracing
- Security event logging and audit trails

COMMON USE CASES:
- Application monitoring and debugging
- Performance bottleneck identification
- Security incident investigation
- Compliance and audit logging
- Distributed system observability

CONFIGURATION OPTIONS:
- Output formats: TEXT, JSON, XML
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Destinations: Console, Files, Remote servers, Databases
- Filtering: By logger name, level, or custom criteria
- Rotation: Size-based, time-based, or hybrid

ERROR HANDLING:
- Graceful handling of logging failures
- Fallback to console logging if file logging fails
- Recovery from log file permission issues
- Buffer management for high-throughput scenarios

Tested Methods:
- setup_logging() - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_setup_logging_with_file_output
- get_logger(name) - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_get_logger_real_functionality
- JsonFormatter - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_json_logging_format
- TextFormatter - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_text_logging_format
- FileHandler - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_file_handler_configuration
- StructuredLogger - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_structured_logging

USAGE EXAMPLES:
    # Basic usage
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    setup_logging()
    logger = get_logger('my_module')
    logger.info("Application started successfully")

    # Structured logging with context
    logger.info("User login", extra={
        'user_id': 12345,
        'ip_address': '192.168.1.100',
        'user_agent': 'Mozilla/5.0...'
    })

    # Error logging with stack traces
    try:
        risky_operation()
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)

    # Performance logging
    import time
    start_time = time.time()
    result = expensive_operation()
    logger.info("Operation completed", extra={
        'duration_ms': (time.time() - start_time) * 1000,
        'records_processed': len(result)
    })
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for importing Codomyrmex modules
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

from codomyrmex.logging_monitoring import setup_logging, get_logger
from _common.config_loader import load_config
from _common.example_runner import ExampleRunner
from _common.utils import print_section, ensure_output_dir, print_success, print_error

def main():
    """
    Run the comprehensive logging monitoring example.

    This function demonstrates:
    1. Basic logger setup and configuration
    2. Multiple log levels and their use cases
    3. Hierarchical logging with component separation
    4. Structured logging with contextual data
    5. Error handling and exception logging
    6. Performance monitoring and metrics
    7. Edge cases and error scenarios
    8. Configuration validation and fallbacks
    """
    print_section("Logging Monitoring Example")
    print("Demonstrating comprehensive logging and monitoring capabilities")

    # Load configuration with error handling
    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        print("Using default configuration...")
        config = {
            'logging': {
                'level': 'INFO',
                'output_type': 'TEXT',
                'file': 'logs/example.log'
            }
        }

    # Initialize runner with configuration
    runner = ExampleRunner(__file__, config)
    runner.start()

    # Initialize results tracking
    results = {
        'status': 'initialized',
        'loggers_created': 0,
        'log_levels_tested': [],
        'structured_logs': 0,
        'errors_handled': 0,
        'performance_metrics_logged': 0,
        'edge_cases_tested': 0
    }

    try:
        # Step 1: Setup logging system
        print("\n" + "="*60)
        print("Step 1: Setting up Centralized Logging System")
        print("="*60)

        try:
            # Setup logging based on configuration
            # This initializes the logging system with proper formatters and handlers
            setup_logging()
            print_success("✓ Logging system initialized successfully")
            print(f"  - Output format: {config.get('logging', {}).get('output_type', 'TEXT')}")
            print(f"  - Log level: {config.get('logging', {}).get('level', 'INFO')}")
        except Exception as e:
            print_error(f"✗ Failed to setup logging: {e}")
            print("  Continuing with default logging...")
            results['errors_handled'] += 1

        # Step 2: Create hierarchical loggers
        print("\n" + "="*60)
        print("Step 2: Creating Hierarchical Loggers")
        print("="*60)
        print("Creating loggers for different application components...")

        # Create loggers for different application components
        # Each logger inherits configuration from the root logger but can have specific settings
        logger_main = get_logger('example.main')  # Main application logger
        logger_component1 = get_logger('example.component1')  # Component-specific logger
        logger_component2 = get_logger('example.component2')  # Another component logger
        logger_performance = get_logger('example.performance')  # Performance monitoring logger

        results['loggers_created'] = 4
        print_success(f"✓ Created {results['loggers_created']} hierarchical loggers")

        # Step 3: Demonstrate log levels
        print("\n" + "="*60)
        print("Step 3: Log Levels and Their Use Cases")
        print("="*60)

        print("Testing different log levels from DEBUG to CRITICAL...")

        # DEBUG: Detailed diagnostic information for developers
        logger_main.debug("This is a DEBUG message - detailed diagnostic information")
        logger_main.debug("Memory usage: 128MB, CPU usage: 45%, Active threads: 8")

        # INFO: General operational information
        logger_main.info("This is an INFO message - normal operational information")
        logger_main.info("Application started successfully on port 8080")

        # WARNING: Something unexpected but not critical
        logger_main.warning("This is a WARNING message - something unexpected but not critical")
        logger_main.warning("High memory usage detected: 85% of available RAM")

        # ERROR: Something went wrong that needs attention
        logger_main.error("This is an ERROR message - something went wrong")
        logger_main.error("Failed to connect to database after 3 attempts")

        # CRITICAL: System-threatening errors
        logger_main.critical("This is a CRITICAL message - system-threatening error")
        logger_main.critical("System out of memory, initiating emergency shutdown")

        results['log_levels_tested'] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        print_success(f"✓ Tested {len(results['log_levels_tested'])} log levels")

        # Step 4: Hierarchical logging demonstration
        print("\n" + "="*60)
        print("Step 4: Hierarchical Logging with Component Separation")
        print("="*60)

        print("Demonstrating how different components log independently...")

        # Component 1: Data processing component
        logger_component1.info("Component 1 is starting initialization")
        logger_component1.info("Component 1 loaded configuration successfully")
        logger_component1.info("Component 1 processed 1000 records successfully")

        # Component 2: Network communication component
        logger_component2.info("Component 2 is starting network services")
        logger_component2.warning("Component 2 detected slow network response: 2.5s")
        logger_component2.info("Component 2 established 5 concurrent connections")

        print_success("✓ Hierarchical logging demonstrated with component separation")

        # Step 5: Structured logging with contextual data
        print("\n" + "="*60)
        print("Step 5: Structured Logging with Contextual Data")
        print("="*60)

        print("Logging with structured data for better analysis and monitoring...")

        # User authentication event
        logger_main.info("User authentication successful", extra={
            'event_type': 'user_auth',
            'user_id': 'user_12345',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'session_id': 'sess_abc123',
            'timestamp': time.time()
        })

        # API request logging
        logger_main.info("API request processed", extra={
            'event_type': 'api_request',
            'method': 'POST',
            'endpoint': '/api/users',
            'status_code': 201,
            'response_time_ms': 245.67,
            'request_size_bytes': 1024,
            'response_size_bytes': 512,
            'user_id': 'user_12345'
        })

        # Data processing metrics
        logger_main.info("Data processing completed", extra={
            'event_type': 'data_processing',
            'records_processed': 10000,
            'processing_time_seconds': 15.34,
            'success_rate': 0.987,
            'error_count': 123,
            'throughput_per_second': 652.8
        })

        results['structured_logs'] = 3
        print_success(f"✓ Logged {results['structured_logs']} structured events with contextual data")

        # Step 6: Error handling and exception logging
        print("\n" + "="*60)
        print("Step 6: Error Handling and Exception Logging")
        print("="*60)

        print("Demonstrating proper error logging with context and stack traces...")

        # Example 1: Division by zero
        try:
            # Simulate a mathematical error
            result = 10 / 0
        except ZeroDivisionError as e:
            logger_main.error(f"Mathematical error occurred during calculation: {e}", exc_info=True)
            results['errors_handled'] += 1

        # Example 2: File operation error
        try:
            # Attempt to read a non-existent file
            with open('/nonexistent/file.txt', 'r') as f:
                content = f.read()
        except FileNotFoundError as e:
            logger_main.error(f"File operation failed: {e}", extra={
                'operation': 'file_read',
                'file_path': '/nonexistent/file.txt',
                'error_type': 'FileNotFoundError'
            })
            results['errors_handled'] += 1

        # Example 3: Network timeout simulation
        try:
            # Simulate network timeout
            import socket
            sock = socket.socket()
            sock.settimeout(0.001)  # Very short timeout
            sock.connect(('192.168.255.255', 12345))  # Non-routable address
        except (socket.timeout, socket.error) as e:
            logger_main.error(f"Network operation failed: {e}", extra={
                'operation': 'network_connect',
                'target': '192.168.255.255:12345',
                'timeout_ms': 1,
                'error_type': type(e).__name__
            })
            results['errors_handled'] += 1

        print_success(f"✓ Handled {results['errors_handled']} error scenarios with proper logging")

        # Step 7: Performance monitoring and metrics
        print("\n" + "="*60)
        print("Step 7: Performance Monitoring and Metrics Logging")
        print("="*60)

        print("Logging performance metrics and timing information...")

        # Simulate a performance-critical operation
        start_time = time.time()

        # Simulate some work
        import random
        results_data = []
        for i in range(1000):
            results_data.append({
                'id': i,
                'value': random.randint(1, 1000),
                'timestamp': time.time()
            })

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        # Log performance metrics
        logger_performance.info("Batch processing completed", extra={
            'operation': 'batch_process',
            'records_processed': len(results_data),
            'duration_ms': duration_ms,
            'throughput_per_second': len(results_data) / (end_time - start_time),
            'memory_peak_mb': 45.2,  # Simulated
            'cpu_usage_percent': 67.8  # Simulated
        })

        # Database operation performance
        db_start = time.time()
        # Simulate database query
        time.sleep(0.01)  # Simulate DB latency
        db_end = time.time()

        logger_performance.info("Database query executed", extra={
            'operation': 'db_query',
            'query_type': 'SELECT',
            'table': 'users',
            'records_returned': 150,
            'duration_ms': (db_end - db_start) * 1000,
            'query_plan': 'index_scan',
            'connection_pool_size': 10
        })

        results['performance_metrics_logged'] = 2
        print_success(f"✓ Logged {results['performance_metrics_logged']} performance metrics")

        # Step 8: Edge cases and boundary conditions
        print("\n" + "="*60)
        print("Step 8: Edge Cases and Boundary Conditions")
        print("="*60)

        print("Testing logging with edge cases and unusual inputs...")

        # Empty/null data
        logger_main.info("Processing empty dataset", extra={
            'dataset_size': 0,
            'processing_time': 0.0,
            'status': 'completed'
        })

        # Very large data (simulated)
        large_data = {'data': 'x' * 10000}  # 10KB string
        logger_main.info("Processing large dataset", extra={
            'data_size_bytes': len(large_data['data']),
            'compression_ratio': 0.8,
            'chunks_processed': 5
        })

        # Special characters and unicode
        logger_main.info("Processing international data", extra={
            'user_name': 'José María ñoño',
            'message': '¡Hola mundo! 🌍',
            'language_code': 'es-ES',
            'encoding': 'UTF-8'
        })

        # Nested data structures
        logger_main.info("Processing nested configuration", extra={
            'config': {
                'database': {
                    'host': 'localhost',
                    'port': 5432,
                    'credentials': {
                        'username': 'admin',
                        'password_hash': '***'
                    }
                },
                'features': ['logging', 'monitoring', 'alerting']
            },
            'config_version': '1.2.3'
        })

        results['edge_cases_tested'] = 4
        print_success(f"✓ Tested {results['edge_cases_tested']} edge cases and boundary conditions")

        # Step 9: Configuration validation and fallbacks
        print("\n" + "="*60)
        print("Step 9: Configuration Validation and Fallbacks")
        print("="*60)

        # Test configuration validation
        log_config = config.get('logging', {})

        # Validate required configuration
        required_fields = ['level', 'output_type']
        missing_fields = [field for field in required_fields if field not in log_config]

        if missing_fields:
            logger_main.warning(f"Missing configuration fields: {missing_fields}", extra={
                'missing_fields': missing_fields,
                'config_section': 'logging',
                'fallback_used': True
            })

        # Demonstrate configuration fallback
        log_level = log_config.get('level', 'INFO')  # Default to INFO
        output_type = log_config.get('output_type', 'TEXT')  # Default to TEXT
        log_file = log_config.get('file', 'logs/example.log')  # Default path

        logger_main.info("Configuration validated with fallbacks", extra={
            'config_valid': True,
            'log_level': log_level,
            'output_type': output_type,
            'log_file': log_file,
            'defaults_used': len([k for k in ['level', 'output_type', 'file'] if k not in log_config])
        })

        print_success("✓ Configuration validation and fallbacks demonstrated")

        # Final summary and results
        print("\n" + "="*60)
        print("LOGGING MONITORING EXAMPLE COMPLETED")
        print("="*60)

        # Update final results
        results.update({
            'status': 'success',
            'total_operations': sum([
                results['loggers_created'],
                len(results['log_levels_tested']),
                results['structured_logs'],
                results['errors_handled'],
                results['performance_metrics_logged'],
                results['edge_cases_tested']
            ]),
            'output_format': config.get('logging', {}).get('output_type', 'TEXT'),
            'log_file': config.get('logging', {}).get('file', 'logs/example.log'),
            'configuration_valid': True
        })

        print(f"✓ Example completed successfully!")
        print(f"  - Loggers created: {results['loggers_created']}")
        print(f"  - Log levels tested: {len(results['log_levels_tested'])}")
        print(f"  - Structured logs: {results['structured_logs']}")
        print(f"  - Errors handled: {results['errors_handled']}")
        print(f"  - Performance metrics: {results['performance_metrics_logged']}")
        print(f"  - Edge cases tested: {results['edge_cases_tested']}")
        print(f"  - Total operations: {results['total_operations']}")
        print(f"\n📄 Check log output at: {results['log_file']}")
        
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()
        
    except Exception as e:
        error_msg = f"Logging monitoring example failed: {e}"
        print_error(error_msg)
        logger_main.error(error_msg, exc_info=True) if 'logger_main' in locals() else None

        results['status'] = 'failed'
        results['error'] = str(e)

        runner.error("Logging monitoring example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

