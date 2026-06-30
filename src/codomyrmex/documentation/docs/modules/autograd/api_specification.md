# Autograd - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `autograd` module provides a from-scratch automatic differentiation engine (Micrograd-style). Supports forward computation and reverse-mode gradient propagation through a dynamic computational graph.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `Value` | Scalar value with automatic gradient tracking and backpropagation |
| `Tensor` | Multi-dimensional tensor with autograd support |

### 2.2 Activation Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `relu` | `(x) -> Value/Tensor` | Rectified Linear Unit activation |
| `sigmoid` | `(x) -> Value/Tensor` | Sigmoid activation |
| `tanh` | `(x) -> Value/Tensor` | Hyperbolic tangent activation |
| `softmax` | `(x) -> Value/Tensor` | Softmax activation |

## 3. Usage Example

```python
from codomyrmex.autograd import Value, relu

a = Value(2.0)
b = Value(3.0)
c = relu(a * b + Value(1.0))
c.backward()
print(a.grad, b.grad)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
