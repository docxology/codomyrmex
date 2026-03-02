# Autograd Engine -- Technical Specification

## Architecture

### Computation Graph

Both `Value` and `Tensor` build a DAG (directed acyclic graph) during forward computation. Each node stores:
- `data` -- the computed value
- `grad` -- accumulated gradient (initialized to 0)
- `_prev` -- set of parent nodes
- `_backward` -- closure that computes local gradient contribution
- `_op` -- string label for the operation (debugging)

### Backward Pass

`backward()` performs:
1. **Topological sort** via DFS from the output node
2. **Seed gradient** -- set output node's grad to 1.0
3. **Reverse traversal** -- call each node's `_backward()` in reverse topological order
4. **Gradient accumulation** -- uses `+=` (not `=`) to handle shared nodes correctly

### Value (Scalar)

- Stores `float` data
- `grad: float` initialized to 0.0
- All arithmetic operators return new `Value` nodes
- `__pow__` supports float/int exponents only (not Value exponents)

### Tensor

- Stores `numpy.ndarray` (float64)
- `grad: np.ndarray | None` initialized to None, allocated on first backward
- Broadcasting is handled by `_unbroadcast()` helper that sums over broadcast dimensions
- Matrix multiply backward uses transposed Jacobians

## Supported Operations

### Value Operations
| Op | Forward | Backward (dout) |
|----|---------|-----------------|
| `a + b` | `a.data + b.data` | `a.grad += dout`, `b.grad += dout` |
| `a * b` | `a.data * b.data` | `a.grad += b.data * dout`, `b.grad += a.data * dout` |
| `a ** n` | `a.data ** n` | `a.grad += n * a.data^(n-1) * dout` |
| `exp(a)` | `e^a.data` | `a.grad += e^a.data * dout` |
| `tanh(a)` | `tanh(a.data)` | `a.grad += (1 - tanh^2) * dout` |
| `relu(a)` | `max(0, a.data)` | `a.grad += (1 if a>0 else 0) * dout` |
| `sigmoid(a)` | `1/(1+e^-a)` | `a.grad += s*(1-s) * dout` |

### Tensor Operations
| Op | Forward | Backward |
|----|---------|----------|
| `a + b` | element-wise add | identity (with unbroadcast) |
| `a * b` | element-wise mul | cross-multiply (with unbroadcast) |
| `a @ b` | matrix multiply | `dout @ b.T`, `a.T @ dout` |
| `sum()` | reduce sum | broadcast ones |
| `mean()` | reduce mean | broadcast 1/n |
| `reshape()` | view change | reshape grad back |
| `softmax()` | stable softmax | Jacobian-vector product |

## Numerical Stability

- Softmax uses the log-sum-exp trick (subtract max before exp)
- No special handling needed for Value since it operates on Python floats (no overflow at typical scales)

## Limitations

- Value does not support `Value ** Value` (only float/int exponents)
- Tensor does not support higher-order gradients
- No GPU acceleration -- NumPy CPU only
- Not designed for large-scale training (use PyTorch/JAX for that)
