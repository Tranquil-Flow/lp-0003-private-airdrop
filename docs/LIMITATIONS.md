# LP-0003 Limitations and Honesty Notes

Status: active blocker ledger.

## Current proven scope

- Pure Rust relation model passes local tests.
- SDK and consumer demo prove 2 distributions, 20 unique safe-lane claims, and duplicate rejection.
- LEZ-shaped local wrapper models distribution and nullifier state, but is not deployed LEZ evidence.
- SPEL/IDL files document the intended public/private surface, but are hand-written fallback artifacts.
- Native/QML Basecamp package is deterministic, but runtime load evidence is still required.

## Current final blockers

- Fresh `RISC0_DEV_MODE=0` proof artifacts for the current source.
- LEZ localnet/testnet deployment and transaction evidence.
- Runtime Basecamp load/activation evidence.
- Final narrated demo URL.
- Public repository URL and upstream PR submission, only after Evi approval.
- Final solution draft with all placeholders removed.

## Non-claims

The project must not claim any of the following until evidence exists:

- safe-lane demo equals final LEZ evidence
- source `.lgx` package equals runtime Basecamp load
- hand-written IDL equals generated/deployed SPEL output
- bool-only proof manifests are proof freshness evidence
- invented CU/gas numbers
- public logs that include private witness fields are acceptable

## Privacy limitations

Fixed allocation is the preferred final path because it avoids leaking per-leaf allocation classes. Timing/order and aggregate claim counts remain public.

## Transport limitations

If raw RISC0 receipts are too large for current LEZ transaction/session limits, the honest final wording is: host-side receipt verification plus LEZ wrapper binding to receipt/journal hashes, with full receipts preserved as file-backed evidence. Do not claim full in-wrapper verification unless implemented and proven.
