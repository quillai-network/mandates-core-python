# mandates_core/utils.py
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict

import ulid
from eth_utils import keccak


def now_iso() -> str:
    """Return current UTC time as RFC 3339 / ISO-8601 with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def new_mandate_id() -> str:
    """Generate a ULID-based mandate ID."""
    return str(ulid.new())


def caip10_address(identifier: str) -> str:
    """
    Extract the address part from a CAIP-10 identifier.
    Example: 'eip155:1:0xabc...' -> '0xabc...'
    """
    parts = identifier.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid CAIP-10 identifier: {identifier}")
    return parts[2]


def canonical_json(obj: Any) -> str:
    """
    Canonical JSON string for hashing.
    This is a simplified JCS-style canonicalization:
    - sort_keys=True
    - no extra spaces
    """
    if is_dataclass(obj):
        obj = asdict(obj)
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)


def keccak256_json(obj: Any) -> str:
    """Compute keccak256 over canonicalized JSON, return 0x-prefixed hex."""
    data = canonical_json(obj).encode("utf-8")
    return "0x" + keccak(data).hex()


def without_signatures(mandate_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of the mandate dict without the 'signatures' field."""
    return {k: v for k, v in mandate_dict.items() if k != "signatures"}
