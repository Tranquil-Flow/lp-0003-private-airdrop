#!/usr/bin/env bash
set -euo pipefail

printf '== LP-0003 safe-lane CI ==\n'

printf '\n== format ==\n'
cargo fmt --all --check

printf '\n== rust tests ==\n'
cargo test --workspace

printf '\n== python tests ==\n'
python3 -m pytest tests -q --ignore=tests/test_ci_safe_lane.py

printf '\n== Basecamp native source package ==\n'
python3 scripts/validate-basecamp-native.py

printf '\n== public transcript privacy audit ==\n'
python3 scripts/audit-public-transcripts.py

printf '\n== local readiness (expected NO-GO until proof artifacts exist) ==\n'
set +e
local_output=$(python3 scripts/validate-submission-readiness.py 2>&1)
local_status=$?
set -e
printf '%s\n' "$local_output"
if [[ $local_status -ne 0 ]] && grep -q 'PENDING RISC0 proof artifacts' <<<"$local_output"; then
  printf 'PASS local readiness remains honestly blocked on RISC0 proof artifacts\n'
elif [[ $local_status -eq 0 ]]; then
  printf 'PASS local readiness validator passed\n'
else
  printf 'FAIL unexpected local readiness output\n' >&2
  exit 1
fi

printf '\n== final publication gate (must remain NO-GO without final evidence) ==\n'
set +e
final_output=$(python3 scripts/final-publication-check.py 2>&1)
final_status=$?
set -e
printf '%s\n' "$final_output"
if [[ $final_status -ne 0 ]] && grep -q 'LP-0003 final publication: NO-GO' <<<"$final_output"; then
  printf 'PASS final publication gate remains NO-GO\n'
else
  printf 'FAIL final publication gate unexpectedly passed or did not report NO-GO\n' >&2
  exit 1
fi
