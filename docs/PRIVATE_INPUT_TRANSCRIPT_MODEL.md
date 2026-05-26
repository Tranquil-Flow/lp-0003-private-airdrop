# Private Input / Public Transcript Model

Status: ACTIVE GUARDRAIL. This document exists because LP-0003 reviewers have focused on witness-like fields and public transcript semantics. It defines the private input / public transcript boundary that the code, evidence extractors, demo script, and final solution prose must preserve.

## Private input / public transcript boundary

The LP-0003 claim relation has two worlds:

1. Private witness data, known only to the claimant/prover and used inside the proof relation.
2. Public transcript data, visible to LEZ, Basecamp, evaluators, observers, logs, and the Lambda Prize solution text.

A final submission is acceptable only if observers can verify distribution membership, one-claim-per-recipient behavior, and allocation correctness without learning which eligible address claimed.

## Private Witness Fields

The following are private witness fields. They must not appear in public journals, public LEZ transaction payloads, raw logs, demo output, or final solution prose as live values:

| Private field | Why it is private | Public replacement |
|---|---|---|
| eligible address / raw claimant address | Links the claim to the original allowlist row | Merkle root plus inclusion proof verified inside RISC0 |
| claimant identity secret | Lets observers correlate the claimant across contexts | Distribution-bound nullifier |
| leaf salt | Can reveal or brute-force the committed leaf | Leaf commitment/Merkle root only |
| Merkle path siblings and directions | Witness material for set membership | Verified root in the public journal |
| claimant signature witness material, if used | Authentication secret or reusable linkage surface | Recipient commitment and proof context hash |

Concrete fixture markers such as `claimant-secret-*`, `leaf-salt-*`, `eligible-address-*`, `claimant_identity_secret`, `merkle_path_siblings`, or `private_witness` are forbidden in public evidence artifacts.

## Public Journal Fields

The public journal may include only verifier-facing transcript fields:

- `distribution_id`
- `merkle_root`
- `nullifier`
- fixed `allocation` or an allocation commitment
- `recipient_commitment`
- `proof_context`
- proof id / image id / receipt hash / journal hash

These are acceptable because they prove the claim relation and replay protection without naming the eligible address.

## Public LEZ transaction payload

The public LEZ transaction payload may carry the public journal, receipt/journal hashes, program id, transaction id, block/slot, and benchmark metadata. It must not contain the private witness values above. In particular, the LEZ payload should bind to `receipt_sha256` and `journal_sha256`; it should not inline the claimant's Merkle path or raw allowlist row.

## Required Test Gates

- `core/tests/relation.rs::valid_claim_emits_public_journal_without_private_witness` serializes a public claim journal and asserts secret test markers do not appear.
- `core/tests/relation.rs::public_journal_schema_is_stable` asserts the public schema has no `secret`, `salt`, or `merkle_path` fields.
- `scripts/audit-public-transcripts.py` scans evaluator-facing public artifacts and fails if private witness markers appear.
- `tests/test_validators.py::test_public_transcript_audit_rejects_private_witness_markers` proves the audit fails closed on leaked private markers.

Final rule: public artifacts must not contain private witness data, only commitments, nullifiers, roots, hashes, ids, and timing/cost evidence.
