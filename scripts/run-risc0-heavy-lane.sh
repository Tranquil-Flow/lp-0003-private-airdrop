#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="${1:-target/lp0003-risc0-final}"
LOG_DIR="submission/raw-logs"
LOG_PATH="$LOG_DIR/risc0-proof-generation.log"
mkdir -p "$OUT_DIR" "$LOG_DIR"

printf '== LP-0003 RISC0 heavy lane ==\n'
printf 'RISC0_DEV_MODE=0\n'
printf 'output_dir=%s\n' "$OUT_DIR"

if [[ "${RISC0_DEV_MODE:-}" != "0" ]]; then
  export RISC0_DEV_MODE=0
fi
export RISC0_PROVER="${RISC0_PROVER:-ipc}"

{
  printf 'RISC0_DEV_MODE=0\n'
  printf 'RISC0_PROVER=%s\n' "$RISC0_PROVER"
  printf 'command=cargo risczero build --manifest-path methods/Cargo.toml\n'
  cargo risczero build --manifest-path methods/Cargo.toml
  printf 'command=cargo run --manifest-path host/Cargo.toml --bin lp0003-risc0-prove-fixture -- %s\n' "$OUT_DIR"
  proof_start="$(python3 - <<'PY'
import time
print(time.monotonic())
PY
)"
  cargo run --manifest-path host/Cargo.toml --bin lp0003-risc0-prove-fixture -- "$OUT_DIR"
  proof_end="$(python3 - <<'PY'
import time
print(time.monotonic())
PY
)"
  python3 - "$proof_start" "$proof_end" <<'PY'
import sys
start = float(sys.argv[1])
end = float(sys.argv[2])
print(f"proof_generation_seconds={max(end - start, 0.001):.3f}")
PY
} 2>&1 | tee "$LOG_PATH"

image_id="$(awk -F= '/^image_id=/{print $2; exit}' "$LOG_PATH")"
receipt="$(awk -F= '/^receipt_borsh=/{print $2; exit}' "$LOG_PATH")"
journal="$(awk -F= '/^journal_borsh=/{print $2; exit}' "$LOG_PATH")"

python3 scripts/prepare-risc0-proof-artifacts.py \
  --receipt "$receipt" \
  --journal "$journal" \
  --image-id "$image_id" \
  --command "RISC0_DEV_MODE=0 RISC0_PROVER=$RISC0_PROVER cargo run --manifest-path host/Cargo.toml --bin lp0003-risc0-prove-fixture -- $OUT_DIR" \
  --raw-log "$LOG_PATH"

python3 scripts/validate-proof-artifacts.py submission/proof-artifacts/manifest.json
python3 scripts/extract-proof-benchmark.py \
  --log "$LOG_PATH" \
  --out submission/PROOF_BENCHMARKS.json \
  --command "RISC0_DEV_MODE=0 RISC0_PROVER=$RISC0_PROVER cargo run --manifest-path host/Cargo.toml --bin lp0003-risc0-prove-fixture -- $OUT_DIR"
python3 scripts/audit-public-transcripts.py
