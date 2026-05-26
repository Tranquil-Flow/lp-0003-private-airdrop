# LP-0003 Privacy Model

Status: DRAFT. This document must be completed before final submission.

## Threat Model

LP-0003 targets claim-time unlinkability against on-chain observers. It does not hide the total number of eligible addresses, total allocation amount, or the fact that a distribution exists. The distributor may know the original eligibility set.

## Observer Learns

- distribution id and Merkle root
- fixed allocation metadata for the distribution
- successful claim nullifiers
- claim timing/order
- recipient commitment, not raw eligible address

## Observer Must Not Learn

- raw eligible address
- leaf secret/salt
- claimant private identity secret
- Merkle path
- which eligible leaf produced a claim

## Residual Leakage

- Small distributions have small anonymity sets.
- Timing correlation may reduce privacy.
- Unique allocation amounts can deanonymize; final demo should use fixed allocation.
- Network metadata is outside the current proof relation.
