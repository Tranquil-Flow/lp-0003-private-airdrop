use std::collections::BTreeSet;

use crate::{
    crypto::{hash_tagged, Hash32},
    merkle::MerkleProof,
    types::{Distribution, EligibleLeaf},
};

#[derive(Debug, Clone)]
pub struct ClaimRequest {
    pub distribution: Distribution,
    pub leaf: EligibleLeaf,
    pub proof: MerkleProof,
    pub recipient_commitment: Hash32,
}

impl ClaimRequest {
    pub fn new(
        distribution: Distribution,
        leaf: EligibleLeaf,
        proof: MerkleProof,
        recipient_secret_or_commitment: &[u8],
    ) -> Self {
        let recipient_commitment = hash_tagged(
            "lp0003:recipient-commitment",
            &[
                &distribution.distribution_id,
                recipient_secret_or_commitment,
            ],
        );
        Self {
            distribution,
            leaf,
            proof,
            recipient_commitment,
        }
    }
}

#[derive(Debug, Default, Clone)]
pub struct ClaimState {
    claimed_nullifiers: BTreeSet<Hash32>,
    accepted_count: usize,
}

impl ClaimState {
    pub fn has_claimed(&self, nullifier: &Hash32) -> bool {
        self.claimed_nullifiers.contains(nullifier)
    }

    pub fn mark_claimed(&mut self, nullifier: Hash32) {
        if self.claimed_nullifiers.insert(nullifier) {
            self.accepted_count += 1;
        }
    }

    pub fn accepted_count(&self) -> usize {
        self.accepted_count
    }
}
