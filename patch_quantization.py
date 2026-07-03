with open("src/codomyrmex/quantization/mlx_quantizer.py", "r") as f:
    content = f.read()

content = content.replace("mx.array", "'mx.array'")
content = content.replace("array: 'mx.array'", "array: 'mx.array' | None")

# Wait, instead of this, let's just use typing.Any for missing mlx.
