# tests/test_mandate_tamper.py

from mandates_core import Mandate, build_core
from eth_account import Account


def test_tampered_core_fails_verification():
    # Generate demo keys
    client_acct = Account.create()
    server_acct = Account.create()

    client_caip10 = f"eip155:1:{client_acct.address}"
    server_caip10 = f"eip155:1:{server_acct.address}"

    # Build primitive core (swap@1) – tweak fields as needed
    core = build_core(
        "swap@1",
        {
            "chainId": 1,
            "tokenIn": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "tokenOut": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
            "amountIn": "100000000",  # 100 USDC (6 decimals)
            "minOut": "165000",
            "recipient": client_acct.address,
            "deadline": "2025-12-31T00:00:00Z",
        },
    )

    # Create mandate
    m = Mandate.new(
        version="0.1.0",
        client=client_caip10,
        server=server_caip10,
        deadline="2025-12-31T00:00:00Z",
        intent="Swap 100 USDC for WBTC on Ethereum mainnet",
        core=core,
    )

    # Server signs first (offer)
    m.sign_as_server(server_acct.key.hex())

    # Client signs after verifying terms
    m.sign_as_client(client_acct.key.hex())

    # Sanity check: everything valid before tampering
    all_ok = m.verify_all()
    assert all_ok is True

    # --- Tamper with the mandate after signing ---
    # e.g. change the amountIn
    m.core["payload"]["amountIn"] = "99999999"

    # Now verification must fail
    all_ok_after_tamper = m.verify_all()
    assert all_ok_after_tamper is False
