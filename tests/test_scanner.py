import json
from src.nodes import checkov_scanner
from src.state import AgentState

def test_scanner_filters_iam_findings(tmp_path, monkeypatch):
    (tmp_path / "main.tf").write_text("resource \"aws_iam_policy\" \"x\" {}")
    monkeypatch.setattr(checkov_scanner, "_run_checkov", lambda _: ({"results": {"failed_checks": [{"check_id": "CKV_AWS_1", "resource": "aws_iam_policy.x"}, {"check_id": "CKV_AWS_20"}]}}, 1))
    result = checkov_scanner.scan(AgentState(repo_path=str(tmp_path)))
    assert len(result.checkov_findings) == 1
    assert result.checkov_findings[0]["check_id"] == "CKV_AWS_1"

