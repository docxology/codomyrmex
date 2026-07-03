import re
with open("src/codomyrmex/quantization/mlx_quantizer.py", "r") as f:
    lines = f.readlines()

with open("src/codomyrmex/quantization/mlx_quantizer.py", "w") as f:
    for line in lines:
        if "except ImportError:" in line:
            f.write("except ImportError:\n")
            f.write("    from typing import Any\n")
            f.write("    class DummyMX:\n")
            f.write("        array = Any\n")
            f.write("        float16 = Any\n")
            f.write("    mx = DummyMX()\n")
            continue
        if "mx = None" in line:
            continue
        f.write(line)
