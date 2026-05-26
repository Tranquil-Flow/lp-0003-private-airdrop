# Private Input / Public Transcript Model

Status: DRAFT. This file exists because LP-0003 reviewers have already focused on witness-like fields and public transcript semantics.

## Private Witness Fields

The following must never appear in public journals, public LEZ transaction payloads, raw logs, or solution prose as live secrets:

- eligible address / raw claimant address
- claimant identity secret
- leaf secret / salt
- Merkle path siblings and directions
- claimant signature witness material, if used

## Public Journal Fields

The public journal may include:

- distribution_id
- Merkle root
- nullifier
- fixed allocation or allocation commitment
- recipient commitment
- proof id / image id / receipt hash

## Required Tests

- Serialize a public claim journal and assert secret test markers do not appear.
- Write raw evidence logs and assert secret markers do not appear.
- Validate that failed/rejected claims do not emit nullifier writes.
