# Logit Processor Module - Agent Guide

**Version**: v0.1.0 | **Status**: Development | **Last Updated**: March 2026

## Overview

The `logit_processor` module allows agents to modify the probability distribution over the vocabulary during text generation.

## Usage

Agents can apply a series of transformations to the logits before sampling. The main classes are:
- `TemperatureProcessor`: Flattens or sharpens the distribution.
- `TopKProcessor`: Truncates all but the highest `k` probabilities.
- `TopPProcessor`: Nucleus sampling.
- `RepetitionPenaltyProcessor`: Applies a penalty to previously generated tokens.

## MCP Tools

- `process_logits`: Applies a chain of standard processors to input logits given specific parameters like temperature and top_k.

## Internal Dependencies

- None. Uses pure NumPy.
