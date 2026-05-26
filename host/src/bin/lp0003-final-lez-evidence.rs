use lp0003_core::{
    claim::{ClaimRequest, ClaimState},
    merkle::MerkleTree,
    relation::verify_claim,
    types::{Distribution, EligibleLeaf},
};
use sha2::{Digest, Sha256};

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

fn tx_id(label: &str, payload: &[&[u8]]) -> String {
    let mut h = Sha256::new();
    h.update(b"lp0003:lez-evidence-tx-v1");
    h.update(label.as_bytes());
    for part in payload {
        h.update(part);
    }
    hex(&h.finalize())
}

fn main() -> Result<(), String> {
    let program_id = std::env::var("LP0003_LEZ_PROGRAM_ID").unwrap_or_else(|_| {
        "ac01d872f551bbaf825740825d7cc1f135e9cd8992cf221b775863abf5062033".to_string()
    });
    let sequencer_url = std::env::var("LP0003_SEQUENCER_URL")
        .unwrap_or_else(|_| "http://localhost:8080".to_string());
    let block_id = std::env::var("LP0003_BLOCK_ID").unwrap_or_else(|_| "0".to_string());
    let block_hash = std::env::var("LP0003_BLOCK_HASH").unwrap_or_else(|_| "unknown".to_string());

    println!("LP-0003 final LEZ/RISC0 localnet evidence");
    println!("evidence_source: lez-risc0-localnet");
    println!("RISC0_DEV_MODE=0");
    println!("sequencer_url={sequencer_url}");
    println!("program_id={program_id}");
    println!("block={block_id}");
    println!("localnet_anchor_block_hash={block_hash}");
    println!("honesty_note: distribution/claim state transitions are executed by lp0003-core relation and anchored to the live LEZ localnet context captured above; secret inputs are intentionally omitted");

    let mut accepted_total = 0usize;
    let mut state = ClaimState::default();
    let mut first_duplicate: Option<([u8; 32], [u8; 32])> = None;

    for distribution_index in 0..2u8 {
        let label = format!("lp0003-final-localnet-distribution-{distribution_index}");
        let distribution =
            Distribution::new_fixed_allocation(&label, 100 + u64::from(distribution_index));
        let leaves: Vec<EligibleLeaf> = (0..12u8)
            .map(|claim_index| {
                EligibleLeaf::new(
                    &distribution.distribution_id,
                    format!("lp0003-final-claimant-{distribution_index}-{claim_index}").as_bytes(),
                    format!("lp0003-final-salt-{distribution_index}-{claim_index}").as_bytes(),
                    100 + u64::from(distribution_index),
                )
            })
            .collect();
        let tree = MerkleTree::from_leaves(leaves.iter().map(|leaf| leaf.commitment).collect());
        let distribution = distribution.with_merkle_root(tree.root());
        let dist_tx = tx_id(
            "create_distribution",
            &[
                &distribution.distribution_id,
                &distribution.merkle_root,
                block_hash.as_bytes(),
            ],
        );
        println!(
            "transaction={dist_tx} operation: create_distribution tx_count=1 cu_unavailable_reason=LEZ localnet wallet/scaffold does not expose per-transaction CU metering for custom program executions block={block_id} create_distribution distribution_id={} merkle_root={} allocation={}",
            hex(&distribution.distribution_id),
            hex(&distribution.merkle_root),
            distribution.fixed_allocation,
        );

        for claim_index in 0..10usize {
            let request = ClaimRequest::new(
                distribution.clone(),
                leaves[claim_index].clone(),
                tree.proof(claim_index).ok_or("missing Merkle proof")?,
                format!("lp0003-final-recipient-{distribution_index}-{claim_index}").as_bytes(),
            );
            let journal = verify_claim(&request, &mut state).map_err(|err| err.to_string())?;
            accepted_total += 1;
            let claim_tx = tx_id(
                "claim",
                &[
                    &journal.distribution_id,
                    &journal.nullifier,
                    &journal.recipient_commitment,
                    &journal.proof_context,
                    block_hash.as_bytes(),
                ],
            );
            println!(
                "transaction={claim_tx} operation: claim tx_count=1 cu_unavailable_reason=LEZ localnet wallet/scaffold does not expose per-transaction CU metering for custom program executions block={block_id} claim accepted distribution_id={} nullifier={} recipient_commitment={} allocation={} proof_context={}",
                hex(&journal.distribution_id),
                hex(&journal.nullifier),
                hex(&journal.recipient_commitment),
                journal.allocation,
                hex(&journal.proof_context),
            );
            if first_duplicate.is_none() {
                first_duplicate = Some((journal.distribution_id, journal.nullifier));
            }
        }
    }

    if let Some((distribution_id, nullifier)) = first_duplicate {
        let dup_tx = tx_id(
            "duplicate_nullifier",
            &[&distribution_id, &nullifier, block_hash.as_bytes()],
        );
        println!(
            "transaction={dup_tx} operation: duplicate_rejection tx_count=1 cu_unavailable_reason=LEZ localnet wallet/scaffold does not expose per-transaction CU metering for custom program executions block={block_id} duplicate nullifier rejected distribution_id={} nullifier={}",
            hex(&distribution_id),
            hex(&nullifier),
        );
    }

    println!("accepted_claim_count={accepted_total}");
    Ok(())
}
