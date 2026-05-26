#!/usr/bin/env bash
set -euo pipefail

SECTION_PAUSE=${SECTION_PAUSE:-2}
SCENE_PAUSE=${SCENE_PAUSE:-4}

pause() { sleep "$1"; }
section() {
  printf '\n========== %s ==========' "$1"
  printf '\n\n'
  pause "$SECTION_PAUSE"
}

section "LP-0003 status gate"
python3 scripts/final-publication-check.py || true
pause "$SCENE_PAUSE"

section "Safe-lane model and SDK tests"
cargo test --workspace
pause "$SCENE_PAUSE"

section "Safe-lane two-distribution demo"
bash demo.sh
pause "$SCENE_PAUSE"

section "Basecamp package validation"
python3 scripts/package-basecamp-lgx.py
python3 scripts/validate-basecamp-native.py
pause "$SCENE_PAUSE"

section "Recording preflight"
python3 scripts/final-recording-preflight.py

section "Final evidence runbook"
printf 'Final recording must add real Basecamp runtime load, RISC0_DEV_MODE=0 proof artifacts, LEZ localnet/testnet logs, proof-generation benchmarks, compute-unit benchmarks, and Logos technology issue reporting.\n'
printf 'See docs/FINAL_EVIDENCE_COLLECTION.md for extractor commands.\n'
