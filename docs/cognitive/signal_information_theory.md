# Signal, Entropy, and the Channel

**Series**: [Cognitive Perspectives](./README.md) | **Topic**: Information Theory

## The Theory

Claude Shannon's 1948 paper established that information is not about meaning but about surprise. The entropy of a source, H = -sum(p_i * log2(p_i)), quantifies the average surprise per symbol -- the irreducible minimum number of bits required to encode a message from that source. High entropy means high unpredictability; low entropy means redundancy and compressibility. This single quantity governs the design of communication systems, cryptographic primitives, and observability architectures.

Shannon's channel coding theorem guarantees that reliable communication is possible at any rate below channel capacity C = max I(X;Y), the maximum mutual information between input and output. Above capacity, errors are unavoidable. Below it, error-correcting codes can drive error probability arbitrarily low. This is not an engineering approximation -- it is a mathematical bound that constrains every protocol, including the Model Context Protocol that bridges PAI and codomyrmex.

Kolmogorov complexity extends Shannon's statistical view to individual objects: the complexity of a string is the length of the shortest program that produces it. Code complexity metrics (cyclomatic complexity, cognitive complexity) are practical approximations of this idea -- measuring how much description a program requires, which correlates with how difficult it is to understand, test, and maintain.

## Architectural Mapping

| Information-Theoretic Concept | Module | Source Path | Implementation |
|-------------------------------|--------|-------------|----------------|
| Shannon entropy | crypto/analysis | [`entropy.py:shannon_entropy()`](../../src/codomyrmex/crypto/analysis/entropy.py) | H computed per-symbol using log2; returns bits per symbol |
| Byte entropy | crypto/analysis | [`entropy.py:byte_entropy()`](../../src/codomyrmex/crypto/analysis/entropy.py) | H over 256-symbol byte alphabet; max 8.0 bits |
| Uniformity testing | crypto/analysis | [`entropy.py:chi_squared_test()`](../../src/codomyrmex/crypto/analysis/entropy.py) | Chi-squared against uniform distribution; p > 0.05 = uniform |
| Serial correlation | crypto/analysis | [`entropy.py:serial_correlation()`](../../src/codomyrmex/crypto/analysis/entropy.py) | Pearson correlation between consecutive bytes; random data ≈ 0 |
| Channel capacity | model_context_protocol | [`server.py`](../../src/codomyrmex/model_context_protocol/) | MCP JSON-RPC as bounded channel; tool schemas define message alphabet |
| Source coding | telemetry | [`tracing/`](../../src/codomyrmex/telemetry/tracing/) | Structured spans as efficient encoding of system state |
| Error-correcting feedback | meme/cybernetic | [`engine.py:PIDController`](../../src/codomyrmex/meme/cybernetic/) | PID control as error-correcting channel with proportional, integral, and derivative terms |
| Steganography | crypto/steganography | [`detection.py`](../../src/codomyrmex/crypto/steganography/) | LSB entropy analysis; high byte entropy (>7.9) flags hidden payloads |

**`shannon_entropy()`** is the most direct implementation of the theory in the codebase. It accepts bytes or strings, counts symbol frequencies, and computes H = -sum(p * log2(p)) exactly as Shannon defined it. The companion `byte_entropy()` specializes to the 256-symbol byte alphabet, returning a value between 0.0 (constant) and 8.0 (uniformly random) -- the theoretical maximum for bytes. Together with `chi_squared_test()` and `serial_correlation()`, these functions form a complete randomness assessment toolkit grounded in the mathematical foundations of information theory.

**The MCP protocol** is an information-theoretic channel. Each tool call is a message; the tool schema constrains the alphabet; the JSON-RPC framing provides error detection. Channel capacity is bounded by the schema's expressiveness -- a tool with 3 parameters and constrained types has lower capacity than one accepting arbitrary JSON. This is not metaphor; it is the direct application of Shannon's framework to protocol design.

## Design Implications

**Measure entropy at system boundaries.** Data entering or leaving the system should have its entropy profiled. Low-entropy input channels waste bandwidth; high-entropy output channels resist error detection. The `shannon_entropy()` function provides this measurement at negligible cost.

**Use entropy as a security signal.** The steganography detection in `crypto/steganography/detection.py` exploits the information-theoretic principle that hidden data increases carrier entropy. Byte entropy above 7.9 bits on non-compressed data is statistically anomalous and warrants investigation.

**Design MCP tool signatures for appropriate channel capacity.** Overly constrained schemas limit what can be communicated; overly permissive schemas increase error surface. Shannon's noisy channel theorem says both extremes are suboptimal. The tool schema is the engineering surface where this tradeoff is resolved.

**The PID controller is an error-correcting system.** The `CyberneticEngine` in `meme/cybernetic/` applies proportional-integral-derivative control to memetic variables. In information-theoretic terms, this is a feedback channel where the error signal (setpoint minus measured) drives corrective output. Shannon's framework applies directly to analyzing the stability and bandwidth of this loop.

## Further Reading

- Shannon, C.E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379--423.
- Cover, T.M. & Thomas, J.A. (2006). *Elements of Information Theory*, 2nd ed. Wiley.
- Kolmogorov, A.N. (1965). Three approaches to the quantitative definition of information. *Problems of Information Transmission*, 1(1), 1--7.
- MacKay, D.J.C. (2003). *Information Theory, Inference, and Learning Algorithms*. Cambridge University Press.
- Gallager, R.G. (1968). *Information Theory and Reliable Communication*. Wiley.

## See Also

- [Active Inference](./active_inference.md) -- Free energy is an information-theoretic quantity; entropy of beliefs drives action selection
- [Stigmergy](./stigmergy.md) -- Pheromone trails as signal channels with evaporation as noise
- [Cognitive Security](./cognitive_security.md) -- Information warfare exploits channel vulnerabilities
- [The Superorganism](../bio/superorganism.md) -- Telemetry as colony sensory apparatus (biological perspective)
- [Stigmergy and the Pheromone Trail](../bio/stigmergy.md) -- Pheromone as signal channel (biological perspective)

*Docxology references*: [GLOSSOPETRAE](https://github.com/docxology/GLOSSOPETRAE) (steganographic channels, Reed-Solomon coding), [InsightSpike-AI](https://github.com/docxology/InsightSpike-AI) (information gain as formal metric), [QuadMath](https://github.com/docxology/QuadMath) (information geometry chapter)

---

*Return to [series index](./README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*
