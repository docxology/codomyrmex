# Autograd Engine

A from-scratch automatic differentiation engine supporting scalar and small tensor operations, inspired by Andrej Karpathy's Micrograd.

## Overview

The autograd module provides reverse-mode automatic differentiation with two core abstractions:

- **Value**: Scalar autograd -- tracks computation graphs for individual floating-point values
- **Tensor**: NumPy-backed tensor autograd -- supports matrix operations with gradient accumulation

Both classes build a directed acyclic graph (DAG) during forward computation, then traverse it in reverse topological order during `backward()` to compute gradients via the chain rule.

## Quick Start

### Scalar Autograd (Value)

```python
from codomyrmex.autograd import Value, tanh

# Build a computation graph
x = Value(2.0, label='x')
y = Value(3.0, label='y')
z = x * y + x ** 2
z.backward()

print(x.grad)  # dz/dx = y + 2x = 3 + 4 = 7.0
print(y.grad)  # dz/dy = x = 2.0
```

### Tensor Autograd

```python
from codomyrmex.autograd import Tensor
import numpy as np

a = Tensor([[1.0, 2.0], [3.0, 4.0]])
b = Tensor([[5.0, 6.0], [7.0, 8.0]])
c = a @ b
loss = c.sum()
loss.backward()

print(a.grad)  # d(sum(A@B))/dA
print(b.grad)  # d(sum(A@B))/dB
```

### Activation Functions

```python
from codomyrmex.autograd import Value, relu, tanh, sigmoid, softmax, Tensor

x = Value(0.5)
y = tanh(x)
y.backward()
print(x.grad)  # dtanh(0.5)/dx

logits = Tensor([1.0, 2.0, 3.0])
probs = softmax(logits)  # numerically stable
```

## Supported Operations

### Value (Scalar)
- Arithmetic: `+`, `-`, `*`, `/`, `**`, unary `-`
- Reflected ops: `radd`, `rmul`, `rsub`, `rtruediv`
- Math: `exp()`, `tanh()`, `relu()`, `sigmoid()`

### Tensor
- Element-wise: `+`, `-`, `*`
- Matrix: `@` (matmul)
- Reductions: `sum()`, `mean()`
- Shape: `reshape()`
- Activations: `relu()`, `tanh()`, `sigmoid()`, `softmax()`

## Dependencies

- `numpy` (core dependency, already in codomyrmex)
- No external autograd libraries -- everything is implemented from scratch
