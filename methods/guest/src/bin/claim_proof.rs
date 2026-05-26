use borsh::{BorshDeserialize, BorshSerialize};
use lp0003_core::{
    claim::ClaimState,
    relation::{verify_claim, ClaimGuestInput},
};
use risc0_zkvm::guest::env;

fn main() {
    // The private witness is Borsh-encoded as a byte vector. Only the public
    // journal is committed. Claimant secrets, leaf salts, and Merkle path
    // witness data remain inside the zkVM execution.
    let input_bytes: Vec<u8> = env::read();
    let input = ClaimGuestInput::try_from_slice(&input_bytes)
        .expect("LP-0003 guest: malformed Borsh ClaimGuestInput");
    let mut state = ClaimState::default();
    let journal = verify_claim(&input.request, &mut state)
        .expect("LP-0003 guest: private allowlist claim relation failed");
    let journal_bytes = borsh::to_vec(&journal).expect("LP-0003 guest: public journal serializes");
    env::commit(&journal_bytes);
}
