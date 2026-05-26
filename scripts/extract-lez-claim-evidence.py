#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "claims" / "claims-summary.json"
RAW_DIR = ROOT / "submission" / "raw-logs"
SECRET_MARKERS = [
    "eligible_address",
    "claimant_secret",
    "leaf_secret",
    "leaf_salt",
    "merkle_path",
    "private witness",
    "witness:",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> int:
    print(f"ERROR {message}")
    return 1


def token_values(pattern: str, text: str) -> set[str]:
    return set(re.findall(pattern, text, flags=re.IGNORECASE))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: extract-lez-claim-evidence.py <raw-lez-risc0-localnet-or-testnet-log>")
        return 2
    src = Path(argv[1]).resolve()
    if not src.exists():
        return fail(f"raw log not found: {src}")
    text = src.read_text(errors="replace")
    lowered = text.lower()

    if any(marker.lower() in lowered for marker in ["safe_lane", "safe-lane", "mock", "dev-only", "not_final"]):
        return fail("safe-lane/mock logs are not final LEZ/RISC0 evidence")
    if re.search(r"(?<!tx-)\bhash\s*:\s*[A-Za-z0-9]+", text, flags=re.IGNORECASE):
        return fail("bare hash: labels are ambiguous; require transaction/sequencer context")
    leaked = [m for m in SECRET_MARKERS if m in lowered]
    if leaked:
        return fail("raw log appears to contain private witness markers: " + ", ".join(leaked))

    source_match = re.search(r"evidence_source\s*[:=]\s*(lez-risc0-localnet|lez-risc0-testnet)", text)
    if not source_match:
        return fail("missing evidence_source: lez-risc0-localnet or lez-risc0-testnet")
    tx_token = r"(?:0x)?[0-9A-Fa-f]{32,128}|[1-9A-HJ-NP-Za-km-z]{32,128}"
    id_token = r"(?:0x)?[0-9A-Fa-f]{32,128}|[1-9A-HJ-NP-Za-km-z]{32,128}"

    if "RISC0_DEV_MODE=0" not in text:
        return fail("missing RISC0_DEV_MODE=0 signal")
    if not re.search(r"\b(program_id|program id)\s*[:=]\s*[0-9A-Fa-f]{32,}", text):
        return fail("missing LEZ program_id signal")
    if not re.search(r"\bsequencer_url\s*[:=]\s*https?://\S+", text, flags=re.IGNORECASE):
        return fail("missing sequencer_url context")
    if not re.search(r"\b(block|slot)\s*[:=]\s*\d+", text, flags=re.IGNORECASE):
        return fail("missing block/slot inclusion context")

    transactions = re.findall(r"\btransaction\s*[:=]\s*(\S+)", text, flags=re.IGNORECASE)
    if not transactions:
        return fail("missing transaction context")
    invalid_txs = [tx for tx in transactions if not re.fullmatch(tx_token, tx)]
    if invalid_txs:
        return fail("transaction ids must be real hash-like localnet/testnet ids, not labels: " + ", ".join(invalid_txs[:3]))

    created = token_values(r"create_distribution\s+distribution_id\s*[:=]\s*(" + id_token + r")", text)
    accepted_pairs = re.findall(
        r"claim accepted\s+distribution_id\s*[:=]\s*(" + id_token + r")\s+nullifier\s*[:=]\s*(" + id_token + r")",
        text,
        flags=re.IGNORECASE,
    )
    accepted_distributions = {dist for dist, _ in accepted_pairs}
    unique_nullifiers = {nullifier for _, nullifier in accepted_pairs}
    duplicate_rejections = re.findall(
        r"transaction\s*[:=]\s*(" + tx_token + r").*duplicate nullifier rejected\s+distribution_id\s*[:=]\s*(" + id_token + r")\s+nullifier\s*[:=]\s*(" + id_token + r")",
        text,
        flags=re.IGNORECASE,
    )

    distributions = created | accepted_distributions
    if len(distributions) < 2:
        return fail("need at least 2 distributions in final evidence")
    if len(unique_nullifiers) < 20:
        return fail("need at least 20 unique accepted claim nullifiers in final evidence")
    if len(accepted_pairs) != len(unique_nullifiers):
        return fail("accepted claim nullifiers are not unique")
    if not duplicate_rejections:
        return fail("missing duplicate-nullifier rejection evidence")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    copied = RAW_DIR / "lez-risc0-claims.log"
    copied.write_text(text)

    data = {
        "final_evidence": True,
        "evidence_source": source_match.group(1),
        "distribution_count": len(distributions),
        "distribution_ids": sorted(distributions),
        "accepted_claim_count": len(accepted_pairs),
        "unique_claim_count": len(unique_nullifiers),
        "duplicate_rejection_count": len(duplicate_rejections),
        "risc0_dev_mode": 0,
        "raw_logs": [str(copied.relative_to(ROOT))],
        "raw_log_sha256": {str(copied.relative_to(ROOT)): sha256_file(copied)},
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "honesty_note": "Accepted only from raw LEZ/RISC0 localnet/testnet logs with RISC0_DEV_MODE=0, tx context, block/slot context, and duplicate rejection evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("wrote submission/claims/claims-summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
