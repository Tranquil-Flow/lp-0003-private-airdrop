#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "submission" / "LEZ_COST_BENCHMARKS.json"
RAW_DIR = ROOT / "submission" / "raw-logs"
REQUIRED_OPS = {"create_distribution", "claim"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def root_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_operation(line: str) -> dict | None:
    m = re.search(r"operation:\s*([A-Za-z0-9_:-]+)", line, flags=re.IGNORECASE)
    if not m:
        return None
    op = {"operation": m.group(1)}
    tx = re.search(r"tx_count\s*[=:]\s*(\d+)", line, flags=re.IGNORECASE)
    if tx:
        op["tx_count"] = int(tx.group(1))
    cu = re.search(r"cu_per_tx\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)", line, flags=re.IGNORECASE)
    if cu:
        value = float(cu.group(1)) if "." in cu.group(1) else int(cu.group(1))
        op["cu_per_tx"] = value
        op["cu_metering_available"] = True
    reason = re.search(r"cu_unavailable_reason\s*[=:]\s*(.+)$", line, flags=re.IGNORECASE)
    if reason:
        op["cu_metering_available"] = False
        op["cu_unavailable_reason"] = reason.group(1).strip()
    return op


def fail(message: str) -> int:
    print(f"ERROR {message}")
    return 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Extract LP-0003 LEZ compute/cost benchmark evidence from a raw localnet/testnet log.")
    parser.add_argument("log", type=Path, help="Raw LEZ benchmark log")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output LEZ_COST_BENCHMARKS.json path")
    args = parser.parse_args(argv[1:])

    if not args.log.exists():
        return fail(f"raw log missing: {args.log}")
    text = args.log.read_text(errors="replace")
    source_match = re.search(r"evidence_source\s*[:=]\s*(lez-risc0-localnet|lez-risc0-testnet)", text)
    if not source_match:
        return fail("missing evidence_source: lez-risc0-localnet or lez-risc0-testnet")

    operations = [op for line in text.splitlines() if (op := parse_operation(line)) is not None]
    op_names = {op.get("operation") for op in operations}
    missing = sorted(REQUIRED_OPS - op_names)
    if missing:
        return fail("missing required operation benchmark(s): " + ", ".join(missing))

    for op in operations:
        if not isinstance(op.get("tx_count"), int) or op["tx_count"] <= 0:
            return fail(f"operation {op.get('operation')} missing positive tx_count")
        if "cu_per_tx" not in op:
            reason = op.get("cu_unavailable_reason")
            if op.get("cu_metering_available") is not False or not isinstance(reason, str) or len(reason) < 12:
                return fail(f"operation {op.get('operation')} missing cu_per_tx or explicit cu_unavailable_reason")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    copied = RAW_DIR / "lez-cost-benchmarks.log"
    copied.write_text(text)
    sequencer = re.search(r"sequencer_url\s*[:=]\s*(\S+)", text)
    data = {
        "final_benchmark_evidence": True,
        "evidence_source": source_match.group(1),
        "operations": operations,
        "raw_logs": [root_rel(copied)],
        "raw_log_sha256": {root_rel(copied): sha256_file(copied)},
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "honesty_note": "CU values are recorded only when exposed by LEZ logs. If unavailable, this artifact records an explicit unavailable rationale instead of inventing gas/CU numbers.",
    }
    if sequencer:
        data["sequencer_url"] = sequencer.group(1)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"wrote LEZ cost benchmark evidence: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
