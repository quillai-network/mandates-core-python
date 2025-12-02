# tests/test_primitives.py
from eth_account import Account
from mandates_core.primitives import build_core


def test_build_core_swap_v1_round_trip():
    # Generate a demo recipient
    client_acct = Account.create()

    payload = {
        "chainId": 1,
        "tokenIn": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "tokenOut": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "amountIn": "100000000",    # 100 USDC (6 decimals)
        "minOut": "165000",
        "recipient": client_acct.address,
        "deadline": "2025-12-31T00:00:00Z",
    }

    core = build_core("swap@1", payload)

    # Shape and kind
    assert isinstance(core, dict)
    assert core["kind"] == "swap@1"
    assert "payload" in core
    # Payload should be passed through untouched for now
    assert core["payload"] == payload


def test_build_core_unknown_kind_raises():
    payload = {"foo": "bar"}

    from mandates_core.primitives import build_core
    import pytest

    with pytest.raises(ValueError) as exc:
        build_core("nonexistent@99", payload)

    assert "Primitive kind 'nonexistent@99' not found" in str(exc.value)
