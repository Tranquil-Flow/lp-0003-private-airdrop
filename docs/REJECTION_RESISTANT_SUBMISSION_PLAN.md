# LP-0003 Rejection-Resistant Submission Plan

Status: execution plan for final publication. The repository must remain NO-GO until `python3 scripts/final-publication-check.py` passes and Evi explicitly approves opening the upstream Logos Lambda Prize PR.

## 1. Objective

Submit LP-0003 as a reviewer-proof private allowlist / airdrop distributor, not merely a repository that satisfies local tests. The final submission must prove, with reproducible evidence, that:

1. A distributor commits to a hidden eligibility set.
2. A claimant can prove eligibility without publishing the eligible address, claimant secret, leaf salt, Merkle path, or witness material.
3. Double claims are prevented by distribution-bound nullifiers.
4. The public transcript is unlinkable to a specific eligible address under the documented threat model.
5. The project is usable through SDK/CLI, SPEL/IDL, and a Basecamp-loadable package.
6. Final evidence is backed by raw logs, hashes, RISC0_DEV_MODE=0 proof artifacts, LEZ localnet/testnet transaction context, benchmarks, and a narrated demo.

The moonlit rule: if we cannot prove it from artifacts, we do not claim it in the upstream PR.

## 2. Lessons from earlier Logos Lambda Prize work

### 2.1 Basecamp must be real runtime evidence

LP-0005 taught the hardest lesson: static HTML or module metadata is not enough for Basecamp. For LP-0003, the native/QML package and `.lgx` archive are only partial evidence. Final acceptance needs a raw Basecamp runtime log that shows the package was loaded/activated by Basecamp and that the LP-0003 claim UI opened.

Required final artifacts:

- `dist/lp0003-private-airdrop.lgx`
- `submission/BASECAMP_LOAD_EVIDENCE.json`
- `submission/raw-logs/basecamp-runtime-load.log`
- package hash and raw-log hash

Rejection guard:

- `scripts/extract-basecamp-load-evidence.py` rejects install-only/package-only logs.
- `scripts/final-publication-check.py` blocks final publication without runtime-load evidence.

### 2.2 Local-ready is not submission-ready

Prior work showed that a clone-and-run demo can be impressive but still not final prize evidence. LP-0003 keeps two gates separate:

- Safe-lane readiness: local Rust tests, SDK/CLI demo, docs, Basecamp package source, validators.
- Final publication readiness: public repo, final narrated video, RISC0_DEV_MODE=0 proof artifacts, LEZ localnet/testnet logs, 2 distributions / 20 unique claims, Basecamp runtime evidence, benchmarks, issue report, and upstream solution-template completion.

The safe-lane may pass while the final checker remains NO-GO. That is intentional.

### 2.3 RISC0 proof freshness must be source-bound

A proof receipt can be valid for an older image and still be invalid as final evidence for the current source. The proof manifest must bind to the current source digest and include:

- `final_proof_evidence: true`
- `risc0_dev_mode: 0`
- image id
- receipt path and SHA-256
- journal path and SHA-256
- current source SHA-256
- raw proof-generation log hash
- exact command containing `RISC0_DEV_MODE=0`

After any source changes under proof-relevant paths, rerun the heavy lane.

### 2.4 LEZ transport and compute-unit limits must be stated honestly

If current LEZ tooling cannot transport a full receipt or expose stable per-transaction compute-unit counters, the final submission must say so precisely. Acceptable evidence records compact receipt/journal commitments, transaction ids, block/slot context, payload sizes, and an explicit unavailable rationale. It must not invent CU numbers.

Required final artifacts:

- `submission/claims/claims-summary.json`
- `submission/raw-logs/lez-risc0-claims.log`
- `submission/LEZ_COST_BENCHMARKS.json`
- `submission/raw-logs/lez-cost-benchmarks.log`

### 2.5 Public transcript privacy must be independently auditable

Competing LP-0003 discussion exposed ambiguity around whether private inputs are really private or appear in public transaction payloads. Our submission must make the boundary explicit:

- Private: eligible address/opening, claimant secret, leaf salt, Merkle path, witness material.
- Public: distribution id, Merkle root, fixed allocation, nullifier, recipient commitment, proof context, receipt/journal commitment, transaction inclusion context.

Guardrails:

- docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md names every public/private field.
- `scripts/audit-public-transcripts.py` scans public artifacts for witness markers.
- Final extractors reject logs that contain private witness markers.

### 2.6 Demo video must not overclaim

Earlier final-video work showed that reviewers need to see both the story and the proof. LP-0003's narrated demo must distinguish:

- safe-lane development demo,
- live/fresh RISC0_DEV_MODE=0 proof generation,
- LEZ localnet/testnet evidence extraction,
- Basecamp runtime load evidence,
- final checker output.

The narration should explicitly say what is live, what is pre-generated but hash-bound, and what limitations remain.

## 3. Current state

### Already built / ready for safe-lane

- Rust workspace with core relation, SDK, CLI, consumer demo, and LEZ-shaped state model.
- Privacy-boundary docs and tests.
- Native/QML Basecamp package source and deterministic `.lgx` packaging.
- RISC0 heavy-lane scripts and proof-artifact validators.
- Evidence extractors for Basecamp, LEZ/RISC0 claims, proof benchmarks, and LEZ CU/cost benchmarks.
- Final recording preflight and upstream solution-template simulation.
- Strict final-publication checker.

### Current final blockers, as of the latest M4 Pro evidence run

`python3 scripts/final-publication-check.py` currently reports these blockers after the latest M4 Pro run:

1. Narrated demo video URL.
2. Basecamp runtime-load evidence.
3. Real LEZ/RISC0 two-distribution / twenty-claim evidence.
4. LEZ compute-unit benchmark evidence.

The fresh `RISC0_DEV_MODE=0` proof-artifact gate now passes with `submission/proof-artifacts/manifest.json`, `receipt.borsh`, and `journal.borsh` copied from the M4 Pro heavy lane. Regenerate it again after any proof-relevant source change; the validator is source-digest-bound and will fail closed if stale.

## 4. Final evidence collection sequence

Run these in order. Do not reorder unless a blocker forces a retry; the sequence is designed to avoid stale proof artifacts.

### Step 1: Freeze source and run local safe-lane

Command:

```bash
bash scripts/ci-safe-lane.sh
python3 scripts/final-recording-preflight.py
python3 scripts/validate-upstream-solution.py --allow-do-not-submit
```

Expected result:

- safe-lane passes;
- final-recording preflight passes;
- upstream simulation passes in DO-NOT-SUBMIT mode.

If source changes after Step 1, repeat Step 1 and Step 2.

### Step 2: Regenerate final RISC0 proof artifacts on the M4 Pro

Preferred command:

```bash
RISC0_DEV_MODE=0 bash scripts/run-risc0-heavy-lane.sh
```

Acceptance criteria:

- raw proof log includes the exact command and `RISC0_DEV_MODE=0`;
- `submission/proof-artifacts/manifest.json` validates;
- `submission/PROOF_BENCHMARKS.json` validates;
- final checker still passes the proof and proof-benchmark gates.

If the heavy lane fails, do not substitute dev-mode evidence. Fix or document a true Logos/RISC0 blocker and open an issue if appropriate.

### Step 3: Capture Basecamp runtime-load evidence

Operator action:

1. Open Logos Basecamp.
2. Load/install `dist/lp0003-private-airdrop.lgx`.
3. Activate the LP-0003 component.
4. Open the claim/distribution UI flow.
5. Save the raw Basecamp runtime log.

Extraction command:

```bash
python3 scripts/extract-basecamp-load-evidence.py path/to/basecamp-runtime.log
```

Acceptance criteria:

- log contains runtime-load and activation/opening signals;
- log contains `loaded_component_id: ...`;
- extractor writes `submission/BASECAMP_LOAD_EVIDENCE.json`;
- final checker passes the Basecamp gate.

Do not use a hand-written log, install-only log, or package hash output as final Basecamp evidence.

### Step 4: Capture LEZ/RISC0 localnet or testnet claim evidence

Operator action:

1. Start and verify the LEZ localnet/testnet/sequencer environment. On the M4 Pro scaffold toolchain, the known commands are:

```bash
lgs doctor --json
lgs localnet reset
lgs localnet status --json
lgs localnet logs > target/lp0003-risc0-final/localnet-before.log
```

2. Deploy or register the LP-0003 program/wrapper. If the project is wired through `scaffold.toml`, prefer `lgs run --reset --localnet-timeout 180`. If deploying a built program ELF directly, use `lgs deploy --program-path <program-elf> --json` and save the JSON output.
3. Run two distributions with ten successful claims each.
4. Submit at least one duplicate-nullifier claim and confirm rejection.
5. Save the raw log including evidence source, RISC0_DEV_MODE=0, program id, transaction ids, block/slot context, accepted claims, and duplicate rejection.

Extraction command:

```bash
python3 scripts/extract-lez-claim-evidence.py path/to/lez-risc0-localnet.log
```

Acceptance criteria:

- `evidence_source: lez-risc0-localnet` or `lez-risc0-testnet`;
- `RISC0_DEV_MODE=0`;
- program id and sequencer/testnet context;
- block or slot inclusion context;
- at least 2 distributions;
- at least 20 unique accepted nullifiers;
- duplicate-nullifier rejection;
- no private witness markers;
- final checker passes the 2-distribution / 20-claim gate.

### Step 5: Capture LEZ compute-unit / cost benchmark evidence

Command:

```bash
python3 scripts/extract-lez-cost-benchmark.py path/to/lez-cost-benchmark.log --out submission/LEZ_COST_BENCHMARKS.json
```

Acceptance criteria:

- `create_distribution` and `claim` operation lines;
- positive `tx_count` for each operation;
- either measured `cu_per_tx` or explicit `cu_unavailable_reason`;
- raw-log hash matches;
- final checker passes the LEZ compute-unit benchmark gate.

If CU counters are unavailable, include exact LEZ version/tooling context and open a Logos issue if it is a tooling gap.

### Step 6: Update Logos technology issue report

If any Logos technology blocker was encountered, open/link the issue(s) in `submission/LOGOS_TECH_ISSUES.md`.

If no issues were encountered in the final run, include both exact phrases:

- `No Logos technology issues were encountered`
- `LP-0003 final run`

Do this only after the final LEZ/Basecamp/RISC0 run is complete.

### Step 7: Record and attach final narrated demo

Use:

```bash
bash scripts/demo-video.sh
```

Narration must cover:

- what LP-0003 implements;
- public/private transcript boundary;
- fixed allocation privacy decision;
- RISC0_DEV_MODE=0 proof generation and artifact hashes;
- LEZ localnet/testnet transaction evidence;
- 2 distributions / 20 unique claims;
- duplicate-nullifier rejection;
- Basecamp runtime load;
- benchmarks and limitations;
- final checker output.

Attach the final URL:

```bash
python3 scripts/attach-final-demo-video.py https://youtu.be/<final-lp0003-demo>
```

### Step 8: Final gate and Evi approval

Run:

```bash
python3 scripts/final-recording-preflight.py
python3 scripts/validate-upstream-solution.py --allow-do-not-submit
python3 scripts/final-publication-check.py
bash scripts/ci-safe-lane.sh
```

Only after `final-publication-check.py` passes:

1. remove the local DO-NOT-SUBMIT banner from the upstream solution draft;
2. rerun `python3 scripts/validate-upstream-solution.py` without `--allow-do-not-submit`;
3. present the exact diff and final command output to Evi;
4. wait for explicit Evi approval before opening the upstream PR.

## 5. Reviewer-facing quality bar

Before publication, the answer to every question below must be yes:

1. Can a reviewer clone the repo and run the safe-lane demo without secret setup?
2. Can a reviewer see exactly which final artifacts came from real RISC0_DEV_MODE=0 runs?
3. Are all raw evidence logs hash-bound?
4. Does the Basecamp evidence prove runtime load, not just packaging?
5. Does LEZ evidence include transaction and block/slot context?
6. Are there 20 unique accepted nullifiers across at least two distributions?
7. Is duplicate claiming visibly rejected?
8. Are private witness markers absent from public artifacts?
9. Are CU/cost numbers measured or explicitly marked unavailable with reason?
10. Does the narrated demo match the docs and not overclaim?
11. Does the upstream solution draft contain no placeholders, pending language, or stale NO-GO text?
12. Has Evi explicitly approved opening the PR?

## 6. Do-not-submit conditions

Do not submit if any of these are true:

- `scripts/final-publication-check.py` reports any blocker.
- Basecamp evidence is package/install-only.
- LEZ evidence is safe-lane/local fixture only.
- Proof artifacts are stale for current source.
- CU values are invented.
- The video is missing or uses placeholder/pending URL text.
- Public artifacts expose eligible addresses, secrets, salts, Merkle paths, or witness material.
- Upstream PR approval from Evi has not been explicitly given.

This is the spell circle. No final claim leaves it unless the evidence glows.
