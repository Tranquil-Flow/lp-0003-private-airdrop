use serde::{Deserialize, Serialize};

use crate::crypto::{hash_tagged, Hash32};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Distribution {
    pub distribution_id: Hash32,
    pub merkle_root: Hash32,
    pub fixed_allocation: u64,
}

impl Distribution {
    pub fn new_fixed_allocation(label: &str, fixed_allocation: u64) -> Self {
        let amount = fixed_allocation.to_le_bytes();
        let distribution_id = hash_tagged("lp0003:distribution", &[label.as_bytes(), &amount]);
        Self {
            distribution_id,
            merkle_root: [0u8; 32],
            fixed_allocation,
        }
    }

    pub fn with_merkle_root(mut self, merkle_root: Hash32) -> Self {
        self.merkle_root = merkle_root;
        self
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EligibleLeaf {
    pub distribution_id: Hash32,
    pub commitment: Hash32,
    pub nullifier: Hash32,
    pub allocation: u64,
}

impl EligibleLeaf {
    pub fn new(
        distribution_id: &Hash32,
        claimant_secret: &[u8],
        leaf_salt: &[u8],
        allocation: u64,
    ) -> Self {
        let amount = allocation.to_le_bytes();
        let commitment = hash_tagged(
            "lp0003:eligible-leaf",
            &[distribution_id, claimant_secret, leaf_salt, &amount],
        );
        let nullifier = hash_tagged("lp0003:nullifier", &[distribution_id, claimant_secret]);
        Self {
            distribution_id: *distribution_id,
            commitment,
            nullifier,
            allocation,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PublicClaimJournal {
    pub distribution_id: Hash32,
    pub merkle_root: Hash32,
    pub nullifier: Hash32,
    pub recipient_commitment: Hash32,
    pub allocation: u64,
    pub proof_context: Hash32,
}
