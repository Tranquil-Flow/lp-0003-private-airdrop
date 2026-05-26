#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

required_docs = [
    'PLAN.md',
    'README.md',
    'docs/SPEC_COMPLIANCE.md',
    'docs/PRIVACY_MODEL.md',
    'docs/PRIVATE_INPUT_TRANSCRIPT_MODEL.md',
    'docs/ARCHITECTURE.md',
    'docs/PROTOCOL.md',
    'docs/INTEGRATION_GUIDE.md',
    'docs/DEMO_VIDEO_SCRIPT.md',
    'docs/LIMITATIONS.md',
    'docs/FINAL_EVIDENCE_COLLECTION.md',
    'submission/FINAL_PUBLICATION_AUDIT.md',
    'submission/PR_DRAFT.md',
]

print('LP-0003 local readiness: NO-GO')
failures = []

missing = [p for p in required_docs if not (ROOT / p).exists()]
if missing:
    for p in missing:
        print(f'MISSING required documentation skeleton: {p}')
        failures.append(p)
else:
    print('PASS required documentation skeleton')

# Implementation gates. These intentionally stay pending until the layer exists.
core_lib = ROOT / 'core' / 'src' / 'lib.rs'
core_text = core_lib.read_text() if core_lib.exists() else ''
if 'pub mod relation' in core_text and 'pub mod merkle' in core_text and 'pub mod claim' in core_text:
    print('PASS core relation implementation')
else:
    print('PENDING core relation implementation')
    failures.append('core relation implementation')

manifest = ROOT / 'submission' / 'proof-artifacts' / 'manifest.json'
if manifest.exists():
    proof_result = subprocess.run(
        ['python3', str(ROOT / 'scripts' / 'validate-proof-artifacts.py'), str(manifest)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proof_result.returncode == 0:
        print('PASS RISC0 proof artifacts')
    else:
        print('PENDING RISC0 proof artifacts')
        failures.append('RISC0 proof artifacts')
else:
    print('PENDING RISC0 proof artifacts')
    failures.append('RISC0 proof artifacts')

if (ROOT / 'interfaces' / 'lp0003.idl.json').exists() and (ROOT / 'interfaces' / 'lp0003.spel').exists():
    print('PASS LEZ/SPEL integration')
else:
    print('PENDING LEZ/SPEL integration')
    failures.append('LEZ/SPEL integration')

if (ROOT / 'demo.sh').exists():
    print('PASS root demo.sh exists')
else:
    print('MISSING root demo.sh')
    failures.append('demo.sh')

sys.exit(1 if failures else 0)
