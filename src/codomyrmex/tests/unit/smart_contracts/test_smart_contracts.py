"""Tests for smart_contracts module."""

import pytest

try:
    from codomyrmex.wallet.contracts import (
        Address,
        Contract,
        ContractCall,
        ContractEvent,
        ContractFunction,
        ContractRegistry,
        EventFilter,
        EventLog,
        Network,
        Transaction,
        TransactionBuilder,
        TransactionStatus,
        ether_to_wei,
        gwei_to_wei,
        wei_to_ether,
    )

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("smart_contracts module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_ETH_ADDRESS = "0x" + "a" * 40  # 42 chars total
SHORT_ETH_ADDRESS = "0x" + "a" * 10  # too short
NO_PREFIX_ADDRESS = "a" * 42  # missing 0x prefix

SAMPLE_ABI = [
    {
        "type": "function",
        "name": "transfer",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [{"name": "owner", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
    },
    {
        "type": "event",
        "name": "Transfer",
        "inputs": [],
    },
]


@pytest.fixture
def eth_address():
    return Address(value=VALID_ETH_ADDRESS, network=Network.ETHEREUM)


@pytest.fixture
def polygon_address():
    return Address(value=VALID_ETH_ADDRESS, network=Network.POLYGON)


@pytest.fixture
def solana_address():
    return Address(value="SoLaNaAdDrEsS123", network=Network.SOLANA)


@pytest.fixture
def contract_with_abi(eth_address):
    return Contract(address=eth_address, abi=SAMPLE_ABI, name="TestERC20")


@pytest.fixture
def empty_contract(eth_address):
    return Contract(address=eth_address)


# ---------------------------------------------------------------------------
# ORIGINAL 19 TESTS (preserved exactly)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNetwork:
    """Test suite for Network."""
    def test_ethereum(self):
        """Verify ethereum behavior."""
        assert Network.ETHEREUM is not None

    def test_polygon(self):
        """Verify polygon behavior."""
        assert Network.POLYGON is not None

    def test_arbitrum(self):
        """Verify arbitrum behavior."""
        assert Network.ARBITRUM is not None

    def test_base(self):
        """Verify base behavior."""
        assert Network.BASE is not None


@pytest.mark.unit
class TestTransactionStatus:
    """Test suite for TransactionStatus."""
    def test_pending(self):
        """Verify pending behavior."""
        assert TransactionStatus.PENDING is not None

    def test_confirmed(self):
        """Verify confirmed behavior."""
        assert TransactionStatus.CONFIRMED is not None

    def test_failed(self):
        """Verify failed behavior."""
        assert TransactionStatus.FAILED is not None


@pytest.mark.unit
class TestAddress:
    """Test suite for Address."""
    def test_create_address(self):
        """Verify create address behavior."""
        addr = Address(value="0x1234567890abcdef")
        assert addr.value == "0x1234567890abcdef"
        assert addr.network == Network.ETHEREUM

    def test_address_with_network(self):
        """Verify address with network behavior."""
        addr = Address(value="0xabc", network=Network.POLYGON)
        assert addr.network == Network.POLYGON


@pytest.mark.unit
class TestTransaction:
    """Test suite for Transaction."""
    def test_create_transaction(self):
        """Verify create transaction behavior."""
        from_addr = Address(value="0xfrom")
        to_addr = Address(value="0xto")
        tx = Transaction(
            hash="0xhash",
            from_address=from_addr,
            to_address=to_addr,
            value=1000,
        )
        assert tx.hash == "0xhash"
        assert tx.value == 1000
        assert tx.status == TransactionStatus.PENDING

    def test_transaction_defaults(self):
        """Verify transaction defaults behavior."""
        from_addr = Address(value="0xfrom")
        to_addr = Address(value="0xto")
        tx = Transaction(hash="0x1", from_address=from_addr, to_address=to_addr, value=0)
        assert tx.data == ""
        assert tx.gas_limit == 21000
        assert tx.gas_price == 0
        assert tx.nonce == 0
        assert tx.block_number is None


@pytest.mark.unit
class TestContractFunction:
    """Test suite for ContractFunction."""
    def test_create_function(self):
        """Verify create function behavior."""
        func = ContractFunction(name="transfer")
        assert func.name == "transfer"
        assert func.payable is False
        assert func.view is False


@pytest.mark.unit
class TestContract:
    """Test suite for Contract."""
    def test_create_contract(self):
        """Verify create contract behavior."""
        addr = Address(value="0xcontract")
        contract = Contract(address=addr)
        assert contract.abi == []
        assert contract.name == ""


@pytest.mark.unit
class TestContractCall:
    """Test suite for ContractCall."""
    def test_create_call(self):
        """Verify create call behavior."""
        addr = Address(value="0xcontract")
        contract = Contract(address=addr, name="ERC20")
        call = ContractCall(contract=contract, function_name="transfer")
        assert call.function_name == "transfer"


@pytest.mark.unit
class TestTransactionBuilder:
    """Test suite for TransactionBuilder."""
    def test_create_builder(self):
        """Verify create builder behavior."""
        addr = Address(value="0xfrom")
        builder = TransactionBuilder(from_address=addr)
        assert builder is not None


@pytest.mark.unit
class TestContractRegistry:
    """Test suite for ContractRegistry."""
    def test_create_registry(self):
        """Verify create registry behavior."""
        registry = ContractRegistry()
        assert registry is not None


@pytest.mark.unit
class TestConversionFunctions:
    """Test suite for ConversionFunctions."""
    def test_wei_to_ether(self):
        """Verify wei to ether behavior."""
        result = wei_to_ether(1000000000000000000)
        assert result == 1.0

    def test_ether_to_wei(self):
        """Verify ether to wei behavior."""
        result = ether_to_wei(1.0)
        assert result == 1000000000000000000

    def test_gwei_to_wei(self):
        """Verify gwei to wei behavior."""
        result = gwei_to_wei(1.0)
        assert result == 1000000000

    def test_roundtrip(self):
        """Verify roundtrip behavior."""
        original = 2.5
        wei = ether_to_wei(original)
        back = wei_to_ether(wei)
        assert abs(back - original) < 1e-10


# ---------------------------------------------------------------------------
# NEW BEHAVIORAL TESTS
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAddressValidation:
    """Deep tests for Address.is_valid property."""

    def test_valid_ethereum_address_42_chars(self, eth_address):
        """Verify valid ethereum address 42 chars behavior."""
        assert eth_address.is_valid is True

    def test_short_ethereum_address_returns_false(self):
        """Verify short ethereum address returns false behavior."""
        addr = Address(value=SHORT_ETH_ADDRESS, network=Network.ETHEREUM)
        assert addr.is_valid is False

    def test_no_0x_prefix_returns_false(self):
        """Verify no 0x prefix returns false behavior."""
        addr = Address(value=NO_PREFIX_ADDRESS, network=Network.ETHEREUM)
        assert addr.is_valid is False

    def test_valid_polygon_address(self, polygon_address):
        """Verify valid polygon address behavior."""
        assert polygon_address.is_valid is True

    def test_short_polygon_address_returns_false(self):
        """Verify short polygon address returns false behavior."""
        addr = Address(value="0xshort", network=Network.POLYGON)
        assert addr.is_valid is False

    def test_valid_arbitrum_address(self):
        """Verify valid arbitrum address behavior."""
        addr = Address(value=VALID_ETH_ADDRESS, network=Network.ARBITRUM)
        assert addr.is_valid is True

    def test_valid_optimism_address(self):
        """Verify valid optimism address behavior."""
        addr = Address(value=VALID_ETH_ADDRESS, network=Network.OPTIMISM)
        assert addr.is_valid is True

    def test_valid_base_address(self):
        """Verify valid base address behavior."""
        addr = Address(value=VALID_ETH_ADDRESS, network=Network.BASE)
        assert addr.is_valid is True

    def test_solana_address_valid_if_non_empty(self, solana_address):
        """Verify solana address valid if non empty behavior."""
        assert solana_address.is_valid is True

    def test_solana_empty_address_invalid(self):
        """Verify solana empty address invalid behavior."""
        addr = Address(value="", network=Network.SOLANA)
        assert addr.is_valid is False


@pytest.mark.unit
class TestAddressStr:
    """Address.__str__ returns value."""

    def test_str_returns_value(self, eth_address):
        """Verify str returns value behavior."""
        assert str(eth_address) == VALID_ETH_ADDRESS

    def test_str_returns_solana_value(self, solana_address):
        """Verify str returns solana value behavior."""
        assert str(solana_address) == "SoLaNaAdDrEsS123"


@pytest.mark.unit
class TestContractFunctionEncode:
    """Deep tests for ContractFunction.encode_call."""

    def test_encode_call_returns_hex_string(self):
        """Verify encode call returns hex string behavior."""
        func = ContractFunction(
            name="transfer",
            inputs=[
                {"name": "to", "type": "address"},
                {"name": "amount", "type": "uint256"},
            ],
        )
        result = func.encode_call("0xrecipient", 1000)
        assert isinstance(result, str)
        assert result.startswith("0x")

    def test_encode_call_hex_chars_only(self):
        """Verify encode call hex chars only behavior."""
        func = ContractFunction(
            name="approve",
            inputs=[
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"},
            ],
        )
        result = func.encode_call("0xspender", 500)
        # After 0x prefix, all chars should be valid hex
        hex_part = result[2:]
        assert all(c in "0123456789abcdef" for c in hex_part)

    def test_encode_call_no_inputs(self):
        """Verify encode call no inputs behavior."""
        func = ContractFunction(name="totalSupply", inputs=[])
        result = func.encode_call()
        assert result.startswith("0x")
        assert len(result) > 2

    def test_different_functions_produce_different_selectors(self):
        """Verify different functions produce different selectors behavior."""
        func_a = ContractFunction(name="transfer", inputs=[{"name": "to", "type": "address"}])
        func_b = ContractFunction(name="approve", inputs=[{"name": "to", "type": "address"}])
        assert func_a.encode_call("0x1") != func_b.encode_call("0x1")


@pytest.mark.unit
class TestContractWithABI:
    """Deep tests for Contract ABI parsing."""

    def test_parses_functions_from_abi(self, contract_with_abi):
        """Verify parses functions from abi behavior."""
        funcs = contract_with_abi.list_functions()
        assert "transfer" in funcs
        assert "balanceOf" in funcs

    def test_ignores_non_function_abi_entries(self, contract_with_abi):
        """Verify ignores non function abi entries behavior."""
        funcs = contract_with_abi.list_functions()
        # The event "Transfer" should NOT appear as a function
        assert "Transfer" not in funcs

    def test_get_function_returns_correct_function(self, contract_with_abi):
        """Verify get function returns correct function behavior."""
        func = contract_with_abi.get_function("transfer")
        assert func is not None
        assert func.name == "transfer"
        assert len(func.inputs) == 2

    def test_get_function_returns_none_for_missing(self, contract_with_abi):
        """Verify get function returns none for missing behavior."""
        func = contract_with_abi.get_function("nonexistent")
        assert func is None

    def test_list_functions_returns_names(self, contract_with_abi):
        """Verify list functions returns names behavior."""
        names = contract_with_abi.list_functions()
        assert isinstance(names, list)
        assert len(names) == 2

    def test_view_function_detected(self, contract_with_abi):
        """Verify view function detected behavior."""
        func = contract_with_abi.get_function("balanceOf")
        assert func is not None
        assert func.view is True

    def test_non_view_function_detected(self, contract_with_abi):
        """Verify non view function detected behavior."""
        func = contract_with_abi.get_function("transfer")
        assert func is not None
        assert func.view is False

    def test_empty_abi_produces_no_functions(self, empty_contract):
        """Verify empty abi produces no functions behavior."""
        assert empty_contract.list_functions() == []


@pytest.mark.unit
class TestContractCallFluent:
    """Deep tests for ContractCall fluent API."""

    def test_with_args_returns_self(self, contract_with_abi):
        """Verify with args returns self behavior."""
        call = ContractCall(contract_with_abi, "transfer")
        result = call.with_args("0xrecipient", 100)
        assert result is call

    def test_with_value_returns_self(self, contract_with_abi):
        """Verify with value returns self behavior."""
        call = ContractCall(contract_with_abi, "transfer")
        result = call.with_value(1000)
        assert result is call

    def test_with_gas_limit_returns_self(self, contract_with_abi):
        """Verify with gas limit returns self behavior."""
        call = ContractCall(contract_with_abi, "transfer")
        result = call.with_gas_limit(50000)
        assert result is call

    def test_fluent_chaining(self, contract_with_abi):
        """Verify fluent chaining behavior."""
        call = (
            ContractCall(contract_with_abi, "transfer")
            .with_args("0xrecipient", 100)
            .with_value(0)
            .with_gas_limit(60000)
        )
        assert call._args == ["0xrecipient", 100]
        assert call._value == 0
        assert call._gas_limit == 60000

    def test_encode_calls_function(self, contract_with_abi):
        """Verify encode calls function behavior."""
        call = ContractCall(contract_with_abi, "transfer")
        call.with_args("0xrecipient", 100)
        encoded = call.encode()
        assert encoded.startswith("0x")

    def test_encode_with_missing_function_raises_value_error(self, contract_with_abi):
        """Verify encode with missing function raises value error behavior."""
        call = ContractCall(contract_with_abi, "nonexistent_function")
        with pytest.raises(ValueError, match="Function not found"):
            call.encode()

    def test_to_transaction_creates_proper_transaction(self, contract_with_abi, eth_address):
        """Verify to transaction creates proper transaction behavior."""
        call = (
            ContractCall(contract_with_abi, "transfer")
            .with_args("0xrecipient", 100)
            .with_value(5000)
            .with_gas_limit(80000)
        )
        from_addr = Address(value=VALID_ETH_ADDRESS)
        tx = call.to_transaction(from_addr, nonce=7)

        assert isinstance(tx, Transaction)
        assert tx.from_address == from_addr
        assert tx.to_address == contract_with_abi.address
        assert tx.value == 5000
        assert tx.gas_limit == 80000
        assert tx.nonce == 7
        assert tx.data.startswith("0x")


@pytest.mark.unit
class TestTransactionBuilderDeep:
    """Deep tests for TransactionBuilder fluent API."""

    def test_fluent_chain_all_methods(self, eth_address):
        """Verify fluent chain all methods behavior."""
        to_addr = Address(value=VALID_ETH_ADDRESS, network=Network.POLYGON)
        builder = (
            TransactionBuilder(eth_address)
            .to(to_addr)
            .value(1000)
            .data("0xdeadbeef")
            .gas_limit(50000)
            .gas_price(20)
            .nonce(3)
        )
        assert builder._to == to_addr
        assert builder._value == 1000
        assert builder._data == "0xdeadbeef"
        assert builder._gas_limit == 50000
        assert builder._gas_price == 20
        assert builder._nonce == 3

    def test_build_creates_transaction_with_hash(self, eth_address):
        """Verify build creates transaction with hash behavior."""
        to_addr = Address(value=VALID_ETH_ADDRESS)
        tx = TransactionBuilder(eth_address).to(to_addr).value(500).build()

        assert isinstance(tx, Transaction)
        assert tx.hash.startswith("0x")
        assert len(tx.hash) > 2
        assert tx.from_address == eth_address
        assert tx.to_address == to_addr
        assert tx.value == 500

    def test_build_without_to_raises_value_error(self, eth_address):
        """Verify build without to raises value error behavior."""
        builder = TransactionBuilder(eth_address).value(100)
        with pytest.raises(ValueError, match="To address is required"):
            builder.build()

    def test_build_preserves_all_fields(self, eth_address):
        """Verify build preserves all fields behavior."""
        to_addr = Address(value=VALID_ETH_ADDRESS)
        tx = (
            TransactionBuilder(eth_address)
            .to(to_addr)
            .value(999)
            .data("0xcafe")
            .gas_limit(75000)
            .gas_price(15)
            .nonce(42)
            .build()
        )
        assert tx.value == 999
        assert tx.data == "0xcafe"
        assert tx.gas_limit == 75000
        assert tx.gas_price == 15
        assert tx.nonce == 42

    def test_different_nonces_produce_different_hashes(self, eth_address):
        """Verify different nonces produce different hashes behavior."""
        to_addr = Address(value=VALID_ETH_ADDRESS)
        tx1 = TransactionBuilder(eth_address).to(to_addr).nonce(1).build()
        tx2 = TransactionBuilder(eth_address).to(to_addr).nonce(2).build()
        assert tx1.hash != tx2.hash


@pytest.mark.unit
class TestContractRegistryDeep:
    """Deep tests for ContractRegistry."""

    def test_register_and_get(self, contract_with_abi):
        """Verify register and get behavior."""
        registry = ContractRegistry()
        registry.register("erc20", contract_with_abi)
        result = registry.get("erc20")
        assert result is contract_with_abi

    def test_get_missing_returns_none(self):
        """Verify get missing returns none behavior."""
        registry = ContractRegistry()
        assert registry.get("nonexistent") is None

    def test_list_returns_registered_names(self, contract_with_abi, empty_contract):
        """Verify list returns registered names behavior."""
        registry = ContractRegistry()
        registry.register("token", contract_with_abi)
        registry.register("bare", empty_contract)
        names = registry.list()
        assert "token" in names
        assert "bare" in names
        assert len(names) == 2

    def test_list_empty_registry(self):
        """Verify list empty registry behavior."""
        registry = ContractRegistry()
        assert registry.list() == []

    def test_register_overwrites_existing(self, contract_with_abi, empty_contract):
        """Verify register overwrites existing behavior."""
        registry = ContractRegistry()
        registry.register("token", contract_with_abi)
        registry.register("token", empty_contract)
        result = registry.get("token")
        assert result is empty_contract


@pytest.mark.unit
class TestConversionFunctionsDeep:
    """Additional conversion function tests."""

    def test_wei_to_ether_zero(self):
        """Verify wei to ether zero behavior."""
        assert wei_to_ether(0) == 0.0

    def test_ether_to_wei_zero(self):
        """Verify ether to wei zero behavior."""
        assert ether_to_wei(0.0) == 0

    def test_gwei_to_wei_zero(self):
        """Verify gwei to wei zero behavior."""
        assert gwei_to_wei(0.0) == 0

    def test_large_wei_value(self):
        """Verify large wei value behavior."""
        result = wei_to_ether(10**18 * 1000)
        assert result == 1000.0

    def test_gwei_to_wei_large(self):
        """Verify gwei to wei large behavior."""
        result = gwei_to_wei(100.0)
        assert result == 100_000_000_000

    def test_fractional_ether(self):
        """Verify fractional ether behavior."""
        result = ether_to_wei(0.001)
        assert result == 10**15


# ---------------------------------------------------------------------------
# EVENT SYSTEM TESTS
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractEvent:
    """Tests for ContractEvent dataclass."""

    def test_create_event_minimal(self):
        """Verify create event minimal behavior."""
        event = ContractEvent(name="Transfer")
        assert event.name == "Transfer"
        assert event.args == {}
        assert event.contract_address is None
        assert event.block_number == 0
        assert event.transaction_hash == ""
        assert event.log_index == 0

    def test_create_event_with_all_fields(self):
        """Verify create event with all fields behavior."""
        addr = Address(value=VALID_ETH_ADDRESS)
        event = ContractEvent(
            name="Approval",
            args={"owner": "0x1", "spender": "0x2", "value": 100},
            contract_address=addr,
            block_number=12345,
            transaction_hash="0xdeadbeef",
            log_index=3,
        )
        assert event.name == "Approval"
        assert event.args["value"] == 100
        assert event.contract_address == addr
        assert event.block_number == 12345
        assert event.transaction_hash == "0xdeadbeef"
        assert event.log_index == 3

    def test_event_timestamp_is_set(self):
        """Verify event timestamp is set behavior."""
        event = ContractEvent(name="Transfer")
        assert event.timestamp is not None


@pytest.mark.unit
class TestEventFilter:
    """Tests for EventFilter matching logic."""

    def test_empty_filter_matches_everything(self):
        """Verify empty filter matches everything behavior."""
        f = EventFilter()
        event = ContractEvent(name="Transfer", block_number=5)
        assert f.matches(event) is True

    def test_filter_by_event_name_match(self):
        """Verify filter by event name match behavior."""
        f = EventFilter().event("Transfer")
        event = ContractEvent(name="Transfer", block_number=1)
        assert f.matches(event) is True

    def test_filter_by_event_name_no_match(self):
        """Verify filter by event name no match behavior."""
        f = EventFilter().event("Approval")
        event = ContractEvent(name="Transfer", block_number=1)
        assert f.matches(event) is False

    def test_filter_from_block(self):
        """Verify filter from block behavior."""
        f = EventFilter().from_block(10)
        assert f.matches(ContractEvent(name="X", block_number=10)) is True
        assert f.matches(ContractEvent(name="X", block_number=15)) is True
        assert f.matches(ContractEvent(name="X", block_number=5)) is False

    def test_filter_to_block(self):
        """Verify filter to block behavior."""
        f = EventFilter().to_block(20)
        assert f.matches(ContractEvent(name="X", block_number=20)) is True
        assert f.matches(ContractEvent(name="X", block_number=25)) is False

    def test_filter_block_range(self):
        """Verify filter block range behavior."""
        f = EventFilter().from_block(10).to_block(20)
        assert f.matches(ContractEvent(name="X", block_number=9)) is False
        assert f.matches(ContractEvent(name="X", block_number=10)) is True
        assert f.matches(ContractEvent(name="X", block_number=15)) is True
        assert f.matches(ContractEvent(name="X", block_number=20)) is True
        assert f.matches(ContractEvent(name="X", block_number=21)) is False

    def test_filter_by_address(self):
        """Verify filter by address behavior."""
        addr = Address(value=VALID_ETH_ADDRESS)
        f = EventFilter().address(addr)
        event_match = ContractEvent(name="X", contract_address=addr)
        event_no_match = ContractEvent(
            name="X", contract_address=Address(value="0x" + "b" * 40)
        )
        assert f.matches(event_match) is True
        assert f.matches(event_no_match) is False

    def test_filter_combined_criteria(self):
        """Verify filter combined criteria behavior."""
        addr = Address(value=VALID_ETH_ADDRESS)
        f = EventFilter().event("Transfer").from_block(5).to_block(15).address(addr)
        good = ContractEvent(
            name="Transfer", block_number=10, contract_address=addr
        )
        wrong_name = ContractEvent(
            name="Approval", block_number=10, contract_address=addr
        )
        wrong_block = ContractEvent(
            name="Transfer", block_number=20, contract_address=addr
        )
        assert f.matches(good) is True
        assert f.matches(wrong_name) is False
        assert f.matches(wrong_block) is False

    def test_filter_fluent_returns_self(self):
        """Verify filter fluent returns self behavior."""
        f = EventFilter()
        assert f.event("X") is f
        assert f.from_block(1) is f
        assert f.to_block(10) is f
        assert f.address(Address(value="0x1")) is f


@pytest.mark.unit
class TestEventLog:
    """Tests for EventLog add, query, count, latest."""

    def test_add_and_query_all(self):
        """Verify add and query all behavior."""
        log = EventLog()
        e1 = ContractEvent(name="Transfer", block_number=1)
        e2 = ContractEvent(name="Approval", block_number=2)
        log.add(e1)
        log.add(e2)
        results = log.query()
        assert len(results) == 2

    def test_query_returns_copy(self):
        """Verify query returns copy behavior."""
        log = EventLog()
        log.add(ContractEvent(name="X"))
        results = log.query()
        results.clear()
        assert log.count() == 1

    def test_query_with_filter(self):
        """Verify query with filter behavior."""
        log = EventLog()
        log.add(ContractEvent(name="Transfer", block_number=1))
        log.add(ContractEvent(name="Approval", block_number=2))
        log.add(ContractEvent(name="Transfer", block_number=3))

        f = EventFilter().event("Transfer")
        results = log.query(f)
        assert len(results) == 2
        assert all(e.name == "Transfer" for e in results)

    def test_count_all(self):
        """Verify count all behavior."""
        log = EventLog()
        log.add(ContractEvent(name="A"))
        log.add(ContractEvent(name="B"))
        log.add(ContractEvent(name="A"))
        assert log.count() == 3

    def test_count_by_name(self):
        """Verify count by name behavior."""
        log = EventLog()
        log.add(ContractEvent(name="Transfer"))
        log.add(ContractEvent(name="Approval"))
        log.add(ContractEvent(name="Transfer"))
        assert log.count("Transfer") == 2
        assert log.count("Approval") == 1
        assert log.count("Missing") == 0

    def test_count_empty(self):
        """Verify count empty behavior."""
        log = EventLog()
        assert log.count() == 0

    def test_latest_single(self):
        """Verify lasingle behavior."""
        log = EventLog()
        log.add(ContractEvent(name="A", block_number=1))
        log.add(ContractEvent(name="B", block_number=5))
        log.add(ContractEvent(name="C", block_number=3))
        latest = log.latest(1)
        assert len(latest) == 1
        assert latest[0].name == "B"

    def test_latest_multiple(self):
        """Verify lamultiple behavior."""
        log = EventLog()
        log.add(ContractEvent(name="A", block_number=1))
        log.add(ContractEvent(name="B", block_number=5))
        log.add(ContractEvent(name="C", block_number=3))
        latest = log.latest(2)
        assert len(latest) == 2
        assert latest[0].block_number == 5
        assert latest[1].block_number == 3

    def test_latest_more_than_available(self):
        """Verify lamore than available behavior."""
        log = EventLog()
        log.add(ContractEvent(name="A", block_number=1))
        latest = log.latest(5)
        assert len(latest) == 1

    def test_latest_empty_log(self):
        """Verify laempty log behavior."""
        log = EventLog()
        assert log.latest() == []


# ---------------------------------------------------------------------------
# ContractRegistry.remove() tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractRegistryRemove:
    """Tests for ContractRegistry.remove() method."""

    def test_remove_existing_returns_true(self, contract_with_abi):
        """Verify remove existing returns true behavior."""
        registry = ContractRegistry()
        registry.register("token", contract_with_abi)
        assert registry.remove("token") is True
        assert registry.get("token") is None

    def test_remove_missing_returns_false(self):
        """Verify remove missing returns false behavior."""
        registry = ContractRegistry()
        assert registry.remove("nonexistent") is False

    def test_remove_then_register_again(self, contract_with_abi, empty_contract):
        """Verify remove then register again behavior."""
        registry = ContractRegistry()
        registry.register("token", contract_with_abi)
        registry.remove("token")
        registry.register("token", empty_contract)
        result = registry.get("token")
        assert result is empty_contract
