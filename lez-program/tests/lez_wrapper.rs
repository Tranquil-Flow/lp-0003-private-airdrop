use lp0003_core::{
    claim::ClaimRequest,
    crypto::{hash_tagged, Hash32},
    merkle::MerkleTree,
    types::{Distribution, EligibleLeaf},
};
use lp0003_lez_program::{
    execute_claim, execute_create_distribution, receipt_journal_commitment, ClaimInstruction,
    LezAirdropState, LezError,
};

fn demo_claim_instruction(label: &str) -> (Distribution, ClaimInstruction) {
    let distribution = Distribution::new_fixed_allocation(label, 100);
    let leaf = EligibleLeaf::new(
        &distribution.distribution_id,
        b"claimant-private-secret",
        b"leaf-private-salt",
        100,
    );
    let tree = MerkleTree::from_leaves(vec![leaf.commitment]);
    let distribution = distribution.with_merkle_root(tree.root());
    let request = ClaimRequest::new(
        distribution.clone(),
        leaf,
        tree.proof(0).unwrap(),
        b"recipient-shielded-destination",
    );
    let journal = lp0003_core::relation::verify_claim(
        &request,
        &mut lp0003_core::claim::ClaimState::default(),
    )
    .unwrap();
    let receipt_sha256: Hash32 = hash_tagged("test:receipt", &[&journal.proof_context]);
    let journal_sha256: Hash32 = hash_tagged("test:journal", &[&journal.proof_context]);
    let receipt_journal_commitment = receipt_journal_commitment(&receipt_sha256, &journal_sha256);

    (
        distribution,
        ClaimInstruction {
            distribution_id: journal.distribution_id,
            merkle_root: journal.merkle_root,
            nullifier: journal.nullifier,
            recipient_commitment: journal.recipient_commitment,
            allocation: journal.allocation,
            proof_context: journal.proof_context,
            receipt_sha256,
            journal_sha256,
            receipt_journal_commitment,
        },
    )
}

#[test]
fn create_distribution_then_claim_mutates_lez_state_once() {
    let (distribution, claim) = demo_claim_instruction("lez-a");
    let mut state = LezAirdropState::default();

    execute_create_distribution(&mut state, distribution.clone()).unwrap();
    let record = execute_claim(&mut state, claim.clone()).unwrap();

    assert_eq!(record.distribution_id, distribution.distribution_id);
    assert_eq!(record.nullifier, claim.nullifier);
    assert_eq!(record.recipient_commitment, claim.recipient_commitment);
    assert_eq!(
        state
            .distribution(&distribution.distribution_id)
            .unwrap()
            .claimed_count,
        1
    );
    assert!(state.has_claimed(&distribution.distribution_id, &claim.nullifier));
}

#[test]
fn duplicate_nullifier_is_rejected_at_lez_boundary() {
    let (distribution, claim) = demo_claim_instruction("lez-b");
    let mut state = LezAirdropState::default();

    execute_create_distribution(&mut state, distribution).unwrap();
    execute_claim(&mut state, claim.clone()).unwrap();
    let err = execute_claim(&mut state, claim).unwrap_err();

    assert_eq!(err, LezError::NullifierAlreadyClaimed);
}

#[test]
fn receipt_journal_commitment_must_bind_claim_payload() {
    let (distribution, mut claim) = demo_claim_instruction("lez-c");
    let mut state = LezAirdropState::default();

    execute_create_distribution(&mut state, distribution).unwrap();
    claim.receipt_journal_commitment = [9u8; 32];
    let err = execute_claim(&mut state, claim).unwrap_err();

    assert_eq!(err, LezError::InvalidReceiptBinding);
}
