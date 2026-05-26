# LP-0003 Protocol

Status: protocol specification with final non-demo RISC0/LEZ evidence attached; narrated demo video pending.

## Threshold Proof Scheme

LP-0003 uses a membership proof over an eligibility Merkle root rather than a threshold committee. The claimant proves privately that they know a leaf opening included in the distribution root. The public journal binds the proof to the distribution id, Merkle root, nullifier, fixed allocation, recipient commitment, and proof/receipt identity.

## Eligibility Commitments

For the final fixed-allocation path:

- `distribution_id = H("lp0003:distribution" || distributor || nonce || merkle_root || allocation_policy_hash)`
- `leaf_commitment = H("lp0003:eligible-leaf" || distribution_id || claimant_identity_commitment || fixed_allocation || leaf_salt)`
- `merkle_root` commits to all eligible leaves.

Raw eligible addresses, leaf salts, and Merkle paths are private witness fields.

## Nullifier Design

The nullifier is distribution-bound:

- `nullifier = H("lp0003:nullifier" || distribution_id || claimant_nullifier_secret)`

The same claimant secret produces different nullifiers for different distributions. LEZ state writes a nullifier only after proof/journal checks pass. Duplicate nullifiers reject without incrementing claim counts.

## LEZ Account Model Compatibility

The LEZ-shaped wrapper models:

- distribution account: distributor, distribution id, Merkle root, fixed allocation, claim limit/count, metadata hash, status
- nullifier record: distribution id, nullifier, recipient commitment, receipt/journal commitment
- `create_distribution`
- `claim`
- read/query surfaces through SPEL/IDL fallback artifacts

The current wrapper binds `receipt_sha256` and `journal_sha256` via `receipt_journal_commitment`. Final non-demo LEZ/RISC0 evidence is attached under `submission/claims/claims-summary.json` and hash-bound to the raw localnet transcript.

## Security Assumptions

- Hash function collision resistance for commitments, roots, nullifiers, and transcript bindings.
- RISC0 receipt soundness for the guest relation once the heavy lane is generated.
- LEZ account uniqueness for distribution/nullifier records.
- Private witness fields remain outside public journals, transaction payloads, and logs.

## Known Limitations

- Fixed allocation is chosen for final acceptance and privacy simplicity; per-leaf variable allocations are future work because they can leak allocation classes.
- Current repository has safe-lane relation/SDK/LEZ-shaped tests plus final `RISC0_DEV_MODE=0` proof artifacts for the current source. Regenerate the proof manifest/artifacts after proof-relevant source changes.
- Basecamp evidence is attached as authenticated runtime-load evidence; if Basecamp auth/runtime behavior changes, regenerate `submission/BASECAMP_LOAD_EVIDENCE.json` from a new raw log.

## Integration Guide

Use the SDK/consumer demo for clone-and-run integration. Use final evidence extractors only on real Basecamp and LEZ/RISC0 logs. See `docs/INTEGRATION_GUIDE.md` and `docs/FINAL_EVIDENCE_COLLECTION.md`.

## Error Codes

The LEZ/interface layer reserves deterministic errors for invalid distribution config, duplicate distribution, closed distribution, invalid Merkle root, invalid receipt image, invalid proof, journal mismatch, duplicate nullifier, malformed payload, malformed recipient commitment, amount mismatch, stale proof, and sequencer unavailability.
