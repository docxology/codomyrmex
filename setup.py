"""Setup script for Codomyrmex.

This file is maintained for compatibility but pyproject.toml is the primary configuration.
For uv users, this file is not used as uv reads from pyproject.toml directly.
"""

from setuptools import setup, find_packages

# Read dependencies from requirements.txt for backward compatibility
def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="codomyrmex",
    version="0.1.0",
    description="A Modular, Extensible Coding Workspace",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Codomyrmex Contributors",
    author_email="contributors@codomyrmex.org",
    url="https://github.com/codomyrmex/codomyrmex",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
            "pre-commit>=3.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords=["coding", "workspace", "modular", "development", "AI", "automation"],
    project_urls={
        "Homepage": "https://github.com/codomyrmex/codomyrmex",
        "Repository": "https://github.com/codomyrmex/codomyrmex",
        "Issues": "https://github.com/codomyrmex/codomyrmex/issues",
        "Documentation": "https://codomyrmex.readthedocs.io/",
    },
)

