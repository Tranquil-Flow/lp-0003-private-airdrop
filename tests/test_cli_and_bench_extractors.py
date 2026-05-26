import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PATH": f"/root/.cargo/bin:{os.environ.get('PATH', '')}"}


def test_cli_writes_safe_lane_claim_summary(tmp_path):
    out = tmp_path / "claims-summary.json"
    result = subprocess.run(
        [
            "cargo",
            "run",
            "-p",
            "lp0003-cli",
            "--quiet",
            "--",
            "safe-lane-evidence",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=ENV,
    )

    assert result.returncode == 0, result.stdout
    assert "wrote safe-lane evidence" in result.stdout
    data = json.loads(out.read_text())
    assert data["distribution_count"] == 2
    assert data["unique_claim_count"] == 20
    assert data["duplicate_rejections_observed"] == 2
    assert data["evidence_source"] == "safe-lane"
    assert data["final_evidence"] is False
    assert data["status"] == "SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE"


def test_extract_proof_benchmark_rejects_missing_risc0_dev_mode(tmp_path):
    log = tmp_path / "proof.log"
    log.write_text("proof_generation_seconds=12.5\n")
    out = tmp_path / "bench.json"
    result = subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "extract-proof-benchmark.py"),
            "--log",
            str(log),
            "--out",
            str(out),
            "--command",
            "cargo run --release",
            "--seconds",
            "12.5",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=ENV,
    )

    assert result.returncode == 1
    assert "RISC0_DEV_MODE=0" in result.stdout
    assert not out.exists()


def test_extract_proof_benchmark_writes_hash_bound_final_schema(tmp_path):
    log = tmp_path / "proof.log"
    log.write_text(
        "RISC0_DEV_MODE=0\n"
        "proof_generation_seconds=12.5\n"
        "receipt_sha256=" + "a" * 64 + "\n"
        "journal_sha256=" + "b" * 64 + "\n"
    )
    out = tmp_path / "bench.json"
    result = subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "extract-proof-benchmark.py"),
            "--log",
            str(log),
            "--out",
            str(out),
            "--command",
            "RISC0_DEV_MODE=0 cargo run --release -p lp0003-host -- prove-demo",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=ENV,
    )

    assert result.returncode == 0, result.stdout
    data = json.loads(out.read_text())
    assert data["final_benchmark_evidence"] is True
    assert data["risc0_dev_mode"] == 0
    assert data["proof_generation_seconds"] == 12.5
    assert data["command"].startswith("RISC0_DEV_MODE=0")
    assert Path(data["source_log"]).name == log.name
    assert list(data["raw_log_sha256"].values()) == [hashlib.sha256(log.read_bytes()).hexdigest()]
