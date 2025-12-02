from mandates_core import Mandate, build_core
from eth_account import Account


def test_path_sign_and_verify():
    # Generate demo keys
    client_acct = Account.create()
    server_acct = Account.create()

    client_caip10 = f"eip155:1:{client_acct.address}"
    server_caip10 = f"eip155:1:{server_acct.address}"

    # Build primitive core (swap@1)
    core = build_core(
        "swap@1",
        {
            "chainId": 1,
            "tokenIn": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "tokenOut": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
            "amountIn": "100000000",  # 100 USDC
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

    # Sign as both parties
    m.sign_as_server(server_acct.key.hex())
    m.sign_as_client(client_acct.key.hex())

    # Verify all
    assert m.verify_all() is True
