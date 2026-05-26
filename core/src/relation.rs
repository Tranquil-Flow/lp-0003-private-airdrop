use thiserror::Error;

use crate::{
    claim::{ClaimRequest, ClaimState},
    crypto::hash_tagged,
    merkle::verify_merkle_proof,
    types::PublicClaimJournal,
};

#[derive(Debug, Clone, PartialEq, Eq, Error)]
pub enum ClaimError {
    #[error("leaf distribution id does not match distribution")]
    DistributionMismatch,
    #[error("claim allocation does not match fixed distribution allocation")]
    AmountMismatch,
    #[error("invalid Merkle proof")]
    InvalidMerkleProof,
    #[error("nullifier already claimed")]
    NullifierAlreadyClaimed,
}

pub fn verify_claim(
    request: &ClaimRequest,
    state: &mut ClaimState,
) -> Result<PublicClaimJournal, ClaimError> {
    if request.leaf.distribution_id != request.distribution.distribution_id {
        return Err(ClaimError::DistributionMismatch);
    }
    if request.leaf.allocation != request.distribution.fixed_allocation {
        return Err(ClaimError::AmountMismatch);
    }
    if !verify_merkle_proof(
        request.leaf.commitment,
        &request.proof,
        &request.distribution.merkle_root,
    ) {
        return Err(ClaimError::InvalidMerkleProof);
    }
    if state.has_claimed(&request.leaf.nullifier) {
        return Err(ClaimError::NullifierAlreadyClaimed);
    }

    let allocation = request.leaf.allocation.to_le_bytes();
    let proof_context = hash_tagged(
        "lp0003:proof-context",
        &[
            &request.distribution.distribution_id,
            &request.distribution.merkle_root,
            &request.leaf.nullifier,
            &request.recipient_commitment,
            &allocation,
        ],
    );

    let journal = PublicClaimJournal {
        distribution_id: request.distribution.distribution_id,
        merkle_root: request.distribution.merkle_root,
        nullifier: request.leaf.nullifier,
        recipient_commitment: request.recipient_commitment,
        allocation: request.leaf.allocation,
        proof_context,
    };
    state.mark_claimed(request.leaf.nullifier);
    Ok(journal)
}
