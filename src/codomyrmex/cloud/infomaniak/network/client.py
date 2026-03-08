"""
Infomaniak Network Client (Neutron/Octavia).

Provides network, router, security group, and load balancer operations.

The client is composed from focused mixin classes for maintainability:

- ``NetworkSubnetMixin`` — network and subnet CRUD
- ``RouterMixin`` — router CRUD and interface management
- ``SecurityGroupMixin`` — security group CRUD and rule management
- ``FloatingIPMixin`` — floating IP allocation and association
- ``LoadBalancerMixin`` — Octavia LB, listener, pool, member, and health monitor ops
"""

from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

from ._floating_ips import FloatingIPMixin
from ._load_balancers import LoadBalancerMixin
from ._networks import NetworkSubnetMixin
from ._routers import RouterMixin
from ._security_groups import SecurityGroupMixin


class InfomaniakNetworkClient(
    NetworkSubnetMixin,
    RouterMixin,
    SecurityGroupMixin,
    FloatingIPMixin,
    LoadBalancerMixin,
    InfomaniakOpenStackBase,
):
    """Client for Infomaniak networking (Neutron) operations.

    Provides methods for managing networks, routers, security groups,
    and load balancers. All resource operations are delegated to
    focused mixin classes for improved maintainability.
    """

    _service_name = "network"
