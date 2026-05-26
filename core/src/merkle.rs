use borsh::{BorshDeserialize, BorshSerialize};

use crate::crypto::{hash_pair, Hash32};

#[derive(Debug, Clone, Copy, PartialEq, Eq, BorshSerialize, BorshDeserialize)]
pub enum Direction {
    Left,
    Right,
}

#[derive(Debug, Clone, PartialEq, Eq, BorshSerialize, BorshDeserialize)]
pub struct ProofStep {
    pub sibling: Hash32,
    pub direction: Direction,
}

#[derive(Debug, Clone, PartialEq, Eq, BorshSerialize, BorshDeserialize)]
pub struct MerkleProof {
    pub steps: Vec<ProofStep>,
}

#[derive(Debug, Clone, PartialEq, Eq, BorshSerialize, BorshDeserialize)]
pub struct MerkleTree {
    levels: Vec<Vec<Hash32>>,
}

impl MerkleTree {
    pub fn from_leaves(mut leaves: Vec<Hash32>) -> Self {
        assert!(!leaves.is_empty(), "MerkleTree requires at least one leaf");
        let mut levels = vec![leaves.clone()];
        while leaves.len() > 1 {
            let mut next = Vec::with_capacity(leaves.len().div_ceil(2));
            for pair in leaves.chunks(2) {
                let left = pair[0];
                let right = *pair.get(1).unwrap_or(&left);
                next.push(hash_pair(&left, &right));
            }
            levels.push(next.clone());
            leaves = next;
        }
        Self { levels }
    }

    pub fn root(&self) -> Hash32 {
        self.levels
            .last()
            .and_then(|l| l.first())
            .copied()
            .unwrap_or([0u8; 32])
    }

    pub fn proof(&self, mut index: usize) -> Option<MerkleProof> {
        if self.levels.first().is_none_or(|l| index >= l.len()) {
            return None;
        }
        let mut steps = Vec::new();
        for level in &self.levels[..self.levels.len().saturating_sub(1)] {
            let is_right = index % 2 == 1;
            let sibling_index = if is_right { index - 1 } else { index + 1 };
            let sibling = *level.get(sibling_index).unwrap_or(&level[index]);
            let direction = if is_right {
                Direction::Left
            } else {
                Direction::Right
            };
            steps.push(ProofStep { sibling, direction });
            index /= 2;
        }
        Some(MerkleProof { steps })
    }
}

pub fn verify_merkle_proof(leaf: Hash32, proof: &MerkleProof, expected_root: &Hash32) -> bool {
    let mut current = leaf;
    for step in &proof.steps {
        current = match step.direction {
            Direction::Left => hash_pair(&step.sibling, &current),
            Direction::Right => hash_pair(&current, &step.sibling),
        };
    }
    &current == expected_root
}
