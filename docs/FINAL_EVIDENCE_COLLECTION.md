# LP-0003 Final Evidence Collection

Status: operator runbook. These helpers are intentionally strict; they should reject weak logs rather than make the submission look ready too early.

## Evidence philosophy

Final LP-0003 claims must be backed by raw logs plus SHA-256 hashes. Prose is not evidence. Safe-lane demos, hand-written IDL, local wrappers, deterministic `.lgx` source packages, and install-only logs are useful development artifacts, but they are not final LEZ/RISC0/Basecamp evidence.

## Basecamp runtime load evidence

Required input: a raw Basecamp runtime log showing the `.lgx` package was actually loaded/activated by Basecamp, not merely built or installed.

Expected signals:

- `Basecamp runtime loaded` or equivalent component-loaded signal
- `loaded_component_id: ...`
- activation/opening signal for the LP-0003 claim UI
- deterministic package present at `dist/lp0003-private-airdrop.lgx`

Command:

```bash
python3 scripts/extract-basecamp-load-evidence.py path/to/basecamp-runtime.log
```

Output:

- `submission/BASECAMP_LOAD_EVIDENCE.json`
- `submission/raw-logs/basecamp-runtime-load.log`

Install/package-only logs are rejected with `install/package-only evidence is not runtime load evidence`.

## LEZ/RISC0 two-distribution / twenty-claim evidence

Required input: a raw LEZ localnet/testnet log, generated with real proof execution for the current source.

Expected signals:

- `evidence_source: lez-risc0-localnet` or `evidence_source: lez-risc0-testnet`
- `RISC0_DEV_MODE=0`
- `program_id: ...`
- sequencer/localnet/testnet context
- block or slot inclusion context
- explicit transaction lines for create and claim actions
- at least two distribution ids
- at least twenty unique accepted claim nullifiers
- at least one duplicate-nullifier rejection

Command:

```bash
python3 scripts/extract-lez-claim-evidence.py path/to/lez-risc0-localnet.log
```

Output:

- `submission/claims/claims-summary.json`
- `submission/raw-logs/lez-risc0-claims.log`

The extractor rejects safe-lane/mock/dev-only logs, ambiguous bare `hash:` labels, and any private witness marker such as `eligible_address`, `claimant_secret`, `leaf_salt`, or `merkle_path`.

## Narrated final demo URL

Attaching the final video updates only the solution draft. It must not flip any LEZ/RISC0/Basecamp gate by itself.

```bash
python3 scripts/attach-final-demo-video.py https://youtu.be/<final-lp0003-demo>
```

Placeholder/pending/old cross-prize URLs are rejected.

## Proof artifact and benchmark evidence

Before the final checker can pass, proof artifacts must be hash-bound and fresh for the current source. Package externally generated `RISC0_DEV_MODE=0` receipt/journal output with:

```bash
python3 scripts/prepare-risc0-proof-artifacts.py \
  --receipt path/to/claim.receipt \
  --journal path/to/claim.journal \
  --raw-log path/to/risc0-proof-generation.log \
  --image-id <64+ hex chars> \
  --command 'RISC0_DEV_MODE=0 cargo run --release -p lp0003-host -- prove-demo'

python3 scripts/validate-proof-artifacts.py submission/proof-artifacts/manifest.json
```

Minimum proof manifest fields:

- `final_proof_evidence: true`
- `risc0_dev_mode: 0`
- `fresh_for_current_source: true`
- `current_source_sha256` matching the tracked source digest
- `image_id`
- `receipt_path` / `receipt_sha256`
- `journal_path` / `journal_sha256`
- `command` containing `RISC0_DEV_MODE=0`

The final checker also requires proof-generation timing evidence in `submission/PROOF_BENCHMARKS.json`. Extract it from the raw proof log with:

```bash
python3 scripts/extract-proof-benchmark.py \
  --log path/to/risc0-proof-generation.log \
  --out submission/PROOF_BENCHMARKS.json \
  --command 'RISC0_DEV_MODE=0 cargo run --release -p lp0003-host -- prove-demo'
```

Minimum fields:

- `final_benchmark_evidence: true`
- `risc0_dev_mode: 0`
- `proof_generation_seconds` greater than zero
- `command` containing `RISC0_DEV_MODE=0`
- `raw_log_sha256` pointing at the raw proof benchmark log

## LEZ compute-unit benchmark evidence

LP-0003 requires compute-unit/cost documentation for on-chain operations. The final checker requires `submission/LEZ_COST_BENCHMARKS.json` to be backed by a raw log and to cover at least:

- `create_distribution`
- `claim`

Extract it with:

```bash
python3 scripts/extract-lez-cost-benchmark.py \
  path/to/lez-cost-benchmark.log \
  --out submission/LEZ_COST_BENCHMARKS.json
```

The raw log should include one `operation:` line per measured operation, for example:

```text
evidence_source: lez-risc0-localnet
sequencer_url: http://127.0.0.1:3040
operation: create_distribution tx_count=2 cu_unavailable_reason=LEZ RPC did not expose per-transaction CU counters
operation: claim tx_count=20 cu_per_tx=12345
```

Minimum fields in the extracted JSON:

- `final_benchmark_evidence: true`
- `evidence_source: lez-risc0-localnet` or `lez-risc0-testnet`
- `operations[]` with `operation`, `tx_count`, and either `cu_per_tx` or `cu_metering_available: false` plus `cu_unavailable_reason`
- `raw_log_sha256` pointing at the raw LEZ benchmark log

Do not invent CU numbers. If the current LEZ surface lacks stable per-transaction CU counters, record the exact unavailable rationale, plus payload sizes, transaction ids, block/slot ids, and sequencer version in the raw log.

## Logos technology issue report

The upstream LP-0003 submission requirements ask for GitHub issues opened for problems encountered with Logos technology. Before final publication, add `submission/LOGOS_TECH_ISSUES.md` with either:

- links to the GitHub issues opened for each Logos technology blocker encountered, or
- an explicit attestation containing `No Logos technology issues were encountered` and `LP-0003 final run` after the final localnet/testnet/Basecamp run is complete.

A vague prose note is intentionally rejected.

## Upstream solution template simulation

Before recording/opening the upstream PR, run the recording preflight and a local structural simulation against the lambda-prize solution template and LP-0003-specific text requirements:

```bash
python3 scripts/final-recording-preflight.py
python3 scripts/validate-upstream-solution.py --allow-do-not-submit
```

The final upstream file must remove the local `DO NOT SUBMIT` banner, at which point the same script should pass without `--allow-do-not-submit`.

## Final verification

After attaching any evidence, run:

```bash
python3 scripts/final-recording-preflight.py
python3 scripts/validate-upstream-solution.py --allow-do-not-submit
python3 scripts/final-publication-check.py
bash scripts/ci-safe-lane.sh
```

`final-publication-check.py` re-hashes raw logs listed in structured evidence files. If a raw log is edited after extraction, the relevant final gate returns to BLOCKER.
