"""
Shared test fixtures for Infomaniak cloud client tests.

Provides stub OpenStack connections, S3 clients, and factory helpers
used across all per-client test files.  Zero ``unittest.mock`` usage.
"""



class _CallRecord:
    """Container for a single call — mirrors ``unittest.mock.call``'s interface."""
    __slots__ = ('args', 'kwargs')

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        return iter((self.args, self.kwargs))

    def __getitem__(self, index):
        return (self.args, self.kwargs)[index]

    def __eq__(self, other):
        if isinstance(other, tuple) and len(other) == 2:
            return self.args == other[0] and self.kwargs == other[1]
        if isinstance(other, _CallRecord):
            return self.args == other.args and self.kwargs == other.kwargs
        return NotImplemented

    def __repr__(self):
        return f"call({self.args}, {self.kwargs})"


# =========================================================================
# Stub — drop-in MagicMock replacement (zero ``unittest.mock``)
# =========================================================================

class Stub:
    """Lightweight MagicMock replacement that records calls.

    Features:
    * **Auto-vivifying attributes** — accessing any undefined attribute
      returns a child ``Stub`` (like ``MagicMock``).
    * **Callable** — calling a ``Stub`` records positional / keyword args
      and returns ``return_value`` (or raises from ``side_effect``).
    * **Call tracking** — ``assert_called_once()``,
      ``assert_called_once_with(...)``, ``assert_not_called()``, and
      ``call_args`` / ``call_count`` work the same as ``MagicMock``.
    * **Restricted mode** — ``Stub(spec=[])`` disables auto-vivification
      so ``hasattr(stub, "anything")`` is ``False``.

    Parameters
    ----------
    spec : list | None
        When an empty list, auto-vivification is disabled.
    **attrs
        Keyword arguments become instance attributes, e.g.
        ``Stub(id="x", name="y")``.
    """

    # Sentinel showing that return_value was never explicitly set
    _UNSET = object()

    def __init__(self, *, spec=None, **attrs):
        object.__setattr__(self, "_stub_children", {})
        object.__setattr__(self, "_stub_calls", [])
        object.__setattr__(self, "_stub_return_value", Stub._UNSET)
        object.__setattr__(self, "_stub_side_effect", None)
        object.__setattr__(self, "_stub_restricted", spec is not None and len(spec) == 0)
        for key, val in attrs.items():
            object.__setattr__(self, key, val)

    # ---- return_value / side_effect as properties -------------------

    @property
    def return_value(self):
        rv = object.__getattribute__(self, "_stub_return_value")
        if rv is Stub._UNSET:
            return None
        return rv

    @return_value.setter
    def return_value(self, value):
        object.__setattr__(self, "_stub_return_value", value)

    @property
    def side_effect(self):
        return object.__getattribute__(self, "_stub_side_effect")

    @side_effect.setter
    def side_effect(self, value):
        object.__setattr__(self, "_stub_side_effect", value)

    # ---- call_args / call_count / call_args_list -------------------

    @property
    def call_args(self):
        """Return the (args, kwargs) of the most recent call, or None."""
        calls = object.__getattribute__(self, "_stub_calls")
        if not calls:
            return None
        return calls[-1]

    @property
    def call_count(self):
        return len(object.__getattribute__(self, "_stub_calls"))

    @property
    def call_args_list(self):
        return list(object.__getattribute__(self, "_stub_calls"))

    # ---- __call__ ---------------------------------------------------

    def __call__(self, *args, **kwargs):
        object.__getattribute__(self, "_stub_calls").append(_CallRecord(args, kwargs))
        se = object.__getattribute__(self, "_stub_side_effect")
        if se is not None:
            # List/iterator: consume one element per call
            if isinstance(se, list):
                if not se:
                    raise StopIteration("side_effect list exhausted")
                item = se.pop(0)
                if isinstance(item, BaseException):
                    raise item
                if isinstance(item, type) and issubclass(item, BaseException):
                    raise item()
                return item
            if callable(se):
                return se(*args, **kwargs)
            if isinstance(se, BaseException):
                raise se
            raise se
        rv = object.__getattribute__(self, "_stub_return_value")
        if rv is Stub._UNSET:
            return None
        return rv

    # ---- auto-vivifying __getattr__ ---------------------------------

    def __getattr__(self, name):
        # Restricted mode: no auto-vivification
        if object.__getattribute__(self, "_stub_restricted"):
            raise AttributeError(name)
        children = object.__getattribute__(self, "_stub_children")
        if name not in children:
            children[name] = Stub()
        return children[name]

    def __setattr__(self, name, value):
        # Setting a concrete attribute removes it from children
        children = object.__getattribute__(self, "_stub_children")
        children.pop(name, None)
        object.__setattr__(self, name, value)

    # ---- assertion helpers (MagicMock-compatible) -------------------

    def assert_called_once(self):
        calls = object.__getattribute__(self, "_stub_calls")
        if len(calls) != 1:
            raise AssertionError(
                f"Expected exactly 1 call, got {len(calls)}"
            )

    def assert_called_once_with(self, *args, **kwargs):
        self.assert_called_once()
        actual_args, actual_kwargs = object.__getattribute__(self, "_stub_calls")[0]
        if actual_args != args or actual_kwargs != kwargs:
            raise AssertionError(
                f"Expected call({args}, {kwargs}), got call({actual_args}, {actual_kwargs})"
            )

    def assert_not_called(self):
        calls = object.__getattribute__(self, "_stub_calls")
        if calls:
            raise AssertionError(
                f"Expected no calls, got {len(calls)}"
            )

    # ---- repr -------------------------------------------------------

    def __repr__(self):
        return "<Stub>"


# =========================================================================
# Connection Fixtures
# =========================================================================

# =========================================================================
# Environment Variable Fixtures
# =========================================================================

# =========================================================================
# Stub Object Factories
# =========================================================================

def make_stub_server(
    server_id="server-123",
    name="test-server",
    status="ACTIVE",
    flavor_id="flavor-1",
    image_id="image-1",
):
    """Create a stub OpenStack server object."""
    return Stub(
        id=server_id,
        name=name,
        status=status,
        flavor={"id": flavor_id},
        image={"id": image_id},
        addresses={"network1": [{"addr": "10.0.0.1"}]},
        key_name="my-key",
        created_at=None,
        updated_at=None,
        availability_zone="dc3-a",
        security_groups=[{"name": "default"}],
    )


def make_stub_volume(
    volume_id="vol-123",
    name="test-volume",
    status="available",
    size=100,
):
    """Create a stub OpenStack volume object."""
    return Stub(
        id=volume_id,
        name=name,
        status=status,
        size=size,
        volume_type="ssd",
        availability_zone="dc3-a",
        is_bootable=False,
        is_encrypted=False,
        attachments=[],
        created_at=None,
    )


def make_stub_network(
    network_id="net-123",
    name="test-network",
    status="ACTIVE",
):
    """Create a stub OpenStack network object."""
    return Stub(
        id=network_id,
        name=name,
        status=status,
        is_shared=False,
        is_router_external=False,
        subnet_ids=["subnet-1"],
    )


def make_stub_zone(
    zone_id="zone-123",
    name="example.com.",
    email="admin@example.com",
):
    """Create a stub DNS zone object."""
    return Stub(
        id=zone_id,
        name=name,
        email=email,
        status="ACTIVE",
        type="PRIMARY",
        ttl=3600,
    )


def make_stub_stack(
    stack_id="stack-123",
    name="test-stack",
    status="CREATE_COMPLETE",
):
    """Create a stub Heat stack object."""
    return Stub(
        id=stack_id,
        name=name,
        status=status,
        status_reason=f"Stack {status}",
        description="Test stack",
        parameters={"key": "value"},
        outputs=[{"output_key": "ip", "output_value": "10.0.0.1"}],
        created_at=None,
        updated_at=None,
    )


def make_stub_image(
    image_id="img-123",
    name="Ubuntu 22.04",
    status="active",
):
    """Create a stub Glance image object."""
    return Stub(
        id=image_id,
        name=name,
        status=status,
        min_disk=10,
        min_ram=512,
        size=2147483648,
        created_at=None,
    )


def make_stub_floating_ip(
    fip_id="fip-123",
    address="195.15.220.10",
    status="ACTIVE",
    port_id="port-abc",
):
    """Create a stub floating IP object."""
    return Stub(
        id=fip_id,
        floating_ip_address=address,
        fixed_ip_address="10.0.0.5",
        status=status,
        port_id=port_id,
    )


def make_stub_container(
    name="test-container",
    count=10,
    bytes_used=1024000,
):
    """Create a stub Swift container object."""
    return Stub(
        name=name,
        count=count,
        bytes=bytes_used,
    )
