# LP-0003 Private Allowlist / Airdrop Distributor

Status: FINAL NON-DEMO EVIDENCE ATTACHED / NO-GO ONLY FOR NARRATED DEMO VIDEO.

This repository is being built for Logos Lambda Prize LP-0003. The current tree is not a final upstream submission until the narrated builder demo video URL is attached and Evi explicitly approves publication / upstream PR creation. All non-demo final-publication gates currently pass in `scripts/final-publication-check.py`.

## What works now

1. Pure Rust relation model for hidden eligibility commitments, Merkle membership, fixed-allocation claims, and distribution-bound nullifiers.
2. SDK, CLI, and consumer demo proving 2 distributions, 20 unique safe-lane claims, and duplicate rejection.
3. LEZ-shaped local execution model for `create_distribution` and `claim`, including duplicate-nullifier replay protection and receipt/journal commitment binding.
4. SPEL/IDL fallback artifacts under `interfaces/`.
5. Native/QML Basecamp source package under `basecamp-app/` with deterministic `.lgx` packaging.
6. Authenticated Basecamp runtime-load evidence attached in `submission/BASECAMP_LOAD_EVIDENCE.json`, hash-bound to `submission/raw-logs/basecamp-runtime-load.log`.
7. Repository-owned RISC Zero heavy lane (`methods/`, `host/`, `scripts/run-risc0-heavy-lane.sh`) with fresh `RISC0_DEV_MODE=0` proof artifacts in `submission/proof-artifacts/`.
8. LEZ/RISC0 localnet evidence for 2 distinct distributions, 20 unique accepted claims, and duplicate-nullifier rejection in `submission/claims/claims-summary.json`, hash-bound to `submission/raw-logs/lez-risc0-claims.log`.
9. Proof-generation and LEZ compute/cost benchmark artifacts in `submission/PROOF_BENCHMARKS.json` and `submission/LEZ_COST_BENCHMARKS.json`; LEZ per-transaction CU counters are recorded as unavailable with explicit rationale rather than invented values.
10. Strict final-publication gates that reject safe-lane claim counts, source-package-only Basecamp evidence, bool-only proof manifests, tampered raw-log hashes, and private witness markers in public transcript artifacts as final evidence.
11. Pushable CI metadata via `.gitlab-ci.yml` plus local `scripts/ci-safe-lane.sh`.

## What is still final-blocking

- Narrated builder demo video URL.
- Evi's explicit approval before opening the upstream Logos Lambda Prize PR.

## Current final-publication gate shape

`python3 scripts/final-publication-check.py` is expected to report `NO-GO` with exactly the narrated demo video blocker and PASS for all other gates:

- PASS public repository URL
- BLOCKER narrated demo video URL
- PASS Basecamp-loadable app evidence
- PASS 2 distributions / 20 unique claims evidence
- PASS fresh RISC0_DEV_MODE=0 proof artifacts
- PASS proof generation benchmark evidence
- PASS LEZ compute unit benchmark evidence
- PASS Logos technology issue report
- PASS public transcript privacy audit
- PASS CI workflow exists
- PASS solution template complete

## Quick verification

```bash
bash scripts/ci-safe-lane.sh
bash demo.sh
python3 scripts/validate-proof-artifacts.py
python3 scripts/audit-public-transcripts.py
python3 scripts/final-publication-check.py
```

The final publication check intentionally remains NO-GO until the narrated demo URL is attached. This is a guardrail, not a failure of the non-demo evidence bundle.

See `PLAN.md` for the original build spellbook, `docs/REJECTION_RESISTANT_SUBMISSION_PLAN.md` for the current final-submission plan, `docs/SPEC_COMPLIANCE.md` for the evidence matrix, and `docs/FINAL_EVIDENCE_COLLECTION.md` for the final raw-log extraction runbook.
