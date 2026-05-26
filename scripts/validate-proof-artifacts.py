#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_MARKERS = [b"RISC0_DEV_MODE=1", b"safe-lane", b"SAFE_LANE", b"mock proof", b"dev-mode"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> int:
    print(f"ERROR {message}")
    return 1


def resolve_manifest_path(value: str, manifest_path: Path) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    root_relative = ROOT / p
    if root_relative.exists() or str(p).startswith("submission/"):
        return root_relative
    return manifest_path.parent / p


def validate(manifest_path: Path) -> tuple[bool, str]:
    try:
        data = json.loads(manifest_path.read_text())
    except Exception as exc:
        return False, f"manifest JSON invalid: {exc}"

    if data.get("final_proof_evidence") is not True:
        return False, "manifest is not marked final_proof_evidence=true"
    if data.get("risc0_dev_mode") != 0:
        return False, "manifest must record risc0_dev_mode=0"
    if data.get("fresh_for_current_source") is not True:
        return False, "manifest must be fresh_for_current_source=true"
    if not re.fullmatch(r"[0-9A-Fa-f]{64,}", str(data.get("image_id", ""))):
        return False, "image_id missing or malformed"
    if "RISC0_DEV_MODE=0" not in str(data.get("command", "")):
        return False, "command must include RISC0_DEV_MODE=0"

    for key, hash_key, label in [
        ("receipt_path", "receipt_sha256", "receipt"),
        ("journal_path", "journal_sha256", "journal"),
    ]:
        rel = data.get(key)
        expected = data.get(hash_key)
        if not isinstance(rel, str) or not rel:
            return False, f"{label} path missing"
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            return False, f"{label} sha256 missing or malformed"
        path = resolve_manifest_path(rel, manifest_path)
        if not path.exists():
            return False, f"{label} file missing: {rel}"
        try:
            payload = path.read_bytes()
        except Exception as exc:
            return False, f"{label} file unreadable: {exc}"
        if any(marker in payload for marker in FORBIDDEN_MARKERS):
            return False, f"{label} artifact contains forbidden dev/mock marker"
        actual = hashlib.sha256(payload).hexdigest()
        if actual != expected:
            return False, f"{label} sha256 mismatch"
    return True, "PASS proof artifact manifest hash binding"


def main(argv: list[str]) -> int:
    manifest = Path(argv[1]).resolve() if len(argv) == 2 else ROOT / "submission" / "proof-artifacts" / "manifest.json"
    if not manifest.exists():
        return fail(f"manifest missing: {manifest}")
    ok, message = validate(manifest)
    if not ok:
        return fail(message)
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
