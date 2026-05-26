# LP-0003 Spec Compliance Matrix

Status: FINAL NON-DEMO EVIDENCE ATTACHED / FINAL PUBLICATION NO-GO ONLY FOR NARRATED DEMO VIDEO.

This matrix mirrors the upstream LP-0003 success criteria. PASS means backed by current tests/artifacts. PARTIAL means a local/source-package surface exists but is not final Logos/RISC0/Basecamp evidence. PENDING means a final gate still lacks the required artifact. As of the current branch tip, all non-demo final evidence gates pass; the narrated builder demo video remains pending.

## Functionality

| Criterion | Status | Evidence |
|---|---:|---|
| Distributor commits to eligibility set without revealing addresses in the public claim transcript | PASS | `core/src/*`, `core/tests/relation.rs` |
| Eligible recipient claims without revealing which address in set they hold | PASS | `valid_claim_emits_public_journal_without_private_witness`, `docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md` |
| Recipient cannot claim more than once | PASS | `duplicate_claim_is_rejected_without_incrementing_count`, `duplicate_nullifier_is_rejected_at_lez_boundary` |
| Observer cannot link completed claim to a specific eligible address | PASS | public journal omits eligible address, claimant secret, leaf salt, Merkle path; `scripts/audit-public-transcripts.py` passes |
| Full privacy model documented | PASS | `docs/PRIVACY_MODEL.md`, `docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md` |
| Working evidence on LEZ local sequencer | PASS | `submission/claims/claims-summary.json`, `submission/raw-logs/lez-risc0-claims.log`, program/localnet context in structured evidence |
| 2 distributions / 20 unique claims with reproducible evidence | PASS | `submission/claims/claims-summary.json`; hash-bound to raw LEZ/RISC0 localnet log |
| Full documentation and clean public repo | PASS except demo/PR approval | public repo URL attached; upstream PR still requires narrated video and explicit Evi approval |

## Usability

| Criterion | Status | Evidence |
|---|---:|---|
| SDK/module for Logos modules | PASS | `sdk/`, `consumer-demo/` |
| Logos Basecamp app GUI loadable in Basecamp | PASS | `submission/BASECAMP_LOAD_EVIDENCE.json`, hash-bound to `submission/raw-logs/basecamp-runtime-load.log` |
| SPEL IDL | PASS | `interfaces/lp0003.idl.json`, `interfaces/lp0003.spel` |
| CI safe-lane metadata | PASS | `.gitlab-ci.yml`, `scripts/ci-safe-lane.sh` |

## Reliability

| Criterion | Status | Evidence |
|---|---:|---|
| Proof generation failures are graceful | PASS | host/prover tests reject unset/dev-only proof mode and invalid Merkle witnesses before expensive prover path |
| Failed/rejected claim does not mark claimant as claimed | PASS | wrong Merkle path and duplicate tests |
| Deterministic documented error codes | PASS | `interfaces/lp0003.idl.json`, `lez-program/src/lib.rs` |
| Final validators reject weak/local evidence | PASS | `tests/test_validators.py`, `tests/test_evidence_extractors.py` |

## Performance

| Criterion | Status | Evidence |
|---|---:|---|
| CU cost documented | PASS | `submission/LEZ_COST_BENCHMARKS.json`; records explicit LEZ CU-unavailable rationale and operation coverage instead of invented numbers |
| Proof benchmark documented | PASS | `submission/PROOF_BENCHMARKS.json`; raw-log-bound fresh `RISC0_DEV_MODE=0` proof timing |

## Supportability

| Criterion | Status | Evidence |
|---|---:|---|
| Deployed/tested on LEZ local sequencer | PASS | `submission/claims/claims-summary.json`, `submission/LEZ_COST_BENCHMARKS.json`, raw logs under `submission/raw-logs/` |
| E2E tests against sequencer in CI | PARTIAL | CI remains safe-lane; final localnet evidence is attached as raw-log-bound artifacts |
| CI green on public branch | PARTIAL | local/fresh-clone test suite passes; public upstream PR not opened yet |
| README documents usage | PASS | `README.md`, `docs/FINAL_EVIDENCE_COLLECTION.md` |
| Reproducible demo script with `RISC0_DEV_MODE=0` evidence | PASS for evidence bundle / PENDING for narrated walkthrough | proof artifacts and final evidence are attached; human-narrated video still pending |
| Narrated video | PENDING | not recorded/attached yet |

## Honesty Notes

- The repository should not be submitted upstream until the narrated builder demo video URL is attached and Evi explicitly approves the PR.
- Static HTML is not Basecamp. This tree has native/QML Basecamp source plus authenticated runtime-load evidence.
- LEZ per-transaction CU counters were not exposed by the current localnet/scaffold surface; the benchmark artifact records this explicitly instead of inventing CU values.
- Safe-lane evidence remains useful for clone-and-run validation, but final 2-distribution / 20-claim evidence is now the raw-log-bound LEZ/RISC0 localnet artifact.
- RISC0_DEV_MODE=0 proof claims are bound to current source through `submission/proof-artifacts/manifest.json`; regenerate the manifest/proof artifacts if proof-relevant source changes.
