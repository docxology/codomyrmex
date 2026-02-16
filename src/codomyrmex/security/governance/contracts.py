from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional
from uuid import uuid4, UUID

class ContractStatus(Enum):
    DRAFT = auto()
    ACTIVE = auto()
    TERMINATED = auto()
    DISPUTED = auto()

class ContractError(Exception):
    """Base exception for contract errors."""
    pass

@dataclass
class ContractTerm:
    """A term or clause in a contract."""
    id: str
    description: str
    mandatory: bool = True

@dataclass
class Party:
    id: str
    name: str
    role: str

@dataclass
class Signature:
    signer_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    digital_signature: str = ""

class Contract:
    """Represents a legal or smart contract between agents."""
    
    def __init__(self, title: str, text: str, parties: List[Party]):
        self.id: UUID = uuid4()
        self.title = title
        self.text = text
        self.parties = parties
        self.signatures: List[Signature] = []
        self.status = ContractStatus.DRAFT
        self.created_at = datetime.now()

    def sign(self, signer_id: str, digital_signature: str = "") -> None:
        """Sign the contract if signer is a valid party."""
        if self.status != ContractStatus.DRAFT:
            raise ValueError("Contract must be in DRAFT status to sign.")
        
        party_ids = [p.id for p in self.parties]
        if signer_id not in party_ids:
            raise ValueError(f"Signer {signer_id} is not a party to this contract.")
        
        if any(s.signer_id == signer_id for s in self.signatures):
             raise ValueError(f"Party {signer_id} has already signed.")

        self.signatures.append(Signature(signer_id, digital_signature=digital_signature))
        
        # Auto-activate if all parties signed
        if len(self.signatures) == len(self.parties):
            self.status = ContractStatus.ACTIVE

    def terminate(self) -> None:
        self.status = ContractStatus.TERMINATED

    def __repr__(self) -> str:
        return f"Contract(id={self.id}, title='{self.title}', status={self.status.name})"
