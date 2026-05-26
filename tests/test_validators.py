import importlib.util
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


def test_local_readiness_reports_expected_gate_state():
    result = run_script("validate-submission-readiness.py")
    assert result.returncode in {0, 1}
    assert (
        "LP-0003 local readiness: GO" in result.stdout
        or "LP-0003 local readiness: NO-GO" in result.stdout
    )
    assert "PASS required documentation skeleton" in result.stdout
    assert "PASS core relation implementation" in result.stdout
    assert (
        "PASS RISC0 proof artifacts" in result.stdout
        or "PENDING RISC0 proof artifacts" in result.stdout
    )
    assert "PASS LEZ/SPEL integration" in result.stdout
    assert "PASS root demo.sh exists" in result.stdout

def test_final_publication_check_reports_hard_publication_gates():
    result = run_script("final-publication-check.py")
    assert result.returncode == 1
    assert "LP-0003 final publication: NO-GO" in result.stdout
    assert "PASS public repository URL" in result.stdout
    assert "BLOCKER narrated demo video URL" in result.stdout
    assert (
        "BLOCKER Basecamp-loadable app evidence" in result.stdout
        or "PASS Basecamp-loadable app evidence" in result.stdout
    )
    assert (
        "BLOCKER 2 distributions / 20 unique claims evidence" in result.stdout
        or "PASS 2 distributions / 20 unique claims evidence" in result.stdout
    )
    assert (
        "BLOCKER fresh RISC0_DEV_MODE=0 proof artifacts" in result.stdout
        or "PASS fresh RISC0_DEV_MODE=0 proof artifacts" in result.stdout
    )
    assert (
        "BLOCKER proof generation benchmark evidence" in result.stdout
        or "PASS proof generation benchmark evidence" in result.stdout
    )
    assert (
        "BLOCKER LEZ compute unit benchmark evidence" in result.stdout
        or "PASS LEZ compute unit benchmark evidence" in result.stdout
    )
    assert (
        "BLOCKER Logos technology issue report" in result.stdout
        or "PASS Logos technology issue report" in result.stdout
    )


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


def current_source_digest() -> str:
    validator_path = ROOT / "scripts" / "validate-proof-artifacts.py"
    spec = importlib.util.spec_from_file_location("lp0003_validate_proof_artifacts_for_tests", validator_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.current_source_digest()


def test_validate_proof_artifacts_rejects_missing_receipt_and_journal(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        '{"final_proof_evidence": true, "risc0_dev_mode": 0, '
        '"fresh_for_current_source": true, "current_source_sha256": "' + current_source_digest() + '", '
        '"image_id": "' + 'ab' * 32 + '", '
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
                "current_source_sha256": current_source_digest(),
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



def test_validate_proof_artifacts_rejects_stale_source_digest(tmp_path):
    import hashlib
    receipt = tmp_path / "claim.receipt"
    journal = tmp_path / "claim.journal"
    receipt.write_bytes(b"real receipt shaped bytes")
    journal.write_bytes(b"public journal bytes")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "final_proof_evidence": True,
                "risc0_dev_mode": 0,
                "fresh_for_current_source": True,
                "current_source_sha256": "0" * 64,
                "image_id": "ab" * 32,
                "receipt_path": str(receipt),
                "journal_path": str(journal),
                "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
                "journal_sha256": hashlib.sha256(journal.read_bytes()).hexdigest(),
                "command": "RISC0_DEV_MODE=0 cargo run --release --bin lp0003-prove",
            }
        )
        + "\n"
    )

    result = run_script("validate-proof-artifacts.py", str(manifest))

    assert result.returncode == 1
    assert "stale for current source digest" in result.stdout


def test_prepare_risc0_proof_artifacts_writes_manifest_validated_by_final_schema(tmp_path):
    receipt = tmp_path / "receipt.bin"
    journal = tmp_path / "journal.bin"
    raw_log = tmp_path / "proof.log"
    canonical_raw_log = ROOT / "submission" / "raw-logs" / "risc0-proof-generation.log"
    previous_canonical_raw_log = canonical_raw_log.read_text() if canonical_raw_log.exists() else None
    receipt.write_bytes(b"RISC0 receipt bytes for LP-0003 final lane")
    journal.write_bytes(b"public journal: distribution nullifier recipient_commitment")
    raw_log.write_text("RISC0_DEV_MODE=0\nproof_generation_seconds=9.25\n")
    out_dir = tmp_path / "proof-artifacts"
    manifest = tmp_path / "manifest.json"

    try:
        result = run_script(
            "prepare-risc0-proof-artifacts.py",
            "--receipt",
            str(receipt),
            "--journal",
            str(journal),
            "--raw-log",
            str(raw_log),
            "--image-id",
            "ab" * 32,
            "--command",
            "RISC0_DEV_MODE=0 cargo run --release -p lp0003-host -- prove-demo",
            "--out-dir",
            str(out_dir),
            "--manifest",
            str(manifest),
        )

        assert result.returncode == 0, result.stdout
        data = json.loads(manifest.read_text())
        assert data["final_proof_evidence"] is True
        assert data["current_source_sha256"] == current_source_digest()
        assert Path(data["receipt_path"]).name == "claim.receipt"
        assert Path(data["journal_path"]).name == "claim.journal"
        validation = run_script("validate-proof-artifacts.py", str(manifest))
        assert validation.returncode == 0, validation.stdout
        assert "PASS proof artifact manifest hash binding" in validation.stdout
    finally:
        if previous_canonical_raw_log is None:
            canonical_raw_log.unlink(missing_ok=True)
        else:
            canonical_raw_log.write_text(previous_canonical_raw_log)


def test_prepare_risc0_proof_artifacts_allows_raw_log_already_in_submission_path(tmp_path):
    raw_log = ROOT / "submission" / "raw-logs" / "risc0-proof-generation.log"
    raw_log.parent.mkdir(parents=True, exist_ok=True)
    previous = raw_log.read_text() if raw_log.exists() else None
    receipt = tmp_path / "receipt.bin"
    journal = tmp_path / "journal.bin"
    out_dir = tmp_path / "proof-artifacts"
    manifest = tmp_path / "manifest.json"
    receipt.write_bytes(b"RISC0 receipt bytes for same-file raw log packaging")
    journal.write_bytes(b"public journal bytes only")
    raw_log.write_text("RISC0_DEV_MODE=0\nproof_generation_seconds=1.5\n")
    try:
        result = run_script(
            "prepare-risc0-proof-artifacts.py",
            "--receipt",
            str(receipt),
            "--journal",
            str(journal),
            "--raw-log",
            str(raw_log),
            "--image-id",
            "ab" * 32,
            "--command",
            "RISC0_DEV_MODE=0 RISC0_PROVER=ipc cargo run --manifest-path host/Cargo.toml",
            "--out-dir",
            str(out_dir),
            "--manifest",
            str(manifest),
        )
        assert result.returncode == 0, result.stdout
        data = json.loads(manifest.read_text())
        assert data["raw_log_path"] == "submission/raw-logs/risc0-proof-generation.log"
    finally:
        if previous is None:
            raw_log.unlink(missing_ok=True)
        else:
            raw_log.write_text(previous)


def test_prepare_risc0_proof_artifacts_rejects_non_final_command(tmp_path):
    receipt = tmp_path / "receipt.bin"
    journal = tmp_path / "journal.bin"
    receipt.write_bytes(b"receipt")
    journal.write_bytes(b"journal")

    result = run_script(
        "prepare-risc0-proof-artifacts.py",
        "--receipt",
        str(receipt),
        "--journal",
        str(journal),
        "--image-id",
        "ab" * 32,
        "--command",
        "cargo run --release -p lp0003-host -- prove-demo",
    )

    assert result.returncode == 1
    assert "RISC0_DEV_MODE=0" in result.stdout


def test_upstream_solution_simulation_passes_draft_in_safety_mode():
    result = run_script("validate-upstream-solution.py", "--allow-do-not-submit")
    assert result.returncode == 0, result.stdout
    assert "LP-0003 upstream solution simulation: PASS" in result.stdout


def test_upstream_solution_simulation_rejects_local_safety_banner_without_override():
    result = run_script("validate-upstream-solution.py")
    assert result.returncode == 1
    assert "DO NOT SUBMIT" in result.stdout



def test_final_recording_preflight_passes_workflow_without_final_evidence():
    result = run_script("final-recording-preflight.py")
    assert result.returncode == 0, result.stdout
    assert "LP-0003 final recording preflight: PASS" in result.stdout


def test_attach_final_demo_video_rejects_placeholder_and_supported_url(tmp_path):
    bad = run_script("attach-final-demo-video.py", "https://youtu.be/pending-lp0003-demo")
    assert bad.returncode == 1
    assert "placeholder" in bad.stdout

    pr_draft = ROOT / "submission" / "PR_DRAFT.md"
    previous = pr_draft.read_text()
    try:
        good = run_script("attach-final-demo-video.py", "https://youtu.be/lp0003-final-demo-evidence")
        assert good.returncode == 0, good.stdout
        updated = pr_draft.read_text()
        assert "- **Narrated demo:** https://youtu.be/lp0003-final-demo-evidence" in updated
        final = run_script("final-publication-check.py")
        assert final.returncode in {0, 1}
        assert "PASS narrated demo video URL" in final.stdout
        assert (
            "BLOCKER Basecamp-loadable app evidence" in final.stdout
            or "PASS Basecamp-loadable app evidence" in final.stdout
        )
    finally:
        pr_draft.write_text(previous)


def test_final_publication_accepts_explicit_logos_no_issues_attestation_but_keeps_other_gates():
    issues = ROOT / "submission" / "LOGOS_TECH_ISSUES.md"
    previous = issues.read_text() if issues.exists() else None
    issues.write_text(
        "# Logos Technology Issues\n\n"
        "No Logos technology issues were encountered during the LP-0003 final run.\n"
    )
    try:
        result = run_script("final-publication-check.py")
        assert result.returncode == 1
        assert "PASS Logos technology issue report" in result.stdout
        assert (
            "BLOCKER fresh RISC0_DEV_MODE=0 proof artifacts" in result.stdout
            or "PASS fresh RISC0_DEV_MODE=0 proof artifacts" in result.stdout
        )
    finally:
        if previous is None:
            issues.unlink(missing_ok=True)
        else:
            issues.write_text(previous)


def test_public_transcript_audit_passes_current_public_artifacts():
    result = run_script("audit-public-transcripts.py")
    assert result.returncode == 0, result.stdout
    assert "LP-0003 public transcript audit: PASS" in result.stdout


def test_public_transcript_audit_rejects_private_witness_markers(tmp_path):
    leaked = tmp_path / "public.log"
    leaked.write_text("accepted claim for claimant-secret-7 with leaf-salt-7\n")

    result = run_script("audit-public-transcripts.py", "--path", str(leaked))

    assert result.returncode == 1
    assert "PRIVATE WITNESS MARKER" in result.stdout
    assert "claimant-secret" in result.stdout


def test_private_transcript_model_doc_names_secret_boundary_and_test_gate():
    text = (ROOT / "docs" / "PRIVATE_INPUT_TRANSCRIPT_MODEL.md").read_text()
    required = [
        "Private input / public transcript boundary",
        "eligible address",
        "claimant identity secret",
        "leaf salt",
        "Merkle path siblings",
        "Public LEZ transaction payload",
        "scripts/audit-public-transcripts.py",
        "must not contain",
    ]
    for phrase in required:
        assert phrase in text


def test_ci_metadata_uses_pushable_gitlab_fallback_not_missing_github_only_claim():
    assert (ROOT / ".gitlab-ci.yml").exists()
    spec = (ROOT / "docs" / "SPEC_COMPLIANCE.md").read_text()
    readme = (ROOT / "README.md").read_text()
    assert ".gitlab-ci.yml" in spec
    assert ".gitlab-ci.yml" in readme
    assert "CI safe-lane" in spec


def test_risc0_heavy_lane_scaffold_is_present_and_not_safe_lane_claimed():
    required_files = [
        "methods/Cargo.toml",
        "methods/build.rs",
        "methods/src/lib.rs",
        "methods/guest/Cargo.toml",
        "methods/guest/src/bin/claim_proof.rs",
        "host/Cargo.toml",
        "host/src/lib.rs",
        "host/src/bin/lp0003-risc0-prove-fixture.rs",
        "scripts/run-risc0-heavy-lane.sh",
    ]
    for rel in required_files:
        assert (ROOT / rel).exists(), rel

    guest = (ROOT / "methods" / "guest" / "src" / "bin" / "claim_proof.rs").read_text()
    host = (ROOT / "host" / "src" / "lib.rs").read_text()
    script = (ROOT / "scripts" / "run-risc0-heavy-lane.sh").read_text()
    assert "ClaimGuestInput" in guest
    assert "env::commit(&journal_bytes)" in guest
    assert "RISC0_DEV_MODE=0" in host
    assert "cargo risczero build --manifest-path methods/Cargo.toml" in script
    assert "proof_generation_seconds=" in script
    assert "extract-proof-benchmark.py" in script
    assert "prepare-risc0-proof-artifacts.py" in script


def test_proof_artifact_source_digest_includes_risc0_heavy_lane_sources():
    for script_name in ["prepare-risc0-proof-artifacts.py", "validate-proof-artifacts.py"]:
        text = (ROOT / "scripts" / script_name).read_text()
        assert '"methods/"' in text
        assert '"host/"' in text
        assert '"scripts/"' in text
