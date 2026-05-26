# LP-0003 Integration Guide

Status: safe-lane integration guide. Final LEZ/RISC0/Basecamp evidence remains pending.

## Clone-and-run safe lane

```bash
cargo test --workspace
cargo run -p lp0003-consumer-demo --quiet
bash demo.sh
```

Expected safe-lane output:

- 2 distributions
- 20 unique claims
- duplicate rejections
- `SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE`

This proves the relation, SDK, and local replay semantics. It is not final LEZ/RISC0 evidence.

## SDK shape

The SDK drives distributor and claimant flows over the pure relation model:

1. create a distribution with a hidden eligibility Merkle root
2. derive distribution-bound claim witnesses
3. produce a public claim journal with no raw witness fields
4. reject duplicate nullifiers

## LEZ/SPEL interface

Fallback interfaces live under `interfaces/`:

- `interfaces/lp0003.idl.json`
- `interfaces/lp0003.spel`

These are hand-written until generated/deployed through the real SPEL/LEZ toolchain. They are useful reviewer-facing interface documentation, not final deployment evidence.

## Basecamp package

Build/package validation:

```bash
python3 scripts/package-basecamp-lgx.py
python3 scripts/validate-basecamp-native.py
```

The package must still be loaded by a real Basecamp runtime and extracted with:

```bash
python3 scripts/extract-basecamp-load-evidence.py path/to/basecamp-runtime.log
```

## Final evidence lane

For final publication, collect raw logs and run:

```bash
python3 scripts/extract-lez-claim-evidence.py path/to/lez-risc0-localnet.log
python3 scripts/validate-proof-artifacts.py submission/proof-artifacts/manifest.json
python3 scripts/final-publication-check.py
```

Do not submit while `final-publication-check.py` reports NO-GO.
