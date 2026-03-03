#!/bin/bash
sed -i '/additional_dependencies: \[types-all\]/d' .pre-commit-config.yaml
