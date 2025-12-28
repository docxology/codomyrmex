"""
Example runner framework for standardized execution.

Provides common functionality for running examples including logging setup,
error handling, and result validation.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional


class ExampleRunner:
    """
    Standardized example execution framework.
    
    Handles common tasks like logging setup, error handling, timing,
    and result validation.
    """
    
    def __init__(self, example_file: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize example runner.
        
        Args:
            example_file: Path to the example file (__file__ from the example)
            config: Optional configuration dictionary
        """
        self.example_file = Path(example_file)
        self.example_name = self.example_file.stem
        self.config = config or {}
        self.start_time = None
        self.logger = None
        
        # Setup logging if configured
        self._setup_logging()
        
        # Add src to path
        self._setup_python_path()
    
    def _setup_python_path(self):
        """Add src directory to Python path."""
        src_path = str(self.example_file.parent.parent.parent / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        try:
            from codomyrmex.logging_monitoring import setup_logging, get_logger
            
            # Configure logging level from config
            log_level = self.config.get('logging', {}).get('level', 'INFO')
            import os
            os.environ['CODOMYRMEX_LOG_LEVEL'] = log_level
            
            # Setup logging
            setup_logging()
            self.logger = get_logger(self.example_name)
            
        except ImportError:
            # Fallback to basic logging
            import logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(self.example_name)
    
    def start(self):
        """Start timing the example execution."""
        self.start_time = time.time()
        if self.logger:
            self.logger.info(f"Starting example: {self.example_name}")
        else:
            print(f"Starting example: {self.example_name}")
    
    def complete(self, message: str = "Example completed successfully"):
        """
        Mark example as complete and log timing.
        
        Args:
            message: Completion message
        """
        if self.start_time:
            duration = time.time() - self.start_time
            full_message = f"{message} (Duration: {duration:.2f}s)"
        else:
            full_message = message
        
        if self.logger:
            self.logger.info(full_message)
        else:
            print(full_message)
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """
        Log an error and optionally exit.
        
        Args:
            message: Error message
            exception: Optional exception that caused the error
        """
        if exception:
            full_message = f"{message}: {str(exception)}"
        else:
            full_message = message
        
        if self.logger:
            self.logger.error(full_message)
            if exception:
                self.logger.exception(exception)
        else:
            print(f"ERROR: {full_message}", file=sys.stderr)
            if exception:
                import traceback
                traceback.print_exc()
    
    def info(self, message: str):
        """
        Log an info message.
        
        Args:
            message: Info message
        """
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def validate_results(self, results: Any, validator: Optional[callable] = None) -> bool:
        """
        Validate example results.
        
        Args:
            results: Results to validate
            validator: Optional custom validation function
            
        Returns:
            True if valid, False otherwise
        """
        if validator:
            try:
                is_valid = validator(results)
                if is_valid:
                    self.info("Results validated successfully")
                else:
                    self.error("Results validation failed")
                return is_valid
            except Exception as e:
                self.error("Error during validation", e)
                return False
        else:
            # Basic validation - just check results exist
            is_valid = results is not None
            if is_valid:
                self.info("Results present")
            else:
                self.error("No results generated")
            return is_valid
    
    def save_results(self, results: Any, output_path: Optional[Path] = None):
        """
        Save results to file.
        
        Args:
            results: Results to save
            output_path: Optional output path (uses config if not provided)
        """
        if output_path is None:
            output_config = self.config.get('output', {})
            output_file = output_config.get('file', f'output/{self.example_name}_results.json')
            output_path = Path(output_file)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save based on format
        output_format = self.config.get('output', {}).get('format', 'json')
        
        try:
            if output_format == 'json':
                import json
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            else:
                # Fallback to string representation
                with open(output_path, 'w') as f:
                    f.write(str(results))
            
            self.info(f"Results saved to: {output_path}")
        except Exception as e:
            self.error(f"Failed to save results to {output_path}", e)

