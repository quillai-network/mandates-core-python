# mandates_core/primitives.py
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict

import requests

DEFAULT_BASE = os.getenv(
    "MANDATE_SPECS_BASE_URL",
    "https://raw.githubusercontent.com/quillai-network/mandate-specs/main/spec",
)


@lru_cache(maxsize=1)
def fetch_registry(base_url: str = DEFAULT_BASE) -> Dict[str, Any]:
    """
    Fetch primitives registry.json from mandate-specs.
    """
    url = f"{base_url}/primitives/registry.json"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()


@lru_cache(maxsize=32)
def fetch_primitive_schema(kind: str, base_url: str = DEFAULT_BASE) -> Dict[str, Any]:
    """
    Fetch a specific primitive's schema by kind (e.g., 'swap@1').
    """
    registry = fetch_registry(base_url)
    entry = next((p for p in registry["primitives"] if p["kind"] == kind), None)
    if not entry:
        raise ValueError(f"Primitive kind '{kind}' not found in registry")

    url = f"{base_url}/{entry['schemaPath']}"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()


def build_core(kind: str, payload: Dict[str, Any], base_url: str = DEFAULT_BASE) -> Dict[str, Any]:
    """
    Build a `core` object using a primitive kind and payload.

    For day-one, this only:
      - checks that the primitive exists in the registry
      - returns {"kind": schema["kind"], "payload": payload}

    Later you can validate `payload` against `schema["payloadSchema"]` using `jsonschema`.
    """
    schema = fetch_primitive_schema(kind, base_url=base_url)
    # TODO: optional jsonschema validation against schema["payloadSchema"]
    return {
      "kind": schema["kind"],
      "payload": payload,
    }
