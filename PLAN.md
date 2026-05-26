# LP-0003 Private Allowlist / Airdrop Distributor Plan

Status: DRAFT / BUILD PLAN
Date: 2026-05-26
Owner: Tranquil-Flow
Working path: /workspace/Projects/logos-basecamp/lp-0003-private-airdrop
Public repo target: https://github.com/Tranquil-Flow/lp-0003-private-airdrop (do not create/push/open PR without explicit approval)
Prize spec source: /workspace/Projects/logos-basecamp/lambda-prize-upstream/prizes/LP-0003.md

## 0. North Star

Build a Lambda Prize submission that is manually reviewer-proof, not merely bot-valid.

LP-0003 asks for a private airdrop / allowlist primitive on LEZ where:

1. A distributor commits to a hidden eligibility set on-chain.
2. Eligible recipients claim without revealing which eligible address they hold.
3. Double claims are impossible via nullifiers or equivalent.
4. Observers cannot link a claim to a specific eligible address.
5. The implementation includes SDK/CLI, SPEL IDL, Basecamp-loadable GUI, LEZ testnet/localnet evidence, CI, docs, benchmarks, 2 distributions, 20 unique claims, and a narrated demo showing RISC0_DEV_MODE=0 proof generation.

The quality bar is higher than the automated upstream validator. Our final gate must fail until exact spec evidence exists.

## 1. Lessons to Bake In From Prior Submissions

### 1.1 LP-0005 rejection lesson: static HTML is not Basecamp

A browser-openable static app plus module.json is not enough. For LP-0003, Basecamp must be treated as a first-class deliverable:

- Build a real LogosBasecamp-loadable app or package.
- Prefer native/QML/Qt plugin shape and .lgx packaging, mirroring the improved LP-0005/LP-0002 patterns.
- Include Basecamp build instructions, downloadable/reproducible assets, and load/open evidence.
- Keep static HTML only as supplementary documentation if present; never mark it PASS for Basecamp compliance.

Final gate requirement:

- scripts/final-publication-check.py must fail if Basecamp evidence is only static HTML or only module metadata.

### 1.2 Local-ready is not submission-ready

A passing local validator is not enough. LP-0003 must separate:

- local implementation readiness: workspace builds, tests pass, root demo.sh works, docs parse.
- final publication readiness: public repo URL, narrated video URL, clean CI, Basecamp load evidence, LEZ deployment/evidence, 2 distributions / 20 claims, proof/benchmark artifacts, exact solution template.

Deliver both validators:

- scripts/validate-submission-readiness.py: local implementation readiness.
- scripts/final-publication-check.py: intentionally failing NO-GO until all public/final evidence exists.

### 1.3 Evidence beats prose

Every final claim needs structured evidence, raw logs, and hashable artifacts.

For LP-0003, final evidence should include:

- submission/distributions/distribution-a.json
- submission/distributions/distribution-b.json
- submission/claims/claims-summary.json
- submission/TESTNET_EVIDENCE.json
- submission/LEZ_COST_BENCHMARKS.json
- submission/PROOF_BENCHMARKS.json
- submission/BASECAMP_NATIVE_BUILD.md
- submission/BASECAMP_LOAD_EVIDENCE.json
- docs/FINAL_EVIDENCE_COLLECTION.md
- submission/FINAL_PUBLICATION_AUDIT.md
- submission/PR_DRAFT.md
- submission/raw-logs/*.log
- hashes of raw logs and packaged assets

Validators should parse raw logs where practical and reject placeholder strings like TBD, placeholder, mock, demo-only, video pending, pending public release.

### 1.4 RISC0 proof freshness matters

After any change to circuit/guest/shared serialization code, archived receipts may still verify against old image IDs but are no longer final evidence for the current source.

Plan gate:

- Include proof artifact manifests with source commit, image id, receipt hash, journal hash, RISC0_DEV_MODE=0, created_at, command, and guest source tree hash.
- final-publication-check.py must fail if proof artifacts predate guest/core source changes or manifest commit differs from HEAD.

### 1.5 Claim honesty around LEZ transport and CU metrics

If LEZ tooling cannot carry raw receipts or expose stable per-transaction CU counters, say so precisely.

Acceptable wording pattern:

- Host-side RISC0_DEV_MODE=0 proof generated and verified.
- LEZ wrapper/localnet/testnet transaction binds to receipt_sha256 and journal commitment.
- Full receipt is file-backed evidence due current LEZ transport limits.
- CU metering unavailable: submission/LEZ_COST_BENCHMARKS.json records cu_metering.available=false with exact reason and links to opened Logos issue.

Unacceptable:

- invented CU values.
- claiming full in-wrapper proof verification if we only did compact receipt-hash binding.
- claiming mock/local fixture evidence is live LEZ evidence.

### 1.6 Competitor PR #44 risk signals

Current LP-0003 competitor:

- PR #44, Timidan, open since 2026-05-08.
- Automated validation passed on 2026-05-13.
- Reviewer/user discussion highlighted two risk areas: LEZ devnet/testnet evidence and private-input/public-transcript semantics.
- The submitter explicitly had to clarify whether witness-like fields in claim_private are shielded/private inputs or visible in public transaction data/logs.

Our response:

- Make public transcript privacy independently verifiable.
- Add tests and docs proving eligible address, salt/secret, Merkle path, and signature/witness material are absent from public journal, public transaction payloads, logs, and submitted LEZ wrapper data.
- Include a docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md that names exactly what is public and private at every stage.

## 2. Proposed Architecture

### 2.1 Workspace layout

Create a Rust workspace with clear crate boundaries:

- Cargo.toml
- README.md
- LICENSE-MIT
- LICENSE-APACHE
- demo.sh
- module.json
- core/
  - Pure deterministic relation and data model.
  - Eligibility commitments, Merkle root, nullifiers, distribution ids, claim journals.
- methods/
  - RISC0 method package.
- methods/guest/
  - RISC0 guest proving private eligibility and claim uniqueness.
- host/
  - RISC0 proof generation/verification adapter.
  - Artifact CLIs for generating real proof receipts and manifests.
- lez-program/
  - LEZ-shaped distribution and claim state machine.
  - create_distribution, claim, query_distribution, query_claim_nullifier.
- sdk/
  - High-level API for distributors and claimants.
  - Used by CLI, consumer demo, Basecamp app bridge.
- cli/
  - lp0003 create-distribution, prove-claim, submit-claim, verify-artifacts, generate-demo-evidence.
- consumer-demo/
  - Clone-and-run demo app importing SDK as library deps.
- basecamp-app/
  - Native/QML/Qt Basecamp-loadable package, metadata, .lgx packaging scripts.
- interfaces/
  - lp0003.spel
  - lp0003.idl.json
- scripts/
  - check-prereqs.sh
  - ci-safe-lane.sh
  - validate-submission-readiness.py
  - final-publication-check.py
  - generate-20-claim-evidence.sh
  - demo-video.sh
  - record-demo-video.sh
  - package-basecamp-lgx.py
  - validate-basecamp-native.sh
  - attach-final-demo-video.py
- docs/
  - ARCHITECTURE.md
  - PRIVACY_MODEL.md
  - PRIVATE_INPUT_TRANSCRIPT_MODEL.md
  - PROTOCOL.md
  - SPEC_COMPLIANCE.md
  - INTEGRATION_GUIDE.md
  - DEMO_VIDEO_SCRIPT.md
  - LIMITATIONS.md
- submission/
  - PR_DRAFT.md
  - FINAL_PUBLICATION_AUDIT.md
  - TESTNET_EVIDENCE.json
  - LEZ_COST_BENCHMARKS.json
  - PROOF_BENCHMARKS.json
  - distributions/
  - claims/
  - proof-artifacts/
  - raw-logs/

### 2.2 Protocol sketch

Definitions:

- distribution_id = H("lp0003:distribution" || distributor_pub || nonce || merkle_root || allocation_policy_hash)
- leaf_secret: claimant-side random secret or shielded identity secret.
- leaf_commitment = H("lp0003:eligible-leaf" || distribution_id || claimant_identity_commitment || allocation || leaf_secret_or_salt)
- merkle_root commits to all eligible leaves.
- nullifier = H("lp0003:nullifier" || distribution_id || claimant_nullifier_secret)
- claim_context = H("lp0003:claim-context" || distribution_id || recipient_commitment || allocation || claim_nonce)
- receipt_journal_commitment = H("lp0003:receipt-journal" || receipt_sha256 || journal_sha256)

Private witness:

- claimant identity secret or shielded account opening.
- leaf_secret/salt.
- Merkle path.
- allocation witness, if allocation is per-leaf.
- optional claimant signature proving control of shielded/private credential.

Public journal:

- distribution_id.
- merkle_root.
- nullifier.
- allocation or allocation_commitment depending selected privacy tradeoff.
- recipient commitment or shielded destination commitment, not raw public wallet address.
- claim_context.
- proof_id / receipt hash / image id.

Explicit privacy choice to decide early:

Option A: fixed allocation per distribution.
- Simpler; journal can expose only distribution amount.
- Best for prize acceptance and 20-claim evidence.

Option B: per-leaf allocation visible at claim.
- More flexible but leaks allocation class.

Recommendation: start with Option A for final submission, with per-leaf allocation documented as future work. LP-0003 scope does not require hiding total allocation and does not require dynamic eligibility.

### 2.3 LEZ state model

Accounts/state:

- Distribution account:
  - distributor_pub
  - distribution_id
  - merkle_root
  - fixed_allocation
  - token_or_gate_target
  - claim_count
  - total_claim_limit
  - status: Active / Closed
  - metadata_hash

- Nullifier account/PDA:
  - distribution_id
  - nullifier
  - claimed_at block/slot if available
  - claim_tx_hash/signature

Instructions:

- create_distribution(distribution_config)
- claim(claim_payload)
- close_distribution(distribution_id)
- query_distribution(distribution_id)
- query_nullifier(distribution_id, nullifier)

Deterministic error codes:

- InvalidDistributionConfig
- DistributionAlreadyExists
- DistributionClosed
- InvalidMerkleRoot
- InvalidReceiptImageId
- InvalidProof
- JournalDistributionMismatch
- JournalRootMismatch
- JournalNullifierMismatch
- NullifierAlreadyClaimed
- ClaimPayloadMalformed
- RecipientCommitmentMalformed
- AmountMismatch
- ProofExpiredOrStale
- InternalSequencerUnavailable

Reliability invariant:

- Failed/rejected claims must not write the nullifier account.
- Nullifier write happens only after proof/journal validation succeeds.

## 3. Privacy Model Requirements

Docs must explicitly state what each party learns.

### 3.1 On-chain observer learns

- A distribution exists.
- Its merkle_root, fixed allocation, total eligible count if included, total claim count, and public metadata hash.
- A nullifier for each successful claim.
- A recipient commitment or shielded destination commitment.
- Timing/order of claims.
- Possibly allocation amount if not hidden by fixed distribution model.

### 3.2 On-chain observer must not learn

- raw eligible addresses.
- which eligible leaf produced a claim.
- Merkle path.
- claimant identity secret.
- leaf salt/secret.
- signature/witness material.

### 3.3 Distributor learns

- The original eligibility set if they created it.
- The final merkle root.
- Claim count and nullifiers.
- Timing of claims.
- They should not learn which eligible member claimed unless they can correlate timing, recipient commitments, off-chain UX, or unique allocation values.

### 3.4 Residual leakage to admit honestly

- Timing correlation may reduce anonymity sets.
- Small distributions provide small anonymity sets.
- Unique allocation amounts can deanonymize claimants, so final demo should use fixed allocations.
- Distributor knows the eligibility set they created; privacy is unlinkability at claim time, not hiding eligibility from the distributor.
- Network-layer metadata is out of scope unless claims are routed through privacy-preserving transport.
- Total eligible count / total allocation are out of scope per spec and may be public.

## 4. Evidence Plan: 2 Distributions / 20 Claims

Create deterministic demo fixtures plus real proof artifacts:

- Distribution A: 10 eligible leaves, fixed allocation, 10 successful unique claims.
- Distribution B: 10 eligible leaves, fixed allocation, 10 successful unique claims.
- Rejection cases:
  - duplicate claim using same nullifier.
  - invalid Merkle path.
  - wrong distribution_id.
  - wrong merkle_root.
  - malformed recipient commitment.

Artifacts:

- submission/distributions/distribution-a.json
- submission/distributions/distribution-b.json
- submission/claims/distribution-a-claims.jsonl
- submission/claims/distribution-b-claims.jsonl
- submission/claims/rejections.jsonl
- submission/claims/claims-summary.json with unique_claim_count=20 and distribution_count=2
- raw logs showing proof generation, submit transactions, accepted/rejected outcomes
- hashes for all logs and artifacts

Validator rules:

- exactly or at least 2 distributions.
- combined unique successful nullifiers >= 20.
- no duplicate nullifier accepted.
- rejected claims do not increment claim_count.
- all evidence references real commands/logs, not hand-written prose only.

## 5. Build Phases

### Phase 0: Grounding and scaffold

Definition of done:

- Repo scaffold exists.
- Prize spec copied into docs/spec/ or referenced in docs.
- Current competitor/criteria audit captured in docs/COMPETITOR_AND_CRITERIA_AUDIT.md.
- CI skeleton and license files present.

Tasks:

1. Create workspace and crate skeleton.
2. Add README with NO-GO status and exact intended evidence gates.
3. Add scripts/check-prereqs.sh for rust, cargo, cargo-risczero, rzup/r0vm, lgs, spel, docker, protoc, python3, cmake/qt if Basecamp native build is in scope.
4. Add docs/SPEC_COMPLIANCE.md with every LP-0003 criterion marked PENDING.
5. Add scripts/validate-submission-readiness.py that initially fails for missing crates/docs/evidence.
6. Add scripts/final-publication-check.py that intentionally fails all final gates.

### Phase 1: Pure Rust relation and tests

Definition of done:

- core crate models distributions, leaves, Merkle inclusion, nullifiers, journals, and error codes.
- Privacy boundary tests prove private witness values are absent from public journal structs.
- Unit tests cover happy path and rejection paths.

Key tests:

- create distribution root from deterministic leaves.
- valid claim produces expected nullifier.
- same claimant/distribution produces same nullifier.
- same claimant/different distribution produces different nullifier.
- invalid Merkle path rejected.
- wrong root rejected.
- duplicate nullifier rejected by state model.
- journal serialization excludes raw identity, salt, Merkle path, and witness fields.

### Phase 2: SDK, CLI, and consumer demo

Definition of done:

- SDK gives clean distributor and claimant APIs.
- CLI can generate distributions, produce claim fixtures, verify journals, and run local claim simulations.
- consumer-demo imports SDK/core as library dependencies and runs realistic scenarios.

Scenarios:

1. Distribution A: create 10-person fixed allocation airdrop and claim all 10.
2. Distribution B: token-gated allowlist registration and claim all 10.
3. Duplicate claim rejected and original accepted claim remains valid.
4. Wrong distribution proof rejected.
5. Proof generation failure surfaced cleanly without marking claimed.

### Phase 3: RISC0 guest/host heavy lane

Definition of done:

- RISC0 guest proves membership and emits public journal.
- Host generates RISC0_DEV_MODE=0 receipts for fixture claims.
- Host verifies receipts and writes manifests.
- Proof freshness validator exists.

Commands to support:

- RISC0_DEV_MODE=0 cargo risczero build --manifest-path methods/guest/Cargo.toml
- RISC0_PROVER=ipc RISC0_DEV_MODE=0 cargo run -p lp0003-host --bin lp0003-prove-fixtures --release
- cargo run -p lp0003-host --bin lp0003-verify-artifacts -- submission/proof-artifacts/manifest.json

Pitfalls to avoid:

- Do not run cargo risczero build at workspace root if it tries to build host binaries for guest target.
- Pin dependencies compatible with RISC0 rustc 1.88.0-dev if ruint or other crates demand newer rustc.
- Prefer external r0vm IPC on macOS to avoid Xcode/Metal linker traps.
- Decode journal wrapping correctly if committing Vec<u8> bytes.

### Phase 4: LEZ program, SPEL IDL, local sequencer evidence

Definition of done:

- LEZ-shaped program accepts create_distribution and claim payloads.
- IDL and .spel include exact discriminators and deterministic errors.
- Local sequencer demo submits distribution and claim transactions.
- Evidence binds LEZ transactions to receipt/journal hashes.

Deliverables:

- lez-program/src/lib.rs
- interfaces/lp0003.spel
- interfaces/lp0003.idl.json
- scripts/validate-idl.py
- submission/TESTNET_EVIDENCE.json
- raw logs for deploy, create distribution, claims, duplicate rejection

Honesty gate:

- If full receipt cannot be transported through LEZ, use compact receipt/journal commitment and document full receipt host-side verification.

### Phase 5: 2 distributions / 20 claim evidence run

Definition of done:

- scripts/generate-20-claim-evidence.sh creates or verifies two real distributions and 20 unique accepted claims.
- The script also runs rejection cases.
- Claims summary and raw logs are machine-validated.

Command:

- RISC0_DEV_MODE=0 bash scripts/generate-20-claim-evidence.sh

Expected outputs:

- PASS distribution_count >= 2
- PASS unique_claim_count >= 20
- PASS duplicate rejection observed
- PASS invalid proof rejection observed
- PASS no private witness values in public logs/artifacts

### Phase 6: Basecamp native app

Definition of done:

- Basecamp app builds as native/QML/Qt loadable package or accepted LogosBasecamp module.
- .lgx package is reproducible.
- Load/open evidence is captured.

Minimum UI flow:

- Create distribution from CSV/fixture.
- View merkle root/distribution id.
- Import claimant secret/fixture.
- Generate proof or invoke CLI-backed proof.
- Submit claim.
- Show accepted claim and nullifier.
- Show duplicate rejection with clear user-facing error.

Files:

- basecamp-app/CMakeLists.txt
- basecamp-app/metadata.json
- basecamp-app/include/IComponent.h if matching Basecamp plugin convention
- basecamp-app/src/*.cpp
- basecamp-app/qml/*.qml
- basecamp-app/resources.qrc
- scripts/package-basecamp-lgx.py
- scripts/validate-basecamp-native.sh

### Phase 7: Docs and submission package

Definition of done:

- Docs precisely match implementation and evidence.
- No stale pending language in final docs after evidence is attached.
- Solution draft uses exact upstream template headings.

Required docs:

- README.md: clean clone usage.
- docs/ARCHITECTURE.md: component diagram and flow.
- docs/PROTOCOL.md: commitment scheme, nullifier scheme, LEZ account model, error codes.
- docs/PRIVACY_MODEL.md: threat model, observer/distributor/user knowledge, residual leakage.
- docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md: public vs private payload/journal/log evidence.
- docs/INTEGRATION_GUIDE.md: SDK/CLI/Basecamp usage.
- docs/SPEC_COMPLIANCE.md: criterion-by-criterion PASS/PARTIAL/PENDING evidence matrix.
- submission/BENCHMARKS.md or JSON files for proof/CU evidence.
- submission/PR_DRAFT.md with solutions/LP-0003.md content.

### Phase 8: Demo video and final publication gate

Definition of done:

- scripts/demo-video.sh runs end-to-end from clean state or clearly explains prereq setup.
- Recording shows RISC0_DEV_MODE=0 terminal output and proof generation.
- Narration covers architecture, privacy model, key decisions, limitations, evidence for 2 distributions / 20 claims, and Basecamp app.
- final-publication-check.py passes only after public repo, video, CI, Basecamp, LEZ, benchmarks, and solution draft are ready.

Recording style:

- Use polished section headers and pauses.
- Avoid overclaiming: distinguish live proof generation, live local sequencer/testnet evidence, and pre-recorded artifacts if any.
- Keep under 12 minutes if possible.

## 6. Validators and Gates

### 6.1 Local readiness validator

scripts/validate-submission-readiness.py should check:

- required files exist.
- cargo fmt/check/test pass for safe-lane crates.
- docs/SPEC_COMPLIANCE.md has all LP-0003 criteria.
- interfaces/lp0003.idl.json parses and discriminators match sha256("global:<instruction>")[:8].
- docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md exists.
- root demo.sh exists and is executable.
- no obvious placeholder/TBD in local-ready docs except final-publication docs that are expected NO-GO.

### 6.2 Final publication validator

scripts/final-publication-check.py should fail until:

- public repo URL exists and module.json.repository is not TBD.
- CI workflow exists and is green on default branch.
- solutions/LP-0003.md or submission/PR_DRAFT.md uses exact upstream headings:
  - Summary
  - Repository
  - Approach
  - Success Criteria Checklist
  - FURPS Self-Assessment
  - Supporting Materials
  - Terms & Conditions
- narrated demo video URL is attached and not marked pending.
- Basecamp app is native/loadable or .lgx packaged with load evidence.
- LEZ deployment/testnet/localnet evidence is present with program id, tx/signature/block/slot or explicit localnet evaluator evidence.
- 2 distributions and >=20 unique claims are proven by structured evidence and raw logs.
- RISC0_DEV_MODE=0 proof artifacts are fresh against current source.
- CU/proof benchmarks exist, or CU unavailable is documented with a Logos issue and exact tooling limitation.
- no private witness leaks are found in public journals/logs/artifacts.
- all raw evidence hashes match.

## 7. Submission Acceptance Checklist

Functionality:

- [ ] Distributor commits to hidden eligibility set on-chain.
- [ ] Recipient claims without revealing eligible address.
- [ ] Double claim prevented by nullifier.
- [ ] Observer cannot link claim to eligible address under stated threat model.
- [ ] Full privacy model documented.
- [ ] Working LEZ demo.
- [ ] 2 distributions / 20 unique claims with reproducible evidence.
- [ ] Clean public repo.

Usability:

- [ ] SDK/module exists.
- [ ] CLI exists.
- [ ] Basecamp-loadable app exists.
- [ ] SPEL IDL exists.

Reliability:

- [ ] Proof generation failure is cleanly surfaced.
- [ ] Failed claim does not mark claimed.
- [ ] Deterministic error codes documented and tested.

Performance:

- [ ] Proof generation time measured.
- [ ] Receipt/journal/payload sizes measured.
- [ ] LEZ operation costs documented or CU limitation recorded honestly.

Supportability:

- [ ] LEZ devnet/testnet/localnet deployment evidence.
- [ ] Sequencer integration tests in CI or documented CI-compatible standalone mode.
- [ ] Default branch CI green.
- [ ] README has clean clone instructions.
- [ ] demo.sh and scripts/demo-video.sh are reproducible.
- [ ] Narrated video included.

## 8. Initial Implementation Task List

Task 1: Create scaffold.
- Create workspace, license files, README, module.json, docs/SPEC_COMPLIANCE.md, scripts/check-prereqs.sh.
- Verification: python3 scripts/validate-submission-readiness.py fails with expected missing implementation gates.

Task 2: Implement core distribution and leaf types.
- Create core/src/types.rs and tests.
- Verification: cargo test -p lp0003-core distribution_types.

Task 3: Implement deterministic Merkle fixture utilities.
- Create core/src/merkle.rs.
- Verification: valid path passes, wrong path fails.

Task 4: Implement nullifier and journal model.
- Create core/src/nullifier.rs and core/src/journal.rs.
- Verification: privacy serialization test confirms no raw witness fields.

Task 5: Implement pure Rust claim relation.
- Create core/src/relation.rs.
- Verification: happy path plus wrong root/wrong distribution/duplicate model tests.

Task 6: Add SDK high-level API.
- Create sdk/src/lib.rs.
- Verification: SDK integration test creates a distribution and claims once.

Task 7: Add CLI safe-lane commands.
- Create cli/src/main.rs.
- Verification: cargo run -p lp0003-cli -- demo-fixtures --out target/lp0003-fixtures.

Task 8: Add consumer-demo.
- Create consumer-demo with 5 scenarios.
- Verification: cargo run -p lp0003-consumer-demo prints all PASS.

Task 9: Add RISC0 guest skeleton.
- Create methods/guest and host boundary types.
- Verification: guest check/build scoped to guest manifest.

Task 10: Add host proof artifact path.
- Create host binaries for prove-fixtures and verify-artifacts.
- Verification: dev-mode smoke first, then M4 heavy-lane RISC0_DEV_MODE=0.

Task 11: Add LEZ wrapper/state model.
- Create lez-program with create_distribution and claim.
- Verification: local tests for accepted claim and duplicate rejection.

Task 12: Generate SPEL/IDL.
- Create interfaces/lp0003.spel and lp0003.idl.json.
- Verification: scripts/validate-idl.py passes discriminators and errors.

Task 13: Add evidence generator.
- Create scripts/generate-20-claim-evidence.sh.
- Verification: creates 2 distributions, 20 claims, and rejection artifacts.

Task 14: Add Basecamp native app package.
- Create basecamp-app native/QML shape and package script.
- Verification: scripts/validate-basecamp-native.sh and package hash.

Task 15: Add final docs and PR draft.
- Fill README, docs, submission/PR_DRAFT.md.
- Verification: local readiness passes; final publication check remains NO-GO until public/video/live evidence attached.

Task 16: Clean-clone rehearsal.
- Clone public/private candidate into fresh temp dir.
- Run demo.sh, CI safe lane, validators.
- Verification: record exact commands and logs under submission/raw-logs/.

Task 17: Final video and solution PR prep.
- Attach video URL, update solution draft, run final-publication-check.py.
- Verification: only after Evi approval, prepare upstream PR; do not open without explicit approval.

## 9. Open Decisions for Evi

1. Fixed allocation only for final demo, with variable allocations future work? Recommendation: yes.
2. Repo name: lp-0003-private-airdrop vs lp-0003-private-allowlist. Recommendation: lp-0003-private-airdrop because it is concrete and demo-friendly.
3. Basecamp implementation depth: full native/QML first-class app now, or scaffold package plus CLI bridge? Recommendation: native/QML package from the start; LP-0005 taught us not to fake this.
4. LEZ evidence target wording: treat evaluator localnet as testnet-equivalent if the current Logos flow expects local sequencer evidence, but keep the docs explicit. Recommendation: use local sequencer/localnet evidence first, then public/evaluator testnet wording only if supported by current tooling/spec clarification.
5. Airdrop vs allowlist demo theme. Recommendation: airdrop for Distribution A, allowlist gate for Distribution B, both using the same primitive.
6. Allocation privacy. Recommendation: fixed amount in final submission to maximize unlinkability and avoid unique-amount leakage.

## 10. Current Risk Register

High risk:

- Basecamp package not accepted as loadable by real LogosBasecamp.
- LEZ/RISC0 transport limitations around full receipts.
- Current LP-0003 PR #44 may be accepted first.
- Proof artifacts going stale after source changes.

Medium risk:

- CU metrics unavailable in current LEZ tooling.
- RISC0 build time / M4 scheduling constraints.
- Public transcript semantics misunderstood by reviewers.
- Demo video overclaims pre-recorded evidence as live.

Mitigations:

- Build final-publication-check.py early and keep it strict.
- Write transcript privacy doc before implementation hides complexity in code.
- Capture raw logs and hashes during every evidence run.
- Avoid source changes after final proof generation unless proofs are regenerated.
- Treat Basecamp as a first-class deliverable, not polish.

## 11. Immediate Next Step

Start with Phase 0 and Phase 1. The first concrete deliverable should be a scaffolded workspace whose validators fail honestly, followed by a pure Rust relation with privacy-boundary tests. Once that moonlit core is correct, the RISC0/LEZ/Basecamp layers can be woven around it without pretending the spell is complete before it is.


## Added final-proof publication guardrails

- `scripts/prepare-risc0-proof-artifacts.py` packages real externally generated `RISC0_DEV_MODE=0` receipt/journal/log artifacts into `submission/proof-artifacts/manifest.json` without fabricating evidence.
- `scripts/validate-proof-artifacts.py` now requires `current_source_sha256`, so stale proof manifests fail after source changes.
- `scripts/validate-upstream-solution.py` simulates the upstream lambda-prize solution-template checks before any public PR is opened.
