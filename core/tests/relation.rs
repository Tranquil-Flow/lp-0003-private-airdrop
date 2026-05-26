use lp0003_core::{
    claim::{ClaimRequest, ClaimState},
    merkle::MerkleTree,
    relation::{verify_claim, ClaimError},
    types::{Distribution, EligibleLeaf, PublicClaimJournal},
};

fn fixture_distribution() -> (Distribution, Vec<EligibleLeaf>, MerkleTree) {
    let distribution = Distribution::new_fixed_allocation("dist-a", 100);
    let leaves: Vec<EligibleLeaf> = (0..4)
        .map(|i| {
            EligibleLeaf::new(
                &distribution.distribution_id,
                format!("claimant-secret-{i}").as_bytes(),
                format!("leaf-salt-{i}").as_bytes(),
                100,
            )
        })
        .collect();
    let tree = MerkleTree::from_leaves(leaves.iter().map(|l| l.commitment).collect());
    (distribution.with_merkle_root(tree.root()), leaves, tree)
}

#[test]
fn valid_claim_emits_public_journal_without_private_witness() {
    let (distribution, leaves, tree) = fixture_distribution();
    let leaf = leaves[2].clone();
    let request = ClaimRequest::new(
        distribution.clone(),
        leaf.clone(),
        tree.proof(2).expect("proof"),
        b"recipient-commitment-2",
    );
    let mut state = ClaimState::default();

    let journal = verify_claim(&request, &mut state).expect("valid claim");

    assert_eq!(journal.distribution_id, distribution.distribution_id);
    assert_eq!(journal.merkle_root, distribution.merkle_root);
    assert_eq!(journal.allocation, 100);
    assert_eq!(state.accepted_count(), 1);

    let public_json = serde_json::to_string(&journal).expect("journal json");
    assert!(!public_json.contains("claimant-secret-2"));
    assert!(!public_json.contains("leaf-salt-2"));
    assert!(!public_json.contains("recipient-commitment-2"));
}

#[test]
fn duplicate_claim_is_rejected_without_incrementing_count() {
    let (distribution, leaves, tree) = fixture_distribution();
    let leaf = leaves[1].clone();
    let request = ClaimRequest::new(
        distribution,
        leaf,
        tree.proof(1).expect("proof"),
        b"recipient-commitment-1",
    );
    let mut state = ClaimState::default();

    verify_claim(&request, &mut state).expect("first claim");
    let err = verify_claim(&request, &mut state).expect_err("duplicate must fail");

    assert_eq!(err, ClaimError::NullifierAlreadyClaimed);
    assert_eq!(state.accepted_count(), 1);
}

#[test]
fn wrong_merkle_path_is_rejected_without_marking_claimed() {
    let (distribution, leaves, tree) = fixture_distribution();
    let leaf = leaves[0].clone();
    let wrong_proof = tree.proof(3).expect("wrong proof");
    let request = ClaimRequest::new(distribution, leaf, wrong_proof, b"recipient-commitment-0");
    let mut state = ClaimState::default();

    let err = verify_claim(&request, &mut state).expect_err("wrong proof must fail");

    assert_eq!(err, ClaimError::InvalidMerkleProof);
    assert_eq!(state.accepted_count(), 0);
}

#[test]
fn same_secret_has_different_nullifier_in_different_distribution() {
    let d1 = Distribution::new_fixed_allocation("dist-a", 100);
    let d2 = Distribution::new_fixed_allocation("dist-b", 100);
    let secret = b"same-claimant-secret";
    let salt = b"same-leaf-salt";

    let l1 = EligibleLeaf::new(&d1.distribution_id, secret, salt, 100);
    let l2 = EligibleLeaf::new(&d2.distribution_id, secret, salt, 100);

    assert_ne!(l1.nullifier, l2.nullifier);
    assert_ne!(l1.commitment, l2.commitment);
}

#[test]
fn public_journal_schema_is_stable() {
    let journal = PublicClaimJournal {
        distribution_id: [1u8; 32],
        merkle_root: [2u8; 32],
        nullifier: [3u8; 32],
        recipient_commitment: [4u8; 32],
        allocation: 100,
        proof_context: [5u8; 32],
    };

    let json = serde_json::to_value(&journal).expect("json");
    assert!(json.get("distribution_id").is_some());
    assert!(json.get("merkle_root").is_some());
    assert!(json.get("nullifier").is_some());
    assert!(json.get("recipient_commitment").is_some());
    assert!(json.get("allocation").is_some());
    assert!(json.get("proof_context").is_some());
    assert!(json.get("secret").is_none());
    assert!(json.get("salt").is_none());
    assert!(json.get("merkle_path").is_none());
}
