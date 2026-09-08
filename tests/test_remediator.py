from src.nodes import iac_remediator
from src.state import AgentState

class FakeChatCompletion:
    @staticmethod
    def create(**kwargs):
        return {"choices": [{"message": {"content": '{"files": {"main.tf": "resource \\\"aws_iam_policy\\\" \\\"x\\\" {}"}}'}}]}

def test_remediator_parses_structured_response(monkeypatch):
    monkeypatch.setattr(iac_remediator.openai, "ChatCompletion", FakeChatCompletion)
    monkeypatch.setattr(iac_remediator, "get_settings", lambda: type("S", (), {"openai_api_key": "test", "llm_model": "test"})())
    result = iac_remediator.remediate(AgentState(repo_path=".", raw_tf_code={"main.tf": "x"}))
    assert "main.tf" in result.remediated_tf_code
