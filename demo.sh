#!/usr/bin/env bash
set -euo pipefail

echo "LP-0003 safe-lane demo"
echo "This is NOT final LEZ/RISC0/Basecamp publication evidence."
echo
cargo run -p lp0003-consumer-demo --quiet
echo
python3 scripts/validate-submission-readiness.py || true
