import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(name: str, *args: str):
    return subprocess.run(
        ["python3", str(ROOT / "scripts" / name), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_solution_draft_contains_substantive_spec_mapping():
    text = (ROOT / "submission" / "PR_DRAFT.md").read_text()
    required_phrases = [
        "hidden eligibility set commitment",
        "distribution-bound nullifier",
        "Public transcript",
        "Basecamp",
        "SPEL",
        "RISC0_DEV_MODE=0",
        "2 distinct distributions",
        "20 unique claims",
        "Proof-generation benchmark",
        "LEZ compute-unit benchmark",
        "Logos technology issues",
        "DO NOT SUBMIT",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_local_readiness_reports_expected_no_go_blockers():
    result = run_script("validate-submission-readiness.py")
    assert result.returncode == 1
    assert "LP-0003 local readiness: NO-GO" in result.stdout
    assert "PASS core relation implementation" in result.stdout
    assert "PENDING RISC0 proof artifacts" in result.stdout
    assert "PASS LEZ/SPEL integration" in result.stdout
    assert "PASS required documentation skeleton" in result.stdout


def test_final_publication_check_reports_hard_publication_gates():
    result = run_script("final-publication-check.py")
    assert result.returncode == 1
    assert "LP-0003 final publication: NO-GO" in result.stdout
    assert "PASS public repository URL" in result.stdout
    assert "BLOCKER narrated demo video URL" in result.stdout
    assert "BLOCKER Basecamp-loadable app evidence" in result.stdout
    assert "BLOCKER 2 distributions / 20 unique claims evidence" in result.stdout
    assert "BLOCKER fresh RISC0_DEV_MODE=0 proof artifacts" in result.stdout
    assert "BLOCKER proof generation benchmark evidence" in result.stdout
    assert "BLOCKER LEZ compute unit benchmark evidence" in result.stdout
    assert "BLOCKER Logos technology issue report" in result.stdout


def test_final_publication_rejects_weak_benchmark_and_issue_artifacts(tmp_path):
    proof_bench = ROOT / "submission" / "PROOF_BENCHMARKS.json"
    cost_bench = ROOT / "submission" / "LEZ_COST_BENCHMARKS.json"
    issues = ROOT / "submission" / "LOGOS_TECH_ISSUES.md"
    prev_proof = proof_bench.read_text() if proof_bench.exists() else None
    prev_cost = cost_bench.read_text() if cost_bench.exists() else None
    prev_issues = issues.read_text() if issues.exists() else None
    proof_bench.write_text('{"status": "placeholder"}\n')
    cost_bench.write_text('{"operations": []}\n')
    issues.write_text("# Logos Technology Issues\n\nNo links or explicit no-issues attestation.\n")
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "BLOCKER proof generation benchmark evidence" in result.stdout
        assert "BLOCKER LEZ compute unit benchmark evidence" in result.stdout
        assert "BLOCKER Logos technology issue report" in result.stdout
        assert "PASS proof generation benchmark evidence" not in result.stdout
        assert "PASS LEZ compute unit benchmark evidence" not in result.stdout
        assert "PASS Logos technology issue report" not in result.stdout
    finally:
        if prev_proof is None:
            proof_bench.unlink(missing_ok=True)
        else:
            proof_bench.write_text(prev_proof)
        if prev_cost is None:
            cost_bench.unlink(missing_ok=True)
        else:
            cost_bench.write_text(prev_cost)
        if prev_issues is None:
            issues.unlink(missing_ok=True)
        else:
            issues.write_text(prev_issues)


def test_final_publication_rejects_safe_lane_claim_counts_as_final_evidence(tmp_path):
    claims_dir = ROOT / "submission" / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)
    claims_summary = claims_dir / "claims-summary.json"
    previous = claims_summary.read_text() if claims_summary.exists() else None
    claims_summary.write_text(
        '{"distribution_count": 2, "unique_claim_count": 20, '
        '"evidence_source": "safe-lane", "final_evidence": false}\n'
    )
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "BLOCKER 2 distributions / 20 unique claims evidence" in result.stdout
        assert "PASS 2 distributions / 20 unique claims evidence" not in result.stdout
    finally:
        if previous is None:
            claims_summary.unlink(missing_ok=True)
        else:
            claims_summary.write_text(previous)


def test_final_publication_rejects_basecamp_source_package_as_load_evidence(tmp_path):
    evidence_path = ROOT / "submission" / "BASECAMP_LOAD_EVIDENCE.json"
    previous = evidence_path.read_text() if evidence_path.exists() else None
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        '{"package_sha256": "abc", "final_load_evidence": false, '
        '"status": "source-package-only-not-load-evidence"}\n'
    )
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "BLOCKER Basecamp-loadable app evidence" in result.stdout
        assert "PASS Basecamp-loadable app evidence" not in result.stdout
    finally:
        if previous is None:
            evidence_path.unlink(missing_ok=True)
        else:
            evidence_path.write_text(previous)


def test_final_publication_rejects_tampered_basecamp_raw_log_hash(tmp_path):
    evidence_path = ROOT / "submission" / "BASECAMP_LOAD_EVIDENCE.json"
    previous = evidence_path.read_text() if evidence_path.exists() else None
    raw_dir = ROOT / "submission" / "raw-logs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_log = raw_dir / "basecamp-runtime-load.log"
    raw_previous = raw_log.read_text() if raw_log.exists() else None
    raw_log.write_text("Basecamp runtime loaded component lp0003\n")
    evidence_path.write_text(
        '{"final_load_evidence": true, "status": "basecamp-runtime-loaded", '
        '"loaded_component_id": "lp0003.private_airdrop.component", '
        '"raw_log_sha256": {"submission/raw-logs/basecamp-runtime-load.log": "not-real"}}\n'
    )
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "BLOCKER Basecamp-loadable app evidence" in result.stdout
        assert "PASS Basecamp-loadable app evidence" not in result.stdout
    finally:
        if previous is None:
            evidence_path.unlink(missing_ok=True)
        else:
            evidence_path.write_text(previous)
        if raw_previous is None:
            raw_log.unlink(missing_ok=True)
        else:
            raw_log.write_text(raw_previous)


def test_final_publication_rejects_tampered_claim_raw_log_hash(tmp_path):
    claims_dir = ROOT / "submission" / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)
    claims_summary = claims_dir / "claims-summary.json"
    previous = claims_summary.read_text() if claims_summary.exists() else None
    raw_dir = ROOT / "submission" / "raw-logs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_log = raw_dir / "lez-risc0-claims.log"
    raw_previous = raw_log.read_text() if raw_log.exists() else None
    raw_log.write_text("evidence_source: lez-risc0-localnet\n")
    claims_summary.write_text(
        '{"distribution_count": 2, "unique_claim_count": 20, '
        '"evidence_source": "lez-risc0-localnet", "final_evidence": true, '
        '"raw_log_sha256": {"submission/raw-logs/lez-risc0-claims.log": "not-real"}}\n'
    )
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "BLOCKER 2 distributions / 20 unique claims evidence" in result.stdout
        assert "PASS 2 distributions / 20 unique claims evidence" not in result.stdout
    finally:
        if previous is None:
            claims_summary.unlink(missing_ok=True)
        else:
            claims_summary.write_text(previous)
        if raw_previous is None:
            raw_log.unlink(missing_ok=True)
        else:
            raw_log.write_text(raw_previous)


def test_final_publication_rejects_bool_only_proof_manifest(tmp_path):
    manifest = ROOT / "submission" / "proof-artifacts" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    previous = manifest.read_text() if manifest.exists() else None
    manifest.write_text('{"risc0_dev_mode": 0, "fresh_for_current_source": true}\n')
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "BLOCKER fresh RISC0_DEV_MODE=0 proof artifacts" in result.stdout
        assert "PASS fresh RISC0_DEV_MODE=0 proof artifacts" not in result.stdout
    finally:
        if previous is None:
            manifest.unlink(missing_ok=True)
        else:
            manifest.write_text(previous)


def test_validate_proof_artifacts_rejects_missing_receipt_and_journal(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"final_proof_evidence": true, "risc0_dev_mode": 0, '
        '"fresh_for_current_source": true, "image_id": "' + 'ab' * 32 + '", '
        '"receipt_path": "submission/proof-artifacts/missing.receipt", '
        '"journal_path": "submission/proof-artifacts/missing.journal", '
        '"receipt_sha256": "' + '0' * 64 + '", '
        '"journal_sha256": "' + '1' * 64 + '", '
        '"command": "RISC0_DEV_MODE=0 cargo run --release"}\n'
    )

    result = run_script("validate-proof-artifacts.py", str(manifest))

    assert result.returncode == 1
    assert "receipt file missing" in result.stdout


def test_validate_proof_artifacts_accepts_hash_bound_synthetic_schema(tmp_path):
    import hashlib
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    receipt = artifact_dir / "claim.receipt"
    journal = artifact_dir / "claim.journal"
    receipt.write_bytes(b"synthetic receipt bytes with no mock markers")
    journal.write_bytes(b"public journal: distribution_id nullifier recipient_commitment")
    receipt_hash = hashlib.sha256(receipt.read_bytes()).hexdigest()
    journal_hash = hashlib.sha256(journal.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "final_proof_evidence": True,
                "risc0_dev_mode": 0,
                "fresh_for_current_source": True,
                "image_id": "ab" * 32,
                "receipt_path": str(receipt),
                "journal_path": str(journal),
                "receipt_sha256": receipt_hash,
                "journal_sha256": journal_hash,
                "command": "RISC0_DEV_MODE=0 cargo run --release --bin lp0003-prove",
            }
        )
        + "\n"
    )

    result = run_script("validate-proof-artifacts.py", str(manifest))

    assert result.returncode == 0, result.stdout
    assert "PASS proof artifact manifest hash binding" in result.stdout
