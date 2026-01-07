#!/usr/bin/env python3
"""
Example: Containerization - Docker Image Management

This example demonstrates:
- Building Docker images from Dockerfiles
- Analyzing image sizes and layers
- Optimizing container images
- Managing container registries

Tested Methods:
- build_image() - Verified in test_containerization.py::TestContainerization::test_build_image
- optimize_image() - Verified in test_containerization_enhanced.py::TestContainerizationEnhanced::test_optimize_image
- analyze_image_size() - Verified in test_containerization_enhanced.py::TestContainerizationEnhanced::test_analyze_image_size
"""

import sys
from pathlib import Path

# Add src to path
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

from codomyrmex.containerization.docker_manager import build_image, analyze_image_size
from codomyrmex.containerization.image_optimizer import ImageOptimizer
from codomyrmex.containerization.build_generator import BuildGenerator
from _common.config_loader import load_config
from _common.example_runner import ExampleRunner
from _common.utils import print_section, print_results, ensure_output_dir

def main():
    """Run the containerization example."""
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Containerization Example")

        # Get containerization settings
        container_config = config.get('containerization', {})

        results = {
            'images_analyzed': 0,
            'images_optimized': 0,
            'builds_generated': 0,
            'total_size_reduction': 0
        }

        # Create output directory for generated files
        output_dir = Path("output/containers")
        ensure_output_dir(output_dir)

        # Analyze existing images
        print("Analyzing container images...")
        images_to_analyze = container_config.get('images_to_analyze', [])

        for image_spec in images_to_analyze:
            try:
                image_name = image_spec.get('name', 'unknown')
                analysis = analyze_image_size(image_name)

                if analysis:
                    print(f"✓ Analyzed {image_name}: {analysis.get('size_mb', 0):.2f} MB")
                    results['images_analyzed'] += 1
                else:
                    print(f"✗ Could not analyze {image_name}")

            except Exception as e:
                print(f"✗ Error analyzing {image_name}: {e}")

        # Generate optimized Dockerfiles
        print("\nGenerating optimized Dockerfiles...")
        build_configs = container_config.get('build_configs', [])

        for i, build_config in enumerate(build_configs, 1):
            try:
                generator = BuildGenerator()

                # Generate multi-stage Dockerfile
                dockerfile_content = generator.generate_multi_stage_dockerfile(
                    base_image=build_config.get('base_image', 'python:3.9-slim'),
                    app_files=build_config.get('app_files', ['app.py']),
                    dependencies=build_config.get('dependencies', []),
                    ports=build_config.get('ports', [8000])
                )

                # Save Dockerfile
                dockerfile_path = output_dir / f"Dockerfile.{i}"
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)

                print(f"✓ Generated Dockerfile: {dockerfile_path}")
                results['builds_generated'] += 1

                # Try to build the image (if Docker is available)
                try:
                    tag = f"codomyrmex-example-{i}:latest"
                    build_result = build_image(str(dockerfile_path), tag)

                    if build_result:
                        print(f"✓ Built image: {tag}")
                    else:
                        print(f"✗ Failed to build image: {tag}")

                except Exception as e:
                    print(f"Note: Image build skipped (Docker not available): {e}")

            except Exception as e:
                print(f"✗ Error generating build config {i}: {e}")

        # Image optimization examples
        print("\nOptimizing container images...")
        optimizer = ImageOptimizer()

        optimization_configs = container_config.get('optimization_configs', [])
        for opt_config in optimization_configs:
            try:
                optimizations = optimizer.suggest_optimizations(
                    image_name=opt_config.get('image', 'python:3.9'),
                    context=opt_config
                )

                if optimizations:
                    size_reduction = sum(opt.get('size_reduction_mb', 0) for opt in optimizations)
                    results['images_optimized'] += 1
                    results['total_size_reduction'] += size_reduction

                    print(f"✓ Generated {len(optimizations)} optimizations, "
                          f"potential {size_reduction:.1f} MB reduction")

            except Exception as e:
                print(f"✗ Error in optimization: {e}")

        # Generate summary report
        results['summary'] = {
            'total_operations': (results['images_analyzed'] +
                               results['images_optimized'] +
                               results['builds_generated']),
            'output_directory': str(output_dir),
            'generated_files': len(list(output_dir.glob("*"))),
            'optimization_potential_mb': results['total_size_reduction']
        }

        print_section("Containerization Results")
        print_results(results['summary'], "Container Management Summary")

        runner.validate_results(results)
        runner.save_results(results)

        runner.complete("Containerization example completed successfully")

    except Exception as e:
        runner.error("Example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

