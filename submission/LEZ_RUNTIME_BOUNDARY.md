# LP-0003 LEZ Runtime Boundary

Status: deployment-probe-only-not-final-claim-or-cost-evidence.

Observed live on the M4 Pro:

- LEZ localnet was managed and ready at http://127.0.0.1:3040.
- RISC0_DEV_MODE=0 was set for the evidence lane.
- lgs deploy claim_proof --program-path ... --json returned status=submitted.
- Program id: ac01d872f551bbaf825740825d7cc1f135e9cd8992cf221b775863abf5062033.
- The strict final extractors correctly refused this probe as final claim/CU evidence because it lacks create/claim transaction ids, 2-distribution/20-claim accepted evidence, duplicate rejection evidence, and operation-bound CU telemetry.

Raw logs:

- submission/raw-logs/lez-deployment-probe.log
- submission/raw-logs/lez-extractor-boundary.log

Structured boundary JSON: submission/LEZ_RUNTIME_BOUNDARY.json
