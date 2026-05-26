import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def discriminator(name: str):
    return list(hashlib.sha256(f"global:{name}".encode()).digest()[:8])


def test_spel_idl_has_required_lp0003_instruction_surface():
    idl_path = ROOT / "interfaces" / "lp0003.idl.json"
    assert idl_path.exists(), "LP-0003 must ship a parseable SPEL IDL JSON artifact"
    idl = json.loads(idl_path.read_text())

    assert idl["name"] == "lp0003_private_airdrop"
    assert idl["version"] == "0.1.0"

    instructions = {ix["name"]: ix for ix in idl["instructions"]}
    assert set(instructions) >= {
        "create_distribution",
        "claim",
        "query_distribution",
        "query_claim_nullifier",
    }

    assert instructions["create_distribution"]["discriminator"] == discriminator("create_distribution")
    assert instructions["claim"]["discriminator"] == discriminator("claim")
    assert instructions["claim"]["execution"] == "private"
    assert instructions["create_distribution"]["execution"] == "public"

    claim_args = {arg["name"] for arg in instructions["claim"]["args"]}
    assert {
        "distribution_id",
        "merkle_root",
        "nullifier",
        "recipient_commitment",
        "allocation",
        "proof_context",
        "receipt_sha256",
        "journal_sha256",
        "receipt_journal_commitment",
    } <= claim_args


def test_human_readable_spel_declares_private_claim_without_witness_fields():
    spel_path = ROOT / "interfaces" / "lp0003.spel"
    assert spel_path.exists(), "LP-0003 must ship a human-readable SPEL surface"
    text = spel_path.read_text()
    assert "private instruction claim" in text
    assert "public instruction create_distribution" in text
    forbidden_public_witness_terms = [
        "claimant_secret",
        "leaf_salt",
        "merkle_path",
        "eligible_address",
    ]
    for term in forbidden_public_witness_terms:
        assert term not in text
