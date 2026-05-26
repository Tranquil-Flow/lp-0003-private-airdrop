use std::path::PathBuf;

fn main() {
    let out = std::env::args()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("target/lp0003-risc0-final"));
    match lp0003_private_airdrop_host::prove_fixture_to_dir(&out) {
        Ok(artifacts) => {
            println!("LP-0003 RISC0 proof generation: PASS");
            println!("RISC0_DEV_MODE=0");
            println!("image_id={}", lp0003_private_airdrop_host::claim_proof_image_id_hex());
            println!("receipt_borsh={}", artifacts.receipt_borsh.display());
            println!("journal_borsh={}", artifacts.journal_borsh.display());
            println!("manifest_txt={}", artifacts.manifest_txt.display());
        }
        Err(err) => {
            eprintln!("LP-0003 RISC0 proof generation: FAIL");
            eprintln!("{err}");
            std::process::exit(1);
        }
    }
}
