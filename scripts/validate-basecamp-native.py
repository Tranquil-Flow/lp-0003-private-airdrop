#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "basecamp-app/CMakeLists.txt",
    "basecamp-app/metadata.json",
    "basecamp-app/include/IComponent.h",
    "basecamp-app/src/Lp0003Component.cpp",
    "basecamp-app/src/Lp0003Component.h",
    "basecamp-app/qml/Main.qml",
    "basecamp-app/resources.qrc",
    "scripts/package-basecamp-lgx.py",
]


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            failures.append(f"MISSING {rel}")

    try:
        metadata = json.loads((ROOT / "basecamp-app" / "metadata.json").read_text())
    except Exception as exc:
        failures.append(f"metadata parse failed: {exc}")
        metadata = {}

    if metadata.get("kind") != "logos-basecamp-native-qml":
        failures.append("metadata kind must be logos-basecamp-native-qml")
    if metadata.get("status") != "source-package-only-not-load-evidence":
        failures.append("metadata must keep honest source-package-only-not-load-evidence status")

    result = subprocess.run(
        ["python3", "scripts/package-basecamp-lgx.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        failures.append("package-basecamp-lgx.py failed:\n" + result.stdout)

    manifest_path = ROOT / "dist" / "lp0003-private-airdrop.lgx.manifest.json"
    if not manifest_path.exists():
        failures.append("missing .lgx manifest after packaging")
    else:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("final_basecamp_load_evidence") is not False:
            failures.append("package manifest must not claim final load evidence")

    if failures:
        print("LP-0003 Basecamp native/QML source package: NO-GO")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("PASS Basecamp native/QML source package")
    print("PASS deterministic .lgx source package")
    print("NOT final Basecamp load evidence: runtime load log still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
