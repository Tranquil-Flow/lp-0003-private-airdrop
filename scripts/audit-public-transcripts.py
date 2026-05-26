#!/usr/bin/env python3
"""Audit evaluator-facing public transcript artifacts for private witness leaks.

This intentionally scans only public/evaluator-facing artifacts, not source code or
protocol prose where words like "secret" are expected. It catches concrete fixture
markers and forbidden witness-shaped field names before a final bundle can glow too
brightly in the wrong places.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_PUBLIC_PATHS = [
    ROOT / "submission" / "raw-logs",
    ROOT / "submission" / "claims",
    ROOT / "submission" / "BASECAMP_LOAD_EVIDENCE.json",
    ROOT / "submission" / "PROOF_BENCHMARKS.json",
    ROOT / "submission" / "LEZ_COST_BENCHMARKS.json",
    ROOT / "submission" / "proof-artifacts" / "manifest.json",
    ROOT / "dist" / "lp0003-private-airdrop.lgx.manifest.json",
]

# Concrete marker prefixes used by fixtures/tests plus forbidden public-field
# labels that would indicate a witness, not merely a commitment/transcript field.
FORBIDDEN_MARKERS = [
    "claimant-secret",
    "leaf-salt",
    "eligible-address",
    "raw-eligible-address",
    "raw_claimant_address",
    "claimant_identity_secret",
    "private_witness",
    "witness_marker",
    "merkle_path_siblings",
    "leaf_secret",
]

TEXT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".txt",
    ".manifest",
}


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and (child.suffix in TEXT_SUFFIXES or ".manifest" in child.name):
                files.append(child)
    return sorted(files)


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def audit(paths: list[Path]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for path in iter_files(paths):
        try:
            text = path.read_text(errors="replace")
        except UnicodeDecodeError:
            continue
        lowered = text.lower()
        for marker in FORBIDDEN_MARKERS:
            if marker.lower() in lowered:
                failures.append(f"PRIVATE WITNESS MARKER {marker} in {display_path(path)}")
    return (not failures, failures)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit LP-0003 public transcript artifacts for private witness leaks")
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Public artifact path to audit. May be passed more than once. Defaults to submission/dist public artifacts.",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in args.path] if args.path else DEFAULT_PUBLIC_PATHS
    ok, failures = audit(paths)
    if ok:
        print("LP-0003 public transcript audit: PASS")
        print(f"Scanned {len(iter_files(paths))} public artifact file(s)")
        return 0
    print("LP-0003 public transcript audit: FAIL")
    for failure in failures:
        print(failure)
    return 1


if __name__ == "__main__":
    sys.exit(main())
