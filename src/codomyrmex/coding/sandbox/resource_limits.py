"""
Resource Limits Configuration

Defines default resource limits and Docker security arguments.
"""

# Default Docker run arguments for security
DEFAULT_DOCKER_ARGS = [
    "--network=none",  # No network access
    "--cap-drop=ALL",  # Drop all capabilities
    "--security-opt=no-new-privileges",  # Prevent privilege escalation
    "--read-only",  # Read-only container
    "--memory=256m",  # Memory limit
    "--memory-swap=256m",  # Disable swap
    "--cpus=0.5",  # CPU limit
    "--pids-limit=50",  # Process limit
]

