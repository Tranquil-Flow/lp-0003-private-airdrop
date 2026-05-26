use sha2::{Digest, Sha256};

pub type Hash32 = [u8; 32];

pub fn hash_tagged(tag: &str, parts: &[&[u8]]) -> Hash32 {
    let mut hasher = Sha256::new();
    hasher.update(tag.as_bytes());
    for part in parts {
        let len = (*part).len() as u64;
        hasher.update(len.to_le_bytes());
        hasher.update(part);
    }
    hasher.finalize().into()
}

pub fn hash_pair(left: &Hash32, right: &Hash32) -> Hash32 {
    hash_tagged("lp0003:merkle-node", &[left, right])
}
