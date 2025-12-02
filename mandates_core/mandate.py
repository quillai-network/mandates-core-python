# mandates_core/mandate.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Literal, Optional

from eth_account import Account
from eth_account.messages import encode_defunct

from .utils import (
    now_iso,
    new_mandate_id,
    caip10_address,
    without_signatures,
    keccak256_json,
)


SignatureAlg = Literal["eip191"]  # you can extend later with "eip712"


@dataclass
class Signature:
    alg: SignatureAlg
    mandateHash: str
    signature: str
    signer: Optional[str] = None
    createdAt: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alg": self.alg,
            "mandateHash": self.mandateHash,
            "signature": self.signature,
            "signer": self.signer,
            "createdAt": self.createdAt,
        }


@dataclass
class Core:
    """Generic core wrapper for a primitive payload."""
    kind: str
    payload: Dict[str, Any]


@dataclass
class Mandate:
    mandateId: str
    version: str
    client: str
    server: str
    createdAt: str
    deadline: str
    intent: str
    core: Dict[str, Any]
    signatures: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ---------- Construction helpers ----------

    @classmethod
    def new(
        cls,
        *,
        version: str,
        client: str,
        server: str,
        deadline: str,
        intent: str,
        core: Dict[str, Any],
        mandate_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> "Mandate":
        """
        Create a new Mandate with generated mandateId + createdAt if not provided.
        """
        return cls(
            mandateId=mandate_id or new_mandate_id(),
            version=version,
            client=client,
            server=server,
            createdAt=created_at or now_iso(),
            deadline=deadline,
            intent=intent,
            core=core,
            signatures={},
        )

    # ---------- Serialization ----------

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # ---------- Hashing ----------

    def canonical_body(self) -> Dict[str, Any]:
        """
        Mandate body for hashing: everything except signatures.
        """
        return without_signatures(self.to_dict())

    def compute_mandate_hash(self) -> str:
        return keccak256_json(self.canonical_body())

    # ---------- Signing ----------

    def _sign(
        self,
        private_key: str,
        role: Literal["client", "server"],
        alg: SignatureAlg = "eip191",
    ) -> Signature:
        if alg != "eip191":
            raise NotImplementedError("Only eip191 is implemented for now")

        mandate_hash = self.compute_mandate_hash()

        # EIP-191 "Ethereum Signed Message" prefix over the 32-byte hash
        message = encode_defunct(hexstr=mandate_hash)
        signed = Account.sign_message(message, private_key=private_key)

        signer_addr = Account.from_key(private_key).address
        sig = Signature(
            alg=alg,
            mandateHash=mandate_hash,
            signature=signed.signature.hex(),
            signer=signer_addr,
            createdAt=now_iso(),
        )

        key = f"{role}Sig"
        self.signatures[key] = sig.to_dict()
        return sig

    def sign_as_client(self, private_key: str, alg: SignatureAlg = "eip191") -> Signature:
        return self._sign(private_key, "client", alg)

    def sign_as_server(self, private_key: str, alg: SignatureAlg = "eip191") -> Signature:
        return self._sign(private_key, "server", alg)

    # ---------- Verification ----------

    def _verify_role(self, role: Literal["client", "server"]) -> bool:
        sig_key = f"{role}Sig"
        sig_data = self.signatures.get(sig_key)
        if not sig_data:
            return False

        alg = sig_data.get("alg")
        if alg != "eip191":
            raise NotImplementedError("Only eip191 verification is implemented")

        expected_mandate_hash = self.compute_mandate_hash()
        if sig_data.get("mandateHash") != expected_mandate_hash:
            return False

        sig_hex = sig_data["signature"]
        message = encode_defunct(hexstr=expected_mandate_hash)
        recovered = Account.recover_message(message, signature=sig_hex)

        # Compare with CAIP-10 address for the role
        caip10 = self.client if role == "client" else self.server
        expected_addr = caip10_address(caip10)

        # Normalize both to checksum for comparison
        expected_addr = Account.from_key(Account.from_key).address if False else expected_addr  # dummy, we just rely on case-insensitive compare
        return recovered.lower() == expected_addr.lower()

    def verify_client(self) -> bool:
        return self._verify_role("client")

    def verify_server(self) -> bool:
        return self._verify_role("server")

    def verify_all(self) -> bool:
        return self.verify_client() and self.verify_server()
