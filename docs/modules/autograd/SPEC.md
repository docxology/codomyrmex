# Autograd Engine Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides from-scratch automatic differentiation (Micrograd-style) with Value and Tensor types. Supports forward computation and backward pass gradient computation for neural network training.

## Functional Requirements

1. Automatic differentiation via backward pass on a computation graph of Value objects
2. Support for relu, tanh, sigmoid, softmax activation functions
3. Numerical gradient checking via central finite differences with configurable epsilon


## Interface

```python
from codomyrmex.autograd import Value, relu, tanh, sigmoid

x = Value(2.0, label="x")
y = x * x + Value(3.0)
y.backward()
print(x.grad)  # dy/dx = 4.0
```

## Exports

Value, Tensor, relu, tanh, sigmoid, softmax

## Navigation

- [Source README](../../src/codomyrmex/autograd/README.md) | [AGENTS.md](AGENTS.md)
