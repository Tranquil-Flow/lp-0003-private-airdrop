#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT.parent / "lambda-prize-upstream"

REQUIRED_TEMPLATE_HEADINGS = [
    "## Summary",
    "## Repository",
    "## Approach",
    "## Success Criteria Checklist",
    "## FURPS Self-Assessment",
    "### Functionality",
    "### Usability",
    "### Reliability",
    "### Performance",
    "### Supportability",
    "## Supporting Materials",
    "## Terms & Conditions",
]
LP0003_REQUIRED_PHRASES = [
    "hidden eligibility set",
    "nullifier",
    "on-chain observer",
    "Basecamp",
    "SPEL",
    "IDL",
    "LEZ",
    "RISC0_DEV_MODE=0",
    "2 distinct distributions",
    "20 unique claims",
    "compute-unit",
    "Proof-generation",
    "GitHub issues",
    "MIT OR Apache-2.0",
]
PLACEHOLDER_PATTERNS = [
    r"<https://github\.com/\.\.\.>",
    r"<Your name or team name>",
    r"Criterion \d+: _explanation_",
    r"\bTBD\b",
    r"\bPending\b",
]


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Simulate the lambda-prize solution-template and LP-0003 rejection checks before opening an upstream PR.")
    parser.add_argument("--solution", type=Path, default=ROOT / "submission" / "PR_DRAFT.md")
    parser.add_argument("--upstream", type=Path, default=UPSTREAM)
    parser.add_argument("--allow-do-not-submit", action="store_true", help="Permit the local safety banner while validating draft completeness")
    parser.add_argument("--require-upstream", action="store_true", help="Fail if sibling lambda-prize upstream reference files are missing")
    args = parser.parse_args(argv[1:])

    if not args.solution.exists():
        return fail(f"solution draft missing: {args.solution}")
    text = args.solution.read_text()
    failures: list[str] = []

    for heading in REQUIRED_TEMPLATE_HEADINGS:
        if heading not in text:
            failures.append(f"missing template heading: {heading}")
    if not re.search(r"^# Solution: LP-0003\b", text, flags=re.MULTILINE):
        failures.append("title must start with '# Solution: LP-0003'")
    if not re.search(r"\*\*Submitted by:\*\*\s+\S", text):
        failures.append("submitted-by field is missing")
    if not re.search(r"- \*\*Repo:\*\* https://github\.com/[^\s/]+/[^\s]+", text):
        failures.append("repository link must be a concrete GitHub URL")
    if "DO NOT SUBMIT" in text and not args.allow_do_not_submit:
        failures.append("draft still contains DO NOT SUBMIT safety banner")

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text):
            failures.append(f"placeholder remains: {pattern}")
    for phrase in LP0003_REQUIRED_PHRASES:
        if phrase not in text:
            failures.append(f"missing LP-0003 evidence phrase: {phrase}")

    checklist_lines = [line for line in text.splitlines() if re.match(r"- \[[ xX]\]", line)]
    if len(checklist_lines) < 12:
        failures.append("success criteria checklist is too thin for LP-0003")
    if not any("[ ]" in line for line in checklist_lines):
        failures.append("draft should keep unchecked final evidence gates until final-publication-check passes")
    if not any("[x]" in line.lower() for line in checklist_lines):
        failures.append("draft should mark completed local criteria explicitly")

    readme = args.upstream / "README.md"
    prize = args.upstream / "prizes" / "LP-0003.md"
    template = args.upstream / "solutions" / "LP-0000.md"
    for path in [readme, prize, template]:
        if not path.exists():
            message = f"upstream reference missing: {path}"
            if args.require_upstream:
                failures.append(message)
            else:
                print(f"WARN {message}; skipping sibling-upstream policy cross-check")
    if readme.exists() and "A silent screencast without explanation is not sufficient" not in readme.read_text():
        failures.append("upstream demo narration policy not found")
    if prize.exists() and "GitHub issues open for any problem encountered with Logos technology" not in prize.read_text():
        failures.append("LP-0003 Logos technology issue requirement not found")

    if failures:
        print("LP-0003 upstream solution simulation: NO-GO")
        for item in failures:
            print(f"BLOCKER {item}")
        return 1
    print("LP-0003 upstream solution simulation: PASS")
    print("This is only a structural/template simulation; final evidence still depends on scripts/final-publication-check.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
