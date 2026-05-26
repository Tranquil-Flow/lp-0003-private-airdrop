import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(script: str, *args: str):
    return subprocess.run(
        ["python3", str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def restore_file(path: Path, previous: str | None):
    if previous is None:
        path.unlink(missing_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(previous)


def test_extract_basecamp_load_evidence_rejects_install_only_log(tmp_path):
    evidence_path = ROOT / "submission" / "BASECAMP_LOAD_EVIDENCE.json"
    previous = evidence_path.read_text() if evidence_path.exists() else None
    package = ROOT / "dist" / "lp0003-private-airdrop.lgx"
    assert package.exists(), "safe-lane package fixture should exist"
    raw_log = tmp_path / "basecamp-install-only.log"
    raw_log.write_text(
        "package installed: dist/lp0003-private-airdrop.lgx\n"
        "package sha256: abcdef\n"
        "no runtime activation happened here\n"
    )

    try:
        result = run_script("extract-basecamp-load-evidence.py", str(raw_log))

        assert result.returncode == 1
        assert "install/package-only evidence is not runtime load evidence" in result.stdout
        if evidence_path.exists():
            data = json.loads(evidence_path.read_text())
            assert data.get("final_load_evidence") is not True
    finally:
        restore_file(evidence_path, previous)


def test_extract_basecamp_load_evidence_accepts_runtime_load_log(tmp_path):
    evidence_path = ROOT / "submission" / "BASECAMP_LOAD_EVIDENCE.json"
    previous = evidence_path.read_text() if evidence_path.exists() else None
    raw_log = tmp_path / "basecamp-runtime.log"
    raw_log.write_text(
        "Basecamp runtime loaded component lp0003-private-airdrop\n"
        "loaded_component_id: lp0003.private_airdrop.component\n"
        "package: dist/lp0003-private-airdrop.lgx\n"
        "activation ok: claim screen opened\n"
    )

    try:
        result = run_script("extract-basecamp-load-evidence.py", str(raw_log))

        assert result.returncode == 0, result.stdout
        assert "wrote submission/BASECAMP_LOAD_EVIDENCE.json" in result.stdout
        data = json.loads(evidence_path.read_text())
        assert data["final_load_evidence"] is True
        assert data["status"] == "basecamp-runtime-loaded"
        assert data["loaded_component_id"] == "lp0003.private_airdrop.component"
        assert data["raw_log_sha256"]
        assert data["package_sha256"]
    finally:
        restore_file(evidence_path, previous)


def test_extract_lez_claim_evidence_rejects_safe_lane_and_bare_hash_labels(tmp_path):
    claims_path = ROOT / "submission" / "claims" / "claims-summary.json"
    previous = claims_path.read_text() if claims_path.exists() else None
    raw_log = tmp_path / "safe-lane.log"
    raw_log.write_text(
        "SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE\n"
        "distribution_id: dist-a\n"
        "claim accepted nullifier: n0 hash: abc\n"
    )

    try:
        result = run_script("extract-lez-claim-evidence.py", str(raw_log))

        assert result.returncode == 1
        assert "safe-lane/mock logs are not final LEZ/RISC0 evidence" in result.stdout
    finally:
        restore_file(claims_path, previous)


def test_extract_lez_claim_evidence_accepts_two_distribution_twenty_claim_runtime_log(tmp_path):
    claims_path = ROOT / "submission" / "claims" / "claims-summary.json"
    previous = claims_path.read_text() if claims_path.exists() else None
    raw_log = tmp_path / "lez-risc0-localnet.log"
    lines = [
        "evidence_source: lez-risc0-localnet",
        "RISC0_DEV_MODE=0",
        "program_id: 9f" + "01" * 31,
        "sequencer_url: http://127.0.0.1:3040",
        "block: 1735",
        "transaction: tx-create-a",
        "create_distribution distribution_id: dist-a",
        "transaction: tx-create-b",
        "create_distribution distribution_id: dist-b",
    ]
    for i in range(20):
        dist = "dist-a" if i < 10 else "dist-b"
        lines.append(f"transaction: tx-claim-{i:02d} claim accepted distribution_id: {dist} nullifier: nf-{i:02d}")
    lines.append("transaction: tx-dup duplicate nullifier rejected distribution_id: dist-a nullifier: nf-00")
    raw_log.write_text("\n".join(lines) + "\n")

    try:
        result = run_script("extract-lez-claim-evidence.py", str(raw_log))

        assert result.returncode == 0, result.stdout
        assert "wrote submission/claims/claims-summary.json" in result.stdout
        data = json.loads(claims_path.read_text())
        assert data["final_evidence"] is True
        assert data["evidence_source"] == "lez-risc0-localnet"
        assert data["distribution_count"] == 2
        assert data["unique_claim_count"] == 20
        assert data["duplicate_rejection_count"] >= 1
        assert data["raw_log_sha256"]
    finally:
        restore_file(claims_path, previous)


def test_attach_final_demo_video_rejects_pending_or_old_placeholder_urls(tmp_path):
    result = run_script("attach-final-demo-video.py", "https://youtu.be/DEMO_PENDING")

    assert result.returncode == 1
    assert "refusing placeholder/pending demo URL" in result.stdout


def test_attach_final_demo_video_updates_solution_draft_without_marking_evidence_ready(tmp_path):
    pr_draft = ROOT / "submission" / "PR_DRAFT.md"
    before = pr_draft.read_text()
    try:
        result = run_script("attach-final-demo-video.py", "https://youtu.be/lp0003-final-demo")
        assert result.returncode == 0, result.stdout
        text = pr_draft.read_text()
        assert "https://youtu.be/lp0003-final-demo" in text
        final = run_script("final-publication-check.py")
        assert (
            "BLOCKER fresh RISC0_DEV_MODE=0 proof artifacts" in final.stdout
            or "PASS fresh RISC0_DEV_MODE=0 proof artifacts" in final.stdout
        )
        assert "BLOCKER 2 distributions / 20 unique claims evidence" in final.stdout
    finally:
        pr_draft.write_text(before)
