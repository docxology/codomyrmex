
import pytest
from codomyrmex.identity import IdentityManager, VerificationLevel
from codomyrmex.wallet import WalletManager
from codomyrmex.defense import ActiveDefense
from codomyrmex.market import ReverseAuction, Bid
from codomyrmex.privacy import CrumbCleaner

def test_identity_lifecycle():
    id_mgr = IdentityManager()
    id_mgr.create_persona("p1", "Alice", VerificationLevel.KYC)
    
    # Export
    data = id_mgr.export_persona("p1")
    assert data["name"] == "Alice"
    assert "crumbs_count" in data
    
    # Revoke
    assert id_mgr.revoke_persona("p1")
    assert id_mgr.get_persona("p1") is None
    assert not id_mgr.revoke_persona("p1") # Already gone

def test_wallet_ops():
    wallet = WalletManager()
    uid = "u1"
    old_addr = wallet.create_wallet(uid)
    
    # Backup
    backup = wallet.backup_wallet(uid)
    assert backup["wallet_id"] == old_addr
    assert "key_hash" in backup
    
    # Rotate
    new_addr = wallet.rotate_keys(uid)
    assert new_addr != old_addr
    assert wallet.get_wallet_address(uid) == new_addr

def test_defense_ops():
    defense = ActiveDefense()
    
    # Update patterns
    new_threat = "sudo rm -rf"
    assert not defense.detect_exploit(new_threat)
    
    defense.update_patterns([new_threat])
    assert defense.detect_exploit(new_threat)
    
    # Report
    report = defense.get_threat_report()
    assert report["exploits_detected"] == 1
    assert report["active_patterns"] >= 5

def test_market_ops():
    market = ReverseAuction()
    aid = market.create_request("p1", "Item", 100)
    
    # Cancel
    assert market.cancel_auction(aid, "p1")
    assert not market.place_bid(aid, "prov1", 50, "desc") # Should fail
    
    # History
    assert len(market.get_history("p1")) == 1
    assert market.get_history("p2") == []

def test_privacy_config():
    privacy = CrumbCleaner()
    data = {"secret_key": "123", "normal": "val"}
    
    # Default behavior
    assert "secret_key" in privacy.scrub(data)
    
    # Configure
    privacy.configure_blacklist(add=["secret_key"])
    assert "secret_key" not in privacy.scrub(data)
    
    # Unconfigure
    privacy.configure_blacklist(remove=["secret_key"])
    assert "secret_key" in privacy.scrub(data)
