"""Tests for smart_contracts module."""

import pytest

try:
    from codomyrmex.smart_contracts import (
        Address,
        Contract,
        ContractCall,
        ContractFunction,
        ContractRegistry,
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


@pytest.mark.unit
class TestNetwork:
    def test_ethereum(self):
        assert Network.ETHEREUM is not None

    def test_polygon(self):
        assert Network.POLYGON is not None

    def test_arbitrum(self):
        assert Network.ARBITRUM is not None

    def test_base(self):
        assert Network.BASE is not None


@pytest.mark.unit
class TestTransactionStatus:
    def test_pending(self):
        assert TransactionStatus.PENDING is not None

    def test_confirmed(self):
        assert TransactionStatus.CONFIRMED is not None

    def test_failed(self):
        assert TransactionStatus.FAILED is not None


@pytest.mark.unit
class TestAddress:
    def test_create_address(self):
        addr = Address(value="0x1234567890abcdef")
        assert addr.value == "0x1234567890abcdef"
        assert addr.network == Network.ETHEREUM

    def test_address_with_network(self):
        addr = Address(value="0xabc", network=Network.POLYGON)
        assert addr.network == Network.POLYGON


@pytest.mark.unit
class TestTransaction:
    def test_create_transaction(self):
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
    def test_create_function(self):
        func = ContractFunction(name="transfer")
        assert func.name == "transfer"
        assert func.payable is False
        assert func.view is False


@pytest.mark.unit
class TestContract:
    def test_create_contract(self):
        addr = Address(value="0xcontract")
        contract = Contract(address=addr)
        assert contract.abi == []
        assert contract.name == ""


@pytest.mark.unit
class TestContractCall:
    def test_create_call(self):
        addr = Address(value="0xcontract")
        contract = Contract(address=addr, name="ERC20")
        call = ContractCall(contract=contract, function_name="transfer")
        assert call.function_name == "transfer"


@pytest.mark.unit
class TestTransactionBuilder:
    def test_create_builder(self):
        addr = Address(value="0xfrom")
        builder = TransactionBuilder(from_address=addr)
        assert builder is not None


@pytest.mark.unit
class TestContractRegistry:
    def test_create_registry(self):
        registry = ContractRegistry()
        assert registry is not None


@pytest.mark.unit
class TestConversionFunctions:
    def test_wei_to_ether(self):
        result = wei_to_ether(1000000000000000000)
        assert result == 1.0

    def test_ether_to_wei(self):
        result = ether_to_wei(1.0)
        assert result == 1000000000000000000

    def test_gwei_to_wei(self):
        result = gwei_to_wei(1.0)
        assert result == 1000000000

    def test_roundtrip(self):
        original = 2.5
        wei = ether_to_wei(original)
        back = wei_to_ether(wei)
        assert abs(back - original) < 1e-10
