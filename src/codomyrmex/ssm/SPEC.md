# SSM Module -- API Specification

## Classes

### SelectiveSSM

Selective State Space Model (S6 kernel) with input-dependent parameters.

#### Constructor

```python
SelectiveSSM(d_model: int, d_state: int = 16, dt_rank: int = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `d_model` | int | required | Input/output dimension |
| `d_state` | int | 16 | SSM hidden state dimension N |
| `dt_rank` | int | d_model // 16 | Rank for Delta projection (min 1) |

#### Methods

##### `forward(x: np.ndarray) -> np.ndarray`

Run selective SSM sequential scan.

- **Input**: `(batch, seq_len, d_model)` float array
- **Output**: `(batch, seq_len, d_model)` float array
- **Complexity**: O(seq_len * d_model * d_state) time, O(d_model * d_state) state memory

---

### MambaBlock

Full Mamba block with projection, convolution, SSM, and gating.

#### Constructor

```python
MambaBlock(d_model: int, d_inner: int = None, d_state: int = 16, d_conv: int = 4)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `d_model` | int | required | Input/output dimension |
| `d_inner` | int | 2 * d_model | Expanded inner dimension |
| `d_state` | int | 16 | SSM state dimension |
| `d_conv` | int | 4 | Causal conv1d kernel size |

#### Methods

##### `forward(x: np.ndarray) -> np.ndarray`

Full Mamba block forward pass.

- **Input**: `(batch, seq, d_model)` float array
- **Output**: `(batch, seq, d_model)` float array

##### `__call__(x: np.ndarray) -> np.ndarray`

Alias for `forward`.

---

### Functions

#### `mamba_forward(x, n_layers=2, d_model=None, d_state=16) -> np.ndarray`

Stack multiple Mamba blocks with residual connections.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | np.ndarray | required | Input (batch, seq, d_model) |
| `n_layers` | int | 2 | Number of stacked blocks |
| `d_model` | int | inferred | Model dimension |
| `d_state` | int | 16 | SSM state dimension |

---

## MCP Tools

### `ssm_forward`

| Parameter | Type | Default |
|-----------|------|---------|
| `sequence_length` | int | 8 |
| `d_model` | int | 16 |
| `d_state` | int | 8 |
| `n_layers` | int | 2 |

**Returns**: `{"status": "success", "output_shape": [...], "d_model": ..., "d_state": ..., "n_layers": ...}`

### `flash_attention_forward`

| Parameter | Type | Default |
|-----------|------|---------|
| `seq_len` | int | 16 |
| `d_model` | int | 32 |
| `block_size` | int | 8 |

**Returns**: `{"status": "success", "output_shape": [...], "max_error_vs_standard": ..., "passed": ...}`
