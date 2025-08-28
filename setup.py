"""Setup script for Codomyrmex."""

from setuptools import setup, find_packages

setup(
    name="codomyrmex",
    version="0.1.0",
    description="A Modular, Extensible Coding Workspace",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)

