# Edge Computing Module

Edge deployment, IoT gateways, and latency-sensitive patterns.

## Quick Start

```python
from codomyrmex.edge_computing import (
    EdgeNode, EdgeFunction, EdgeCluster, EdgeSynchronizer,
)

# Create cluster
cluster = EdgeCluster()
cluster.register_node(EdgeNode("node1", "Kitchen Hub"))

# Deploy function
func = EdgeFunction("temp_check", "Temperature Check", handler=check_temp)
cluster.deploy_to_all(func)

# State sync
sync = EdgeSynchronizer()
sync.update_local({"temp": 72.5})
```

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
