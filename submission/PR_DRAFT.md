# Solution: LP-0003 — Private Allowlist / Airdrop Distributor

**Submitted by:** Tranquil-Flow

**Status:** DO NOT SUBMIT. This is a high-quality solution draft, not a final upstream filing. It must remain unpublished until `scripts/final-publication-check.py` passes and Evi explicitly approves the public repository / upstream PR.

## Summary

LP-0003 implements a private allowlist / airdrop distributor for LEZ. The design uses a hidden eligibility set commitment, distribution-bound nullifier derivation, and a public claim transcript that proves eligibility without revealing the eligible address, claimant secret, leaf salt, or Merkle path.

The current evidence bundle proves the core relation, SDK, consumer integration, LEZ-shaped state transition surface, SPEL/IDL fallback, deterministic native/QML Basecamp source package, authenticated Basecamp runtime-load evidence, fresh RISC0_DEV_MODE=0 proof artifacts, LEZ localnet 2-distribution / 20-claim evidence, and raw-log-bound benchmark evidence. The final submission remains intentionally blocked only on the narrated demo video URL and Evi's explicit approval to open the upstream PR.

## Repository

- **Repo:** https://github.com/Tranquil-Flow/lp-0003-private-airdrop — public staging repo exists; do not open the upstream Logos PR until final evidence is attached and Evi explicitly approves.
- **License:** MIT OR Apache-2.0.
- **Primary verification command:** `bash scripts/ci-safe-lane.sh`
- **Final publication command:** `python3 scripts/final-publication-check.py`

## Approach

### Commitment scheme

For each distribution, the distributor builds a fixed eligibility set. Each eligible leaf commits to:

- `distribution_id`
- claimant secret / shielded account witness
- leaf salt
- fixed allocation

The public distribution account exposes only the Merkle root, distribution id, and fixed allocation. The fixed allocation is deliberate for the final demo: variable per-recipient amounts can become a linking side channel when only a few recipients share a unique amount.

### Claim proof

A claimant proves membership in the committed eligibility set and emits a public journal containing:

- distribution id
- Merkle root
- distribution-bound nullifier
- recipient commitment
- fixed allocation
- proof context

Public transcript rule: the journal and LEZ payload must not contain the eligible address, claimant secret, leaf salt, or Merkle path. The relation tests serialize the public journal and assert those witness markers are absent.

### Double-claim prevention

The nullifier is distribution-bound. The same claimant can legitimately participate in two separate distributions, but cannot claim twice within the same distribution. The LEZ-shaped state model rejects duplicate `(distribution_id, nullifier)` records and preserves retry behavior for invalid or rejected claims.

### LEZ integration

The repository ships a local LEZ-shaped program crate and SPEL/IDL fallback artifacts for the public instruction surface:

- `create_distribution`
- `claim`
- `query_distribution`
- `query_claim_nullifier`

The final submission must replace local/safe-lane evidence with raw-log-bound LEZ localnet/testnet evidence showing program id, sequencer context, block/slot inclusion, transaction ids, 2 distinct distributions, 20 unique claims, duplicate-nullifier rejection, and the exact public data an on-chain observer can see.

### Basecamp integration

The repository includes a native/QML Basecamp source package and deterministic `.lgx` packaging. This is not final Basecamp evidence by itself. Final evidence requires a Basecamp runtime log showing the package actually loaded and activated in Logos Basecamp, then extraction through `scripts/extract-basecamp-load-evidence.py`.

### RISC0 proof evidence

The final proof lane must provide fresh `RISC0_DEV_MODE=0` proof artifacts for the current source. `scripts/validate-proof-artifacts.py` requires a hash-bound manifest containing image id, receipt path/hash, journal path/hash, freshness marker, and the exact command used.

## Success Criteria Checklist

### Functionality

- [x] Local relation: distributor commits to an eligibility set without publishing individual addresses.
- [x] Local relation: eligible recipient can claim without revealing the eligible address in the public transcript.
- [x] Local relation / LEZ-shaped state: distribution-bound nullifier prevents double claims.
- [x] Privacy model documents public observer, distributor, and claimant knowledge.
- [x] Final LEZ localnet evidence attached with program id, sequencer block context, two distributions, twenty unique accepted claims, and duplicate-nullifier rejection.
- [x] Final evidence for 2 distinct distributions and 20 unique claims attached in `submission/claims/claims-summary.json`.

### Usability

- [x] SDK / consumer-demo surface exists.
- [x] SPEL / IDL fallback artifacts exist.
- [x] Basecamp native/QML source package exists.
- [x] Basecamp runtime-load evidence attached in `submission/BASECAMP_LOAD_EVIDENCE.json`.
- [ ] Downloadable public repository assets attached.

### Reliability

- [x] Rejected invalid Merkle path does not mark claimant as claimed.
- [x] Duplicate claim returns a deterministic duplicate-nullifier error.
- [x] Final validators reject safe-lane/mock evidence as final evidence.
- [x] RISC0 proof-generation failure path proven against the final host/prover lane: host tests reject unset/dev-only proof mode and invalid Merkle witnesses before invoking the expensive prover.

### Performance

- [x] Proof-generation benchmark attached in `submission/PROOF_BENCHMARKS.json` and fresh proof artifacts attached in `submission/proof-artifacts/`.
- [x] LEZ compute-unit benchmark attached in `submission/LEZ_COST_BENCHMARKS.json`; the LEZ localnet/scaffold surface does not expose stable per-transaction CU counters for custom program executions, so the artifact records explicit unavailability rationale instead of invented CU numbers.

### Supportability

- [x] Safe-lane CI script exists and passes locally.
- [x] Final evidence collection runbook exists.
- [ ] CI is green on the public default branch.
- [ ] Reproducible real local sequencer demo with `RISC0_DEV_MODE=0` passes.
- [ ] Narrated builder demo video URL attached.
- [x] GitHub issues / Logos technology issues: final-run no-issues attestation is attached in `submission/LOGOS_TECH_ISSUES.md`.

## FURPS Self-Assessment

### Functionality

The core primitive supports hidden set commitment, membership proof, distribution-bound nullifier uniqueness, and fixed-allocation claim publication. The attached final evidence now covers two distributions, twenty unique accepted claims, and duplicate-nullifier rejection with raw-log-bound LEZ localnet context.

### Usability

The SDK and consumer demo provide a clone-and-run integration surface. The Basecamp app source is native/QML rather than static HTML, reducing the rejection risk seen in earlier submissions. Authenticated runtime-load evidence is attached and hash-bound to its raw Basecamp log.

### Reliability

The design treats failed proofs and duplicate claims as non-success paths and tests that invalid claims do not increment accepted claim state. The final host/prover lane now also has focused tests proving unset `RISC0_DEV_MODE` is rejected and invalid Merkle witnesses fail during host preflight before the expensive prover is invoked.

### Performance

The final evidence includes proof-generation timing and LEZ compute/cost documentation. The LEZ scaffold did not expose stable per-transaction CU counters for custom program executions, so the benchmark artifact records explicit unavailability rationale, operation counts, transaction identifiers, block context, and raw-log hashes rather than inventing gas/CU numbers.

### Supportability

The repo includes a strict safe-lane CI, final-publication checker, evidence extractors, and docs. These guardrails intentionally keep the project in NO-GO until every external artifact is attached and hash-bound; after this evidence pass, the remaining NO-GO is the narrated demo video URL.

## Supporting Materials

- `README.md` — current status and quick verification.
- `PLAN.md` — original implementation plan and final gates.
- `docs/REJECTION_RESISTANT_SUBMISSION_PLAN.md` — current final evidence plan incorporating prior Logos Lambda Prize lessons and rejection guardrails.
- `docs/PROTOCOL.md` — protocol design.
- `docs/PRIVACY_MODEL.md` and `docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md` — privacy/threat model.
- `docs/SPEC_COMPLIANCE.md` — LP-0003 criteria matrix.
- `docs/FINAL_EVIDENCE_COLLECTION.md` — final raw-log extraction runbook.
- `scripts/ci-safe-lane.sh` — local safe-lane validation.
- `scripts/final-publication-check.py` — strict final gate.
- `scripts/extract-basecamp-load-evidence.py` — Basecamp runtime-load evidence extractor.
- `scripts/extract-lez-claim-evidence.py` — LEZ/RISC0 2-distribution / 20-claim evidence extractor.
- `scripts/extract-proof-benchmark.py` — raw-log-bound proof timing benchmark extractor.
- `scripts/extract-lez-cost-benchmark.py` — raw-log-bound LEZ CU/cost benchmark extractor.
- `scripts/prepare-risc0-proof-artifacts.py` — packages externally generated RISC0_DEV_MODE=0 receipt/journal output into the final hash-bound manifest.
- `scripts/validate-proof-artifacts.py` — RISC0 proof artifact validator.
- `scripts/final-recording-preflight.py` — validates that the narrated recording workflow covers all LP-0003 final evidence scenes and safety gates.
- `scripts/validate-upstream-solution.py` — lambda-prize solution-template and LP-0003 structural simulation before opening the upstream PR.

## Terms & Conditions

By submitting this solution, I confirm that I have read and agree to the Terms & Conditions.
