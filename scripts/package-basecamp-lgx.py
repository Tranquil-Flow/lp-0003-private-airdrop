#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "basecamp-app"
DIST = ROOT / "dist"
PACKAGE = DIST / "lp0003-private-airdrop.lgx"
FIXED_ZIP_TIME = (2026, 5, 26, 0, 0, 0)

INCLUDE = [
    "CMakeLists.txt",
    "metadata.json",
    "include/IComponent.h",
    "src/Lp0003Component.cpp",
    "src/Lp0003Component.h",
    "qml/Main.qml",
    "resources.qrc",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    missing = [rel for rel in INCLUDE if not (APP / rel).exists()]
    if missing:
        raise SystemExit(f"missing Basecamp source files: {', '.join(missing)}")

    metadata = json.loads((APP / "metadata.json").read_text())
    if metadata.get("status") != "source-package-only-not-load-evidence":
        raise SystemExit("metadata must honestly mark package as source-package-only-not-load-evidence")

    DIST.mkdir(exist_ok=True)
    if PACKAGE.exists():
        PACKAGE.unlink()

    with zipfile.ZipFile(PACKAGE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in sorted(INCLUDE):
            source = APP / rel
            info = zipfile.ZipInfo(f"basecamp-app/{rel}", FIXED_ZIP_TIME)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, source.read_bytes())

    digest = sha256(PACKAGE)
    manifest = {
        "package": str(PACKAGE.relative_to(ROOT)),
        "sha256": digest,
        "status": "source-package-only-not-load-evidence",
        "final_basecamp_load_evidence": False,
        "included_files": sorted(INCLUDE),
    }
    (DIST / "lp0003-private-airdrop.lgx.manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {PACKAGE}")
    print(f"sha256 {digest}")
    print("status source-package-only-not-load-evidence")
    print("NOTE: this is not final Basecamp runtime load evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
