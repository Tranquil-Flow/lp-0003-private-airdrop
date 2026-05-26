#!/usr/bin/env bash
set -euo pipefail

missing=0
for cmd in cargo rustc python3; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "PASS $cmd: $(command -v "$cmd")"
  else
    echo "MISSING $cmd"
    missing=1
  fi
done

for cmd in cargo-risczero rzup r0vm lgs spel docker protoc cmake; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "OPTIONAL-PRESENT $cmd: $(command -v "$cmd")"
  else
    echo "OPTIONAL-MISSING $cmd"
  fi
done

exit "$missing"
