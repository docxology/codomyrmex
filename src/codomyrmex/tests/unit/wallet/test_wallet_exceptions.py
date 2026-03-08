"""Zero-mock tests for wallet exceptions module.

Tests all exception classes with real instantiation and attribute inspection.
"""

import pytest

from codomyrmex.wallet.exceptions import (
    ContractError,
    GasEstimationError,
    InsufficientFundsError,
    RitualError,
    TransactionError,
    WalletError,
    WalletKeyError,
    WalletNotFoundError,
)


class TestWalletError:
    """Tests for the base WalletError exception."""

    def test_basic_construction(self):
        err = WalletError("something failed")
        assert "something failed" in str(err)

    def test_code_attribute(self):
        err = WalletError("msg", code="CUSTOM_CODE")
        assert err.code == "CUSTOM_CODE"

    def test_details_attribute(self):
        err = WalletError("msg", details={"key": "value"})
        assert err.details == {"key": "value"}

    def test_default_code_is_empty_string(self):
        err = WalletError("msg")
        assert err.code == ""

    def test_default_details_is_empty_dict(self):
        err = WalletError("msg")
        assert err.details == {}

    def test_error_dict_property(self):
        err = WalletError("test message", code="TEST", details={"x": 1})
        d = err.error_dict
        assert d["error_type"] == "WalletError"
        assert d["code"] == "TEST"
        assert "test message" in d["message"]
        assert d["details"] == {"x": 1}

    def test_is_exception(self):
        err = WalletError("msg")
        assert isinstance(err, Exception)

    def test_can_be_raised(self):
        with pytest.raises(WalletError, match="wallet failed"):
            raise WalletError("wallet failed")


class TestWalletNotFoundError:
    """Tests for WalletNotFoundError."""

    def test_construction_with_user_id(self):
        err = WalletNotFoundError("user123")
        assert "user123" in str(err)
        assert err.user_id == "user123"

    def test_error_code_is_wallet_not_found(self):
        err = WalletNotFoundError("alice")
        assert err.code == "WALLET_NOT_FOUND"

    def test_details_contains_user_id(self):
        err = WalletNotFoundError("bob")
        assert err.details["user_id"] == "bob"

    def test_default_message(self):
        err = WalletNotFoundError()
        assert "Wallet not found" in str(err)

    def test_custom_message(self):
        err = WalletNotFoundError("user42", message="Custom msg")
        assert "user42" in str(err)
        assert "Custom msg" in str(err)

    def test_is_wallet_error(self):
        err = WalletNotFoundError("alice")
        assert isinstance(err, WalletError)

    def test_empty_user_id(self):
        err = WalletNotFoundError("")
        assert err.user_id == ""
        assert "Wallet not found" in str(err)


class TestWalletKeyError:
    """Tests for WalletKeyError."""

    def test_basic_construction(self):
        err = WalletKeyError("Key operation failed")
        assert "Key operation failed" in str(err)

    def test_error_code(self):
        err = WalletKeyError()
        assert err.code == "KEY_ERROR"

    def test_key_type_attribute(self):
        err = WalletKeyError("msg", key_type="RSA")
        assert err.key_type == "RSA"

    def test_details_contain_key_type(self):
        err = WalletKeyError("msg", key_type="ECDSA")
        assert err.details["key_type"] == "ECDSA"

    def test_default_key_type_is_empty(self):
        err = WalletKeyError()
        assert err.key_type == ""

    def test_is_wallet_error(self):
        err = WalletKeyError()
        assert isinstance(err, WalletError)


class TestRitualError:
    """Tests for RitualError."""

    def test_basic_construction(self):
        err = RitualError("Ritual failed")
        assert "Ritual failed" in str(err)

    def test_error_code(self):
        err = RitualError()
        assert err.code == "RITUAL_ERROR"

    def test_ritual_step_attribute(self):
        err = RitualError("msg", ritual_step="step2")
        assert err.ritual_step == "step2"

    def test_details_contain_ritual_step(self):
        err = RitualError("msg", ritual_step="verify_phrase")
        assert err.details["ritual_step"] == "verify_phrase"

    def test_is_wallet_error(self):
        err = RitualError()
        assert isinstance(err, WalletError)


class TestInsufficientFundsError:
    """Tests for InsufficientFundsError."""

    def test_construction_with_values(self):
        err = InsufficientFundsError(required=10.0, available=5.0, currency="ETH")
        assert err.required == 10.0
        assert err.available == 5.0
        assert err.currency == "ETH"

    def test_error_code(self):
        err = InsufficientFundsError()
        assert err.code == "INSUFFICIENT_FUNDS"

    def test_message_contains_amounts(self):
        err = InsufficientFundsError(required=100.0, available=50.0, currency="BTC")
        msg = str(err)
        assert "100" in msg
        assert "50" in msg
        assert "BTC" in msg

    def test_details_structure(self):
        err = InsufficientFundsError(required=3.0, available=1.5, currency="SOL")
        assert err.details["required"] == 3.0
        assert err.details["available"] == 1.5
        assert err.details["currency"] == "SOL"

    def test_default_currency_is_eth(self):
        err = InsufficientFundsError()
        assert err.currency == "ETH"

    def test_is_wallet_error(self):
        err = InsufficientFundsError()
        assert isinstance(err, WalletError)

    def test_error_dict_contains_all_fields(self):
        err = InsufficientFundsError(required=5.0, available=2.0)
        d = err.error_dict
        assert d["error_type"] == "InsufficientFundsError"
        assert d["code"] == "INSUFFICIENT_FUNDS"


class TestTransactionError:
    """Tests for TransactionError."""

    def test_basic_construction(self):
        err = TransactionError("TX failed")
        assert "TX failed" in str(err)

    def test_error_code(self):
        err = TransactionError()
        assert err.code == "TX_ERROR"

    def test_tx_hash_attribute(self):
        err = TransactionError(tx_hash="0xabc123")
        assert err.tx_hash == "0xabc123"

    def test_reason_attribute(self):
        err = TransactionError(reason="out of gas")
        assert err.reason == "out of gas"

    def test_details_structure(self):
        err = TransactionError(tx_hash="0xdef", reason="reverted")
        assert err.details["tx_hash"] == "0xdef"
        assert err.details["reason"] == "reverted"

    def test_is_wallet_error(self):
        err = TransactionError()
        assert isinstance(err, WalletError)


class TestContractError:
    """Tests for ContractError."""

    def test_basic_construction(self):
        err = ContractError("Contract error")
        assert "Contract error" in str(err)

    def test_error_code(self):
        err = ContractError()
        assert err.code == "CONTRACT_ERROR"

    def test_contract_address_attribute(self):
        err = ContractError(contract_address="0xCAFE")
        assert err.contract_address == "0xCAFE"

    def test_function_name_attribute(self):
        err = ContractError(function_name="transfer")
        assert err.function_name == "transfer"

    def test_details_structure(self):
        err = ContractError(contract_address="0xBEEF", function_name="mint")
        assert err.details["contract_address"] == "0xBEEF"
        assert err.details["function_name"] == "mint"

    def test_is_wallet_error(self):
        err = ContractError()
        assert isinstance(err, WalletError)


class TestGasEstimationError:
    """Tests for GasEstimationError."""

    def test_basic_construction(self):
        err = GasEstimationError("Gas estimation failed")
        assert "Gas estimation failed" in str(err)

    def test_error_code(self):
        err = GasEstimationError()
        assert err.code == "GAS_ESTIMATION_ERROR"

    def test_is_wallet_error(self):
        err = GasEstimationError()
        assert isinstance(err, WalletError)

    def test_default_message(self):
        err = GasEstimationError()
        assert "Gas estimation failed" in str(err)
