#!/usr/bin/env python3
"""
Orchestrator script for Container Optimization.

This script demonstrates how to use the ContainerOptimizer and ResourceTuner
to analyze and optimize Docker images and running containers.
"""

import sys
import json
import fire
from loguru import logger
from codomyrmex.container_optimization.optimizer import ContainerOptimizer
from codomyrmex.container_optimization.resource_tuner import ResourceTuner

class ContainerOrchestrator:
    """Orchestrates container optimization tasks."""

    def __init__(self):
        self.optimizer = ContainerOptimizer()
        self.tuner = ResourceTuner()

    def analyze_image(self, image_name: str):
        """Analyze a Docker image and print a report."""
        logger.info(f"Analyzing image: {image_name}")
        try:
            report = self.optimizer.get_optimization_report(image_name)
            print(json.dumps(report, indent=2))
        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            sys.exit(1)

    def tune_container(self, container_id: str):
        """Analyze a running container's resource usage and suggest limits."""
        logger.info(f"Tuning container: {container_id}")
        try:
            usage = self.tuner.analyze_usage(container_id)
            suggestions = self.tuner.suggest_limits(usage)
            result = {
                "usage": usage.to_dict(),
                "suggestions": suggestions
            }
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Failed to tune container: {e}")
            sys.exit(1)

    def list_images(self):
        """List available Docker images."""
        if not self.optimizer.client:
            logger.error("Docker client not available")
            return
        images = self.optimizer.client.images.list()
        for img in images:
            tags = img.tags if img.tags else [img.id]
            print(f"- {tags[0]}")

if __name__ == "__main__":
    fire.Fire(ContainerOrchestrator)
