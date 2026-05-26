# LP-0003 Spec Compliance Matrix

Status: SAFE-LANE PARTIAL / FINAL PUBLICATION NO-GO.

This matrix mirrors the upstream LP-0003 success criteria. PASS means backed by current local tests/artifacts. PARTIAL means a local/source-package surface exists but is not final Logos/RISC0/Basecamp evidence. PENDING means a final gate still lacks the required artifact.

## Functionality

| Criterion | Status | Evidence |
|---|---:|---|
| Distributor commits to eligibility set without revealing addresses in the public claim transcript | PASS (local relation) | `core/src/*`, `core/tests/relation.rs` |
| Eligible recipient claims without revealing which address in set they hold | PASS (local relation) | `valid_claim_emits_public_journal_without_private_witness`, `docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md` |
| Recipient cannot claim more than once | PASS (local + LEZ-shaped model) | `duplicate_claim_is_rejected_without_incrementing_count`, `duplicate_nullifier_is_rejected_at_lez_boundary` |
| Observer cannot link completed claim to a specific eligible address | PASS (local transcript model) | public journal omits eligible address, claimant secret, leaf salt, Merkle path |
| Full privacy model documented | PASS | `docs/PRIVACY_MODEL.md`, `docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md` |
| Working demo on LEZ testnet/local sequencer | PENDING | Real LEZ/localnet run not attached |
| 2 distributions / 20 unique claims with reproducible evidence | PARTIAL | `consumer-demo`, `demo.sh`; safe-lane only, not final LEZ/RISC0 evidence |
| Full documentation and clean public repo | PENDING | Public repo/publication approval pending |

## Usability

| Criterion | Status | Evidence |
|---|---:|---|
| SDK/module for Logos modules | PASS (safe-lane SDK) | `sdk/`, `consumer-demo/` |
| Logos Basecamp app GUI loadable in Basecamp | PARTIAL | Native/QML source package and deterministic `.lgx` exist; runtime load evidence pending |
| SPEL IDL | PARTIAL | `interfaces/lp0003.idl.json`, `interfaces/lp0003.spel`; hand-written fallback until generated/deployed via real tooling |
| CI safe-lane | PASS | `.gitlab-ci.yml`, `scripts/ci-safe-lane.sh` |

## Reliability

| Criterion | Status | Evidence |
|---|---:|---|
| Proof generation failures are graceful | PENDING | RISC0 host/prover lane pending |
| Failed/rejected claim does not mark claimant as claimed | PASS | wrong Merkle path and duplicate tests |
| Deterministic documented error codes | PARTIAL | `interfaces/lp0003.idl.json`, `lez-program/src/lib.rs` |
| Final validators reject weak/local evidence | PASS | `tests/test_validators.py` checks safe-lane claims and source-package-only Basecamp evidence are blockers |

## Performance

| Criterion | Status | Evidence |
|---|---:|---|
| CU cost documented | PENDING | `submission/LEZ_COST_BENCHMARKS.json` pending raw-log-bound LEZ/localnet telemetry or explicit unavailable rationale |
| Proof benchmark documented | PENDING | `submission/PROOF_BENCHMARKS.json` pending raw-log-bound fresh `RISC0_DEV_MODE=0` proof timing |

## Supportability

| Criterion | Status | Evidence |
|---|---:|---|
| Deployed/tested on LEZ devnet/testnet/local sequencer | PENDING | Not attached |
| E2E tests against sequencer in CI | PENDING | Current CI is safe-lane only |
| CI green on default branch | PENDING | Local safe-lane passes; public branch/Actions pending |
| README documents usage | PARTIAL | Draft README exists; final operator docs pending |
| Reproducible demo script with RISC0_DEV_MODE=0 | PENDING | `demo.sh` is safe-lane only and intentionally does not claim RISC0 |
| Narrated video | PENDING | Not recorded |

## Honesty Notes

- Local implementation readiness is not final submission readiness.
- Static HTML is not Basecamp. This tree now has a native/QML source package, but that still is not final Basecamp runtime load evidence.
- Mock/local fixture evidence must not be counted as LEZ deployment evidence.
- Safe-lane 2-distribution / 20-claim output must not be counted as final RISC0/LEZ evidence.
- RISC0_DEV_MODE=0 claims require fresh proof artifacts for current source.
