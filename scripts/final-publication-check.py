#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def raw_hashes_valid(raw_log_sha256) -> bool:
    if not isinstance(raw_log_sha256, dict) or not raw_log_sha256:
        return False
    for rel_path, expected in raw_log_sha256.items():
        if not isinstance(rel_path, str) or not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            return False
        log_path = (ROOT / rel_path).resolve()
        try:
            log_path.relative_to(ROOT)
        except ValueError:
            return False
        if not log_path.exists() or sha256_file(log_path) != expected:
            return False
    return True
print('LP-0003 final publication: NO-GO')
blockers = []

def blocker(name: str):
    print(f'BLOCKER {name}')
    blockers.append(name)

def pass_gate(name: str):
    print(f'PASS {name}')

# Public repo gate.
module_path = ROOT / 'module.json'
repo = ''
if module_path.exists():
    try:
        repo = json.loads(module_path.read_text()).get('repository', '')
    except Exception:
        repo = ''
if re.match(r'^https://github\.com/[^/]+/[^/]+/?$', repo or '') and 'TBD' not in repo:
    pass_gate('public repository URL')
else:
    blocker('public repository URL')

# Video gate.
pr_draft = (ROOT / 'submission' / 'PR_DRAFT.md').read_text() if (ROOT / 'submission' / 'PR_DRAFT.md').exists() else ''
if re.search(r'https://(www\.)?(youtube\.com|youtu\.be|loom\.com|vimeo\.com)/\S+', pr_draft) and 'Pending' not in pr_draft:
    pass_gate('narrated demo video URL')
else:
    blocker('narrated demo video URL')

# Basecamp gate. A deterministic .lgx source package is useful, but final
# readiness requires real runtime load/activation evidence from Basecamp.
basecamp_evidence = ROOT / 'submission' / 'BASECAMP_LOAD_EVIDENCE.json'
try:
    basecamp = json.loads(basecamp_evidence.read_text()) if basecamp_evidence.exists() else {}
    package_path = ROOT / 'dist' / 'lp0003-private-airdrop.lgx'
    basecamp_ready = (
        package_path.exists()
        and basecamp.get('final_load_evidence') is True
        and basecamp.get('status') == 'basecamp-runtime-loaded'
        and raw_hashes_valid(basecamp.get('raw_log_sha256'))
        and bool(basecamp.get('loaded_component_id'))
    )
    if basecamp_ready:
        pass_gate('Basecamp-loadable app evidence')
    else:
        blocker('Basecamp-loadable app evidence')
except Exception:
    blocker('Basecamp-loadable app evidence')

# Distribution/claim evidence gate. Safe-lane counts are useful, but final
# publication must be backed by real RISC0/LEZ/localnet evidence.
claims_summary = ROOT / 'submission' / 'claims' / 'claims-summary.json'
try:
    data = json.loads(claims_summary.read_text()) if claims_summary.exists() else {}
    final_claim_evidence = (
        data.get('distribution_count', 0) >= 2
        and data.get('unique_claim_count', 0) >= 20
        and data.get('final_evidence') is True
        and data.get('evidence_source') in {'lez-risc0-localnet', 'lez-risc0-testnet'}
        and raw_hashes_valid(data.get('raw_log_sha256'))
    )
    if final_claim_evidence:
        pass_gate('2 distributions / 20 unique claims evidence')
    else:
        blocker('2 distributions / 20 unique claims evidence')
except Exception:
    blocker('2 distributions / 20 unique claims evidence')

# Proof freshness gate.
manifest = ROOT / 'submission' / 'proof-artifacts' / 'manifest.json'
try:
    import importlib.util
    validator_path = ROOT / 'scripts' / 'validate-proof-artifacts.py'
    spec = importlib.util.spec_from_file_location('lp0003_validate_proof_artifacts', validator_path)
    validator = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(validator)
    ok, _message = validator.validate(manifest) if manifest.exists() else (False, 'missing')
    if ok:
        pass_gate('fresh RISC0_DEV_MODE=0 proof artifacts')
    else:
        blocker('fresh RISC0_DEV_MODE=0 proof artifacts')
except Exception:
    blocker('fresh RISC0_DEV_MODE=0 proof artifacts')

# Benchmark gates. LP-0003 requires proof-generation time and LEZ compute-unit
# documentation. These must be raw-log-bound, not prose-only numbers.
proof_bench_path = ROOT / 'submission' / 'PROOF_BENCHMARKS.json'
try:
    proof_bench = json.loads(proof_bench_path.read_text()) if proof_bench_path.exists() else {}
    proof_bench_ready = (
        proof_bench.get('final_benchmark_evidence') is True
        and proof_bench.get('risc0_dev_mode') == 0
        and isinstance(proof_bench.get('proof_generation_seconds'), (int, float))
        and proof_bench.get('proof_generation_seconds') > 0
        and 'RISC0_DEV_MODE=0' in str(proof_bench.get('command', ''))
        and raw_hashes_valid(proof_bench.get('raw_log_sha256'))
    )
    if proof_bench_ready:
        pass_gate('proof generation benchmark evidence')
    else:
        blocker('proof generation benchmark evidence')
except Exception:
    blocker('proof generation benchmark evidence')

cost_bench_path = ROOT / 'submission' / 'LEZ_COST_BENCHMARKS.json'
try:
    cost_bench = json.loads(cost_bench_path.read_text()) if cost_bench_path.exists() else {}
    operations = cost_bench.get('operations')
    op_names = {op.get('operation') for op in operations} if isinstance(operations, list) else set()
    op_evidence_ok = isinstance(operations, list) and all(
        isinstance(op, dict)
        and op.get('tx_count', 0) > 0
        and (
            isinstance(op.get('cu_per_tx'), (int, float))
            or (op.get('cu_metering_available') is False and bool(op.get('cu_unavailable_reason')))
        )
        for op in operations
    )
    cost_bench_ready = (
        cost_bench.get('final_benchmark_evidence') is True
        and cost_bench.get('evidence_source') in {'lez-risc0-localnet', 'lez-risc0-testnet'}
        and {'create_distribution', 'claim'} <= op_names
        and op_evidence_ok
        and raw_hashes_valid(cost_bench.get('raw_log_sha256'))
    )
    if cost_bench_ready:
        pass_gate('LEZ compute unit benchmark evidence')
    else:
        blocker('LEZ compute unit benchmark evidence')
except Exception:
    blocker('LEZ compute unit benchmark evidence')

# Logos issue-report gate. The public submission must either link issues opened
# for Logos technology problems encountered, or explicitly attest that the final
# run encountered no Logos-technology blockers requiring an issue.
issues_path = ROOT / 'submission' / 'LOGOS_TECH_ISSUES.md'
issues_text = issues_path.read_text() if issues_path.exists() else ''
issue_links = re.findall(r'https://github\.com/[^\s)]+/issues/\d+', issues_text)
explicit_no_issue = (
    'No Logos technology issues were encountered' in issues_text
    and 'LP-0003 final run' in issues_text
)
if issue_links or explicit_no_issue:
    pass_gate('Logos technology issue report')
else:
    blocker('Logos technology issue report')

# CI gate.
if (ROOT / '.github' / 'workflows').exists() or (ROOT / '.gitlab-ci.yml').exists():
    pass_gate('CI workflow exists')
else:
    blocker('CI workflow exists')

# Solution template gate.
required = ['## Summary','## Repository','## Approach','## Success Criteria Checklist','## FURPS Self-Assessment','## Terms & Conditions']
if all(h in pr_draft for h in required) and 'TBD' not in pr_draft and 'Pending' not in pr_draft and 'DRAFT' not in pr_draft:
    pass_gate('solution template complete')
else:
    blocker('solution template complete')

sys.exit(1 if blockers else 0)
