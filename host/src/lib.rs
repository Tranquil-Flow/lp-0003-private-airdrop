use borsh::BorshDeserialize;
use lp0003_core::{
    claim::{ClaimRequest, ClaimState},
    merkle::MerkleTree,
    relation::{verify_claim, ClaimGuestInput},
    types::{Distribution, EligibleLeaf, PublicClaimJournal},
};
use risc0_zkvm::{default_prover, ExecutorEnv, Receipt};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

pub use lp0003_private_airdrop_methods::{CLAIM_PROOF_ELF, CLAIM_PROOF_ID};

pub struct ProofArtifacts {
    pub receipt_borsh: PathBuf,
    pub journal_borsh: PathBuf,
    pub manifest_txt: PathBuf,
}

pub fn claim_proof_image_id_bytes() -> [u8; 32] {
    digest_to_bytes(CLAIM_PROOF_ID)
}

pub fn claim_proof_image_id_hex() -> String {
    hex::encode(claim_proof_image_id_bytes())
}

pub fn fixture_guest_input() -> ClaimGuestInput {
    let distribution = Distribution::new_fixed_allocation("lp0003-risc0-final-fixture", 100);
    let leaves: Vec<EligibleLeaf> = (0..4)
        .map(|i| {
            EligibleLeaf::new(
                &distribution.distribution_id,
                format!("risc0-claimant-secret-{i}").as_bytes(),
                format!("risc0-leaf-salt-{i}").as_bytes(),
                100,
            )
        })
        .collect();
    let tree = MerkleTree::from_leaves(leaves.iter().map(|leaf| leaf.commitment).collect());
    let distribution = distribution.with_merkle_root(tree.root());
    let leaf = leaves[2].clone();
    let request = ClaimRequest::new(
        distribution,
        leaf,
        tree.proof(2).expect("fixture proof exists"),
        b"lp0003-risc0-recipient-commitment-2",
    );
    ClaimGuestInput { request }
}

pub fn build_guest_input_bytes(input: &ClaimGuestInput) -> Result<Vec<u8>, String> {
    borsh::to_vec(input).map_err(|err| format!("encode ClaimGuestInput: {err}"))
}

pub fn decode_public_journal_bytes(bytes: &[u8]) -> Result<PublicClaimJournal, String> {
    PublicClaimJournal::try_from_slice(bytes).map_err(|err| format!("decode PublicClaimJournal: {err}"))
}

pub fn decode_risc0_committed_journal(bytes: &[u8]) -> Result<PublicClaimJournal, String> {
    let inner: Vec<u8> = risc0_zkvm::serde::from_slice(bytes)
        .map_err(|err| format!("decode RISC0 journal Vec<u8>: {err}"))?;
    decode_public_journal_bytes(&inner)
}

pub fn decode_any_journal_bytes(bytes: &[u8]) -> Result<PublicClaimJournal, String> {
    decode_public_journal_bytes(bytes).or_else(|_| decode_risc0_committed_journal(bytes))
}

pub fn prove(input: &ClaimGuestInput) -> Result<(Receipt, PublicClaimJournal), String> {
    if std::env::var("RISC0_DEV_MODE").as_deref() != Ok("0") {
        return Err("refusing to prove unless RISC0_DEV_MODE=0 is set in the environment".into());
    }

    let mut preflight_state = ClaimState::default();
    verify_claim(&input.request, &mut preflight_state)
        .map_err(|err| format!("preflight claim relation: {err}"))?;

    let input_bytes = build_guest_input_bytes(input)?;
    let env = ExecutorEnv::builder()
        .write(&input_bytes)
        .map_err(|err| format!("write Borsh ClaimGuestInput into ExecutorEnv: {err}"))?
        .build()
        .map_err(|err| format!("build ExecutorEnv: {err}"))?;
    let prove_info = default_prover()
        .prove(env, CLAIM_PROOF_ELF)
        .map_err(|err| format!("prove RISC0 LP-0003 receipt: {err}"))?;
    let receipt = prove_info.receipt;
    receipt
        .verify(CLAIM_PROOF_ID)
        .map_err(|err| format!("verify freshly produced receipt: {err}"))?;
    let journal = decode_any_journal_bytes(&receipt.journal.bytes)?;
    Ok((receipt, journal))
}

pub fn prove_fixture_to_dir(output_dir: &Path) -> Result<ProofArtifacts, String> {
    prove_to_dir(&fixture_guest_input(), output_dir)
}

pub fn prove_to_dir(input: &ClaimGuestInput, output_dir: &Path) -> Result<ProofArtifacts, String> {
    let (receipt, journal) = prove(input)?;
    let receipt_bytes = borsh::to_vec(&receipt).map_err(|err| format!("encode receipt: {err}"))?;
    let journal_bytes = receipt.journal.bytes.clone();
    write_proof_artifacts(output_dir, &receipt_bytes, &journal_bytes, &journal)
}

pub fn write_proof_artifacts(
    output_dir: &Path,
    receipt_bytes: &[u8],
    journal_bytes: &[u8],
    journal: &PublicClaimJournal,
) -> Result<ProofArtifacts, String> {
    std::fs::create_dir_all(output_dir).map_err(|err| format!("create artifact dir: {err}"))?;
    let receipt_borsh = output_dir.join("receipt.borsh");
    let journal_borsh = output_dir.join("journal.borsh");
    let manifest_txt = output_dir.join("manifest.txt");
    std::fs::write(&receipt_borsh, receipt_bytes).map_err(|err| format!("write receipt: {err}"))?;
    std::fs::write(&journal_borsh, journal_bytes).map_err(|err| format!("write journal: {err}"))?;
    let manifest = format!(
        "LP-0003 RISC0 claim proof artifacts\n\
         risc0_dev_mode=0\n\
         image_id={}\n\
         receipt_borsh={}\n\
         journal_borsh={}\n\
         receipt_sha256={}\n\
         journal_sha256={}\n\
         distribution_id={}\n\
         merkle_root={}\n\
         nullifier={}\n\
         recipient_commitment={}\n\
         allocation={}\n\
         proof_context={}\n\
         privacy_note=eligible address, claimant secret, leaf salt, and Merkle path remain private witness data\n",
        claim_proof_image_id_hex(),
        receipt_borsh.display(),
        journal_borsh.display(),
        sha256_hex(receipt_bytes),
        sha256_hex(journal_bytes),
        hex::encode(journal.distribution_id),
        hex::encode(journal.merkle_root),
        hex::encode(journal.nullifier),
        hex::encode(journal.recipient_commitment),
        journal.allocation,
        hex::encode(journal.proof_context),
    );
    std::fs::write(&manifest_txt, manifest).map_err(|err| format!("write manifest: {err}"))?;
    Ok(ProofArtifacts {
        receipt_borsh,
        journal_borsh,
        manifest_txt,
    })
}

fn sha256_hex(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

fn digest_to_bytes(words: [u32; 8]) -> [u8; 32] {
    let mut out = [0u8; 32];
    for (i, word) in words.iter().enumerate() {
        out[i * 4..i * 4 + 4].copy_from_slice(&word.to_le_bytes());
    }
    out
}
