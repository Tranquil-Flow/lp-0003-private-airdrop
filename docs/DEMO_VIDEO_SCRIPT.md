# LP-0003 Demo Video Script

Status: recording plan. Do not film as final until real RISC0/LEZ/Basecamp evidence exists.

## Recording principles

- Narrate honestly: safe-lane local execution is not final LEZ/RISC0 evidence.
- Show `RISC0_DEV_MODE=0` only in the heavy/final proof lane, never as part of the safe-lane demo unless the command truly runs real proofs.
- Show Basecamp runtime load if available; package generation alone is only source/package evidence.
- Keep the final video under roughly 12 minutes.

## Scene 1 — Project and status

Open with the repo root and state:

```bash
python3 scripts/final-publication-check.py || true
```

Explain that the final checker is strict and blocks any missing evidence.

## Scene 2 — Safe-lane relation and SDK

```bash
cargo test --workspace
bash demo.sh
```

Narration cue: this proves hidden eligibility commitments, distribution-bound nullifiers, 2 distributions / 20 safe-lane claims, and duplicate rejection in the deterministic model.

## Scene 3 — Basecamp package / runtime

Source/package validation:

```bash
python3 scripts/package-basecamp-lgx.py
python3 scripts/validate-basecamp-native.py
```

Final recording must additionally show Basecamp loading/activating the `.lgx` package and then run:

```bash
python3 scripts/extract-basecamp-load-evidence.py path/to/basecamp-runtime.log
```

## Scene 4 — RISC0/LEZ final evidence

Final recording must show the real heavy lane, including `RISC0_DEV_MODE=0`, LEZ localnet/testnet transaction context, two distribution creations, twenty unique claims, one duplicate-nullifier rejection, proof-generation timing, and LEZ compute unit / compute-unit benchmark evidence.

After raw log capture:

```bash
python3 scripts/prepare-risc0-proof-artifacts.py \
  --receipt path/to/claim.receipt \
  --journal path/to/claim.journal \
  --raw-log path/to/risc0-proof-generation.log \
  --image-id <64+ hex chars> \
  --command 'RISC0_DEV_MODE=0 cargo run --release -p lp0003-host -- prove-demo'
python3 scripts/extract-proof-benchmark.py \
  --log path/to/risc0-proof-generation.log \
  --out submission/PROOF_BENCHMARKS.json \
  --command 'RISC0_DEV_MODE=0 cargo run --release -p lp0003-host -- prove-demo'
python3 scripts/extract-lez-claim-evidence.py path/to/lez-risc0-localnet.log
python3 scripts/extract-lez-cost-benchmark.py path/to/lez-cost-benchmark.log \
  --out submission/LEZ_COST_BENCHMARKS.json
python3 scripts/validate-proof-artifacts.py submission/proof-artifacts/manifest.json
```

## Scene 5 — Logos issue report and final gate

After the final run, add `submission/LOGOS_TECH_ISSUES.md` with GitHub issue links for encountered Logos technology problems, or an explicit final-run no-issues attestation if none occurred.


```bash
python3 scripts/final-publication-check.py
```

Only a PASS here, plus Evi approval, should precede public repo push or upstream Lambda Prize PR creation.
