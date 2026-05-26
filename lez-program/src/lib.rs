//! Local LEZ-shaped execution boundary for LP-0003.
//!
//! This crate models the public/private instruction surface that will be wired
//! into a real LEZ program. It is intentionally dependency-light so the replay,
//! duplicate-nullifier, and receipt/journal binding rules are testable before
//! live deployment.

use std::collections::{BTreeMap, BTreeSet};

use lp0003_core::{
    crypto::{hash_tagged, Hash32},
    types::Distribution,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DistributionAccount {
    pub distribution_id: Hash32,
    pub merkle_root: Hash32,
    pub fixed_allocation: u64,
    pub claimed_count: u64,
}

impl From<Distribution> for DistributionAccount {
    fn from(distribution: Distribution) -> Self {
        Self {
            distribution_id: distribution.distribution_id,
            merkle_root: distribution.merkle_root,
            fixed_allocation: distribution.fixed_allocation,
            claimed_count: 0,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ClaimInstruction {
    pub distribution_id: Hash32,
    pub merkle_root: Hash32,
    pub nullifier: Hash32,
    pub recipient_commitment: Hash32,
    pub allocation: u64,
    pub proof_context: Hash32,
    pub receipt_sha256: Hash32,
    pub journal_sha256: Hash32,
    pub receipt_journal_commitment: Hash32,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ClaimRecord {
    pub distribution_id: Hash32,
    pub nullifier: Hash32,
    pub recipient_commitment: Hash32,
    pub proof_context: Hash32,
    pub receipt_journal_commitment: Hash32,
}

#[derive(Debug, Clone, PartialEq, Eq, Error)]
pub enum LezError {
    #[error("distribution account already exists")]
    DistributionAlreadyExists,
    #[error("distribution account not found")]
    DistributionNotFound,
    #[error("claim journal merkle root does not match distribution")]
    MerkleRootMismatch,
    #[error("claim journal allocation does not match distribution allocation")]
    AllocationMismatch,
    #[error("claim nullifier already exists")]
    NullifierAlreadyClaimed,
    #[error("receipt/journal commitment is invalid")]
    InvalidReceiptBinding,
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct LezAirdropState {
    distributions: BTreeMap<Hash32, DistributionAccount>,
    claimed_nullifiers: BTreeSet<(Hash32, Hash32)>,
    claims: BTreeMap<(Hash32, Hash32), ClaimRecord>,
}

impl LezAirdropState {
    pub fn distribution(&self, distribution_id: &Hash32) -> Option<&DistributionAccount> {
        self.distributions.get(distribution_id)
    }

    pub fn has_claimed(&self, distribution_id: &Hash32, nullifier: &Hash32) -> bool {
        self.claimed_nullifiers
            .contains(&(*distribution_id, *nullifier))
    }

    pub fn claim_record(
        &self,
        distribution_id: &Hash32,
        nullifier: &Hash32,
    ) -> Option<&ClaimRecord> {
        self.claims.get(&(*distribution_id, *nullifier))
    }
}

pub fn receipt_journal_commitment(receipt_sha256: &Hash32, journal_sha256: &Hash32) -> Hash32 {
    hash_tagged(
        "lp0003:receipt-journal-commitment",
        &[receipt_sha256, journal_sha256],
    )
}

pub fn execute_create_distribution(
    state: &mut LezAirdropState,
    distribution: Distribution,
) -> Result<(), LezError> {
    if state
        .distributions
        .contains_key(&distribution.distribution_id)
    {
        return Err(LezError::DistributionAlreadyExists);
    }
    state
        .distributions
        .insert(distribution.distribution_id, distribution.into());
    Ok(())
}

pub fn execute_claim(
    state: &mut LezAirdropState,
    claim: ClaimInstruction,
) -> Result<ClaimRecord, LezError> {
    let distribution = state
        .distributions
        .get_mut(&claim.distribution_id)
        .ok_or(LezError::DistributionNotFound)?;

    if claim.merkle_root != distribution.merkle_root {
        return Err(LezError::MerkleRootMismatch);
    }
    if claim.allocation != distribution.fixed_allocation {
        return Err(LezError::AllocationMismatch);
    }
    if receipt_journal_commitment(&claim.receipt_sha256, &claim.journal_sha256)
        != claim.receipt_journal_commitment
    {
        return Err(LezError::InvalidReceiptBinding);
    }

    let key = (claim.distribution_id, claim.nullifier);
    if state.claimed_nullifiers.contains(&key) {
        return Err(LezError::NullifierAlreadyClaimed);
    }

    let record = ClaimRecord {
        distribution_id: claim.distribution_id,
        nullifier: claim.nullifier,
        recipient_commitment: claim.recipient_commitment,
        proof_context: claim.proof_context,
        receipt_journal_commitment: claim.receipt_journal_commitment,
    };

    state.claimed_nullifiers.insert(key);
    state.claims.insert(key, record.clone());
    distribution.claimed_count += 1;
    Ok(record)
}
