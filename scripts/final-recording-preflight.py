#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_RECORDING_FILES = [
    "docs/DEMO_VIDEO_SCRIPT.md",
    "docs/FINAL_EVIDENCE_COLLECTION.md",
    "scripts/demo-video.sh",
    "scripts/attach-final-demo-video.py",
    "scripts/prepare-risc0-proof-artifacts.py",
    "scripts/extract-basecamp-load-evidence.py",
    "scripts/extract-lez-claim-evidence.py",
    "scripts/extract-proof-benchmark.py",
    "scripts/extract-lez-cost-benchmark.py",
    "scripts/final-publication-check.py",
]
REQUIRED_SCRIPT_PHRASES = [
    "Narrate",
    "RISC0_DEV_MODE=0",
    "Basecamp runtime load",
    "2 distributions",
    "twenty unique",
    "duplicate-nullifier",
    "proof-generation",
    "compute unit",
    "final-publication-check.py",
]


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(ROOT / "scripts" / name), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_RECORDING_FILES:
        if not (ROOT / rel).exists():
            failures.append(f"missing recording workflow file: {rel}")

    script_text = (ROOT / "docs" / "DEMO_VIDEO_SCRIPT.md").read_text() if (ROOT / "docs" / "DEMO_VIDEO_SCRIPT.md").exists() else ""
    for phrase in REQUIRED_SCRIPT_PHRASES:
        if phrase not in script_text:
            failures.append(f"demo script missing recording cue: {phrase}")

    attach = run_script("attach-final-demo-video.py", "https://example.com/not-a-supported-video")
    if attach.returncode == 0 or "supported https video URL" not in attach.stdout:
        failures.append("attach-final-demo-video.py did not reject unsupported demo URL")

    upstream = run_script("validate-upstream-solution.py", "--allow-do-not-submit")
    if upstream.returncode != 0:
        failures.append("upstream solution simulation does not pass in safety mode")

    pr_text = (ROOT / "submission" / "PR_DRAFT.md").read_text() if (ROOT / "submission" / "PR_DRAFT.md").exists() else ""
    if "DO NOT SUBMIT" not in pr_text:
        failures.append("local PR draft safety banner missing before final evidence")
    if re.search(r"^- \*\*Narrated demo:\*\* https://", pr_text, flags=re.MULTILINE) and "DO NOT SUBMIT" in pr_text:
        # This is not fatal by itself; users may attach a private draft URL. We only remind.
        print("WARN narrated demo URL is present while safety banner remains; final publication still requires all evidence gates")

    if failures:
        print("LP-0003 final recording preflight: NO-GO")
        for item in failures:
            print(f"BLOCKER {item}")
        return 1
    print("LP-0003 final recording preflight: PASS")
    print("Recording workflow is ready; final publication still requires real evidence and Evi approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
