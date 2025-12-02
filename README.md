# mandates-core (Python)

Python SDK for creating, signing, and verifying **Mandates** — deterministic agreements between AI or human agents — designed to work with the ERC-8004 agent ecosystem and the Mandate Specs repository.

This SDK mirrors the TypeScript `@quillai-network/mandates-core` package and adds support for building `core` payloads from remote **Primitives** hosted in the `mandate-specs` repo.

---

## Features

- Create structured Mandate objects with strongly-typed fields
- Canonicalize and hash Mandates for signing
- Generate and verify EIP-191 signatures for client and server agents
- Build `core` payloads from remote primitives (for example, `swap@1`)
- Keep the Mandate schema in sync with the [mandate-specs](https://github.com/quillai-network/mandate-specs) repository

---

## Installation

```bash
pip install mandates-core
```

## Quickstart

```python
from eth_account import Account
from mandates_core import Mandate, build_core
```

# 1. Create demo accounts and CAIP-10 identifiers

```python
client_acct = Account.create()
server_acct = Account.create()

client_caip10 = f"eip155:1:{client_acct.address}"
server_caip10 = f"eip155:1:{server_acct.address}"
```

# 2. Build a primitive core (swap@1) from the remote registry

```python
core = build_core(
    "swap@1",
    {
        "chainId": 1,
        "tokenIn": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "tokenOut": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "amountIn": "100000000",      # 100 USDC (6 decimals)
        "minOut": "165000",
        "recipient": client_acct.address,
        "deadline": "2025-12-31T00:00:00Z",
    },
)
```
# 3. Create a Mandate

```python
m = Mandate(
    version="0.1.0",
    client=client_caip10,
    server=server_caip10,
    deadline="2025-12-31T00:10:00Z",
    intent="Swap 100 USDC for WBTC on Ethereum mainnet",
    core=core,
)
```

# 4. Sign as server then client

```python
m.sign_as_server(server_acct.key.hex())
m.sign_as_client(client_acct.key.hex())
```

# 5. Verify signatures

```python
result = m.verify_all()
print("Client signature valid:", result["client"]["ok"])
print("Server signature valid:", result["server"]["ok"])
print("All valid:", result["all_ok"])
```


# mandates-core (Python)

Python SDK for creating, signing, and verifying **Mandates** — deterministic agreements between AI or human agents — designed to work with the ERC-8004 agent ecosystem and the Mandate Specs repository.

This SDK mirrors the TypeScript `@quillai-network/mandates-core` package and adds support for building `core` payloads from remote **Primitives** hosted in the `mandate-specs` repo.

---

## Features

- Create structured Mandate objects with strongly-typed fields
- Canonicalize and hash Mandates for signing
- Generate and verify EIP-191 signatures for client and server agents
- Build `core` payloads from remote primitives (for example, `swap@1`)
- Keep the Mandate schema in sync with the [mandate-specs](https://github.com/quillai-network/mandate-specs) repository

---

## Installation

```bash
pip install mandates-core
````

Requires **Python 3.10+**.

---

## Quickstart

```python
from eth_account import Account
from mandates_core import Mandate, build_core

# 1. Create demo accounts and CAIP-10 identifiers
client_acct = Account.create()
server_acct = Account.create()

client_caip10 = f"eip155:1:{client_acct.address}"
server_caip10 = f"eip155:1:{server_acct.address}"

# 2. Build a primitive core (swap@1) from the remote registry
core = build_core(
    "swap@1",
    {
        "chainId": 1,
        "tokenIn": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "tokenOut": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "amountIn": "100000000",      # 100 USDC (6 decimals)
        "minOut": "165000",
        "recipient": client_acct.address,
        "deadline": "2025-12-31T00:00:00Z",
    },
)

# 3. Create a Mandate
m = Mandate(
    version="0.1.0",
    client=client_caip10,
    server=server_caip10,
    deadline="2025-12-31T00:10:00Z",
    intent="Swap 100 USDC for WBTC on Ethereum mainnet",
    core=core,
)

# 4. Sign as server then client
m.sign_as_server(server_acct.key.hex())
m.sign_as_client(client_acct.key.hex())

# 5. Verify signatures
result = m.verify_all()
print("Client signature valid:", result["client"]["ok"])
print("Server signature valid:", result["server"]["ok"])
print("All valid:", result["all_ok"])
```

---

## Primitives and the Remote Registry

By default, `build_core` resolves primitives from the `mandate-specs` GitHub repository:

* Registry: `spec/primitives/registry.json`
* Example entry for `swap@1`:

  ```json
  {
    "kind": "swap@1",
    "name": "swap",
    "version": 1,
    "schemaPath": "primitives/swap/swap@1.schema.json",
    "description": "Chain-agnostic token swap primitive."
  }
  ```

The SDK fetches:

1. `registry.json` to locate a primitive by `kind`
2. The primitive schema at `schemaPath`
3. Returns a `core` object of the form:

```python
{
    "kind": "swap@1",
    "payload": { ...your swap fields... }
}
```

You can override the base URL if you want to point to a fork or snapshot:

```python
import mandates_core.primitives as primitives

core = primitives.build_core(
    "swap@1",
    payload,
    base_url="https://raw.githubusercontent.com/your-org/your-specs-repo/main/spec",
)
```

---

## Development

* Clone the repository

* Create a virtual environment and install dependencies:

  ```bash
  pip install -e ".[dev]"
  ```

* Run tests:

  ```bash
  pytest
  ```

---

## License

Released under the MIT License.

