//! Safe-lane LP-0003 SDK helpers.
//!
//! This SDK layer currently proves the pure Rust relation and consumer-demo
//! surface. It is explicitly not final LEZ/RISC0 evidence.

use std::collections::BTreeSet;

use lp0003_core::{
    claim::{ClaimRequest, ClaimState},
    merkle::MerkleTree,
    relation::{verify_claim, ClaimError},
    types::{Distribution, EligibleLeaf},
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum SdkError {
    #[error("claim relation failed: {0}")]
    Claim(#[from] ClaimError),
    #[error("missing Merkle proof for leaf {0}")]
    MissingProof(usize),
    #[error("expected duplicate rejection but got {0:?}")]
    UnexpectedDuplicateResult(Result<(), ClaimError>),
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DistributionReport {
    pub distribution_label: String,
    pub successful_claims: usize,
    pub unique_nullifiers: usize,
    pub rejected_claims: usize,
    pub duplicate_rejection_observed: bool,
    pub status: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TwoDistributionReport {
    pub distribution_count: usize,
    pub unique_claim_count: usize,
    pub duplicate_rejections_observed: usize,
    pub status: String,
}

pub fn run_demo_distribution(
    label: &str,
    claim_count: usize,
    allocation: u64,
) -> Result<DistributionReport, SdkError> {
    let distribution = Distribution::new_fixed_allocation(label, allocation);
    let leaves = demo_leaves(&distribution, claim_count, allocation);
    let tree = MerkleTree::from_leaves(leaves.iter().map(|leaf| leaf.commitment).collect());
    let distribution = distribution.with_merkle_root(tree.root());
    let mut state = ClaimState::default();
    let mut unique = BTreeSet::new();

    for (index, leaf) in leaves.iter().enumerate() {
        let proof = tree.proof(index).ok_or(SdkError::MissingProof(index))?;
        let recipient = format!("{label}-recipient-{index}");
        let request = ClaimRequest::new(
            distribution.clone(),
            leaf.clone(),
            proof,
            recipient.as_bytes(),
        );
        let journal = verify_claim(&request, &mut state)?;
        unique.insert(journal.nullifier);
    }

    let duplicate_request = ClaimRequest::new(
        distribution,
        leaves[0].clone(),
        tree.proof(0).ok_or(SdkError::MissingProof(0))?,
        format!("{label}-recipient-duplicate").as_bytes(),
    );
    let duplicate = verify_claim(&duplicate_request, &mut state);
    let duplicate_rejection_observed =
        matches!(duplicate, Err(ClaimError::NullifierAlreadyClaimed));
    if !duplicate_rejection_observed {
        return Err(SdkError::UnexpectedDuplicateResult(duplicate.map(|_| ())));
    }

    Ok(DistributionReport {
        distribution_label: label.to_string(),
        successful_claims: state.accepted_count(),
        unique_nullifiers: unique.len(),
        rejected_claims: 1,
        duplicate_rejection_observed,
        status: "SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE".to_string(),
    })
}

pub fn run_two_distribution_demo() -> Result<TwoDistributionReport, SdkError> {
    let a = run_demo_distribution("distribution-a", 10, 100)?;
    let b = run_demo_distribution("distribution-b", 10, 100)?;
    Ok(TwoDistributionReport {
        distribution_count: 2,
        unique_claim_count: a.unique_nullifiers + b.unique_nullifiers,
        duplicate_rejections_observed: usize::from(a.duplicate_rejection_observed)
            + usize::from(b.duplicate_rejection_observed),
        status: "SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE".to_string(),
    })
}

fn demo_leaves(distribution: &Distribution, count: usize, allocation: u64) -> Vec<EligibleLeaf> {
    (0..count)
        .map(|i| {
            EligibleLeaf::new(
                &distribution.distribution_id,
                format!("{i}:claimant-secret").as_bytes(),
                format!("{i}:leaf-salt").as_bytes(),
                allocation,
            )
        })
        .collect()
}
