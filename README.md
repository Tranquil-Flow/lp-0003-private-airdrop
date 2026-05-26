# LP-0003 Private Allowlist / Airdrop Distributor

Status: SAFE-LANE PARTIAL / NO-GO for final publication.

This repository is being built for Logos Lambda Prize LP-0003. The current tree is not a final submission until `scripts/final-publication-check.py` passes and Evi explicitly approves publication / upstream PR creation.

## What works now

1. Pure Rust relation model for hidden eligibility commitments, Merkle membership, fixed-allocation claims, and distribution-bound nullifiers.
2. SDK, CLI, and consumer demo proving 2 distributions, 20 unique safe-lane claims, and duplicate rejection.
3. LEZ-shaped local execution model for `create_distribution` and `claim`, including duplicate-nullifier replay protection and receipt/journal commitment binding.
4. SPEL/IDL fallback artifacts under `interfaces/`.
5. Native/QML Basecamp source package under `basecamp-app/` with deterministic `.lgx` packaging.
6. Evidence extraction/helpers for final Basecamp runtime-load logs, LEZ/RISC0 claim logs, proof artifact hash validation, and narrated-video attachment.
7. Strict final-publication gates that reject safe-lane claim counts, source-package-only Basecamp evidence, bool-only proof manifests, and tampered raw-log hashes as final evidence.

## What is still final-blocking

- Fresh `RISC0_DEV_MODE=0` proof artifacts for current source.
- Real LEZ/localnet/testnet deployment and transaction evidence.
- Runtime Basecamp load/activation evidence.
- Narrated demo video.
- Proof generation and LEZ compute-unit benchmark evidence.
- GitHub issue links for Logos technology problems encountered, or an explicit no-issues attestation after the final run.
- Public repository URL is attached; upstream submission PR still requires explicit Evi approval.
- Final solution template with all placeholders removed.

## Quick verification

```bash
bash scripts/ci-safe-lane.sh
bash demo.sh
cargo run -p lp0003-cli -- safe-lane-evidence --out submission/claims/claims-summary.safe-lane.json
```

The safe-lane CI intentionally treats final publication as NO-GO until real evidence is attached. This is a guardrail, not a failure.

See `PLAN.md` for the full spellbook, `docs/SPEC_COMPLIANCE.md` for the evidence matrix, and `docs/FINAL_EVIDENCE_COLLECTION.md` for the final raw-log extraction runbook.
