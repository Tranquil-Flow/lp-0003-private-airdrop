#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_seconds(log_text: str, explicit: str | None) -> float | None:
    if explicit is not None:
        try:
            return float(explicit)
        except ValueError:
            return None
    patterns = [
        r"proof_generation_seconds\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)",
        r"proof generation seconds\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)",
        r"proof generated in\s*([0-9]+(?:\.[0-9]+)?)\s*s",
        r"elapsed\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)\s*s",
    ]
    for pattern in patterns:
        m = re.search(pattern, log_text, flags=re.IGNORECASE)
        if m:
            return float(m.group(1))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract LP-0003 proof benchmark evidence from a raw RISC0 proof log.")
    parser.add_argument("--log", required=True, type=Path, help="Raw proof generation log")
    parser.add_argument("--out", required=True, type=Path, help="Output PROOF_BENCHMARKS.json path")
    parser.add_argument("--command", required=True, help="Exact proof-generation command that produced the log")
    parser.add_argument("--seconds", help="Override proof generation seconds if the log format lacks a parseable value")
    args = parser.parse_args()

    if "RISC0_DEV_MODE=0" not in args.command:
        print("ERROR command must include RISC0_DEV_MODE=0")
        return 1
    if not args.log.exists():
        print(f"ERROR raw log missing: {args.log}")
        return 1
    log_text = args.log.read_text(errors="replace")
    if "RISC0_DEV_MODE=0" not in log_text:
        print("ERROR raw proof log must contain RISC0_DEV_MODE=0")
        return 1
    seconds = parse_seconds(log_text, args.seconds)
    if seconds is None or seconds <= 0:
        print("ERROR proof generation seconds missing or non-positive")
        return 1

    data = {
        "final_benchmark_evidence": True,
        "risc0_dev_mode": 0,
        "proof_generation_seconds": seconds,
        "command": args.command,
        "source_log": display_path(args.log),
        "raw_log_sha256": {display_path(args.log): sha256_file(args.log)},
        "notes": [
            "Extracted from raw proof-generation output.",
            "This benchmark file is not sufficient by itself; final readiness also requires proof artifacts, LEZ claim evidence, and demo video evidence.",
        ],
    }

    receipt_match = re.search(r"receipt_sha256\s*[=:]\s*([0-9a-f]{64})", log_text, flags=re.IGNORECASE)
    journal_match = re.search(r"journal_sha256\s*[=:]\s*([0-9a-f]{64})", log_text, flags=re.IGNORECASE)
    if receipt_match:
        data["receipt_sha256"] = receipt_match.group(1).lower()
    if journal_match:
        data["journal_sha256"] = journal_match.group(1).lower()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"wrote proof benchmark evidence: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
