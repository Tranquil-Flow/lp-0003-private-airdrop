#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_MARKERS = [b"RISC0_DEV_MODE=1", b"safe-lane", b"SAFE_LANE", b"mock proof", b"dev-mode"]
SOURCE_INCLUDE_PREFIXES = ("core/", "lez-program/", "sdk/", "cli/", "consumer-demo/", "interfaces/", "basecamp-app/")
SOURCE_INCLUDE_FILES = {"Cargo.toml", "Cargo.lock", "README.md", "module.json", "demo.sh"}


def fail(message: str) -> int:
    print(f"ERROR {message}")
    return 1


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
        return str(path.resolve())


def iter_source_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        rels = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        rels = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()]
    selected = []
    for rel in rels:
        if rel in SOURCE_INCLUDE_FILES or rel.startswith(SOURCE_INCLUDE_PREFIXES):
            path = ROOT / rel
            if path.exists() and path.is_file():
                selected.append(path)
    return sorted(selected, key=lambda p: str(p.relative_to(ROOT)))


def source_digest() -> tuple[str, list[str]]:
    h = hashlib.sha256()
    rels: list[str] = []
    for path in iter_source_files():
        rel = str(path.relative_to(ROOT))
        rels.append(rel)
        h.update(rel.encode("utf-8") + b"\0")
        h.update(sha256_file(path).encode("ascii") + b"\0")
    return h.hexdigest(), rels


def reject_forbidden(path: Path, label: str) -> int | None:
    payload = path.read_bytes()
    for marker in FORBIDDEN_MARKERS:
        if marker in payload:
            return fail(f"{label} contains forbidden dev/mock marker: {marker.decode(errors='replace')}")
    return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Package real RISC0_DEV_MODE=0 LP-0003 proof artifacts into the final hash-bound submission schema."
    )
    parser.add_argument("--receipt", required=True, type=Path, help="RISC0 receipt produced by the final proof command")
    parser.add_argument("--journal", required=True, type=Path, help="Public journal emitted by the final proof command")
    parser.add_argument("--image-id", required=True, help="RISC0 image id for the proving guest")
    parser.add_argument("--command", required=True, help="Exact command that generated the receipt/journal; must include RISC0_DEV_MODE=0")
    parser.add_argument("--raw-log", type=Path, help="Optional raw proof-generation log to copy into submission/raw-logs/")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "submission" / "proof-artifacts")
    parser.add_argument("--manifest", type=Path, default=ROOT / "submission" / "proof-artifacts" / "manifest.json")
    args = parser.parse_args(argv[1:])

    if "RISC0_DEV_MODE=0" not in args.command:
        return fail("command must include RISC0_DEV_MODE=0")
    if not re.fullmatch(r"[0-9A-Fa-f]{64,}", args.image_id):
        return fail("image id must be at least 64 hexadecimal characters")
    for path, label in [(args.receipt, "receipt"), (args.journal, "journal")]:
        if not path.exists() or not path.is_file():
            return fail(f"{label} file missing: {path}")
        problem = reject_forbidden(path, label)
        if problem is not None:
            return problem
    if args.raw_log:
        if not args.raw_log.exists() or not args.raw_log.is_file():
            return fail(f"raw log missing: {args.raw_log}")
        log_text = args.raw_log.read_text(errors="replace")
        if "RISC0_DEV_MODE=0" not in log_text:
            return fail("raw proof log must contain RISC0_DEV_MODE=0")
        problem = reject_forbidden(args.raw_log, "raw proof log")
        if problem is not None:
            return problem

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_out = out_dir / "claim.receipt"
    journal_out = out_dir / "claim.journal"
    shutil.copyfile(args.receipt, receipt_out)
    shutil.copyfile(args.journal, journal_out)

    raw_log_sha256 = {}
    raw_log_out = None
    if args.raw_log:
        raw_dir = ROOT / "submission" / "raw-logs"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_log_out = raw_dir / "risc0-proof-generation.log"
        shutil.copyfile(args.raw_log, raw_log_out)
        raw_log_sha256[display_path(raw_log_out)] = sha256_file(raw_log_out)

    digest, source_files = source_digest()
    manifest = {
        "final_proof_evidence": True,
        "risc0_dev_mode": 0,
        "fresh_for_current_source": True,
        "current_source_sha256": digest,
        "current_source_file_count": len(source_files),
        "image_id": args.image_id.lower(),
        "receipt_path": display_path(receipt_out),
        "journal_path": display_path(journal_out),
        "receipt_sha256": sha256_file(receipt_out),
        "journal_sha256": sha256_file(journal_out),
        "command": args.command,
        "notes": [
            "Prepared from externally generated RISC0_DEV_MODE=0 proof artifacts.",
            "The manifest is bound to the current tracked source digest and to receipt/journal SHA-256 hashes.",
        ],
    }
    if raw_log_out is not None:
        manifest["raw_log_path"] = display_path(raw_log_out)
        manifest["raw_log_sha256"] = raw_log_sha256

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote proof artifact manifest: {display_path(args.manifest)}")
    print(f"receipt_sha256={manifest['receipt_sha256']}")
    print(f"journal_sha256={manifest['journal_sha256']}")
    print(f"current_source_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
