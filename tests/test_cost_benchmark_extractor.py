import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_extract_lez_cost_benchmark_requires_required_operations(tmp_path):
    log = tmp_path / "cost.log"
    log.write_text(
        "evidence_source: lez-risc0-localnet\n"
        "operation: create_distribution tx_count=2 cu_unavailable_reason=LEZ RPC did not expose per-transaction CU counters\n"
    )
    out = tmp_path / "cost.json"
    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "extract-lez-cost-benchmark.py"), str(log), "--out", str(out)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 1
    assert "claim" in result.stdout
    assert not out.exists()


def test_extract_lez_cost_benchmark_writes_hash_bound_schema(tmp_path):
    log = tmp_path / "cost.log"
    log.write_text(
        "evidence_source: lez-risc0-localnet\n"
        "sequencer_url: http://127.0.0.1:3040\n"
        "operation: create_distribution tx_count=2 cu_unavailable_reason=LEZ RPC did not expose per-transaction CU counters\n"
        "operation: claim tx_count=20 cu_per_tx=12345\n"
    )
    out = tmp_path / "cost.json"
    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "extract-lez-cost-benchmark.py"), str(log), "--out", str(out)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout
    data = json.loads(out.read_text())
    assert data["final_benchmark_evidence"] is True
    assert data["evidence_source"] == "lez-risc0-localnet"
    operations = {op["operation"]: op for op in data["operations"]}
    assert operations["create_distribution"]["cu_metering_available"] is False
    assert operations["claim"]["cu_per_tx"] == 12345
    assert len(next(iter(data["raw_log_sha256"].values()))) == 64
