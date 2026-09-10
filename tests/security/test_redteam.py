from app.redteam.attacks import run_red_team


def test_red_team_mitigates_critical_cases():
    report = run_red_team()
    assert report["security_score"] > 0
    assert report["critical_vulnerabilities"] == 0, "All critical red-team cases must be mitigated"
