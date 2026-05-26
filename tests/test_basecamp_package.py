import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_basecamp_native_source_shape_exists():
    required = [
        "basecamp-app/CMakeLists.txt",
        "basecamp-app/metadata.json",
        "basecamp-app/include/IComponent.h",
        "basecamp-app/src/Lp0003Component.cpp",
        "basecamp-app/src/Lp0003Component.h",
        "basecamp-app/qml/Main.qml",
        "basecamp-app/resources.qrc",
        "scripts/package-basecamp-lgx.py",
        "scripts/validate-basecamp-native.py",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), f"missing Basecamp native source artifact: {rel}"

    metadata = json.loads((ROOT / "basecamp-app" / "metadata.json").read_text())
    assert metadata["id"] == "lp0003-private-airdrop"
    assert metadata["kind"] == "logos-basecamp-native-qml"
    assert metadata["status"] == "source-package-only-not-load-evidence"


def test_lgx_packaging_is_deterministic_and_honest(tmp_path):
    package = ROOT / "dist" / "lp0003-private-airdrop.lgx"
    if package.exists():
        package.unlink()

    first = subprocess.run(
        ["python3", "scripts/package-basecamp-lgx.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    assert "source-package-only-not-load-evidence" in first.stdout
    assert package.exists()
    first_hash = hashlib.sha256(package.read_bytes()).hexdigest()

    second = subprocess.run(
        ["python3", "scripts/package-basecamp-lgx.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    second_hash = hashlib.sha256(package.read_bytes()).hexdigest()
    assert first_hash == second_hash
    assert first_hash in second.stdout


def test_basecamp_validator_passes_source_package_but_not_load_evidence():
    result = subprocess.run(
        ["python3", "scripts/validate-basecamp-native.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0
    assert "PASS Basecamp native/QML source package" in result.stdout
    assert "NOT final Basecamp load evidence" in result.stdout
