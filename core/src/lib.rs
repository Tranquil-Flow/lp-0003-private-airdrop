//! LP-0003 core relation model.
//!
//! Pure deterministic model for private allowlist / airdrop claims. No LEZ or
//! RISC0 dependency lives here; this is the testable ground truth.

pub mod claim;
pub mod crypto;
pub mod merkle;
pub mod relation;
pub mod types;
