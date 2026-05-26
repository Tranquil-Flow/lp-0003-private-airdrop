import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_consumer_demo_reports_twenty_safe_lane_claims():
    result = subprocess.run(
        ["cargo", "run", "-p", "lp0003-consumer-demo", "--quiet"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0
    assert "LP-0003 consumer demo: PASS" in result.stdout
    assert "distributions: 2" in result.stdout
    assert "unique claims: 20" in result.stdout
    assert "SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE" in result.stdout
