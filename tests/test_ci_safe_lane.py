import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ci_safe_lane_script_runs_all_non_heavy_gates():
    script = ROOT / "scripts" / "ci-safe-lane.sh"
    assert script.exists()
    text = script.read_text()
    for required in [
        "cargo fmt --all --check",
        "cargo test --workspace",
        "python3 -m pytest tests -q",
        "python3 scripts/validate-basecamp-native.py",
        "python3 scripts/validate-submission-readiness.py",
        "python3 scripts/final-publication-check.py",
    ]:
        assert required in text

    result = subprocess.run(
        ["bash", "scripts/ci-safe-lane.sh"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "PASS final publication gate remains NO-GO" in result.stdout
